"""Rule definitions for the expert system knowledge base.

No university admission rules are defined in this module yet.
"""

from collections.abc import Callable
from dataclasses import dataclass

from expert_system.models import ApplicantFacts, RuleResult


RuleEvaluationFunction = Callable[[ApplicantFacts], RuleResult]


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
