"""Tests for course-level inference and rule-result preservation."""

import pytest

from expert_system.engine import (
    COURSE_RULE_MAP,
    evaluate_all_courses,
    evaluate_course,
    evaluate_general_eligibility,
)
from expert_system.models import ApplicantFacts, CourseEvaluation


def make_facts(**overrides: object) -> ApplicantFacts:
    """Create facts that pass the general rules and Medicine rule by default."""
    values = {
        "al_results": {"Biology": "A", "Chemistry": "C", "Physics": "S"},
        "same_sitting": True,
        "al_attempts": 1,
        "common_general_paper_mark": 30,
        "previous_state_university_registration": False,
        "ol_results": {"English": "C", "Sinhala": "C"},
        "height_cm": 147.32,
        "nursing_physical_condition_met": True,
    }
    values.update(overrides)
    return ApplicantFacts(**values)  # type: ignore[arg-type]


def test_course_rule_mapping_contains_expected_rules() -> None:
    assert {
        course: [rule.id for rule in rules]
        for course, rules in COURSE_RULE_MAP.items()
    } == {
        "Medicine": ["R05"],
        "Dental Surgery": ["R06"],
        "Veterinary Science": ["R07"],
        "Engineering": ["R08"],
        "Nursing": ["R09", "R10", "R11"],
        "Pharmacy": ["R12", "R13"],
        "Information Technology": ["R14"],
        "Law": ["R15", "R16", "R17"],
        "Quantity Surveying": ["R18", "R19", "R20", "R21"],
    }


def test_r03_failure_makes_every_course_ineligible() -> None:
    applicant = make_facts(common_general_paper_mark=29)

    general_results = evaluate_general_eligibility(applicant)
    evaluations = evaluate_all_courses(applicant)

    assert [result.rule_id for result in general_results] == [
        "R01",
        "R02",
        "R03",
        "R04",
    ]
    assert next(result for result in general_results if result.rule_id == "R03").passed is False
    assert all(evaluation.eligible is False for evaluation in evaluations)
    assert all("R03 - Common General Paper" in evaluation.explanation for evaluation in evaluations)


def test_general_rules_and_r05_make_medicine_eligible() -> None:
    evaluation = evaluate_course(make_facts(), "Medicine")

    assert isinstance(evaluation, CourseEvaluation)
    assert evaluation.course_name == "Medicine"
    assert evaluation.eligible is True
    assert all(result.passed for result in evaluation.general_rule_results)
    assert [result.rule_id for result in evaluation.course_rule_results] == ["R05"]
    assert "FINAL RESULT: ELIGIBLE" in evaluation.explanation


def test_medicine_is_ineligible_when_r05_fails() -> None:
    applicant = make_facts(
        al_results={"Biology": "C", "Chemistry": "S", "Physics": "S"}
    )

    evaluation = evaluate_course(applicant, "Medicine")

    assert all(result.passed for result in evaluation.general_rule_results)
    assert evaluation.course_rule_results[0].passed is False
    assert evaluation.eligible is False
    assert "R05 - Medicine Subject/Grade" in evaluation.explanation


@pytest.mark.parametrize(
    ("overrides", "failed_rule"),
    [
        (
            {
                "al_results": {
                    "Biology": "S",
                    "Chemistry": "S",
                    "Accounting": "S",
                }
            },
            "R09",
        ),
        ({"ol_results": {"English": "F"}}, "R10"),
        ({"height_cm": 147.31}, "R11"),
    ],
)
def test_nursing_requires_r09_and_r10_and_r11(
    overrides: dict[str, object],
    failed_rule: str,
) -> None:
    evaluation = evaluate_course(make_facts(**overrides), "Nursing")

    results = {result.rule_id: result.passed for result in evaluation.course_rule_results}
    assert list(results) == ["R09", "R10", "R11"]
    assert results[failed_rule] is False
    assert evaluation.eligible is False


@pytest.mark.parametrize(
    ("overrides", "failed_rule"),
    [
        (
            {"al_results": {"Biology": "A", "Chemistry": "S", "Physics": "A"}},
            "R12",
        ),
        ({"ol_results": {"English": "F"}}, "R13"),
    ],
)
def test_pharmacy_requires_r12_and_r13(
    overrides: dict[str, object],
    failed_rule: str,
) -> None:
    evaluation = evaluate_course(make_facts(**overrides), "Pharmacy")

    results = {result.rule_id: result.passed for result in evaluation.course_rule_results}
    assert list(results) == ["R12", "R13"]
    assert results[failed_rule] is False
    assert evaluation.eligible is False


def valid_law_facts(**overrides: object) -> ApplicantFacts:
    """Create facts satisfying R15, R16, R17, and all general rules."""
    values = {
        "al_results": {"Accounting": "C", "Biology": "C", "Chemistry": "S"},
        "ol_results": {"English": "C", "Sinhala": "C"},
    }
    values.update(overrides)
    return make_facts(**values)


def test_law_requires_r15_and_r16_and_r17() -> None:
    passing = evaluate_course(valid_law_facts(), "Law")
    failing_r15 = evaluate_course(
        valid_law_facts(
            al_results={"Accounting": "C", "Biology": "S", "Chemistry": "S"}
        ),
        "Law",
    )
    failing_r16 = evaluate_course(
        valid_law_facts(ol_results={"English": "S", "Sinhala": "C"}),
        "Law",
    )
    failing_r17 = evaluate_course(
        valid_law_facts(ol_results={"English": "C", "Sinhala": "S"}),
        "Law",
    )

    assert passing.eligible is True
    assert [result.rule_id for result in passing.course_rule_results] == [
        "R15",
        "R16",
        "R17",
    ]
    assert failing_r15.eligible is False
    assert failing_r15.course_rule_results[0].passed is False
    assert failing_r16.eligible is False
    assert failing_r16.course_rule_results[1].passed is False
    assert failing_r17.eligible is False
    assert failing_r17.course_rule_results[2].passed is False


def test_invalid_course_name_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="Unknown course 'Unknown Course'"):
        evaluate_course(make_facts(), "Unknown Course")
