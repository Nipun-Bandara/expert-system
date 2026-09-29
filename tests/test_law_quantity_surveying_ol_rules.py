"""Tests for the fully specified O/L rules R16, R17, and R19-R21."""

import pytest

from expert_system.knowledge_base import R16, R17, R19, R20, R21, SOURCE, Rule
from expert_system.models import ApplicantFacts, RuleResult


def make_facts(ol_results: dict[str, str]) -> ApplicantFacts:
    """Create applicant facts for direct O/L rule evaluation."""
    return ApplicantFacts(
        al_results={},
        same_sitting=True,
        al_attempts=1,
        common_general_paper_mark=30,
        previous_state_university_registration=False,
        ol_results=ol_results,
    )


def assert_result(result: RuleResult, rule: Rule, expected: bool) -> None:
    """Assert rule identity, decision, explanation, and source metadata."""
    assert result.rule_id == rule.id
    assert result.passed is expected
    assert ("PASS:" if expected else "FAIL:") in result.message
    assert result.source == SOURCE
    assert result.page == rule.page


@pytest.mark.parametrize(
    ("grade", "expected"),
    [("B", True), ("C", True), ("S", False)],
)
def test_r16_law_ol_english(grade: str, expected: bool) -> None:
    result = R16.evaluate(make_facts({"English": grade}))

    assert_result(result, R16, expected)


def test_r16_fails_when_english_is_missing() -> None:
    result = R16.evaluate(make_facts({}))

    assert_result(result, R16, False)
    assert "not supplied" in result.message


@pytest.mark.parametrize(
    ("ol_results", "expected"),
    [
        ({"Sinhala": "C"}, True),
        ({"Tamil": "C"}, True),
        ({"Sinhala": "S", "Tamil": "A"}, True),
        ({"Sinhala": "A", "Tamil": "S"}, True),
        ({"Sinhala": "S", "Tamil": "S"}, False),
        ({"Sinhala": "S"}, False),
        ({"Tamil": "S"}, False),
        ({}, False),
    ],
)
def test_r17_covers_every_sinhala_or_tamil_branch(
    ol_results: dict[str, str],
    expected: bool,
) -> None:
    result = R17.evaluate(make_facts(ol_results))

    assert_result(result, R17, expected)
    assert "Sinhala" in result.message
    assert "Tamil" in result.message
    assert " OR " in result.message


@pytest.mark.parametrize(
    ("rule", "subject", "passing_grade", "failing_grade"),
    [
        (R19, "Mathematics", "C", "S"),
        (R20, "Science", "S", "F"),
        (R21, "English", "C", "S"),
    ],
)
def test_quantity_surveying_ol_grade_boundaries(
    rule: Rule,
    subject: str,
    passing_grade: str,
    failing_grade: str,
) -> None:
    passing_result = rule.evaluate(make_facts({subject: passing_grade}))
    failing_result = rule.evaluate(make_facts({subject: failing_grade}))

    assert_result(passing_result, rule, True)
    assert_result(failing_result, rule, False)


@pytest.mark.parametrize(
    "rule",
    [R19, R20, R21],
)
def test_quantity_surveying_ol_rule_fails_when_subject_is_missing(rule: Rule) -> None:
    result = rule.evaluate(make_facts({}))

    assert_result(result, rule, False)
    assert "not supplied" in result.message
