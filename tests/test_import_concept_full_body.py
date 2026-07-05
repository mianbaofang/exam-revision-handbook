from types import SimpleNamespace
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "import_concept_explanations.py"
SCRIPT_SPEC = spec_from_file_location("import_concept_explanations", SCRIPT_PATH)
assert SCRIPT_SPEC and SCRIPT_SPEC.loader
SCRIPT_MODULE = module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SCRIPT_MODULE)
apply_concept_explanations = SCRIPT_MODULE.apply_concept_explanations


def test_apply_concept_explanations_replaces_full_topic_body():
    guide = SimpleNamespace(
        topic_title="2.3 - Market failure: External costs and benefits",
        essence="old essence",
        analogy="old analogy",
        mini_worked_example="old example",
        worked_solution_steps=["old step"],
        pitfall="old pitfall",
        checklist=["old concept"],
    )
    plan = SimpleNamespace(topic_guides=[guide])

    imported, missing = apply_concept_explanations(
        plan,
        [
            {
                "topic_title": guide.topic_title,
                "essence": "External costs and benefits are side effects on people outside the transaction.",
                "analogy": "A noisy party helps the host but keeps the neighbours awake.",
                "mini_worked_example": "Mark private benefit, then add or subtract the third-party effect.",
                "worked_solution_steps": [
                    "Identify who buys and sells.",
                    "Identify the third party.",
                    "Decide whether the side effect is a cost or benefit.",
                ],
                "pitfall": "Do not call every unfair outcome an externality; a third party must be affected.",
                "explanations": [
                    "An external cost is harm to a third party.",
                    "An external benefit is a gain to a third party.",
                ],
            }
        ],
    )

    assert imported == 1
    assert missing == []
    assert (
        guide.essence
        == "External costs and benefits are side effects on people outside the transaction."
    )
    assert guide.analogy == "A noisy party helps the host but keeps the neighbours awake."
    assert (
        guide.mini_worked_example
        == "Mark private benefit, then add or subtract the third-party effect."
    )
    assert guide.worked_solution_steps == [
        "Identify who buys and sells.",
        "Identify the third party.",
        "Decide whether the side effect is a cost or benefit.",
    ]
    assert (
        guide.pitfall
        == "Do not call every unfair outcome an externality; a third party must be affected."
    )
    assert guide.checklist == [
        "An external cost is harm to a third party.",
        "An external benefit is a gain to a third party.",
    ]
