"""
OpenGPU Relay Adapter for OpenCoder

This module provides an adapter that connects OpenCoder to the OpenGPU Relay network.
It uses an OpenAI-compatible client to communicate with models hosted on OpenGPU.

Assumptions about OpenGPU Relay API:
  - Base URL format: https://relaygpu.com/backend/openai/v1 (configurable)
  - Note: relay.opengpu.network returns 302 redirects that don't work with litellm
- Authentication via API key header
- OpenAI-compatible endpoint structure (/chat/completions)
- Supports streaming and non-streaming responses

Reference: https://opengpu-network.gitbook.io/relay/
"""

import os
from typing import Any, AsyncGenerator, Optional
from dataclasses import dataclass, field

from openai import AsyncOpenAI
from loguru import logger


# Custom Exceptions
class OpenGPUError(Exception):
    """Base exception for OpenGPU adapter."""
    pass


def normalize_model_for_api(model: str) -> str:
    """Normalize model name for API comparison.
    
    Only removes "openai/" prefix. Other providers are kept as-is.
    
    Args:
        model: Model name (e.g., "openai/gpt-5.2", "Qwen/Qwen3-Coder")
    
    Returns:
        Normalized model name for comparison
    """
    if model.startswith("openai/"):
        return model[7:]  # Remove "openai/" prefix
    return model


class OpenGPUAPIError(OpenGPUError):
    """Exception for API-related errors."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class OpenGPUAuthError(OpenGPUError):
    """Exception for authentication errors."""
    pass


# Aider import - optional
try:
    from aider.models import Model as AiderModel
except ImportError:
    AiderModel = None


# Preferred models - only show these models in the UI
# Set to None to show all available models
# Format: provider/model-name
PREFERRED_MODELS = [
    # OpenGPU models
    "anthropic/claude-opus-4-6",
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-5.2",
    "deepseek-ai/DeepSeek-V3.1",
    "Qwen/Qwen3-Coder",
    "moonshotai/kimi-k2.5",
    "qwen/qwen2.5-vl-72b-instruct",
    # Ollama models
    "ollama/gpt-oss:20b",
    "ollama/llama3.2:3b",
    "ollama/deepseek-r1:8b",
]


@dataclass
class OpenGPUConfig:
    """Configuration for OpenGPU Relay connection.
    
    Attributes:
        base_url: The base URL for the OpenGPU Relay API.
        api_key: API key for authentication.
        default_model: Default model to use if not specified.
        timeout: Request timeout in seconds.
        max_tokens: Maximum tokens for model responses.
    """
    base_url: str = "https://relaygpu.com/backend/openai/v1"
    api_key: str = ""
    default_model: str = ""
    timeout: float = 120.0
    max_tokens: int = 4096


class OpenGPUAdapter:
    """Adapter for connecting to OpenGPU Relay models.
    
    This class provides a wrapper around the OpenAI-compatible client
    to work with Aider's model interface. It handles the connection
    to OpenGPU Relay and provides methods for chat completions.
    
    Example:
        >>> config = OpenGPUConfig(
        ...     base_url="https://relay.opengpu.network/v1",
        ...     api_key="your-api-key",
        ...     default_model="gpt-4o"
        ... )
        >>> adapter = OpenGPUAdapter(config)
        >>> response = await adapter.chat_complete([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """
    
    def __init__(self, config: Optional[OpenGPUConfig] = None) -> None:
        """Initialize the OpenGPU adapter.
        
        Args:
            config: Configuration for the adapter. If not provided,
                   will attempt to load from environment variables.
        """
        self.config = config or self._load_config_from_env()
        self._client: Optional[AsyncOpenAI] = None
    
    def _load_config_from_env(self) -> OpenGPUConfig:
        """Load configuration from environment variables.
        
        Returns:
            OpenGPUConfig with values from environment.
        """
        return OpenGPUConfig(
            base_url=os.getenv("OPENGPU_BASE_URL", "https://relaygpu.com/backend/openai/v1"),
            api_key=os.getenv("OPENGPU_API_KEY", ""),
            default_model=os.getenv("OPENGPU_MODEL", ""),
            timeout=float(os.getenv("OPENGPU_TIMEOUT", "120.0")),
            max_tokens=int(os.getenv("OPENGPU_MAX_TOKENS", "4096"))
        )
    
    @property
    def client(self) -> AsyncOpenAI:
        """Get or create the OpenAI-compatible client.
        
        Returns:
            AsyncOpenAI client configured for OpenGPU Relay.
        """
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                timeout=self.config.timeout,
                max_retries=3,
                default_headers={
                    "X-API-Key": self.config.api_key
                }
            )
        return self._client
    
    async def chat_complete(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any
    ) -> dict[str, Any] | AsyncGenerator[dict[str, Any], None]:
        """Send a chat completion request to OpenGPU Relay.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Model to use. Defaults to config.default_model.
            temperature: Sampling temperature (0.0 to 2.0).
            stream: Whether to stream the response.
            **kwargs: Additional model-specific parameters.
        
        Returns:
            Response dictionary or async generator for streaming.
        
        Raises:
            Exception: If the API request fails.
        """
        if not model:
            model = self.config.default_model
        
        # Parse model name to extract provider
        # Format: "provider/model-name" or just "model-name"
        # Examples: "ollama/llama3.2:3b", "openai/gpt-5.2", "anthropic/claude-opus-4-6", "gpt-oss:20b"
        # IMPORTANT: For OpenGPU relay, models like "Qwen/Qwen3-Coder" should NOT be split
        # because "Qwen" is not a litellm provider, it's part of the model name
        # Only split if the prefix is a known provider (openai, anthropic, ollama)
        known_providers = ["openai", "anthropic", "ollama"]
        if "/" in model:
            potential_provider = model.split("/")[0].lower()
            if potential_provider in known_providers:
                provider, model_name = model.split("/", 1)
            else:
                # Unknown provider prefix - treat the whole thing as the model name
                # and use openai-compatible endpoint
                provider = "openai"
                model_name = model
        else:
            # Default to openai-compatible endpoint if no provider specified
            provider = "openai"
            model_name = model
        
        # Determine the correct endpoint based on provider
        # Note: Ollama uses a different path structure
        # Base URL for backend services - use relaygpu.com directly to avoid redirects
        backend_base = "https://relaygpu.com/backend"
        
        if provider == "ollama":
            # Ollama: /v2/ollama/api/chat (not /backend/ollama/v1/...)
            provider_url = "https://relay.opengpu.network/v2/ollama/api/chat"
        elif provider == "anthropic":
            # Anthropic: /backend/anthropic/v1/messages
            provider_url = f"{backend_base}/anthropic/v1/messages"
        else:
            # OpenAI-compatible (openai, deepseek, qwen, moonshotai, etc.): /backend/openai/v1/chat/completions
            provider_url = f"{backend_base}/openai/v1/chat/completions"
        
        logger.info(f"Sending request to {provider_url} with model {model_name}")
        
        # Build request - only include valid fields for the provider
        request_params = {
            "model": model_name,
            "messages": messages
        }
        
        # Only add temperature for non-ollama providers (ollama uses different param)
        if provider != "ollama":
            request_params["temperature"] = temperature
            request_params["max_tokens"] = self.config.max_tokens
        
        if stream:
            return self._stream_chat(request_params, provider_url)
        else:
            # Use httpx directly for custom endpoint
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    provider_url,
                    json=request_params,
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()
    
    async def _stream_chat(
        self,
        request_params: dict[str, Any],
        provider_url: str = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Handle streaming chat responses.
        
        Args:
            request_params: Parameters for the chat completion request.
            provider_url: The provider-specific URL to call.
        
        Yields:
            Chunk dictionaries for each streaming response.
        """
        import httpx
        
        request_params["stream"] = True
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                provider_url,
                json=request_params,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.config.timeout
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        yield line
    
    async def close(self) -> None:
        """Close the client connection."""
        if self._client is not None:
            await self.client.close()
            self._client = None
    
    async def get_available_models(self) -> list[dict]:
        """Get list of available models from OpenGPU Relay.
        
        Returns:
            List of model info dictionaries with name, provider, and type.
        """
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://relay.opengpu.network/v2/models",
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse models from the response
            models = []
            seen_models = set()  # Avoid duplicates
            
            # Process auto, direct, and opengpu categories
            for category in ['auto', 'direct', 'opengpu']:
                if category in data:
                    for provider, provider_models in data[category].items():
                        for model_info in provider_models:
                            # Only include text-to-text models for coding
                            if model_info.get('tag') == 'text-to-text':
                                # Model names from API may already include provider prefix
                                # e.g., "anthropic/claude-opus-4-6" with provider "anthropic"
                                model_name = model_info['name']
                                if '/' in model_name:
                                    # Already has provider prefix, use as-is
                                    full_name = model_name
                                else:
                                    # No prefix, add provider
                                    full_name = f"{provider}/{model_name}"
                                
                                # Skip if already added (avoid duplicates)
                                if full_name in seen_models:
                                    continue
                                
                                # Filter by preferred models if configured
                                if PREFERRED_MODELS is not None:
                                    # Check if this model is in the preferred list
                                    model_lower = full_name.lower()
                                    preferred_lower = [p.lower() for p in PREFERRED_MODELS]
                                    # Check exact match or partial match
                                    if not any(
                                        model_lower == p or 
                                        model_lower.endswith('/' + p.split('/')[-1].lower())
                                        for p in preferred_lower
                                    ):
                                        continue
                                
                                seen_models.add(full_name)
                                
                                # Format display name: extract last part and clean up
                                display_name = self._format_model_display_name(
                                    provider, 
                                    model_info['name']
                                )
                                models.append({
                                    "name": full_name,
                                    "display_name": display_name,
                                    "provider": provider,
                                    "type": model_info.get('tag', 'text-to-text'),
                                    "category": category
                                })
            
            return models
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    def _format_model_display_name(self, provider: str, model_name: str) -> str:
        """Format model name for display in UI.
        
        Args:
            provider: The provider name (e.g., 'ollama', 'openai', 'anthropic')
            model_name: The model name from API
            
        Returns:
            Formatted display name (e.g., 'Gpt-oss:20b', 'Qwen3-Coder')
        """
        # Extract the last part after / if present
        display = model_name.split('/')[-1] if '/' in model_name else model_name
        
        # Remove provider prefix duplicates (e.g., 'openai/openai/gpt-5.2' -> 'gpt-5.2')
        if provider.lower() in display.lower():
            parts = display.split('/')
            # Get the last meaningful part
            for part in reversed(parts):
                if part.lower() != provider.lower():
                    display = part
                    break
        
        # Handle specific model naming conventions
        # Keep original casing for most part but fix common issues
        
        # Handle GPT models - keep "GPT" capitalized, rest lowercase
        if display.lower().startswith('gpt'):
            display = display.replace('GPT', 'Gpt').replace('gpt', 'Gpt')
        
        # Handle Llama models - keep "Llama" capitalized
        if display.lower().startswith('llama'):
            display = display.replace('Llama', 'Llama').replace('llama', 'Llama')
        
        # Handle DeepSeek models - use lowercase "deepseek" to match user preference
        if 'deepseek' in display.lower():
            display = display.replace('DeepSeek', 'Deepseek').replace('deepseek', 'Deepseek')
            # Keep capital V for version numbers
            if 'v3' in display.lower():
                display = display.replace('v3', 'V3')
        
        # Handle Qwen models - keep "Qwen" capitalized
        if 'qwen' in display.lower():
            display = display.replace('Qwen', 'Qwen').replace('qwen', 'Qwen')
        
        # Handle Claude - keep capitalized
        if 'claude' in display.lower():
            display = display.replace('Claude', 'Claude').replace('claude', 'Claude')
        
        # Handle Kimi - keep capitalized
        if 'kimi' in display.lower():
            display = display.replace('Kimi', 'Kimi').replace('kimi', 'Kimi')
        
        # Ensure model sizes (like :20b, :3b) stay lowercase
        # Already in lowercase from API, so just ensure consistency
        
        return display
    
    async def get_pricing(self) -> list[dict]:
        """Get pricing information from OpenGPU Relay.
        
        Returns:
            List of pricing info dictionaries.
        """
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://relay.opengpu.network/v2/pricing",
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
            return data.get("pricing", [])
        except Exception as e:
            logger.error(f"Error fetching pricing: {e}")
            return []


class AiderOpenGPUModel:
    """Wrapper to make OpenGPUAdapter compatible with Aider's model interface.
    
    Aider expects a model class with specific methods. This wrapper
    adapts the OpenGPU adapter to work with Aider's expectations.
    
    Reference: https://github.com/Aider-AI/aider
    """
    
    def __init__(
        self,
        model_name: str,
        adapter: Optional[OpenGPUAdapter] = None
    ) -> None:
        """Initialize the Aider-compatible model wrapper.
        
        Args:
            model_name: The model identifier to use.
            adapter: OpenGPUAdapter instance. If not provided, creates one.
        """
        self.model_name = model_name
        self.adapter = adapter or OpenGPUAdapter()
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        stream: bool = False
    ) -> dict[str, Any] | AsyncGenerator[dict[str, Any], None]:
        """Send chat request to the model.
        
        Args:
            messages: List of message dictionaries.
            stream: Whether to stream the response.
        
        Returns:
            Model response or stream generator.
        """
        return await self.adapter.chat_complete(
            messages=messages,
            model=self.model_name,
            stream=stream
        )
    
    async def __aenter__(self) -> "AiderOpenGPUModel":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.adapter.close()
