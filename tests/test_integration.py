"""End-to-end applicant scenarios across facts, rules, and inference."""

import pytest

from expert_system.engine import evaluate_course
from expert_system.models import ApplicantFacts, CourseEvaluation


HANDBOOK_2025 = "student_handbook_english_2025/2026.pdf"
HANDBOOK = "student_handbook_english_2025/2026.pdf"


def make_applicant(**overrides: object) -> ApplicantFacts:
    """Create a generally eligible Medicine applicant with optional changes."""
    values = {
        "al_results": {"Biology": "C", "Chemistry": "C", "Physics": "S"},
        "same_sitting": True,
        "al_attempts": 1,
        "common_general_paper_mark": 30,
        "previous_state_university_registration": False,
        "ol_results": {},
        "height_cm": None,
        "nursing_physical_condition_met": None,
    }
    values.update(overrides)
    return ApplicantFacts(**values)  # type: ignore[arg-type]


def failed_rule_ids(evaluation: CourseEvaluation) -> list[str]:
    """Return failed general and course rule IDs in evaluation order."""
    return [
        result.rule_id
        for result in [
            *evaluation.general_rule_results,
            *evaluation.course_rule_results,
        ]
        if not result.passed
    ]


def assert_evaluation(
    evaluation: CourseEvaluation,
    *,
    eligible: bool,
    failed_rules: list[str],
) -> None:
    """Assert final status, failed IDs, trace content, and complete metadata."""
    assert evaluation.eligible is eligible
    assert failed_rule_ids(evaluation) == failed_rules
    assert (
        "FINAL RESULT: ELIGIBLE"
        if eligible
        else "FINAL RESULT: NOT ELIGIBLE"
    ) in evaluation.explanation

    all_results = [
        *evaluation.general_rule_results,
        *evaluation.course_rule_results,
    ]
    for result in all_results:
        assert result.source
        assert result.page > 0
        assert result.rule_id in evaluation.explanation
        assert f"{result.source}, page {result.page}" in evaluation.explanation

    for rule_id in failed_rules:
        assert f"- {rule_id} -" in evaluation.explanation


@pytest.mark.parametrize(
    ("overrides", "failed_rule", "page"),
    [
        ({"common_general_paper_mark": 29}, "R03", 9),
        ({"al_attempts": 4}, "R02", 9),
        ({"previous_state_university_registration": True}, "R04", 13),
    ],
    ids=[
        "scenario_1_cgp_below_30",
        "scenario_2_more_than_three_attempts",
        "scenario_3_prior_registration",
    ],
)
def test_general_failures_disqualify_otherwise_eligible_medicine_applicant(
    overrides: dict[str, object],
    failed_rule: str,
    page: int,
) -> None:
    evaluation = evaluate_course(make_applicant(**overrides), "Medicine")

    assert_evaluation(evaluation, eligible=False, failed_rules=[failed_rule])
    failed_result = next(
        result
        for result in evaluation.general_rule_results
        if result.rule_id == failed_rule
    )
    assert failed_result.source == HANDBOOK_2025
    assert failed_result.page == page


def test_scenario_4_medicine_is_eligible_with_c_c_s() -> None:
    evaluation = evaluate_course(make_applicant(), "Medicine")

    assert_evaluation(evaluation, eligible=True, failed_rules=[])
    assert evaluation.course_rule_results[0].rule_id == "R05"


def test_scenario_5_medicine_fails_with_c_s_s() -> None:
    applicant = make_applicant(
        al_results={"Biology": "C", "Chemistry": "S", "Physics": "S"}
    )

    evaluation = evaluate_course(applicant, "Medicine")

    assert_evaluation(evaluation, eligible=False, failed_rules=["R05"])


def test_scenario_6_dental_surgery_succeeds_with_s_s_s() -> None:
    applicant = make_applicant(
        al_results={"Biology": "S", "Chemistry": "S", "Physics": "S"}
    )

    evaluation = evaluate_course(applicant, "Dental Surgery")

    assert_evaluation(evaluation, eligible=True, failed_rules=[])


def test_scenario_7_engineering_succeeds_with_required_subjects() -> None:
    applicant = make_applicant(
        al_results={
            "Combined Mathematics": "S",
            "Physics": "S",
            "Chemistry": "S",
        }
    )

    evaluation = evaluate_course(applicant, "Engineering")

    assert_evaluation(evaluation, eligible=True, failed_rules=[])


def test_scenario_8_engineering_fails_without_combined_mathematics() -> None:
    applicant = make_applicant(
        al_results={"Biology": "S", "Physics": "S", "Chemistry": "S"}
    )

    evaluation = evaluate_course(applicant, "Engineering")

    assert_evaluation(evaluation, eligible=False, failed_rules=["R08"])


def test_scenario_9_nursing_passes_r09_through_r11() -> None:
    applicant = make_applicant(
        al_results={"Biology": "S", "Chemistry": "S", "Physics": "S"},
        ol_results={"English": "S"},
        height_cm=147.32,
        nursing_physical_condition_met=True,
    )

    evaluation = evaluate_course(applicant, "Nursing")

    assert_evaluation(evaluation, eligible=True, failed_rules=[])
    assert [result.rule_id for result in evaluation.course_rule_results] == [
        "R09",
        "R10",
        "R11",
    ]


def test_scenario_10_nursing_fails_ol_english_r10() -> None:
    applicant = make_applicant(
        al_results={"Biology": "S", "Chemistry": "S", "Physics": "S"},
        ol_results={"English": "F"},
        height_cm=148,
        nursing_physical_condition_met=True,
    )

    evaluation = evaluate_course(applicant, "Nursing")

    assert_evaluation(evaluation, eligible=False, failed_rules=["R10"])


def test_scenario_11_pharmacy_passes_required_al_and_ol_grades() -> None:
    applicant = make_applicant(
        al_results={"Chemistry": "C", "Physics": "S", "Biology": "S"},
        ol_results={"English": "S"},
    )

    evaluation = evaluate_course(applicant, "Pharmacy")

    assert_evaluation(evaluation, eligible=True, failed_rules=[])


def test_scenario_12_pharmacy_fails_when_chemistry_is_s() -> None:
    applicant = make_applicant(
        al_results={"Chemistry": "S", "Physics": "S", "Biology": "S"},
        ol_results={"English": "S"},
    )

    evaluation = evaluate_course(applicant, "Pharmacy")

    assert_evaluation(evaluation, eligible=False, failed_rules=["R12"])


@pytest.mark.parametrize(
    ("al_results", "eligible", "failed_rules"),
    [
        (
            {"Higher Mathematics": "C", "Accounting": "S", "Economics": "S"},
            True,
            [],
        ),
        (
            {"Higher Mathematics": "S", "Accounting": "A", "Economics": "A"},
            False,
            ["R14"],
        ),
    ],
    ids=["r14_pass", "r14_fail"],
)
def test_finalized_information_technology_scenarios(
    al_results: dict[str, str],
    eligible: bool,
    failed_rules: list[str],
) -> None:
    evaluation = evaluate_course(
        make_applicant(al_results=al_results),
        "Information Technology",
    )

    assert_evaluation(
        evaluation,
        eligible=eligible,
        failed_rules=failed_rules,
    )
    result = evaluation.course_rule_results[0]
    assert result.source == HANDBOOK
    assert result.page == 83


@pytest.mark.parametrize(
    ("al_results", "ol_results", "eligible", "failed_rules"),
    [
        (
            {"Accounting": "C", "Biology": "C", "Chemistry": "S"},
            {"English": "C", "Sinhala": "C"},
            True,
            [],
        ),
        (
            {"Accounting": "C", "Biology": "S", "Chemistry": "S"},
            {"English": "C", "Sinhala": "C"},
            False,
            ["R15"],
        ),
        (
            {"Accounting": "C", "Biology": "C", "Chemistry": "S"},
            {"English": "S", "Sinhala": "C"},
            False,
            ["R16"],
        ),
        (
            {"Accounting": "C", "Biology": "C", "Chemistry": "S"},
            {"English": "C", "Sinhala": "S", "Tamil": "S"},
            False,
            ["R17"],
        ),
    ],
    ids=["law_pass", "r15_fail", "r16_fail", "r17_fail"],
)
def test_finalized_law_scenarios(
    al_results: dict[str, str],
    ol_results: dict[str, str],
    eligible: bool,
    failed_rules: list[str],
) -> None:
    evaluation = evaluate_course(
        make_applicant(al_results=al_results, ol_results=ol_results),
        "Law",
    )

    assert_evaluation(
        evaluation,
        eligible=eligible,
        failed_rules=failed_rules,
    )
    r15 = evaluation.course_rule_results[0]
    assert r15.source == HANDBOOK
    assert r15.page == 90


@pytest.mark.parametrize(
    ("al_results", "ol_results", "eligible", "failed_rules"),
    [
        (
            {"Combined Mathematics": "S", "Accounting": "S", "Physics": "S"},
            {"Mathematics": "C", "Science": "S", "English": "C"},
            True,
            [],
        ),
        (
            {"Biology": "S", "Accounting": "S", "Physics": "S"},
            {"Mathematics": "C", "Science": "S", "English": "C"},
            False,
            ["R18"],
        ),
        (
            {"Combined Mathematics": "S", "Accounting": "S", "Physics": "S"},
            {"Mathematics": "S", "Science": "S", "English": "C"},
            False,
            ["R19"],
        ),
        (
            {"Combined Mathematics": "S", "Accounting": "S", "Physics": "S"},
            {"Mathematics": "C", "Science": "F", "English": "C"},
            False,
            ["R20"],
        ),
        (
            {"Combined Mathematics": "S", "Accounting": "S", "Physics": "S"},
            {"Mathematics": "C", "Science": "S", "English": "S"},
            False,
            ["R21"],
        ),
    ],
    ids=["quantity_surveying_pass", "r18_fail", "r19_fail", "r20_fail", "r21_fail"],
)
def test_finalized_quantity_surveying_scenarios(
    al_results: dict[str, str],
    ol_results: dict[str, str],
    eligible: bool,
    failed_rules: list[str],
) -> None:
    evaluation = evaluate_course(
        make_applicant(al_results=al_results, ol_results=ol_results),
        "Quantity Surveying",
    )

    assert_evaluation(
        evaluation,
        eligible=eligible,
        failed_rules=failed_rules,
    )
    r18 = evaluation.course_rule_results[0]
    assert r18.source == HANDBOOK
    assert r18.page == 84
