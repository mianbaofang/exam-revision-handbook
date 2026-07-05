"""Tests for FallbackProvider class."""

import json
import logging

import pytest

from intl_exam_guide.llm import ConceptExplanation, ConceptJob, FallbackProvider


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    return tmp_path / "output"


@pytest.fixture
def fallback_provider(temp_output_dir):
    """Create a FallbackProvider instance."""
    return FallbackProvider(temp_output_dir)


@pytest.fixture
def sample_jobs():
    """Create sample concept jobs for testing."""
    return [
        ConceptJob(
            topic_id="topic_001",
            topic_title="Newton's Laws of Motion",
            concept_term="inertia",
            subject="Physics",
            level="IGCSE",
            context_snippet="An object at rest stays at rest unless acted upon by a force.",
        ),
        ConceptJob(
            topic_id="topic_002",
            topic_title="Market Equilibrium",
            concept_term="supply and demand",
            subject="Economics",
            level="A-Level",
            context_snippet="The price at which quantity supplied equals quantity demanded.",
        ),
        ConceptJob(
            topic_id="topic_003",
            topic_title="Chemical Bonding",
            concept_term="ionic bond",
            subject="Chemistry",
            level="IGCSE",
            context_snippet="Transfer of electrons between atoms forms ionic bonds.",
        ),
    ]


class TestFallbackProvider:
    """Test suite for FallbackProvider."""

    def test_initialization(self, temp_output_dir):
        """Test FallbackProvider initializes correctly."""
        provider = FallbackProvider(temp_output_dir)
        assert provider.output_dir == temp_output_dir

    def test_initialization_with_string_path(self, temp_output_dir):
        """Test FallbackProvider accepts string paths."""
        provider = FallbackProvider(str(temp_output_dir))
        assert provider.output_dir == temp_output_dir

    def test_estimate_cost_returns_zero(self, fallback_provider, sample_jobs):
        """Test estimate_cost always returns 0.0."""
        cost = fallback_provider.estimate_cost(sample_jobs)
        assert cost == 0.0

    def test_estimate_cost_with_empty_jobs(self, fallback_provider):
        """Test estimate_cost with empty job list."""
        cost = fallback_provider.estimate_cost([])
        assert cost == 0.0

    def test_creates_concepts_directory(self, fallback_provider, sample_jobs):
        """Test that concepts directory is created."""
        fallback_provider.generate_concept_explanations(sample_jobs)

        concepts_dir = fallback_provider.output_dir / "concepts"
        assert concepts_dir.exists()
        assert concepts_dir.is_dir()

    def test_creates_concept_jobs_json(self, fallback_provider, sample_jobs):
        """Test that concept_jobs.json file is created."""
        fallback_provider.generate_concept_explanations(sample_jobs)

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        assert jobs_file.exists()
        assert jobs_file.is_file()

    def test_json_format_correct(self, fallback_provider, sample_jobs):
        """Test that JSON file has correct format."""
        fallback_provider.generate_concept_explanations(sample_jobs)

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        with open(jobs_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 3

        # Check first job
        first_job = data[0]
        assert "topic_id" in first_job
        assert "concept_term" in first_job
        assert "context" in first_job
        assert first_job["topic_id"] == "topic_001"
        assert first_job["concept_term"] == "inertia"
        assert "object at rest" in first_job["context"]

    def test_json_contains_all_jobs(self, fallback_provider, sample_jobs):
        """Test that all jobs are written to JSON."""
        fallback_provider.generate_concept_explanations(sample_jobs)

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        with open(jobs_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        topic_ids = [job["topic_id"] for job in data]
        concept_terms = [job["concept_term"] for job in data]

        assert "topic_001" in topic_ids
        assert "topic_002" in topic_ids
        assert "topic_003" in topic_ids
        assert "inertia" in concept_terms
        assert "supply and demand" in concept_terms
        assert "ionic bond" in concept_terms

    def test_returns_pending_explanations(self, fallback_provider, sample_jobs):
        """Test that returned explanations have pending status."""
        explanations = fallback_provider.generate_concept_explanations(sample_jobs)

        assert len(explanations) == 3
        for explanation in explanations:
            assert isinstance(explanation, ConceptExplanation)
            assert explanation.status == "pending"

    def test_explanations_have_correct_terms(self, fallback_provider, sample_jobs):
        """Test that returned explanations have correct concept terms."""
        explanations = fallback_provider.generate_concept_explanations(sample_jobs)

        concept_terms = [exp.concept_term for exp in explanations]
        assert "inertia" in concept_terms
        assert "supply and demand" in concept_terms
        assert "ionic bond" in concept_terms

    def test_explanations_have_fallback_metadata(self, fallback_provider, sample_jobs):
        """Test that explanations have fallback metadata."""
        explanations = fallback_provider.generate_concept_explanations(sample_jobs)

        for explanation in explanations:
            assert "fallback" in explanation.metadata
            assert explanation.metadata["fallback"] is True

    def test_logs_warning_message(self, fallback_provider, sample_jobs, caplog):
        """Test that warning message is logged."""
        with caplog.at_level(logging.WARNING):
            fallback_provider.generate_concept_explanations(sample_jobs)

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "WARNING"
        assert "LLM unavailable" in record.message
        assert "3 concept jobs written" in record.message
        assert "concept_jobs.json" in record.message
        assert "generate explanations manually" in record.message.lower()

    def test_overwrites_existing_file(self, fallback_provider, sample_jobs):
        """Test that existing concept_jobs.json is overwritten."""
        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        jobs_file.parent.mkdir(parents=True, exist_ok=True)

        # Write initial data
        with open(jobs_file, "w") as f:
            json.dump([{"old": "data"}], f)

        # Generate new jobs
        fallback_provider.generate_concept_explanations(sample_jobs)

        # Verify old data is replaced
        with open(jobs_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 3
        assert "old" not in str(data)

    def test_handles_empty_job_list(self, fallback_provider):
        """Test handling of empty job list."""
        explanations = fallback_provider.generate_concept_explanations([])

        assert explanations == []

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        with open(jobs_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data == []

    def test_unicode_handling(self, fallback_provider):
        """Test that Unicode characters are handled correctly."""
        unicode_job = ConceptJob(
            topic_id="topic_unicode",
            topic_title="化学反应",
            concept_term="氧化还原反应",
            subject="Chemistry",
            level="IGCSE",
            context_snippet="电子转移导致氧化数变化。",
        )

        fallback_provider.generate_concept_explanations([unicode_job])

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        with open(jobs_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data[0]["concept_term"] == "氧化还原反应"
        assert "电子转移" in data[0]["context"]

    def test_max_concurrency_parameter_ignored(self, fallback_provider, sample_jobs):
        """Test that max_concurrency parameter is accepted but ignored."""
        explanations_5 = fallback_provider.generate_concept_explanations(
            sample_jobs, max_concurrency=5
        )
        explanations_10 = fallback_provider.generate_concept_explanations(
            sample_jobs, max_concurrency=10
        )

        # Both should produce same results
        assert len(explanations_5) == len(explanations_10) == 3

    def test_json_is_pretty_printed(self, fallback_provider, sample_jobs):
        """Test that JSON file is formatted with indentation."""
        fallback_provider.generate_concept_explanations(sample_jobs)

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        content = jobs_file.read_text(encoding="utf-8")

        # Check for indentation
        assert "  {" in content or '  "topic_id"' in content
        # Should have newlines (not minified)
        assert content.count("\n") > 3

    def test_context_snippet_preservation(self, fallback_provider):
        """Test that context_snippet is preserved correctly in JSON."""
        long_context = "This is a very long context snippet. " * 10
        job = ConceptJob(
            topic_id="topic_long",
            topic_title="Test Topic",
            concept_term="test term",
            subject="Test",
            level="IGCSE",
            context_snippet=long_context,
        )

        fallback_provider.generate_concept_explanations([job])

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        with open(jobs_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data[0]["context"] == long_context

    def test_backward_compatibility_format(self, fallback_provider, sample_jobs):
        """Test that output keeps legacy fields while using the canonical job contract."""
        fallback_provider.generate_concept_explanations(sample_jobs)

        jobs_file = fallback_provider.output_dir / "concepts" / "concept_jobs.json"
        with open(jobs_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for job in data:
            assert {"topic_id", "concept_term", "context"}.issubset(job.keys())
            assert {"id", "topic_title", "source_points", "task", "contract_version"}.issubset(
                job.keys()
            )
            assert isinstance(job["topic_id"], str)
            assert isinstance(job["concept_term"], str)
            assert isinstance(job["context"], str)
            assert job["contract_version"] == "v0.4-pedagogy-mvp"
