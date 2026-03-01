"""
LiteLLM Patch for OpenGPU Relay

This module patches litellm to use httpx directly instead of its internal client,
avoiding the "Your request was blocked" error from OpenGPU.

IMPORTANT: This module must be imported BEFORE any import of aider.

Usage:
    from opencoder.core.litellm_patch import patch_litellm_for_opengpu
    patch_litellm_for_opengpu()
    
    # Then import aider normally
    from aider.coders import Coder
"""

import os
import asyncio
import httpx
from typing import Any, Dict, List, Optional
from loguru import logger


class OpenGPUPatchError(Exception):
    """Error específico del parche de OpenGPU."""
    pass


class MockMessage:
    """Mock del objeto Message que litellm espera."""
    
    def __init__(self, content: str, role: str = "assistant"):
        self.content = content
        self.role = role
    
    def __repr__(self):
        return f"Message(role='{self.role}', content='{self.content[:50]}...')"


class MockChoice:
    """Mock del objeto Choice que litellm espera."""
    
    def __init__(self, message: MockMessage, finish_reason: str = "stop"):
        self.message = message
        self.finish_reason = finish_reason
        self.index = 0
    
    def __repr__(self):
        return f"Choice(finish_reason='{self.finish_reason}')"


class MockUsage:
    """Mock del objeto Usage que litellm espera."""
    
    def __init__(self, prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
    
    def __repr__(self):
        return f"Usage(total={self.total_tokens})"


class MockCompletionResponse:
    """
    Mock de la respuesta de completion que litellm y Aider esperan.
    
    This class mimics the OpenAI response structure so that
    litellm and Aider can process it correctly.
    """
    
    def __init__(
        self,
        choices: List[MockChoice],
        model: str,
        usage: MockUsage,
        response_id: str = "",
        created: int = 0,
    ):
        self.choices = choices
        self.model = model
        self.usage = usage
        self.id = response_id
        self.created = created
        self.object = "chat.completion"
    
    def __repr__(self):
        return f"CompletionResponse(model='{self.model}', choices={len(self.choices)})"


async def _call_opengpu_async(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs
) -> Dict[str, Any]:
    """
    Realiza una llamada asíncrona a OpenGPU usando httpx.
    
    Args:
        base_url: URL base de OpenGPU.
        api_key: API key de autenticación.
        model: Nombre del modelo.
        messages: Lista de mensajes.
        temperature: Temperatura de muestreo.
        max_tokens: Máximo de tokens.
        **kwargs: Parámetros adicionales.
    
    Returns:
        Respuesta JSON de OpenGPU.
    
    Raises:
        OpenGPUPatchError: Si la llamada falla.
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    
    # Build payload with only valid parameters
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": "auto",
    }
    
    # Add optional valid parameters
    if "top_p" in kwargs:
        payload["top_p"] = kwargs["top_p"]
    if "stream" in kwargs:
        payload["stream"] = kwargs["stream"]
    if "stop" in kwargs:
        payload["stop"] = kwargs["stop"]
    
    logger.debug(f"[OpenGPU Patch] Calling: {url}")
    logger.debug(f"[OpenGPU Patch] Model: {model}")
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )
            
            # Log status for debugging
            logger.debug(f"[OpenGPU Patch] Status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"[OpenGPU Patch] Error {response.status_code}: {error_text}")
                raise OpenGPUPatchError(f"OpenGPU error {response.status_code}: {error_text}")
            
            return response.json()
    
    except httpx.TimeoutException:
        raise OpenGPUPatchError("Timeout calling OpenGPU")
    except httpx.RequestError as e:
        raise OpenGPUPatchError(f"Network error: {str(e)}")


def custom_completion(
    model: str,
    messages: List[Dict[str, str]],
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs
) -> MockCompletionResponse:
    """
    Custom completion function that uses httpx directly.
    
    This function replaces litellm.completion to avoid the problematic headers
    that cause "Your request was blocked" in OpenGPU.
    
    Args:
        model: Model name (e.g., "openai/Qwen/Qwen3-Coder" or "Qwen/Qwen3-Coder").
        messages: List of messages with role and content.
        api_key: OpenGPU API key.
        api_base: OpenGPU base URL.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens in response.
        **kwargs: Additional parameters.
    
    Returns:
        MockCompletionResponse with the model response.
    """
    # Get configuration from environment variables if not provided
    final_api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENGPU_API_KEY", "")
    final_base_url = api_base or os.getenv("OPENAI_API_BASE") or os.getenv("OPENGPU_BASE_URL", "https://relaygpu.com/backend/openai/v1")
    
    # Clean the model: remove "openai/" prefix if present
    # Keep full model name including provider
    clean_model = model
    
    logger.info(f"[OpenGPU Patch] Completion request")
    logger.info(f"[OpenGPU Patch]   Model: {clean_model}")
    logger.info(f"[OpenGPU Patch]   Base URL: {final_base_url}")
    logger.info(f"[OpenGPU Patch]   Messages: {len(messages)}")
    
    # Execute async call
    try:
        # Always create a new event loop to avoid conflicts
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                _call_opengpu_async(
                    base_url=final_base_url,
                    api_key=final_api_key,
                    model=clean_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            )
            result = future.result(timeout=180)
    except Exception as e:
        logger.error(f"[OpenGPU Patch] Error in completion: {e}")
        raise
    
    # Parse response
    choices = []
    for choice_data in result.get("choices", []):
        message = MockMessage(
            content=choice_data.get("message", {}).get("content", ""),
            role=choice_data.get("message", {}).get("role", "assistant")
        )
        choices.append(MockChoice(
            message=message,
            finish_reason=choice_data.get("finish_reason", "stop")
        ))
    
    usage_data = result.get("usage", {})
    usage = MockUsage(
        prompt_tokens=usage_data.get("prompt_tokens", 0),
        completion_tokens=usage_data.get("completion_tokens", 0),
        total_tokens=usage_data.get("total_tokens", 0)
    )
    
    response = MockCompletionResponse(
        choices=choices,
        model=result.get("model", clean_model),
        usage=usage,
        response_id=result.get("id", ""),
        created=result.get("created", 0)
    )
    
    logger.info(f"[OpenGPU Patch] Response received: {len(choices)} choices")
    logger.info(f"[OpenGPU Patch] Tokens: {usage.total_tokens}")
    
    return response


def patch_litellm_for_opengpu():
    """
    Apply the monkey patch to litellm to use httpx directly.
    
    This function must be called BEFORE importing aider or any
    module that uses litellm.
    
    Example:
        >>> from opencoder.core.litellm_patch import patch_litellm_for_opengpu
        >>> patch_litellm_for_opengpu()
        >>> # Now import aider
        >>> from aider.coders import Coder
    
    Raises:
        ImportError: If litellm is not installed.
    """
    try:
        import litellm
        
        # Save reference to original function (in case it needs to be restored)
        if not hasattr(litellm, '_original_completion'):
            litellm._original_completion = litellm.completion
        
        # Apply the patch
        litellm.completion = custom_completion
        
        # Also patch other functions that might be used
        if hasattr(litellm, 'acompletion'):
            # Create async version of custom_completion
            async def custom_acompletion(*args, **kwargs):
                return custom_completion(*args, **kwargs)
            litellm.acompletion = custom_acompletion
        
        logger.success("[OpenGPU Patch] litellm patched successfully")
        logger.info("[OpenGPU Patch] Now litellm will use httpx directly for OpenGPU")
        
    except ImportError as e:
        logger.warning(f"[OpenGPU Patch] litellm is not installed: {e}")
        logger.info("[OpenGPU Patch] Patch is not needed if litellm is not used")
    except Exception as e:
        logger.error(f"[OpenGPU Patch] Error applying patch: {e}")
        raise


def unpatch_litellm():
    """
    Restore litellm to its original state.
    
    Useful for testing or temporarily disabling the patch.
    """
    try:
        import litellm
        
        if hasattr(litellm, '_original_completion'):
            litellm.completion = litellm._original_completion
            delattr(litellm, '_original_completion')
            logger.info("[OpenGPU Patch] litellm restored to original state")
    
    except ImportError:
        pass
