"""Tests for LLM provider factory."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from intl_exam_guide.llm import create_llm_provider
from intl_exam_guide.llm.fallback_provider import FallbackProvider


def test_create_llm_provider_fallback() -> None:
    """Test creating fallback provider."""
    config = {
        "llm": {
            "provider": "fallback",
            "fallback": {
                "output_dir": "test_concepts",
            },
        }
    }

    provider = create_llm_provider(config)

    assert isinstance(provider, FallbackProvider)
    assert provider.output_dir == Path("test_concepts")


def test_create_llm_provider_none() -> None:
    """Test that 'none' provider creates fallback provider."""
    config = {
        "llm": {
            "provider": "none",
            "fallback": {
                "output_dir": "concepts",
            },
        }
    }

    provider = create_llm_provider(config)

    assert isinstance(provider, FallbackProvider)


def test_create_llm_provider_openai_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating OpenAI provider with valid API key."""
    monkeypatch.setenv("TEST_API_KEY", "sk-test123")

    config = {
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key_env": "TEST_API_KEY",
                "model": "gpt-4",
                "max_retries": 3,
                "timeout_seconds": 30,
                "cost_limit_per_handbook_usd": 5.0,
                "max_concurrency": 5,
            },
        }
    }

    provider = create_llm_provider(config)

    # Should create OpenAIProvider
    assert provider is not None
    assert provider.__class__.__name__ == "OpenAIProvider"
    assert provider.model == "gpt-4"
    assert provider.max_retries == 3
    assert provider.timeout == 30
    assert provider.cost_limit == 5.0


def test_create_llm_provider_openai_missing_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that missing API key falls back to fallback provider."""
    monkeypatch.delenv("TEST_API_KEY", raising=False)

    config = {
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key_env": "TEST_API_KEY",
                "model": "gpt-4",
            },
            "fallback": {
                "enabled": True,
                "output_dir": "concepts",
            },
        }
    }

    provider = create_llm_provider(config)

    # Should fall back to FallbackProvider when API key is missing
    assert isinstance(provider, FallbackProvider)


def test_create_llm_provider_openai_missing_api_key_no_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that missing API key returns None when fallback disabled."""
    monkeypatch.delenv("TEST_API_KEY", raising=False)

    config = {
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key_env": "TEST_API_KEY",
                "model": "gpt-4",
            },
            "fallback": {
                "enabled": False,
            },
        }
    }

    provider = create_llm_provider(config)

    # Should return None when fallback is disabled
    assert provider is None


def test_create_llm_provider_invalid_provider_with_fallback() -> None:
    """Test that invalid provider name falls back to fallback provider."""
    config = {
        "llm": {
            "provider": "invalid_provider",
            "fallback": {
                "enabled": True,
                "output_dir": "concepts",
            },
        }
    }

    provider = create_llm_provider(config)

    # Should fall back to FallbackProvider
    assert isinstance(provider, FallbackProvider)


def test_create_llm_provider_invalid_provider_no_fallback() -> None:
    """Test that invalid provider name returns None when fallback disabled."""
    config = {
        "llm": {
            "provider": "invalid_provider",
            "fallback": {
                "enabled": False,
            },
        }
    }

    provider = create_llm_provider(config)

    # Should return None when fallback is disabled
    assert provider is None


def test_create_llm_provider_default_values() -> None:
    """Test that provider creation works with minimal config."""
    config = {"llm": {}}

    provider = create_llm_provider(config)

    # Should default to fallback provider
    assert isinstance(provider, FallbackProvider)


def test_create_llm_provider_openai_with_custom_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test creating OpenAI provider with custom settings."""
    monkeypatch.setenv("CUSTOM_KEY", "sk-custom123")

    config = {
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key_env": "CUSTOM_KEY",
                "model": "gpt-4-turbo",
                "max_retries": 5,
                "timeout_seconds": 60,
                "cost_limit_per_handbook_usd": 10.0,
                "max_concurrency": 10,
            },
        }
    }

    provider = create_llm_provider(config)

    assert provider is not None
    assert provider.model == "gpt-4-turbo"
    assert provider.max_retries == 5
    assert provider.timeout == 60
    assert provider.cost_limit == 10.0


def test_create_fallback_provider_with_custom_output_dir() -> None:
    """Test creating fallback provider with custom output directory."""
    config = {
        "llm": {
            "provider": "fallback",
            "fallback": {
                "output_dir": "custom/output/dir",
            },
        }
    }

    provider = create_llm_provider(config)

    assert isinstance(provider, FallbackProvider)
    assert provider.output_dir == Path("custom/output/dir")


def test_create_fallback_provider_default_output_dir() -> None:
    """Test creating fallback provider with default output directory."""
    config = {
        "llm": {
            "provider": "fallback",
        }
    }

    provider = create_llm_provider(config)

    assert isinstance(provider, FallbackProvider)
    assert provider.output_dir == Path(".")


def test_create_openai_provider_handles_creation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that OpenAI provider creation errors are handled gracefully."""
    monkeypatch.setenv("TEST_API_KEY", "sk-test123")

    # Mock the OpenAIProvider import to raise an exception
    with patch("intl_exam_guide.llm.openai_provider.OpenAIProvider") as mock_openai_class:
        mock_openai_class.side_effect = Exception("OpenAI initialization failed")

        config = {
            "llm": {
                "provider": "openai",
                "openai": {
                    "api_key_env": "TEST_API_KEY",
                    "model": "gpt-4",
                },
                "fallback": {
                    "enabled": True,
                    "output_dir": "concepts",
                },
            }
        }

        provider = create_llm_provider(config)

        # Should fall back to FallbackProvider when OpenAI creation fails
        assert isinstance(provider, FallbackProvider)


def test_create_openai_provider_with_missing_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that missing OpenAI import is handled gracefully."""
    monkeypatch.setenv("TEST_API_KEY", "sk-test123")

    config = {
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key_env": "TEST_API_KEY",
                "model": "gpt-4",
            },
            "fallback": {
                "enabled": True,
                "output_dir": "concepts",
            },
        }
    }

    # Mock the import to raise ImportError
    import sys

    # Create a mock module that raises ImportError
    def mock_import(name, *args, **kwargs):
        if "openai_provider" in name:
            raise ImportError("openai_provider module not found")
        # Use the real import for everything else
        return __import__(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        # Clear the module cache to force re-import
        if "intl_exam_guide.llm.openai_provider" in sys.modules:
            del sys.modules["intl_exam_guide.llm.openai_provider"]

        provider = create_llm_provider(config)

        # Should fall back to FallbackProvider when import fails
        assert isinstance(provider, FallbackProvider)


def test_create_llm_provider_preserves_provider_interface() -> None:
    """Test that all created providers implement the LLMContextProvider protocol."""
    from intl_exam_guide.llm import ConceptJob

    # Test with fallback provider
    config_fallback = {"llm": {"provider": "fallback"}}
    provider_fallback = create_llm_provider(config_fallback)

    assert provider_fallback is not None
    assert hasattr(provider_fallback, "generate_concept_explanations")
    assert hasattr(provider_fallback, "estimate_cost")

    # Test that methods are callable
    job = ConceptJob(
        topic_id="test_001",
        topic_title="Test Topic",
        concept_term="Test Concept",
        subject="Mathematics",
        level="IGCSE",
        context_snippet="Test context",
    )

    cost = provider_fallback.estimate_cost([job])
    assert isinstance(cost, float)
    assert cost >= 0
