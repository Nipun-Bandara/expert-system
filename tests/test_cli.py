"""Tests for CLI parsing, prompting, collection, and display helpers."""

import pytest

from expert_system.cli import (
    collect_applicant_facts,
    display_course_evaluation,
    evaluate_all_courses_workflow,
    evaluate_specific_course_workflow,
    parse_grade,
    parse_mark,
    parse_positive_float,
    parse_positive_integer,
    parse_yes_no,
    prompt_grade,
    run,
)
from expert_system.engine import COURSE_RULE_MAP
from expert_system.explanations import build_course_explanation
from expert_system.models import ApplicantFacts, CourseEvaluation, RuleResult


@pytest.mark.parametrize("value", ["y", "Y", "yes", " YES "])
def test_parse_yes_no_accepts_yes_variants(value: str) -> None:
    assert parse_yes_no(value) is True


@pytest.mark.parametrize("value", ["n", "N", "no", " NO "])
def test_parse_yes_no_accepts_no_variants(value: str) -> None:
    assert parse_yes_no(value) is False


@pytest.mark.parametrize("value", ["", "maybe", "true", "1"])
def test_parse_yes_no_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_yes_no(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("a", "A"), (" B ", "B"), ("c", "C"), ("s", "S"), ("f", "F")],
)
def test_parse_grade_accepts_only_supported_grades(value: str, expected: str) -> None:
    assert parse_grade(value) == expected


@pytest.mark.parametrize("value", ["", "D", "A+", "pass"])
def test_parse_grade_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_grade(value)


@pytest.mark.parametrize("value", ["1", "3", " 2 "])
def test_parse_positive_integer(value: str) -> None:
    assert parse_positive_integer(value) >= 1


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "text"])
def test_parse_positive_integer_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_positive_integer(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("0", 0.0), ("30", 30.0), ("100", 100.0)],
)
def test_parse_mark_boundaries(value: str, expected: float) -> None:
    assert parse_mark(value) == expected


@pytest.mark.parametrize("value", ["-0.1", "100.1", "text"])
def test_parse_mark_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_mark(value)


@pytest.mark.parametrize("value", ["0", "-1", "text"])
def test_parse_positive_float_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_positive_float(value)


def test_prompt_grade_reprompts_instead_of_replacing_invalid_input() -> None:
    responses = iter(["D", "c"])
    output: list[str] = []

    result = prompt_grade("Grade: ", lambda _: next(responses), output.append)

    assert result == "C"
    assert output and output[0].startswith("Invalid input:")


def test_collect_applicant_facts_collects_course_relevant_fields() -> None:
    responses = iter(
        [
            "Biology",
            "A",
            "Chemistry",
            "C",
            "Physics",
            "S",
            "yes",
            "1",
            "30",
            "no",
            "S",
            "147.32",
            "yes",
        ]
    )

    facts = collect_applicant_facts(
        ["Nursing"], lambda _: next(responses), lambda _: None
    )

    assert facts.al_results == {"biology": "A", "chemistry": "C", "physics": "S"}
    assert facts.ol_results == {"english": "S"}
    assert facts.same_sitting is True
    assert facts.height_cm == 147.32
    assert facts.nursing_physical_condition_met is True


def test_display_course_evaluation_shows_rule_details_and_sources() -> None:
    general_result = RuleResult(
        rule_id="R03",
        rule_name="Common General Paper",
        passed=True,
        message="CGP requirement satisfied.",
        source="handbook.pdf",
        page=9,
    )
    course_result = RuleResult(
        rule_id="R12",
        rule_name="Pharmacy A/L Grades",
        passed=False,
        message="Chemistry requirement not satisfied.",
        source="handbook.pdf",
        page=58,
    )
    explanation = build_course_explanation(
        "Pharmacy",
        False,
        [general_result],
        [course_result],
    )
    evaluation = CourseEvaluation(
        course_name="Pharmacy",
        eligible=False,
        general_rule_results=[general_result],
        course_rule_results=[course_result],
        explanation=explanation,
    )
    output: list[str] = []

    display_course_evaluation(evaluation, output.append)
    rendered = "\n".join(output)

    assert "Pharmacy" in rendered
    assert "FINAL RESULT: NOT ELIGIBLE" in rendered
    assert "GENERAL RULE TRACE" in rendered
    assert "PASS R03 - Common General Paper" in rendered
    assert "COURSE RULE TRACE" in rendered
    assert "FAIL R12 - Pharmacy A/L Grades" in rendered
    assert "FAILED REQUIREMENTS" in rendered
    assert "SOURCE REFERENCES" in rendered
    assert "handbook.pdf, page 58 (R12)" in rendered


def test_run_can_exit_from_main_menu() -> None:
    output: list[str] = []

    run(lambda _: "3", output.append)

    assert output[0] == "Sri Lankan University Course Eligibility Expert System"
    assert output[-1] == "Goodbye."


def test_cli_workflows_select_the_explicit_inference_modes() -> None:
    applicant = ApplicantFacts(
        al_results={"Biology": "A", "Chemistry": "C", "Physics": "S"},
        same_sitting=True,
        al_attempts=1,
        common_general_paper_mark=30,
        previous_state_university_registration=False,
        ol_results={"English": "C", "Sinhala": "C"},
        height_cm=148,
        nursing_physical_condition_met=True,
    )

    selected = evaluate_specific_course_workflow(applicant, "Medicine")
    all_courses = evaluate_all_courses_workflow(applicant)

    assert selected.inference_mode == "backward chaining"
    assert selected.inference_trace is not None
    assert selected.inference_trace.evaluated_rule_ids == [
        "R01", "R02", "R03", "R04", "R05"
    ]
    assert len(all_courses) == len(COURSE_RULE_MAP)
    assert all(
        evaluation.inference_mode == "forward chaining"
        for evaluation in all_courses
    )
