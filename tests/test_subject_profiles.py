from intl_exam_guide.models import Topic
from intl_exam_guide.planning.subject_profiles import (
    ACCOUNTING,
    BIOLOGY,
    BUSINESS,
    CHEMISTRY,
    ECONOMICS,
    GENERIC,
    HISTORY,
    MATHEMATICS,
    PHYSICS,
    resolve_subject_profile,
)


def test_declared_subject_area_routes_to_broad_profiles():
    assert resolve_subject_profile("Mathematics", Topic("N1 Number"), "").example_domain == (
        MATHEMATICS.example_domain
    )
    assert resolve_subject_profile("Economics", Topic("Market"), "").example_domain == (
        ECONOMICS.example_domain
    )
    assert resolve_subject_profile("Business", Topic("Stakeholders"), "").example_domain == (
        BUSINESS.example_domain
    )
    assert resolve_subject_profile("Accounting", Topic("Ledger"), "").example_domain == (
        ACCOUNTING.example_domain
    )
    assert resolve_subject_profile("History", Topic("Causes"), "").example_domain == (
        HISTORY.example_domain
    )
    assert resolve_subject_profile("Chemistry", Topic("Atoms"), "").example_domain == (
        CHEMISTRY.example_domain
    )
    assert resolve_subject_profile("Biology", Topic("Cells"), "").example_domain == (
        BIOLOGY.example_domain
    )
    assert resolve_subject_profile("Physics", Topic("Forces"), "").example_domain == (
        PHYSICS.example_domain
    )
    assert resolve_subject_profile("Art and Design", Topic("Portfolio"), "").example_domain == (
        GENERIC.example_domain
    )


def test_ambiguous_science_uses_source_text_for_chemistry_biology_and_physics():
    assert (
        resolve_subject_profile(
            "Science",
            Topic("Bonding"),
            "ionic bonding, covalent structure, acid and alkali reactions",
        ).example_domain
        == CHEMISTRY.example_domain
    )
    assert (
        resolve_subject_profile(
            "Combined Science",
            Topic("Cell transport"),
            "cells, enzymes, osmosis, photosynthesis and respiration",
        ).example_domain
        == BIOLOGY.example_domain
    )
    assert (
        resolve_subject_profile(
            "Demo Science",
            Topic("Motion"),
            "forces, acceleration, waves, electricity and circuits",
        ).example_domain
        == PHYSICS.example_domain
    )


def test_mathematics_prefix_route_only_applies_when_text_looks_mathematical():
    assert (
        resolve_subject_profile(
            None,
            Topic("N4 - Structure and calculation"),
            "sets, vectors, algebra and probability",
        ).example_domain
        == MATHEMATICS.example_domain
    )
    assert (
        resolve_subject_profile(
            None,
            Topic("N4 - Non-maths title"),
            "portfolio annotation and creative process",
        ).example_domain
        == GENERIC.example_domain
    )


def test_ambiguous_subject_uses_source_text_for_economics_and_accounting():
    assert (
        resolve_subject_profile(
            "General",
            Topic("Markets"),
            "demand, supply, scarcity, opportunity cost and market equilibrium",
        ).example_domain
        == ECONOMICS.example_domain
    )
    assert (
        resolve_subject_profile(
            "Example",
            Topic("Records"),
            "source document, double entry, trial balance and bank reconciliation",
        ).example_domain
        == ACCOUNTING.example_domain
    )


def test_ambiguous_subject_uses_source_text_for_business_and_history():
    assert (
        resolve_subject_profile(
            "General",
            Topic("Stakeholders"),
            "business ownership stakeholders marketing mix and cash flow forecasting",
        ).example_domain
        == BUSINESS.example_domain
    )
    assert (
        resolve_subject_profile(
            "General",
            Topic("Sources"),
            "historical source evidence chronology causes consequences and continuity",
        ).example_domain
        == HISTORY.example_domain
    )


def test_history_source_text_recognizes_cambridge_question_headings():
    assert (
        resolve_subject_profile(
            "General",
            Topic("6 - What caused the First World War?"),
            "What caused the First World War? Treaty of Versailles League of Nations appeasement",
        ).example_domain
        == HISTORY.example_domain
    )
