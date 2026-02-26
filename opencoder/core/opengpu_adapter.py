"""
OpenGPU Relay Adapter for OpenCoder

This module provides an adapter that connects OpenCoder to the OpenGPU Relay network.
It uses an OpenAI-compatible client to communicate with models hosted on OpenGPU.

Assumptions about OpenGPU Relay API:
- Base URL format: https://relay.opengpu.network/v1 (configurable)
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
    base_url: str = "https://relay.opengpu.network/v1"
    api_key: str = ""
    default_model: str = "gpt-4o"
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
            base_url=os.getenv("OPENGPU_BASE_URL", "https://relay.opengpu.network/v1"),
            api_key=os.getenv("OPENGPU_API_KEY", ""),
            default_model=os.getenv("OPENGPU_MODEL", "gpt-4o"),
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
                max_retries=3
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
        
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.config.max_tokens,
            **kwargs
        }
        
        if stream:
            return self._stream_chat(request_params)
        else:
            response = await self.client.chat.completions.create(**request_params)
            return response.model_dump()
    
    async def _stream_chat(
        self,
        request_params: dict[str, Any]
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Handle streaming chat responses.
        
        Args:
            request_params: Parameters for the chat completion request.
        
        Yields:
            Chunk dictionaries for each streaming response.
        """
        request_params["stream"] = True
        stream = await self.client.chat.completions.create(**request_params)
        
        async for chunk in stream:
            yield chunk.model_dump()
    
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
                    f"{self.config.base_url}/v2/models",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse models from the response
            models = []
            
            # Process auto and direct categories
            for category in ['auto', 'direct']:
                if category in data:
                    for provider, provider_models in data[category].items():
                        if provider == 'openai' or provider == 'anthropic':
                            for model_info in provider_models:
                                if model_info.get('tag') == 'text-to-text':
                                    full_name = f"{provider}/{model_info['name']}"
                                    models.append({
                                        "name": full_name,
                                        "provider": provider,
                                        "type": "text-to-text",
                                        "category": category
                                    })
            
            return models
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            # Return empty list instead of hardcoded fallback
            return []
    
    async def get_pricing(self) -> list[dict]:
        """Get pricing information from OpenGPU Relay.
        
        Returns:
            List of pricing info dictionaries.
        """
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/v2/pricing",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
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
