"""
Tests for skill_interface module.

Tests both SkillHandbookGenerator and IncrementalGenerator classes.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from intl_exam_guide.models import (
    AssessmentPaper,
    Qualification,
    SourceRecord,
    Topic,
)
from intl_exam_guide.skill_interface import (
    GenerationProgress,
    IncrementalGenerator,
    SkillHandbookGenerator,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_qualification():
    """Create a sample qualification for testing."""
    return Qualification(
        title="Test GCSE Mathematics",
        code="TEST-8300",
        qualification_type="international_gcse",
        subject_area="Mathematics",
        page_url="https://example.com/test-8300",
        summary=[
            "Number and algebra",
            "Geometry and measures",
        ],
        topics=[
            Topic(
                title="Algebraic expressions",
                points=[
                    "Simplify algebraic expressions",
                    "Expand brackets",
                ],
                level_tags=["foundation", "higher"],
            ),
            Topic(
                title="Linear equations",
                points=[
                    "Solve linear equations",
                ],
                level_tags=["foundation", "higher"],
            ),
        ],
        assessments=[
            AssessmentPaper(
                title="Paper 1: Non-calculator",
                details=["1 hour 30 minutes"],
            ),
        ],
        source=SourceRecord(
            provider="test",
            page_url="https://example.com/test-8300",
        ),
        audience_note="Test students",
    )


@pytest.fixture
def mock_llm_callback():
    """Create a mock LLM callback."""

    async def callback(prompt: str) -> str:
        """Mock LLM that returns JSON-formatted response."""
        return json.dumps(
            {
                "explanation": "This is a test explanation for the concept.",
                "analogy": "Think of it like a test analogy.",
                "example": "For example, in testing...",
                "common_misconception": "Students often confuse this with that.",
            }
        )

    return callback


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "handbook_output"
    output_dir.mkdir()
    return output_dir


# ============================================================================
# SkillHandbookGenerator Tests
# ============================================================================


class TestSkillHandbookGenerator:
    """Tests for SkillHandbookGenerator class."""

    def test_init(self, mock_llm_callback):
        """Test generator initialization."""
        gen = SkillHandbookGenerator(mock_llm_callback)
        assert gen.llm_callback == mock_llm_callback
        assert gen.progress_callback is None

    def test_init_with_progress_callback(self, mock_llm_callback):
        """Test generator initialization with progress callback."""
        progress_callback = MagicMock()
        gen = SkillHandbookGenerator(mock_llm_callback, progress_callback)
        assert gen.llm_callback == mock_llm_callback
        assert gen.progress_callback == progress_callback

    @pytest.mark.anyio
    async def test_generate_basic(
        self,
        sample_qualification,
        mock_llm_callback,
        temp_output_dir,
    ):
        """Test basic handbook generation."""
        gen = SkillHandbookGenerator(mock_llm_callback)

        with patch("intl_exam_guide.skill_interface.render_html") as mock_render:
            with patch("intl_exam_guide.skill_interface.validate_plan") as mock_validate:
                mock_render.return_value = temp_output_dir / "handbook.html"
                mock_validate.return_value = []

                result = await gen.generate(
                    qualification=sample_qualification,
                    output_dir=temp_output_dir,
                    skip_pdf=True,  # Skip PDF for speed
                )

                assert result == temp_output_dir / "handbook.html"
                mock_render.assert_called_once()

    @pytest.mark.anyio
    async def test_generate_with_progress_callback(
        self,
        sample_qualification,
        mock_llm_callback,
        temp_output_dir,
    ):
        """Test generation with progress tracking."""
        progress_calls = []

        def progress_callback(progress: GenerationProgress):
            progress_calls.append(
                {
                    "stage": progress.stage,
                    "current": progress.current,
                    "total": progress.total,
                    "message": progress.message,
                }
            )

        gen = SkillHandbookGenerator(mock_llm_callback, progress_callback)

        with patch("intl_exam_guide.skill_interface.render_html") as mock_render:
            with patch("intl_exam_guide.skill_interface.validate_plan") as mock_validate:
                mock_render.return_value = temp_output_dir / "handbook.html"
                mock_validate.return_value = []

                await gen.generate(
                    qualification=sample_qualification,
                    output_dir=temp_output_dir,
                    skip_pdf=True,
                )

                # Check that progress was reported
                assert len(progress_calls) > 0
                stages = [call["stage"] for call in progress_calls]
                assert "planning" in stages
                assert "complete" in stages

    def test_build_concept_prompt(
        self,
        mock_llm_callback,
    ):
        """Test concept prompt building."""
        from intl_exam_guide.llm.provider import ConceptJob

        gen = SkillHandbookGenerator(mock_llm_callback)

        job = ConceptJob(
            topic_id="test_001",
            topic_title="Linear equations",
            concept_term="slope",
            subject="Mathematics",
            level="IGCSE",
            context_snippet="Understanding slope in linear relationships",
        )

        prompt = gen._build_concept_prompt(job)

        assert "Linear equations" in prompt
        assert "slope" in prompt
        assert "Mathematics" in prompt
        assert "IGCSE" in prompt
        assert "mastery_summary" in prompt
        assert "What to master" in prompt
        assert "no one-visual-per-subject quota" in prompt
        assert "Visuals may contain text labels" in prompt
        assert "Never create a generic subject poster" in prompt

    def test_parse_concept_response_json(
        self,
        mock_llm_callback,
    ):
        """Test parsing JSON concept response."""
        gen = SkillHandbookGenerator(mock_llm_callback)

        response = json.dumps(
            {
                "explanation": "Test explanation",
                "analogy": "Test analogy",
                "example": "Test example",
                "common_misconception": "Test misconception",
            }
        )

        result = gen._parse_concept_response("slope", response)

        assert result.concept_term == "slope"
        assert result.explanation == "Test explanation"
        assert result.analogy == "Test analogy"
        assert result.example == "Test example"
        assert result.common_misconception == "Test misconception"
        assert result.status == "generated"

    def test_parse_concept_response_plain_text(
        self,
        mock_llm_callback,
    ):
        """Test parsing plain text concept response."""
        gen = SkillHandbookGenerator(mock_llm_callback)

        response = "This is a plain text explanation without JSON."

        result = gen._parse_concept_response("slope", response)

        assert result.concept_term == "slope"
        assert result.explanation == response
        assert result.status == "generated"

    @pytest.mark.anyio
    async def test_generate_concepts_async(
        self,
        mock_llm_callback,
    ):
        """Test async concept generation."""
        from intl_exam_guide.llm.provider import ConceptJob

        gen = SkillHandbookGenerator(mock_llm_callback)

        jobs = [
            ConceptJob(
                topic_id=f"test_{i:03d}",
                topic_title=f"Topic {i}",
                concept_term=f"concept_{i}",
                subject="Mathematics",
                level="IGCSE",
                context_snippet=f"Context for concept {i}",
            )
            for i in range(3)
        ]

        explanations = await gen._generate_concepts_async(jobs)

        assert len(explanations) == 3
        for i, explanation in enumerate(explanations):
            assert explanation.concept_term == f"concept_{i}"
            assert explanation.status == "generated"


# ============================================================================
# IncrementalGenerator Tests
# ============================================================================


class TestIncrementalGenerator:
    """Tests for IncrementalGenerator class."""

    def test_init(self, sample_qualification, temp_output_dir):
        """Test generator initialization."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        assert gen.qualification == sample_qualification
        assert gen.output_dir == temp_output_dir
        assert gen.plan is None
        assert gen.concept_jobs == []
        assert gen.current_concept_index == 0

    def test_step1_prepare(self, sample_qualification, temp_output_dir):
        """Test step 1: preparation."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        info = gen.step1_prepare()

        assert "total_topics" in info
        assert "total_concepts" in info
        assert "total_practice" in info
        assert info["total_topics"] > 0
        assert gen.plan is not None

    def test_step2_get_next_concept(self, sample_qualification, temp_output_dir):
        """Test getting next concept to generate."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        gen.step1_prepare()
        task = gen.step2_get_next_concept()

        if gen.concept_jobs:
            assert task["status"] == "ready"
            assert "concept_term" in task
            assert "prompt" in task
            assert task["concept_index"] == 1
        else:
            assert task["status"] == "done"

    def test_step2_submit_concept(self, sample_qualification, temp_output_dir):
        """Test submitting generated concept."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        gen.step1_prepare()

        if gen.concept_jobs:
            initial_index = gen.current_concept_index

            gen.step2_submit_concept(
                content="Test explanation",
                analogy="Test analogy",
                misconception="Test misconception",
                mastery_summary="Use algebraic rules to simplify and expand expressions accurately.",
            )

            assert gen.current_concept_index == initial_index + 1
            explanation = gen.concept_explanations[initial_index]
            assert explanation.explanation == "Test explanation"
            assert explanation.status == "generated"
            assert (
                explanation.metadata["mastery_summary"]
                == "Use algebraic rules to simplify and expand expressions accurately."
            )

    def test_incremental_entries_include_writer_mastery_summary(
        self,
        sample_qualification,
        temp_output_dir,
    ):
        """Test incremental entries preserve Writer-owned mastery summary."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        gen.step1_prepare()
        if not gen.concept_jobs:
            pytest.skip("Sample qualification produced no concept jobs")

        gen.step2_submit_concept(
            content="Expressions can be simplified by combining like terms and applying bracket rules.",
            analogy="It is like sorting matching stationery before packing a pencil case.",
            mastery_summary="Simplify expressions and expand brackets without changing their value.",
        )

        entries = gen._incremental_entries()

        assert entries[0]["mastery_summary"] == (
            "Simplify expressions and expand brackets without changing their value."
        )

    def test_step2_skip_concept(self, sample_qualification, temp_output_dir):
        """Test skipping a concept."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        gen.step1_prepare()

        if gen.concept_jobs:
            initial_index = gen.current_concept_index

            gen.step2_skip_concept()

            assert gen.current_concept_index == initial_index + 1
            explanation = gen.concept_explanations[initial_index]
            assert explanation.status == "failed"

    def test_step3_render(self, sample_qualification, temp_output_dir):
        """Test final rendering step."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        gen.step1_prepare()

        # Skip all concepts
        while gen.current_concept_index < len(gen.concept_jobs):
            gen.step2_skip_concept()

        with patch("intl_exam_guide.skill_interface.render_html") as mock_render:
            with patch("intl_exam_guide.skill_interface.validate_plan") as mock_validate:
                mock_render.return_value = temp_output_dir / "handbook.html"
                mock_validate.return_value = []

                result = gen.step3_render(skip_pdf=True)

                assert "html_path" in result
                assert result["html_path"] == str(temp_output_dir / "handbook.html")
                mock_render.assert_called_once()

    def test_get_progress(self, sample_qualification, temp_output_dir):
        """Test progress tracking."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        # Before preparation
        progress = gen.get_progress()
        assert progress["step"] == "preparation"

        # After preparation
        gen.step1_prepare()
        progress = gen.get_progress()
        assert progress["concepts_total"] == len(gen.concept_jobs)
        assert progress["concepts_generated"] == 0

    def test_save_and_load_state(self, sample_qualification, temp_output_dir):
        """Test state save and load."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        gen.step1_prepare()

        # Generate some concepts
        if gen.concept_jobs:
            gen.step2_submit_concept("Test content 1")
            if len(gen.concept_jobs) > 1:
                gen.step2_submit_concept("Test content 2")

        # Save state
        state_file = temp_output_dir / "state.json"
        gen.save_state(state_file)

        assert state_file.exists()

        # Create new generator and load state
        gen2 = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )
        gen2.step1_prepare()
        gen2.load_state(state_file)

        # Check state was restored
        assert gen2.current_concept_index == gen.current_concept_index
        assert len(gen2.concept_explanations) == len(gen.concept_explanations)

    def test_step2_submit_without_prepare_raises_error(
        self,
        sample_qualification,
        temp_output_dir,
    ):
        """Test that submitting concept without prepare raises error."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        # Should raise ValueError since step1_prepare not called
        with pytest.raises(ValueError):
            gen.step2_submit_concept("Test content")

    def test_step3_render_without_prepare_raises_error(
        self,
        sample_qualification,
        temp_output_dir,
    ):
        """Test that rendering without prepare raises error."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        # Should raise ValueError since step1_prepare not called
        with pytest.raises(ValueError):
            gen.step3_render()


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.anyio
    async def test_full_automated_workflow(
        self,
        sample_qualification,
        mock_llm_callback,
        temp_output_dir,
    ):
        """Test complete automated generation workflow."""
        progress_stages = []

        def track_progress(progress: GenerationProgress):
            progress_stages.append(progress.stage)

        gen = SkillHandbookGenerator(mock_llm_callback, track_progress)

        with patch("intl_exam_guide.skill_interface.render_html") as mock_render:
            with patch("intl_exam_guide.skill_interface.validate_plan") as mock_validate:
                mock_render.return_value = temp_output_dir / "handbook.html"
                mock_validate.return_value = []

                result = await gen.generate(
                    qualification=sample_qualification,
                    output_dir=temp_output_dir,
                    skip_pdf=True,
                )

                assert result == temp_output_dir / "handbook.html"
                assert "planning" in progress_stages
                assert "complete" in progress_stages

    def test_full_incremental_workflow(
        self,
        sample_qualification,
        temp_output_dir,
    ):
        """Test complete incremental generation workflow."""
        gen = IncrementalGenerator(
            qualification=sample_qualification,
            output_dir=temp_output_dir,
        )

        # Step 1: Prepare
        info = gen.step1_prepare()
        assert info["total_topics"] > 0

        # Step 2: Generate all concepts
        while True:
            task = gen.step2_get_next_concept()
            if task["status"] == "done":
                break
            gen.step2_submit_concept(f"Explanation for {task['concept_term']}")

        # Step 3: Render
        with patch("intl_exam_guide.skill_interface.render_html") as mock_render:
            with patch("intl_exam_guide.skill_interface.validate_plan") as mock_validate:
                mock_render.return_value = temp_output_dir / "handbook.html"
                mock_validate.return_value = []

                result = gen.step3_render(skip_pdf=True)

                assert "html_path" in result
                assert result["html_path"] == str(temp_output_dir / "handbook.html")


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_topics_qualification(self, temp_output_dir):
        """Test handling qualification with no topics."""
        qualification = Qualification(
            title="Empty Qualification",
            code="EMPTY",
            qualification_type="international_gcse",
            subject_area="Test",
            page_url="https://example.com",
            summary=[],
            topics=[],  # Empty topics
            assessments=[],
            source=SourceRecord(provider="test", page_url="https://example.com"),
            audience_note="Test",
        )

        gen = IncrementalGenerator(
            qualification=qualification,
            output_dir=temp_output_dir,
        )

        info = gen.step1_prepare()
        assert info["total_topics"] == 0
        assert info["total_concepts"] == 0

        # Should immediately be done
        task = gen.step2_get_next_concept()
        assert task["status"] == "done"

    @pytest.mark.anyio
    async def test_llm_callback_error_handling(
        self,
        sample_qualification,
        temp_output_dir,
    ):
        """Test handling of LLM callback errors."""

        async def failing_callback(prompt: str) -> str:
            raise Exception("LLM API error")

        gen = SkillHandbookGenerator(failing_callback)

        from intl_exam_guide.llm.provider import ConceptJob

        jobs = [
            ConceptJob(
                topic_id="test_001",
                topic_title="Test Topic",
                concept_term="test_concept",
                subject="Mathematics",
                level="IGCSE",
                context_snippet="Test context",
            )
        ]

        explanations = await gen._generate_concepts_async(jobs)

        # Should return failed status, not crash
        assert len(explanations) == 1
        assert explanations[0].status == "failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
