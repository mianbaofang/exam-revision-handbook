"""LLM provider interface for generating concept explanations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol


@dataclass
class ConceptJob:
    """Concept generation task for LLM processing.

    Attributes:
        topic_id: Unique identifier for the topic (e.g., "concept_001")
        topic_title: Human-readable topic title
        concept_term: The specific concept term to explain
        subject: Subject area (e.g., "Mathematics", "Economics")
        level: Educational level ("IGCSE" or "A-Level")
        context_snippet: Relevant text from the syllabus/specification
    """

    topic_id: str
    topic_title: str
    concept_term: str
    subject: str
    level: str
    context_snippet: str


@dataclass
class ConceptExplanation:
    """LLM-generated concept explanation with metadata.

    Attributes:
        concept_term: The concept term that was explained
        explanation: The main explanation text
        analogy: Optional analogy to aid understanding
        example: Optional concrete example
        common_misconception: Optional common misconception to address
        status: Generation status ("generated", "pending", or "failed")
        metadata: Additional metadata (tokens used, cost, model name, etc.)
    """

    concept_term: str
    explanation: str
    analogy: str | None = None
    example: str | None = None
    common_misconception: str | None = None
    status: Literal["generated", "pending", "failed"] = "pending"
    metadata: dict[str, str | int | float] = field(default_factory=dict)


class LLMContextProvider(Protocol):
    """Protocol for LLM providers that generate concept explanations.

    Implementers must provide batch concept generation with concurrency control
    and cost estimation capabilities.
    """

    def generate_concept_explanations(
        self,
        jobs: list[ConceptJob],
        max_concurrency: int = 5,
    ) -> list[ConceptExplanation]:
        """Generate concept explanations for a batch of jobs.

        Args:
            jobs: List of concept generation tasks
            max_concurrency: Maximum number of concurrent LLM requests

        Returns:
            List of concept explanations with status and metadata

        Raises:
            CostLimitExceededError: If estimated cost exceeds configured limits
        """
        ...

    def estimate_cost(self, jobs: list[ConceptJob]) -> float:
        """Estimate the cost in USD for processing a batch of jobs.

        Args:
            jobs: List of concept generation tasks

        Returns:
            Estimated cost in USD
        """
        ...


class CostLimitExceededError(Exception):
    """Raised when estimated LLM cost exceeds configured limits.

    Attributes:
        estimated_cost: The estimated cost that exceeded the limit
        cost_limit: The configured cost limit
        job_count: Number of jobs in the batch
    """

    def __init__(self, estimated_cost: float, cost_limit: float, job_count: int):
        self.estimated_cost = estimated_cost
        self.cost_limit = cost_limit
        self.job_count = job_count
        super().__init__(
            f"Estimated cost ${estimated_cost:.2f} exceeds limit ${cost_limit:.2f} "
            f"for {job_count} jobs"
        )
