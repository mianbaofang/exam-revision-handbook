"""Tests for configuration loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from intl_exam_guide.config import (
    DEFAULT_CONFIG,
    get_api_key_from_env,
    load_config,
)


def test_load_config_missing_file(tmp_path: Path) -> None:
    """Test that missing config file returns defaults."""
    config_path = tmp_path / "nonexistent.yml"
    config = load_config(config_path)

    assert config == DEFAULT_CONFIG
    assert config["llm"]["provider"] == "fallback"


def test_load_config_empty_file(tmp_path: Path) -> None:
    """Test that empty config file returns defaults."""
    config_path = tmp_path / "empty.yml"
    config_path.write_text("", encoding="utf-8")

    config = load_config(config_path)
    assert config == DEFAULT_CONFIG


def test_load_config_valid(tmp_path: Path) -> None:
    """Test loading a valid config file."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
llm:
  provider: openai
  openai:
    api_key_env: MY_API_KEY
    model: gpt-4-turbo
    max_retries: 5
    timeout_seconds: 60
    cost_limit_per_handbook_usd: 10.0
    max_concurrency: 10
generation:
  explanation_style: formal
  output_language: zh-CN
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config["llm"]["provider"] == "openai"
    assert config["llm"]["openai"]["api_key_env"] == "MY_API_KEY"
    assert config["llm"]["openai"]["model"] == "gpt-4-turbo"
    assert config["llm"]["openai"]["max_retries"] == 5
    assert config["llm"]["openai"]["timeout_seconds"] == 60
    assert config["llm"]["openai"]["cost_limit_per_handbook_usd"] == 10.0
    assert config["llm"]["openai"]["max_concurrency"] == 10
    assert config["generation"]["explanation_style"] == "formal"
    assert config["generation"]["output_language"] == "zh-CN"


def test_load_config_partial_override(tmp_path: Path) -> None:
    """Test that partial config overrides defaults correctly."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
llm:
  provider: openai
  openai:
    model: gpt-3.5-turbo
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    # Overridden values
    assert config["llm"]["provider"] == "openai"
    assert config["llm"]["openai"]["model"] == "gpt-3.5-turbo"

    # Default values still present
    assert config["llm"]["openai"]["api_key_env"] == "OPENAI_API_KEY"
    assert config["llm"]["openai"]["max_retries"] == 3
    assert config["generation"]["explanation_style"] == "friendly"


def test_load_config_invalid_yaml(tmp_path: Path) -> None:
    """Test that invalid YAML raises ValueError."""
    config_path = tmp_path / "invalid.yml"
    config_path.write_text(
        """
llm:
  provider: [unclosed list
  openai:
    model: gpt-4
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid YAML"):
        load_config(config_path)


def test_validate_config_missing_llm_section() -> None:
    """Test that missing LLM section raises ValueError."""
    from intl_exam_guide.config import _validate_config

    with pytest.raises(ValueError, match="Missing 'llm' section"):
        _validate_config({})


def test_validate_config_invalid_provider() -> None:
    """Test that invalid provider name raises ValueError."""
    from intl_exam_guide.config import _validate_config

    with pytest.raises(ValueError, match="Invalid LLM provider"):
        _validate_config({"llm": {"provider": "invalid_provider"}})


def test_validate_config_openai_missing_required_fields() -> None:
    """Test that OpenAI config without required fields raises ValueError."""
    from intl_exam_guide.config import _validate_config

    # Missing openai section
    with pytest.raises(ValueError, match="Missing 'openai' section"):
        _validate_config({"llm": {"provider": "openai"}})

    # Missing api_key_env
    with pytest.raises(ValueError, match="Missing required field.*api_key_env"):
        _validate_config({"llm": {"provider": "openai", "openai": {"model": "gpt-4"}}})

    # Missing model
    with pytest.raises(ValueError, match="Missing required field.*model"):
        _validate_config({"llm": {"provider": "openai", "openai": {"api_key_env": "KEY"}}})


def test_validate_config_invalid_numeric_values() -> None:
    """Test that invalid numeric values raise ValueError."""
    from intl_exam_guide.config import _validate_config

    # Negative max_retries
    with pytest.raises(ValueError, match="max_retries must be a non-negative integer"):
        _validate_config(
            {
                "llm": {
                    "provider": "openai",
                    "openai": {
                        "api_key_env": "KEY",
                        "model": "gpt-4",
                        "max_retries": -1,
                    },
                }
            }
        )

    # Non-positive timeout
    with pytest.raises(ValueError, match="timeout_seconds must be a positive number"):
        _validate_config(
            {
                "llm": {
                    "provider": "openai",
                    "openai": {
                        "api_key_env": "KEY",
                        "model": "gpt-4",
                        "timeout_seconds": 0,
                    },
                }
            }
        )

    # Negative cost limit
    with pytest.raises(ValueError, match="cost_limit.*must be a non-negative number"):
        _validate_config(
            {
                "llm": {
                    "provider": "openai",
                    "openai": {
                        "api_key_env": "KEY",
                        "model": "gpt-4",
                        "cost_limit_per_handbook_usd": -5.0,
                    },
                }
            }
        )

    # Invalid max_concurrency
    with pytest.raises(ValueError, match="max_concurrency must be a positive integer"):
        _validate_config(
            {
                "llm": {
                    "provider": "openai",
                    "openai": {
                        "api_key_env": "KEY",
                        "model": "gpt-4",
                        "max_concurrency": 0,
                    },
                }
            }
        )


def test_validate_config_invalid_explanation_style() -> None:
    """Test that invalid explanation style raises ValueError."""
    from intl_exam_guide.config import _validate_config

    with pytest.raises(ValueError, match="Invalid explanation_style"):
        _validate_config(
            {
                "llm": {"provider": "fallback"},
                "generation": {"explanation_style": "invalid_style"},
            }
        )


def test_validate_config_invalid_output_language() -> None:
    """Test that invalid output language raises ValueError."""
    from intl_exam_guide.config import _validate_config

    with pytest.raises(ValueError, match="Invalid output_language"):
        _validate_config(
            {
                "llm": {"provider": "fallback"},
                "generation": {"output_language": "invalid_lang"},
            }
        )


def test_validate_config_valid_openai() -> None:
    """Test that valid OpenAI config passes validation."""
    from intl_exam_guide.config import _validate_config

    config = {
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key_env": "OPENAI_API_KEY",
                "model": "gpt-4",
                "max_retries": 3,
                "timeout_seconds": 30,
                "cost_limit_per_handbook_usd": 5.0,
                "max_concurrency": 5,
            },
        }
    }

    # Should not raise
    _validate_config(config)


def test_validate_config_valid_fallback() -> None:
    """Test that valid fallback config passes validation."""
    from intl_exam_guide.config import _validate_config

    config = {"llm": {"provider": "fallback"}}

    # Should not raise
    _validate_config(config)


def test_get_api_key_from_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test getting API key from environment variable."""
    monkeypatch.setenv("TEST_API_KEY", "sk-test123")

    config = {
        "llm": {
            "openai": {
                "api_key_env": "TEST_API_KEY",
            }
        }
    }

    api_key = get_api_key_from_env(config)
    assert api_key == "sk-test123"


def test_get_api_key_from_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing environment variable returns None."""
    # Ensure the variable doesn't exist
    monkeypatch.delenv("TEST_API_KEY", raising=False)

    config = {
        "llm": {
            "openai": {
                "api_key_env": "TEST_API_KEY",
            }
        }
    }

    api_key = get_api_key_from_env(config)
    assert api_key is None


def test_get_api_key_from_env_missing_config() -> None:
    """Test that missing config returns None."""
    api_key = get_api_key_from_env({})
    assert api_key is None


def test_deep_merge() -> None:
    """Test deep merge functionality."""
    from intl_exam_guide.config import _deep_merge

    base = {
        "a": 1,
        "b": {"c": 2, "d": 3},
        "e": 4,
    }

    override = {
        "b": {"c": 10},
        "e": 20,
        "f": 30,
    }

    result = _deep_merge(base, override)

    assert result == {
        "a": 1,
        "b": {"c": 10, "d": 3},
        "e": 20,
        "f": 30,
    }

    # Verify base wasn't modified
    assert base["b"]["c"] == 2
    assert base["e"] == 4
