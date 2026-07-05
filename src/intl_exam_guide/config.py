"""Configuration management for the revision guide generator.

This module handles loading and validating configuration from YAML files.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "llm": {
        "provider": "fallback",
        "openai": {
            "api_key_env": "OPENAI_API_KEY",
            "model": "gpt-4",
            "max_retries": 3,
            "timeout_seconds": 30,
            "cost_limit_per_handbook_usd": 5.0,
            "max_concurrency": 5,
        },
        "fallback": {
            "enabled": True,
            "output_dir": ".",
        },
    },
    "generation": {
        "questions_per_topic": 1,
        "explanation_style": "friendly",
        "output_language": "en",
    },
    "images": {
        "provider": "prompt-queue",
    },
}


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load configuration from YAML file with fallback to defaults.

    Args:
        config_path: Path to config.yml file. If None, looks for config.yml
                    in the project root. If file doesn't exist, returns defaults.

    Returns:
        Configuration dictionary with all required fields

    Raises:
        ValueError: If YAML is invalid or configuration structure is incorrect
    """
    # Determine config file path
    if config_path is None:
        # Look for config.yml in project root (parent of src/)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.yml"

    # If config file doesn't exist, return defaults
    if not config_path.exists():
        logger.info(
            f"Config file not found at {config_path}, using default configuration. "
            "Copy config.example.yml to config.yml to customize settings."
        )
        return DEFAULT_CONFIG.copy()

    # Load YAML
    try:
        import yaml

        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f)

        if user_config is None:
            logger.warning(f"Empty config file at {config_path}, using defaults")
            return DEFAULT_CONFIG.copy()

    except ImportError:
        logger.error(
            "PyYAML not installed. Install with: pip install pyyaml. Using default config."
        )
        return DEFAULT_CONFIG.copy()
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file {config_path}: {e}") from e
    except Exception as e:
        raise ValueError(f"Error reading config file {config_path}: {e}") from e

    # Merge with defaults (user config overrides defaults)
    config = _deep_merge(DEFAULT_CONFIG, user_config)

    # Validate configuration
    _validate_config(config)

    logger.info(f"Loaded configuration from {config_path}")
    return config


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override dict into base dict.

    Args:
        base: Base dictionary (will not be modified)
        override: Override dictionary

    Returns:
        New merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def _validate_config(config: dict[str, Any]) -> None:
    """Validate configuration structure and values.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate LLM provider
    if "llm" not in config:
        raise ValueError("Missing 'llm' section in configuration")

    llm_config = config["llm"]
    provider = llm_config.get("provider")

    if provider not in ["openai", "fallback", "none", None]:
        raise ValueError(
            f"Invalid LLM provider '{provider}'. Must be 'openai', 'fallback', or 'none'"
        )

    # Validate OpenAI config if using OpenAI
    if provider == "openai":
        if "openai" not in llm_config:
            raise ValueError("Missing 'openai' section when provider is 'openai'")

        openai_config = llm_config["openai"]
        required_fields = ["api_key_env", "model"]

        for field in required_fields:
            if field not in openai_config:
                raise ValueError(f"Missing required field 'llm.openai.{field}'")

        # Validate numeric fields
        if "max_retries" in openai_config:
            max_retries = openai_config["max_retries"]
            if not isinstance(max_retries, int) or max_retries < 0:
                raise ValueError("llm.openai.max_retries must be a non-negative integer")

        if "timeout_seconds" in openai_config:
            timeout = openai_config["timeout_seconds"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ValueError("llm.openai.timeout_seconds must be a positive number")

        if "cost_limit_per_handbook_usd" in openai_config:
            cost_limit = openai_config["cost_limit_per_handbook_usd"]
            if not isinstance(cost_limit, (int, float)) or cost_limit < 0:
                raise ValueError(
                    "llm.openai.cost_limit_per_handbook_usd must be a non-negative number"
                )

        if "max_concurrency" in openai_config:
            max_concurrency = openai_config["max_concurrency"]
            if not isinstance(max_concurrency, int) or max_concurrency < 1:
                raise ValueError("llm.openai.max_concurrency must be a positive integer")

    # Validate generation config
    if "generation" in config:
        gen_config = config["generation"]

        if "explanation_style" in gen_config:
            valid_styles = ["friendly", "formal", "life", "story", "detective", "adventure"]
            style = gen_config["explanation_style"]
            if style not in valid_styles:
                raise ValueError(
                    f"Invalid explanation_style '{style}'. "
                    f"Must be one of: {', '.join(valid_styles)}"
                )

        if "output_language" in gen_config:
            valid_languages = ["en", "zh-CN"]
            lang = gen_config["output_language"]
            if lang not in valid_languages:
                raise ValueError(
                    f"Invalid output_language '{lang}'. "
                    f"Must be one of: {', '.join(valid_languages)}"
                )


def get_api_key_from_env(config: dict[str, Any]) -> str | None:
    """Get OpenAI API key from environment variable specified in config.

    Args:
        config: Configuration dictionary

    Returns:
        API key string or None if not found
    """
    api_key_env = config.get("llm", {}).get("openai", {}).get("api_key_env")
    if not api_key_env:
        return None

    api_key = os.environ.get(api_key_env)
    if not api_key:
        logger.warning(
            f"Environment variable '{api_key_env}' not set. OpenAI provider will not be available."
        )
        return None

    return api_key
