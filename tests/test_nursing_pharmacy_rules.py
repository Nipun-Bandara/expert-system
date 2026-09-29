"""Independent tests for Nursing and Pharmacy rules R09-R13."""

import pytest

from expert_system.knowledge_base import R09, R10, R11, R12, R13, SOURCE, Rule
from expert_system.models import ApplicantFacts, RuleResult


def make_facts(**overrides: object) -> ApplicantFacts:
    """Create facts with valid Nursing and Pharmacy defaults."""
    values = {
        "al_results": {"Biology": "S", "Chemistry": "C", "Physics": "S"},
        "same_sitting": True,
        "al_attempts": 1,
        "common_general_paper_mark": 30,
        "previous_state_university_registration": False,
        "ol_results": {"English": "S"},
        "height_cm": 147.32,
        "nursing_physical_condition_met": True,
    }
    values.update(overrides)
    return ApplicantFacts(**values)  # type: ignore[arg-type]


def assert_result(result: RuleResult, rule: Rule, expected: bool) -> None:
    """Assert the common rule-result fields."""
    assert result.rule_id == rule.id
    assert result.passed is expected
    assert result.message
    assert result.source == SOURCE
    assert result.page == rule.page


@pytest.mark.parametrize(
    ("grades", "expected"),
    [
        ({"Biology": "S", "Chemistry": "S", "Physics": "S"}, True),
        ({"Biology": "S", "Chemistry": "S"}, False),
        ({"Biology": "S", "Chemistry": "S", "Physics": "F"}, False),
    ],
)
def test_r09_nursing_al_subjects(grades: dict[str, str], expected: bool) -> None:
    result = R09.evaluate(make_facts(al_results=grades))

    assert_result(result, R09, expected)


@pytest.mark.parametrize(
    ("ol_results", "expected"),
    [({"English": "S"}, True), ({"English": "F"}, False), ({}, False)],
)
def test_r10_nursing_ol_english(
    ol_results: dict[str, str],
    expected: bool,
) -> None:
    result = R10.evaluate(make_facts(ol_results=ol_results))

    assert_result(result, R10, expected)


@pytest.mark.parametrize(
    ("height_cm", "expected"),
    [(147.31, False), (147.32, True), (148.0, True)],
)
def test_r11_nursing_height_boundary(height_cm: float, expected: bool) -> None:
    result = R11.evaluate(make_facts(height_cm=height_cm))

    assert_result(result, R11, expected)
    assert "147.32 cm" in result.message


def test_r11_fails_when_physical_condition_is_not_recorded_as_satisfied() -> None:
    result = R11.evaluate(make_facts(nursing_physical_condition_met=False))

    assert_result(result, R11, False)
    assert "not recorded as satisfied" in result.message


@pytest.mark.parametrize(
    ("height_cm", "condition", "missing_field"),
    [
        (None, True, "height_cm"),
        (147.32, None, "nursing_physical_condition_met"),
        (None, None, "height_cm"),
    ],
)
def test_r11_fails_with_insufficient_information(
    height_cm: float | None,
    condition: bool | None,
    missing_field: str,
) -> None:
    result = R11.evaluate(
        make_facts(
            height_cm=height_cm,
            nursing_physical_condition_met=condition,
        )
    )

    assert_result(result, R11, False)
    assert "insufficient information" in result.message
    assert missing_field in result.message


@pytest.mark.parametrize(
    ("grades", "expected"),
    [
        ({"Chemistry": "C", "Physics": "S", "Biology": "S"}, True),
        ({"Chemistry": "S", "Physics": "A", "Biology": "A"}, False),
    ],
)
def test_r12_pharmacy_grade_boundaries(
    grades: dict[str, str],
    expected: bool,
) -> None:
    result = R12.evaluate(make_facts(al_results=grades))

    assert_result(result, R12, expected)


def test_r12_fails_when_a_required_subject_is_missing() -> None:
    result = R12.evaluate(
        make_facts(al_results={"Chemistry": "C", "Physics": "S"})
    )

    assert_result(result, R12, False)
    assert "missing required subjects: Biology" in result.message


@pytest.mark.parametrize(
    ("ol_results", "expected"),
    [({"English": "S"}, True), ({"English": "F"}, False), ({}, False)],
)
def test_r13_pharmacy_ol_english(
    ol_results: dict[str, str],
    expected: bool,
) -> None:
    result = R13.evaluate(make_facts(ol_results=ol_results))

    assert_result(result, R13, expected)
