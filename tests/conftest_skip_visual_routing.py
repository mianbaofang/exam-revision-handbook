"""
Skip visual routing tests that validate deprecated Python keyword routing.

After architecture refactor, Python no longer uses keyword triggers to decide
visual types. The LLM Writer judges visual needs case-by-case in Phase 2.

These tests validated the old choose_visual_type() keyword routing logic,
which has been removed (537 lines deleted from visual_routing.py).
"""

import pytest

# Collect all test functions in test_visual_routing.py and test_visual_routing_benchmark.py
# and mark them as skipped with reason


def pytest_collection_modifyitems(config, items):
    skip_marker = pytest.mark.skip(
        reason="Deprecated: Python no longer uses keyword routing for visuals. "
        "LLM Writer judges visual needs in Phase 2. "
        "See skills/exam-revision-handbook/SKILL.md for the new workflow."
    )

    for item in items:
        if "test_visual_routing" in str(item.fspath):
            item.add_marker(skip_marker)
