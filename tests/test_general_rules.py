"""Tests for the sourced general eligibility rules R01-R04."""

import pytest

from expert_system.knowledge_base import GENERAL_RULES, R01, R02, R03, R04, SOURCE
from expert_system.models import ApplicantFacts, RuleResult


def make_facts(**overrides: object) -> ApplicantFacts:
    """Create applicant facts with valid defaults for general-rule tests."""
    values = {
        "al_results": {"Subject One": "A", "Subject Two": "S", "Subject Three": "C"},
        "same_sitting": True,
        "al_attempts": 1,
        "common_general_paper_mark": 30,
        "previous_state_university_registration": False,
        "ol_results": {},
    }
    values.update(overrides)
    return ApplicantFacts(**values)  # type: ignore[arg-type]


def assert_complete_result(
    result: RuleResult,
    *,
    rule_id: str,
    passed: bool,
    page: int,
) -> None:
    """Assert that a result includes its outcome, explanation, and citation."""
    assert result.rule_id == rule_id
    assert result.passed is passed
    assert result.message
    assert result.source == SOURCE
    assert result.page == page


def test_general_rule_collection_contains_only_r01_through_r04() -> None:
    assert [rule.id for rule in GENERAL_RULES] == ["R01", "R02", "R03", "R04"]


def test_r01_passes_for_three_s_or_better_results_in_same_sitting() -> None:
    result = R01.evaluate(make_facts())

    assert_complete_result(result, rule_id="R01", passed=True, page=9)


def test_r01_fails_when_results_are_not_from_same_sitting() -> None:
    result = R01.evaluate(make_facts(same_sitting=False))

    assert_complete_result(result, rule_id="R01", passed=False, page=9)


def test_r01_fails_when_any_grade_is_below_s() -> None:
    result = R01.evaluate(
        make_facts(
            al_results={"Subject One": "A", "Subject Two": "C", "Subject Three": "F"}
        )
    )

    assert_complete_result(result, rule_id="R01", passed=False, page=9)


def test_r01_fails_unless_exactly_three_results_are_supplied() -> None:
    result = R01.evaluate(
        make_facts(al_results={"Subject One": "A", "Subject Two": "S"})
    )

    assert_complete_result(result, rule_id="R01", passed=False, page=9)


@pytest.mark.parametrize(
    ("attempts", "expected"),
    [(1, True), (3, True), (4, False)],
)
def test_r02_enforces_maximum_attempt_limit(attempts: int, expected: bool) -> None:
    result = R02.evaluate(make_facts(al_attempts=attempts))

    assert_complete_result(result, rule_id="R02", passed=expected, page=9)


@pytest.mark.parametrize(
    ("mark", "expected"),
    [(29, False), (30, True), (100, True)],
)
def test_r03_enforces_common_general_paper_minimum(
    mark: float,
    expected: bool,
) -> None:
    result = R03.evaluate(make_facts(common_general_paper_mark=mark))

    assert_complete_result(result, rule_id="R03", passed=expected, page=9)


@pytest.mark.parametrize(
    ("previously_registered", "expected"),
    [(False, True), (True, False)],
)
def test_r04_reverses_prior_registration_for_eligibility(
    previously_registered: bool,
    expected: bool,
) -> None:
    result = R04.evaluate(
        make_facts(previous_state_university_registration=previously_registered)
    )

    assert_complete_result(result, rule_id="R04", passed=expected, page=13)
    if previously_registered:
        assert "disqualified" in result.message
    else:
        assert "rule is satisfied" in result.message
