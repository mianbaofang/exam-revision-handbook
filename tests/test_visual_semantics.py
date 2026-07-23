from intl_exam_guide.auditing.visual_semantics import visual_semantic_issues


def semantic_contract(visual_kind="process"):
    return {
        "schema_version": "v1-visual-semantic-contract",
        "learning_claim": "Students can trace the causal sequence.",
        "intended_inference": "The response returns the variable toward its target state.",
        "visual_kind": visual_kind,
        "required_elements": ["stimulus", "response", "target state"],
        "required_relationships": ["stimulus causes response"],
        "required_labels": ["stimulus", "response"],
        "forbidden_misconceptions": ["response moves the variable farther from target"],
    }


def visual_entry(filename, contract):
    return {
        "id": "visual_001",
        "file": filename,
        "recommended_route": {"route": "exact-svg"},
        "semantic_contract": contract,
    }


def test_exact_svg_text_card_is_not_an_explanatory_visual(tmp_path):
    (tmp_path / "card.svg").write_text(
        "<svg><rect x='0' y='0' width='100' height='50'/><text>Stimulus</text></svg>",
        encoding="utf-8",
    )

    issues = visual_semantic_issues(
        visual_entry("card.svg", semantic_contract()), tmp_path
    )
    codes = {issue["code"] for issue in issues}

    assert "visual.svg_text_card" in codes
    assert "visual.svg_direction_missing" in codes


def test_rect_and_text_table_is_allowed_when_semantics_declare_a_table(tmp_path):
    (tmp_path / "table.svg").write_text(
        "<svg><rect x='0' y='0' width='100' height='50'/><text>Compare</text></svg>",
        encoding="utf-8",
    )

    issues = visual_semantic_issues(
        visual_entry("table.svg", semantic_contract("table")), tmp_path
    )

    assert issues == []


def test_rect_and_text_bar_chart_is_not_rejected_as_a_text_card(tmp_path):
    (tmp_path / "bars.svg").write_text(
        "<svg><rect x='10' y='40' width='20' height='60'/><rect x='40' y='10' width='20' height='90'/><text>Values</text></svg>",
        encoding="utf-8",
    )

    issues = visual_semantic_issues(
        visual_entry("bars.svg", semantic_contract("bar-chart")), tmp_path
    )

    assert not any(issue["code"] == "visual.svg_text_card" for issue in issues)


def test_declared_text_card_cannot_claim_exact_svg_even_with_geometry(tmp_path):
    (tmp_path / "card.svg").write_text(
        "<svg><circle cx='10' cy='10' r='5'/><text>Remember this</text></svg>",
        encoding="utf-8",
    )

    issues = visual_semantic_issues(
        visual_entry("card.svg", semantic_contract("text-card")), tmp_path
    )

    assert any(issue["code"] == "visual.svg_text_card" for issue in issues)


def test_directional_process_svg_passes_structural_checks(tmp_path):
    (tmp_path / "process.svg").write_text(
        """
        <svg xmlns='http://www.w3.org/2000/svg'>
          <defs><marker id='arrow'><path d='M0 0 L10 5 L0 10z'/></marker></defs>
          <rect x='0' y='0' width='30' height='20'/>
          <rect x='70' y='0' width='30' height='20'/>
          <line x1='30' y1='10' x2='70' y2='10' marker-end='url(#arrow)'/>
        </svg>
        """,
        encoding="utf-8",
    )

    issues = visual_semantic_issues(
        visual_entry("process.svg", semantic_contract()), tmp_path
    )

    assert issues == []


def test_non_text_visual_requires_complete_writer_semantic_contract():
    entry = {
        "id": "visual_001",
        "recommended_route": {"route": "external-infographic"},
        "semantic_contract": {"schema_version": "v1-visual-semantic-contract"},
    }

    issues = visual_semantic_issues(entry)

    assert {issue["code"] for issue in issues} == {
        "visual.semantic_contract_incomplete"
    }
