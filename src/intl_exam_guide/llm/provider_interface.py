"""Compatibility exports for the canonical LLM provider interface."""

from __future__ import annotations

from intl_exam_guide.llm.provider import (
    ConceptExplanation,
    ConceptJob,
    CostLimitExceededError,
    LLMContextProvider,
)

__all__ = [
    "ConceptJob",
    "ConceptExplanation",
    "CostLimitExceededError",
    "LLMContextProvider",
]
