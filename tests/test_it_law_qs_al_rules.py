"""Branch tests for A/L rules R14, R15, and R18."""

import pytest

from expert_system.knowledge_base import R14, R15, R18, SOURCE, Rule
from expert_system.models import ApplicantFacts, RuleResult


def make_facts(al_results: dict[str, str]) -> ApplicantFacts:
    """Create applicant facts for direct A/L rule evaluation."""
    return ApplicantFacts(
        al_results=al_results,
        same_sitting=True,
        al_attempts=1,
        common_general_paper_mark=30,
        previous_state_university_registration=False,
        ol_results={},
    )


def assert_result(result: RuleResult, rule: Rule, expected: bool) -> None:
    """Assert outcome, explanation, and source metadata."""
    assert result.rule_id == rule.id
    assert result.passed is expected
    assert ("PASS:" if expected else "FAIL:") in result.message
    assert result.source == SOURCE
    assert result.page == rule.page


@pytest.mark.parametrize(
    "qualifying_subject",
    ["Higher Mathematics", "Combined Mathematics", "Mathematics", "Physics"],
)
def test_r14_passes_for_each_grade_c_or_branch(qualifying_subject: str) -> None:
    grades = {
        qualifying_subject: "C",
        "Accounting": "S",
        "Economics": "S",
    }

    result = R14.evaluate(make_facts(grades))

    assert_result(result, R14, True)
    assert f"{qualifying_subject}=C" in result.message


def test_r14_fails_when_no_listed_subject_has_c_or_better() -> None:
    result = R14.evaluate(
        make_facts({"Higher Mathematics": "S", "Accounting": "A", "Economics": "A"})
    )

    assert_result(result, R14, False)


def test_r14_fails_with_fewer_than_three_passed_al_subjects() -> None:
    result = R14.evaluate(
        make_facts({"Higher Mathematics": "C", "Accounting": "S", "Economics": "F"})
    )

    assert_result(result, R14, False)


@pytest.mark.parametrize(
    "grades",
    [
        {"Accounting": "C", "Biology": "C", "Chemistry": "S"},
        {"Accounting": "C", "Buddhism": "C", "English": "S"},
        {"Accounting": "C", "Biology": "C", "Buddhism": "S"},
    ],
)
def test_r15_passes_for_every_valid_subject_list_branch(
    grades: dict[str, str],
) -> None:
    result = R15.evaluate(make_facts(grades))

    assert_result(result, R15, True)


@pytest.mark.parametrize(
    "grades",
    [
        {"Buddhism": "C", "English": "C", "Tamil": "S"},
        {"Accounting": "C", "Buddhism": "C", "Art": "S"},
    ],
)
def test_r15_fails_invalid_subject_list_branches(grades: dict[str, str]) -> None:
    result = R15.evaluate(make_facts(grades))

    assert_result(result, R15, False)


def test_r15_fails_without_two_c_grades() -> None:
    result = R15.evaluate(
        make_facts({"Accounting": "C", "Biology": "S", "Chemistry": "S"})
    )

    assert_result(result, R15, False)


@pytest.mark.parametrize(
    "grades",
    [
        {"Combined Mathematics": "S", "Accounting": "S", "Physics": "S"},
        {"Higher Mathematics": "S", "Economics": "S", "Chemistry": "S"},
        {
            "Combined Mathematics": "S",
            "Higher Mathematics": "S",
            "Business Studies": "S",
        },
    ],
)
def test_r18_passes_for_each_math_count_branch(grades: dict[str, str]) -> None:
    result = R18.evaluate(make_facts(grades))

    assert_result(result, R18, True)


@pytest.mark.parametrize(
    "grades",
    [
        {"Accounting": "S", "Physics": "S", "Chemistry": "S"},
        {"Combined Mathematics": "S", "Accounting": "S", "Art": "S"},
        {"Combined Mathematics": "S", "Accounting": "S", "Physics": "F"},
    ],
)
def test_r18_fails_when_any_exact_condition_is_unsatisfied(
    grades: dict[str, str],
) -> None:
    result = R18.evaluate(make_facts(grades))

    assert_result(result, R18, False)
