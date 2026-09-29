"""Sourced general eligibility rules for the expert system knowledge base."""

from collections.abc import Callable
from dataclasses import dataclass

from expert_system.grades import count_grades_at_least
from expert_system.models import ApplicantFacts, RuleResult


RuleEvaluationFunction = Callable[[ApplicantFacts], RuleResult]
SOURCE = "student_handbook_english_2025/2026.pdf"


@dataclass
class Rule:
    """A sourced rule and the function used to evaluate it."""

    id: str
    name: str
    applies_to: str
    source: str
    page: int
    evaluation_function: RuleEvaluationFunction

    def evaluate(self, facts: ApplicantFacts) -> RuleResult:
        """Evaluate this rule against supplied applicant facts."""
        return self.evaluation_function(facts)


def _evaluate_r01(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the minimum grade and one-sitting requirement."""
    has_three_results = len(facts.al_results) == 3
    all_at_least_s = (
        count_grades_at_least(facts.al_results.values(), "S") == 3
        if has_three_results
        else False
    )
    passed = has_three_results and all_at_least_s and facts.same_sitting

    if passed:
        message = (
            "Exactly three A/L subjects have grade S or better and were obtained "
            "in one sitting."
        )
    elif not has_three_results:
        message = "Exactly three A/L subject results must be supplied."
    elif not all_at_least_s:
        message = "All three A/L subjects must have grade S or better."
    else:
        message = "The three A/L results were not obtained in one sitting."

    return RuleResult(
        rule_id="R01",
        rule_name="Minimum Grade & Sitting",
        passed=passed,
        message=message,
        source=SOURCE,
        page=9,
    )


def _evaluate_r02(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the maximum A/L attempt limit."""
    passed = facts.al_attempts <= 3
    message = (
        f"A/L attempt count {facts.al_attempts} is within the maximum of 3."
        if passed
        else f"A/L attempt count {facts.al_attempts} exceeds the maximum of 3."
    )
    return RuleResult(
        rule_id="R02",
        rule_name="Maximum Attempt Limit",
        passed=passed,
        message=message,
        source=SOURCE,
        page=9,
    )


def _evaluate_r03(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Common General Paper minimum mark."""
    passed = facts.common_general_paper_mark >= 30
    mark = f"{facts.common_general_paper_mark:g}"
    message = (
        f"Common General Paper mark {mark} satisfies the required minimum of 30%."
        if passed
        else f"Common General Paper mark {mark} is below the required minimum of 30%."
    )
    return RuleResult(
        rule_id="R03",
        rule_name="Common General Paper",
        passed=passed,
        message=message,
        source=SOURCE,
        page=9,
    )


def _evaluate_r04(facts: ApplicantFacts) -> RuleResult:
    """Disqualify an applicant who has previously registered internally."""
    passed = not facts.previous_state_university_registration
    message = (
        "Applicant has not previously registered as an internal student in a Sri "
        "Lankan state university, so this rule is satisfied."
        if passed
        else "Applicant has previously registered as an internal student in a Sri "
        "Lankan state university and is disqualified by this rule."
    )
    return RuleResult(
        rule_id="R04",
        rule_name="Prior Registration",
        passed=passed,
        message=message,
        source=SOURCE,
        page=13,
    )


R01 = Rule(
    id="R01",
    name="Minimum Grade & Sitting",
    applies_to="All applicants",
    source=SOURCE,
    page=9,
    evaluation_function=_evaluate_r01,
)

R02 = Rule(
    id="R02",
    name="Maximum Attempt Limit",
    applies_to="All applicants",
    source=SOURCE,
    page=9,
    evaluation_function=_evaluate_r02,
)

R03 = Rule(
    id="R03",
    name="Common General Paper",
    applies_to="All applicants",
    source=SOURCE,
    page=9,
    evaluation_function=_evaluate_r03,
)

R04 = Rule(
    id="R04",
    name="Prior Registration",
    applies_to="All applicants",
    source=SOURCE,
    page=13,
    evaluation_function=_evaluate_r04,
)

GENERAL_RULES = (R01, R02, R03, R04)


MEDICAL_SCIENCE_SUBJECTS = ("Biology", "Chemistry", "Physics")
ENGINEERING_SUBJECTS = ("Chemistry", "Combined Mathematics", "Physics")


def _relevant_grades(
    facts: ApplicantFacts,
    required_subjects: tuple[str, ...],
) -> dict[str, str]:
    """Return supplied grades for required subjects using their exact names."""
    return {
        subject: facts.al_results[subject.casefold()]
        for subject in required_subjects
        if subject.casefold() in facts.al_results
    }


def _subject_details(
    required_subjects: tuple[str, ...],
    supplied_grades: dict[str, str],
) -> str:
    """Format required subjects and supplied relevant grades for an explanation."""
    required = ", ".join(required_subjects)
    supplied = ", ".join(
        f"{subject}={grade}" for subject, grade in supplied_grades.items()
    )
    return (
        f"Required subjects: {required}. "
        f"Supplied relevant grades: {supplied or 'none'}."
    )


def _evaluate_three_subject_s_requirement(
    facts: ApplicantFacts,
    *,
    rule_id: str,
    rule_name: str,
    required_subjects: tuple[str, ...],
    page: int,
) -> RuleResult:
    """Evaluate a requirement for three named subjects at grade S or better."""
    supplied = _relevant_grades(facts, required_subjects)
    missing = [subject for subject in required_subjects if subject not in supplied]
    details = _subject_details(required_subjects, supplied)

    if missing:
        passed = False
        reason = (
            f"FAIL: missing required subjects: {', '.join(missing)}."
        )
    else:
        passed = count_grades_at_least(supplied.values(), "S") == 3
        reason = (
            "PASS: all three required subjects have grade S or better."
            if passed
            else "FAIL: at least one required subject has a grade below S."
        )

    return RuleResult(
        rule_id=rule_id,
        rule_name=rule_name,
        passed=passed,
        message=f"{details} {reason}",
        source=SOURCE,
        page=page,
    )


def _evaluate_r05(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Medicine subject and grade requirement."""
    supplied = _relevant_grades(facts, MEDICAL_SCIENCE_SUBJECTS)
    missing = [
        subject for subject in MEDICAL_SCIENCE_SUBJECTS if subject not in supplied
    ]
    details = _subject_details(MEDICAL_SCIENCE_SUBJECTS, supplied)

    if missing:
        passed = False
        reason = f"FAIL: missing required subjects: {', '.join(missing)}."
    else:
        all_at_least_s = count_grades_at_least(supplied.values(), "S") == 3
        at_least_two_c = count_grades_at_least(supplied.values(), "C") >= 2
        passed = all_at_least_s and at_least_two_c
        if passed:
            reason = (
                "PASS: all three required subjects have grade S or better and at "
                "least two have grade C or better."
            )
        elif not all_at_least_s:
            reason = "FAIL: at least one required subject has a grade below S."
        else:
            reason = (
                "FAIL: fewer than two required subjects have grade C or better."
            )

    return RuleResult(
        rule_id="R05",
        rule_name="Medicine Subject/Grade",
        passed=passed,
        message=f"{details} {reason}",
        source=SOURCE,
        page=50,
    )


def _evaluate_r06(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Dental Surgery subject and grade requirement."""
    return _evaluate_three_subject_s_requirement(
        facts,
        rule_id="R06",
        rule_name="Dental Surgery Subject/Grade",
        required_subjects=MEDICAL_SCIENCE_SUBJECTS,
        page=51,
    )


def _evaluate_r07(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Veterinary Science subject and grade requirement."""
    return _evaluate_three_subject_s_requirement(
        facts,
        rule_id="R07",
        rule_name="Veterinary Science Subject/Grade",
        required_subjects=MEDICAL_SCIENCE_SUBJECTS,
        page=51,
    )


def _evaluate_r08(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Engineering subject and grade requirement."""
    return _evaluate_three_subject_s_requirement(
        facts,
        rule_id="R08",
        rule_name="Engineering Subject/Grade",
        required_subjects=ENGINEERING_SUBJECTS,
        page=68,
    )


R05 = Rule(
    id="R05",
    name="Medicine Subject/Grade",
    applies_to="Medicine",
    source=SOURCE,
    page=50,
    evaluation_function=_evaluate_r05,
)

R06 = Rule(
    id="R06",
    name="Dental Surgery Subject/Grade",
    applies_to="Dental Surgery",
    source=SOURCE,
    page=51,
    evaluation_function=_evaluate_r06,
)

R07 = Rule(
    id="R07",
    name="Veterinary Science Subject/Grade",
    applies_to="Veterinary Science",
    source=SOURCE,
    page=51,
    evaluation_function=_evaluate_r07,
)

R08 = Rule(
    id="R08",
    name="Engineering Subject/Grade",
    applies_to="Engineering",
    source=SOURCE,
    page=68,
    evaluation_function=_evaluate_r08,
)

COURSE_RULES = (R05, R06, R07, R08)
