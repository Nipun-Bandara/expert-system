"""Tests for course-specific rules R05-R08."""

import pytest

from expert_system.knowledge_base import R05, R06, R07, R08, SOURCE, Rule
from expert_system.models import ApplicantFacts, RuleResult


MEDICAL_SUBJECTS = ("Biology", "Chemistry", "Physics")
ENGINEERING_SUBJECTS = ("Chemistry", "Combined Mathematics", "Physics")


def make_facts(al_results: dict[str, str]) -> ApplicantFacts:
    """Create applicant facts for direct course-rule evaluation."""
    return ApplicantFacts(
        al_results=al_results,
        same_sitting=True,
        al_attempts=1,
        common_general_paper_mark=30,
        previous_state_university_registration=False,
        ol_results={},
    )


def assert_result_details(
    result: RuleResult,
    rule: Rule,
    required_subjects: tuple[str, ...],
    expected: bool,
) -> None:
    """Assert complete rule identity, citation, subject details, and outcome."""
    assert result.rule_id == rule.id
    assert result.passed is expected
    assert result.source == SOURCE
    assert result.page == rule.page
    assert "Required subjects:" in result.message
    assert "Supplied relevant grades:" in result.message
    assert "PASS:" in result.message if expected else "FAIL:" in result.message
    for subject in required_subjects:
        assert subject in result.message


@pytest.mark.parametrize(
    ("rule", "required_subjects", "grades"),
    [
        (R05, MEDICAL_SUBJECTS, {"Biology": "A", "Chemistry": "C", "Physics": "S"}),
        (R06, MEDICAL_SUBJECTS, {"Biology": "S", "Chemistry": "S", "Physics": "S"}),
        (R07, MEDICAL_SUBJECTS, {"Biology": "S", "Chemistry": "S", "Physics": "S"}),
        (
            R08,
            ENGINEERING_SUBJECTS,
            {"Chemistry": "S", "Combined Mathematics": "S", "Physics": "S"},
        ),
    ],
)
def test_exact_valid_subject_combinations_pass(
    rule: Rule,
    required_subjects: tuple[str, ...],
    grades: dict[str, str],
) -> None:
    result = rule.evaluate(make_facts(grades))

    assert_result_details(result, rule, required_subjects, True)


@pytest.mark.parametrize(
    ("rule", "required_subjects", "grades"),
    [
        (R05, MEDICAL_SUBJECTS, {"Biology": "A", "Chemistry": "C"}),
        (R06, MEDICAL_SUBJECTS, {"Biology": "S", "Chemistry": "S"}),
        (R07, MEDICAL_SUBJECTS, {"Biology": "S", "Chemistry": "S"}),
        (R08, ENGINEERING_SUBJECTS, {"Chemistry": "S", "Physics": "S"}),
    ],
)
def test_missing_required_subject_fails(
    rule: Rule,
    required_subjects: tuple[str, ...],
    grades: dict[str, str],
) -> None:
    result = rule.evaluate(make_facts(grades))

    assert_result_details(result, rule, required_subjects, False)
    assert "missing required subjects" in result.message


@pytest.mark.parametrize(
    ("rule", "required_subjects", "grades"),
    [
        (R05, MEDICAL_SUBJECTS, {"Biology": "A", "Chemistry": "C", "Physics": "F"}),
        (R06, MEDICAL_SUBJECTS, {"Biology": "S", "Chemistry": "S", "Physics": "F"}),
        (R07, MEDICAL_SUBJECTS, {"Biology": "S", "Chemistry": "S", "Physics": "F"}),
        (
            R08,
            ENGINEERING_SUBJECTS,
            {"Chemistry": "S", "Combined Mathematics": "S", "Physics": "F"},
        ),
    ],
)
def test_one_f_grade_fails(
    rule: Rule,
    required_subjects: tuple[str, ...],
    grades: dict[str, str],
) -> None:
    result = rule.evaluate(make_facts(grades))

    assert_result_details(result, rule, required_subjects, False)
    assert "below S" in result.message


@pytest.mark.parametrize(
    ("grades", "expected"),
    [
        ({"Biology": "C", "Chemistry": "C", "Physics": "S"}, True),
        ({"Biology": "C", "Chemistry": "S", "Physics": "S"}, False),
        ({"Biology": "A", "Chemistry": "B", "Physics": "C"}, True),
    ],
)
def test_medicine_grade_combinations(
    grades: dict[str, str],
    expected: bool,
) -> None:
    result = R05.evaluate(make_facts(grades))

    assert_result_details(result, R05, MEDICAL_SUBJECTS, expected)
