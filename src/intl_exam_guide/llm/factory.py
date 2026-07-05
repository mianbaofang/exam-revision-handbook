"""Factory for creating LLM providers based on configuration.

This module provides a factory function to instantiate the appropriate
LLM provider based on the configuration settings.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from intl_exam_guide.llm.fallback_provider import FallbackProvider
from intl_exam_guide.llm.provider import LLMContextProvider

logger = logging.getLogger(__name__)


def create_llm_provider(config: dict[str, Any]) -> LLMContextProvider | None:
    """Create an LLM provider based on configuration.

    Args:
        config: Configuration dictionary containing 'llm' section

    Returns:
        LLMContextProvider instance or None if no provider can be created
        Returns FallbackProvider if:
        - provider is "fallback" or "none"
        - provider is "openai" but API key is missing
        - provider is "openai" but fallback is enabled and creation fails
    """
    llm_config = config.get("llm", {})
    provider_name = llm_config.get("provider", "fallback")

    # Normalize provider name
    if provider_name is None or provider_name == "none":
        provider_name = "fallback"

    logger.info(f"Creating LLM provider: {provider_name}")

    # Handle fallback provider
    if provider_name == "fallback":
        return _create_fallback_provider(llm_config)

    # Handle OpenAI provider
    if provider_name == "openai":
        openai_provider = _create_openai_provider(llm_config, config)

        # If OpenAI creation failed and fallback is enabled, use fallback
        if openai_provider is None and llm_config.get("fallback", {}).get("enabled", True):
            logger.warning("Falling back to fallback provider due to OpenAI setup failure")
            return _create_fallback_provider(llm_config)

        return openai_provider

    # Unknown provider
    logger.error(
        f"Unknown LLM provider '{provider_name}'. Valid options: 'openai', 'fallback', 'none'"
    )

    # Use fallback as last resort
    if llm_config.get("fallback", {}).get("enabled", True):
        logger.warning("Falling back to fallback provider due to invalid provider name")
        return _create_fallback_provider(llm_config)

    return None


def _create_openai_provider(
    llm_config: dict[str, Any], full_config: dict[str, Any]
) -> LLMContextProvider | None:
    """Create OpenAI provider with configuration.

    Args:
        llm_config: LLM configuration section
        full_config: Full configuration dictionary (for getting API key)

    Returns:
        OpenAIProvider instance or None if creation fails
    """
    try:
        from intl_exam_guide.llm.openai_provider import OpenAIProvider
    except ImportError as e:
        logger.error(f"Failed to import OpenAIProvider: {e}")
        return None

    openai_config = llm_config.get("openai", {})

    # Get API key from environment
    from intl_exam_guide.config import get_api_key_from_env

    api_key = get_api_key_from_env(full_config)

    if not api_key:
        env_var = openai_config.get("api_key_env", "OPENAI_API_KEY")
        logger.warning(
            f"OpenAI API key not found in environment variable '{env_var}'. "
            "Cannot create OpenAI provider."
        )
        return None

    # Create provider with configuration
    try:
        provider = OpenAIProvider(
            api_key=api_key,
            model=openai_config.get("model", "gpt-4"),
            max_retries=openai_config.get("max_retries", 3),
            timeout=openai_config.get("timeout_seconds", 30),
            cost_limit_usd=openai_config.get("cost_limit_per_handbook_usd", 5.0),
        )
        logger.info(f"Created OpenAI provider with model {openai_config.get('model', 'gpt-4')}")
        return provider

    except Exception as e:
        logger.error(f"Failed to create OpenAI provider: {e}")
        return None


def _create_fallback_provider(llm_config: dict[str, Any]) -> FallbackProvider:
    """Create fallback provider with configuration.

    Args:
        llm_config: LLM configuration section

    Returns:
        FallbackProvider instance
    """
    fallback_config = llm_config.get("fallback", {})
    output_dir = fallback_config.get("output_dir", ".")

    provider = FallbackProvider(output_dir=Path(output_dir))
    logger.info(f"Created fallback provider (output_dir: {output_dir})")
    return provider
