"""Tests for complete course-decision explanations."""

from expert_system.explanations import build_course_explanation
from expert_system.models import RuleResult


def make_result(
    rule_id: str,
    rule_name: str,
    passed: bool,
    message: str,
    source: str,
    page: int,
) -> RuleResult:
    """Create a rule result for explanation tests."""
    return RuleResult(rule_id, rule_name, passed, message, source, page)


def test_failed_rule_ids_and_sources_are_included_in_explanation() -> None:
    general_results = [
        make_result(
            "R03",
            "Common General Paper",
            True,
            "CGP requirement satisfied.",
            "UGC-SL-ADMISSIONS-HANDBOOK-2025-2026",
            9,
        )
    ]
    course_results = [
        make_result(
            "R05",
            "Medicine Subject/Grade",
            False,
            "At least two subjects must have C or better.",
            "UGC-SL-ADMISSIONS-HANDBOOK-2025-2026",
            50,
        )
    ]

    explanation = build_course_explanation(
        "Medicine",
        False,
        general_results,
        course_results,
    )

    assert "FINAL RESULT: NOT ELIGIBLE" in explanation
    assert "GENERAL RULE TRACE" in explanation
    assert "PASS R03 - Common General Paper" in explanation
    assert "COURSE RULE TRACE" in explanation
    assert "FAIL R05 - Medicine Subject/Grade" in explanation
    assert "FAILED REQUIREMENTS" in explanation
    assert "- R05 - Medicine Subject/Grade" in explanation
    assert "At least two subjects must have C or better." in explanation
    assert "SOURCE REFERENCES" in explanation
    assert "UGC-SL-ADMISSIONS-HANDBOOK-2025-2026, page 9 (R03)" in explanation
    assert "UGC-SL-ADMISSIONS-HANDBOOK-2025-2026, page 50 (R05)" in explanation


def test_eligible_explanation_reports_no_failed_requirements() -> None:
    result = make_result(
        "R01",
        "Minimum Grade & Sitting",
        True,
        "Requirement satisfied.",
        "UGC-SL-ADMISSIONS-HANDBOOK-2025-2026",
        9,
    )

    explanation = build_course_explanation(
        "Medicine",
        True,
        [result],
        [],
    )

    assert "FINAL RESULT: ELIGIBLE" in explanation
    assert "FAILED REQUIREMENTS\nNone." in explanation
