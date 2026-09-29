"""Small inference helpers for evaluating rules against applicant facts."""

from collections.abc import Iterable

from expert_system.knowledge_base import (
    GENERAL_RULES,
    R05,
    R06,
    R07,
    R08,
    R09,
    R10,
    R11,
    R12,
    R13,
    R14,
    R15,
    R16,
    R17,
    R18,
    R19,
    R20,
    R21,
    Rule,
)
from expert_system.models import ApplicantFacts, CourseEvaluation, RuleResult


COURSE_RULE_MAP: dict[str, tuple[Rule, ...]] = {
    "Medicine": (R05,),
    "Dental Surgery": (R06,),
    "Veterinary Science": (R07,),
    "Engineering": (R08,),
    "Nursing": (R09, R10, R11),
    "Pharmacy": (R12, R13),
    "Information Technology": (R14,),
    "Law": (R15, R16, R17),
    "Quantity Surveying": (R18, R19, R20, R21),
}


def evaluate_rule(rule: Rule, facts: ApplicantFacts) -> RuleResult:
    """Evaluate one rule against the supplied facts."""
    return rule.evaluate(facts)


def evaluate_rules(rules: Iterable[Rule], facts: ApplicantFacts) -> list[RuleResult]:
    """Evaluate rules in order and return their individual results."""
    return [evaluate_rule(rule, facts) for rule in rules]


def evaluate_general_eligibility(applicant: ApplicantFacts) -> list[RuleResult]:
    """Evaluate every general rule and preserve each individual result."""
    return evaluate_rules(GENERAL_RULES, applicant)


def _build_explanation(
    course_name: str,
    general_results: list[RuleResult],
    course_results: list[RuleResult],
) -> str:
    """Build a concise explanation from failed or successful rule results."""
    failed_general = [result for result in general_results if not result.passed]
    failed_course = [result for result in course_results if not result.passed]

    if not failed_general and not failed_course:
        return (
            f"Eligible for {course_name}: all general and course-specific rules "
            "passed."
        )

    parts = [f"Not eligible for {course_name}."]
    if failed_general:
        failures = ", ".join(
            f"{result.rule_id} - {result.rule_name}" for result in failed_general
        )
        parts.append(f"Failed general rules: {failures}.")
    if failed_course:
        failures = ", ".join(
            f"{result.rule_id} - {result.rule_name}" for result in failed_course
        )
        parts.append(f"Failed course-specific rules: {failures}.")
    return " ".join(parts)


def _course_evaluation_from_results(
    course_name: str,
    general_results: list[RuleResult],
    course_results: list[RuleResult],
) -> CourseEvaluation:
    """Create a structured course evaluation from completed rule results."""
    eligible = all(result.passed for result in general_results) and all(
        result.passed for result in course_results
    )
    return CourseEvaluation(
        course_name=course_name,
        eligible=eligible,
        general_rule_results=list(general_results),
        course_rule_results=list(course_results),
        explanation=_build_explanation(
            course_name,
            general_results,
            course_results,
        ),
    )


def evaluate_course(
    applicant: ApplicantFacts,
    course_name: str,
) -> CourseEvaluation:
    """Evaluate all general and assigned rules for one course."""
    try:
        course_rules = COURSE_RULE_MAP[course_name]
    except (KeyError, TypeError) as error:
        available = ", ".join(COURSE_RULE_MAP)
        raise ValueError(
            f"Unknown course {course_name!r}. Available courses: {available}"
        ) from error

    general_results = evaluate_general_eligibility(applicant)
    course_results = evaluate_rules(course_rules, applicant)
    return _course_evaluation_from_results(
        course_name,
        general_results,
        course_results,
    )


def evaluate_all_courses(applicant: ApplicantFacts) -> list[CourseEvaluation]:
    """Evaluate every mapped course while retaining all supporting rule results."""
    general_results = evaluate_general_eligibility(applicant)
    evaluations = []
    for course_name, course_rules in COURSE_RULE_MAP.items():
        course_results = evaluate_rules(course_rules, applicant)
        evaluations.append(
            _course_evaluation_from_results(
                course_name,
                general_results,
                course_results,
            )
        )
    return evaluations
