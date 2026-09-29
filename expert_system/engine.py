"""Small inference helpers for evaluating rules against applicant facts."""

from collections.abc import Iterable

from expert_system.knowledge_base import Rule
from expert_system.models import ApplicantFacts, RuleResult


def evaluate_rule(rule: Rule, facts: ApplicantFacts) -> RuleResult:
    """Evaluate one rule against the supplied facts."""
    return rule.evaluate(facts)


def evaluate_rules(rules: Iterable[Rule], facts: ApplicantFacts) -> list[RuleResult]:
    """Evaluate rules in order and return their individual results."""
    return [evaluate_rule(rule, facts) for rule in rules]
