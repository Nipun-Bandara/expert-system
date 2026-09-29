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
from expert_system.explanations import build_course_explanation
from expert_system.models import (
    ApplicantFacts,
    BackwardChainingResult,
    CourseEvaluation,
    EligibilityConclusion,
    ForwardChainingResult,
    InferenceTrace,
    RuleResult,
)


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


def _course_evaluation_from_results(
    course_name: str,
    general_results: list[RuleResult],
    course_results: list[RuleResult],
    *,
    inference_mode: str,
    trace: InferenceTrace,
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
        explanation=build_course_explanation(
            course_name,
            eligible,
            general_results,
            course_results,
            inference_mode,
            trace.goal if inference_mode == "backward chaining" else None,
        ),
        inference_trace=trace,
    )


def backward_chaining(
    applicant: ApplicantFacts,
    course_name: str,
) -> BackwardChainingResult:
    """Start with one course goal and evaluate only its required rules.

    This is a small, goal-directed evaluator for the fixed course rule map; it
    is not a general-purpose logic-programming engine.
    """
    try:
        course_rules = COURSE_RULE_MAP[course_name]
    except (KeyError, TypeError) as error:
        available = ", ".join(COURSE_RULE_MAP)
        raise ValueError(
            f"Unknown course {course_name!r}. Available courses: {available}"
        ) from error

    general_results = evaluate_general_eligibility(applicant)
    course_results = evaluate_rules(course_rules, applicant)
    all_results = [*general_results, *course_results]
    eligible = all(result.passed for result in all_results)
    conclusion = EligibilityConclusion(course_name, eligible)
    goal = f"eligible for {course_name}"
    trace = InferenceTrace(
        inference_mode="backward chaining",
        goal=goal,
        required_rule_ids=[rule.id for rule in (*GENERAL_RULES, *course_rules)],
        evaluated_rule_results=all_results,
        derived_conclusions=[conclusion],
        failed_conditions=[result for result in all_results if not result.passed],
        final_conclusion=conclusion,
    )
    evaluation = _course_evaluation_from_results(
        course_name,
        general_results,
        course_results,
        inference_mode="backward chaining",
        trace=trace,
    )
    return BackwardChainingResult(evaluation=evaluation, trace=trace)


def forward_chaining(applicant: ApplicantFacts) -> ForwardChainingResult:
    """Start with applicant facts and derive every supported course conclusion.

    Rules are evaluated once in their knowledge-base order.  The implementation
    is intentionally a fixed, data-driven pass rather than a RETE engine.
    """
    general_results = evaluate_general_eligibility(applicant)
    course_results_by_name = {
        course_name: evaluate_rules(course_rules, applicant)
        for course_name, course_rules in COURSE_RULE_MAP.items()
    }
    evaluated_results = [
        *general_results,
        *[
            result
            for course_results in course_results_by_name.values()
            for result in course_results
        ],
    ]
    conclusions = [
        EligibilityConclusion(
            course_name,
            all(result.passed for result in general_results)
            and all(result.passed for result in course_results),
        )
        for course_name, course_results in course_results_by_name.items()
    ]
    trace = InferenceTrace(
        inference_mode="forward chaining",
        goal=None,
        required_rule_ids=[result.rule_id for result in evaluated_results],
        evaluated_rule_results=evaluated_results,
        derived_conclusions=conclusions,
        failed_conditions=[
            result for result in evaluated_results if not result.passed
        ],
    )
    evaluations: list[CourseEvaluation] = []
    for course_name in COURSE_RULE_MAP:
        course_results = course_results_by_name[course_name]
        evaluations.append(
            _course_evaluation_from_results(
                course_name,
                general_results,
                course_results,
                inference_mode="forward chaining",
                trace=trace,
            )
        )
    return ForwardChainingResult(evaluations=evaluations, trace=trace)


def evaluate_course(
    applicant: ApplicantFacts,
    course_name: str,
) -> CourseEvaluation:
    """Compatibility wrapper for goal-directed course evaluation."""
    return backward_chaining(applicant, course_name).evaluation


def evaluate_all_courses(applicant: ApplicantFacts) -> list[CourseEvaluation]:
    """Compatibility wrapper for data-driven evaluation of every course."""
    return forward_chaining(applicant).evaluations
