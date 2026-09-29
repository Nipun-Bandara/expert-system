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
