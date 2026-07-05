"""Tests for LLM provider interface and data structures."""

from __future__ import annotations

import pytest

from intl_exam_guide.llm import (
    ConceptExplanation,
    ConceptJob,
    CostLimitExceededError,
    LLMContextProvider,
)


# Mock provider implementation for testing


class MockLLMProvider:
    """Mock LLM provider for testing the protocol."""

    def __init__(
        self,
        cost_per_job: float = 0.01,
        should_fail: bool = False,
        max_cost_limit: float | None = None,
    ):
        self.cost_per_job = cost_per_job
        self.should_fail = should_fail
        self.max_cost_limit = max_cost_limit
        self.generated_count = 0

    def generate_concept_explanations(
        self,
        jobs: list[ConceptJob],
        max_concurrency: int = 5,
    ) -> list[ConceptExplanation]:
        """Mock implementation that generates test explanations."""
        # Check cost limit if configured
        if self.max_cost_limit is not None:
            estimated = self.estimate_cost(jobs)
            if estimated > self.max_cost_limit:
                raise CostLimitExceededError(estimated, self.max_cost_limit, len(jobs))

        results = []
        for job in jobs:
            if self.should_fail:
                explanation = ConceptExplanation(
                    concept_term=job.concept_term,
                    explanation="",
                    status="failed",
                    metadata={
                        "error": "Mock failure",
                        "model": "mock-model",
                    },
                )
            else:
                explanation = ConceptExplanation(
                    concept_term=job.concept_term,
                    explanation=f"Mock explanation for {job.concept_term}",
                    analogy=f"Think of {job.concept_term} like a simple analogy",
                    example=f"For example, {job.concept_term} can be seen in...",
                    common_misconception=f"Students often confuse {job.concept_term} with...",
                    status="generated",
                    metadata={
                        "tokens": 150,
                        "cost": self.cost_per_job,
                        "model": "mock-model",
                        "concurrency": max_concurrency,
                    },
                )
            results.append(explanation)
            self.generated_count += 1

        return results

    def estimate_cost(self, jobs: list[ConceptJob]) -> float:
        """Mock cost estimation."""
        return len(jobs) * self.cost_per_job


# Fixtures


@pytest.fixture
def sample_job() -> ConceptJob:
    """Create a sample concept job for testing."""
    return ConceptJob(
        topic_id="concept_001",
        topic_title="2.3 - Market failure: External costs and benefits",
        concept_term="External costs",
        subject="Economics",
        level="IGCSE",
        context_snippet="External costs and benefits affect third parties.",
    )


@pytest.fixture
def sample_jobs() -> list[ConceptJob]:
    """Create multiple sample concept jobs for batch testing."""
    return [
        ConceptJob(
            topic_id="concept_001",
            topic_title="2.3 - Market failure: External costs",
            concept_term="External costs",
            subject="Economics",
            level="IGCSE",
            context_snippet="External costs are costs borne by third parties.",
        ),
        ConceptJob(
            topic_id="concept_002",
            topic_title="2.3 - Market failure: External benefits",
            concept_term="External benefits",
            subject="Economics",
            level="IGCSE",
            context_snippet="External benefits are benefits enjoyed by third parties.",
        ),
        ConceptJob(
            topic_id="concept_003",
            topic_title="P1.1 - Algebra: Surds",
            concept_term="Surds",
            subject="Mathematics",
            level="A-Level",
            context_snippet="Surds are irrational numbers involving roots.",
        ),
    ]


# Tests for ConceptJob


def test_concept_job_creation(sample_job):
    """Test that ConceptJob can be created with all required fields."""
    assert sample_job.topic_id == "concept_001"
    assert sample_job.topic_title == "2.3 - Market failure: External costs and benefits"
    assert sample_job.concept_term == "External costs"
    assert sample_job.subject == "Economics"
    assert sample_job.level == "IGCSE"
    assert sample_job.context_snippet == "External costs and benefits affect third parties."


def test_concept_job_is_dataclass(sample_job):
    """Test that ConceptJob behaves as a dataclass."""
    # Should have __dataclass_fields__
    assert hasattr(sample_job, "__dataclass_fields__")
    # Should be able to replace fields
    updated = sample_job.__class__(
        topic_id=sample_job.topic_id,
        topic_title="Updated title",
        concept_term=sample_job.concept_term,
        subject=sample_job.subject,
        level=sample_job.level,
        context_snippet=sample_job.context_snippet,
    )
    assert updated.topic_title == "Updated title"


# Tests for ConceptExplanation


def test_concept_explanation_with_all_fields():
    """Test ConceptExplanation with all fields populated."""
    explanation = ConceptExplanation(
        concept_term="External costs",
        explanation="Costs borne by third parties not involved in the transaction.",
        analogy="Like secondhand smoke affecting non-smokers.",
        example="Factory pollution harming nearby residents.",
        common_misconception="Students confuse external costs with production costs.",
        status="generated",
        metadata={"tokens": 120, "cost": 0.015, "model": "gpt-4"},
    )

    assert explanation.concept_term == "External costs"
    assert explanation.status == "generated"
    assert explanation.analogy is not None
    assert explanation.example is not None
    assert explanation.common_misconception is not None
    assert explanation.metadata["tokens"] == 120
    assert explanation.metadata["cost"] == 0.015


def test_concept_explanation_with_minimal_fields():
    """Test ConceptExplanation with only required fields."""
    explanation = ConceptExplanation(
        concept_term="Surds",
        explanation="Irrational numbers involving roots.",
    )

    assert explanation.concept_term == "Surds"
    assert explanation.explanation == "Irrational numbers involving roots."
    assert explanation.analogy is None
    assert explanation.example is None
    assert explanation.common_misconception is None
    assert explanation.status == "pending"
    assert explanation.metadata == {}


def test_concept_explanation_status_values():
    """Test that ConceptExplanation accepts valid status values."""
    for status in ["generated", "pending", "failed"]:
        explanation = ConceptExplanation(
            concept_term="Test",
            explanation="Test explanation",
            status=status,  # type: ignore
        )
        assert explanation.status == status


def test_concept_explanation_metadata_types():
    """Test that metadata can hold various types."""
    explanation = ConceptExplanation(
        concept_term="Test",
        explanation="Test explanation",
        metadata={
            "string_value": "test",
            "int_value": 100,
            "float_value": 0.05,
            "model": "gpt-4",
        },
    )

    assert explanation.metadata["string_value"] == "test"
    assert explanation.metadata["int_value"] == 100
    assert explanation.metadata["float_value"] == 0.05


# Tests for CostLimitExceededError


def test_cost_limit_exceeded_error_creation():
    """Test that CostLimitExceededError captures all relevant information."""
    error = CostLimitExceededError(
        estimated_cost=15.50,
        cost_limit=10.00,
        job_count=100,
    )

    assert error.estimated_cost == 15.50
    assert error.cost_limit == 10.00
    assert error.job_count == 100
    assert "$15.50" in str(error)
    assert "$10.00" in str(error)
    assert "100 jobs" in str(error)


def test_cost_limit_exceeded_error_is_exception():
    """Test that CostLimitExceededError can be raised and caught."""
    with pytest.raises(CostLimitExceededError) as exc_info:
        raise CostLimitExceededError(20.0, 10.0, 50)

    assert exc_info.value.estimated_cost == 20.0
    assert exc_info.value.cost_limit == 10.0
    assert exc_info.value.job_count == 50


# Tests for LLMContextProvider protocol with mock


def test_mock_provider_implements_protocol():
    """Test that MockLLMProvider implements the protocol."""
    provider: LLMContextProvider = MockLLMProvider()

    # Should have the required methods
    assert hasattr(provider, "generate_concept_explanations")
    assert hasattr(provider, "estimate_cost")
    assert callable(provider.generate_concept_explanations)
    assert callable(provider.estimate_cost)


def test_provider_generates_single_explanation(sample_job):
    """Test generating a single concept explanation."""
    provider = MockLLMProvider(cost_per_job=0.02)

    results = provider.generate_concept_explanations([sample_job])

    assert len(results) == 1
    assert results[0].concept_term == "External costs"
    assert results[0].status == "generated"
    assert "Mock explanation" in results[0].explanation
    assert results[0].analogy is not None
    assert results[0].example is not None
    assert results[0].common_misconception is not None
    assert results[0].metadata["cost"] == 0.02
    assert results[0].metadata["model"] == "mock-model"


def test_provider_generates_batch_explanations(sample_jobs):
    """Test generating multiple concept explanations in batch."""
    provider = MockLLMProvider(cost_per_job=0.01)

    results = provider.generate_concept_explanations(sample_jobs, max_concurrency=3)

    assert len(results) == 3
    assert all(r.status == "generated" for r in results)
    assert results[0].concept_term == "External costs"
    assert results[1].concept_term == "External benefits"
    assert results[2].concept_term == "Surds"
    assert all(r.metadata["concurrency"] == 3 for r in results)


def test_provider_respects_max_concurrency(sample_jobs):
    """Test that max_concurrency parameter is passed through."""
    provider = MockLLMProvider()

    results = provider.generate_concept_explanations(sample_jobs, max_concurrency=10)

    assert all(r.metadata["concurrency"] == 10 for r in results)


def test_provider_handles_failures(sample_jobs):
    """Test provider behavior when generation fails."""
    provider = MockLLMProvider(should_fail=True)

    results = provider.generate_concept_explanations(sample_jobs)

    assert len(results) == 3
    assert all(r.status == "failed" for r in results)
    assert all(r.explanation == "" for r in results)
    assert all("error" in r.metadata for r in results)


def test_provider_estimate_cost_single_job(sample_job):
    """Test cost estimation for a single job."""
    provider = MockLLMProvider(cost_per_job=0.015)

    cost = provider.estimate_cost([sample_job])

    assert cost == 0.015


def test_provider_estimate_cost_batch(sample_jobs):
    """Test cost estimation for multiple jobs."""
    provider = MockLLMProvider(cost_per_job=0.02)

    cost = provider.estimate_cost(sample_jobs)

    assert cost == 0.06  # 3 jobs * 0.02


def test_provider_raises_cost_limit_exceeded(sample_jobs):
    """Test that provider raises CostLimitExceededError when limit is exceeded."""
    provider = MockLLMProvider(cost_per_job=5.0, max_cost_limit=10.0)

    with pytest.raises(CostLimitExceededError) as exc_info:
        provider.generate_concept_explanations(sample_jobs)

    assert exc_info.value.estimated_cost == 15.0  # 3 jobs * 5.0
    assert exc_info.value.cost_limit == 10.0
    assert exc_info.value.job_count == 3


def test_provider_processes_within_cost_limit(sample_jobs):
    """Test that provider processes jobs when within cost limit."""
    provider = MockLLMProvider(cost_per_job=2.0, max_cost_limit=10.0)

    results = provider.generate_concept_explanations(sample_jobs)

    assert len(results) == 3
    assert all(r.status == "generated" for r in results)


def test_provider_tracks_generation_count(sample_jobs):
    """Test that provider tracks how many explanations were generated."""
    provider = MockLLMProvider()

    assert provider.generated_count == 0

    provider.generate_concept_explanations([sample_jobs[0]])
    assert provider.generated_count == 1

    provider.generate_concept_explanations(sample_jobs[1:])
    assert provider.generated_count == 3


def test_empty_job_list():
    """Test handling of empty job list."""
    provider = MockLLMProvider()

    results = provider.generate_concept_explanations([])
    cost = provider.estimate_cost([])

    assert results == []
    assert cost == 0.0


def test_concept_job_different_levels():
    """Test concept jobs for different educational levels."""
    igcse_job = ConceptJob(
        topic_id="concept_001",
        topic_title="Basic Economics",
        concept_term="Supply",
        subject="Economics",
        level="IGCSE",
        context_snippet="Supply is the quantity available.",
    )

    a_level_job = ConceptJob(
        topic_id="concept_002",
        topic_title="Advanced Economics",
        concept_term="Price Elasticity",
        subject="Economics",
        level="A-Level",
        context_snippet="Price elasticity measures responsiveness.",
    )

    assert igcse_job.level == "IGCSE"
    assert a_level_job.level == "A-Level"
    assert igcse_job.subject == a_level_job.subject


def test_concept_job_different_subjects():
    """Test concept jobs for different subjects."""
    subjects = ["Mathematics", "Economics", "Physics", "Chemistry", "Biology"]

    for subject in subjects:
        job = ConceptJob(
            topic_id=f"concept_{subject.lower()}",
            topic_title=f"Topic in {subject}",
            concept_term="Test concept",
            subject=subject,
            level="IGCSE",
            context_snippet="Test context",
        )
        assert job.subject == subject
