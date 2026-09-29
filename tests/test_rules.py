"""Tests for the rule evaluation architecture using a synthetic rule."""

from expert_system.engine import evaluate_rule, evaluate_rules
from expert_system.knowledge_base import Rule
from expert_system.models import ApplicantFacts, RuleResult


DUMMY_SOURCE = "Synthetic Test Source"
DUMMY_PAGE = 12


def make_facts(*, dummy_condition: bool) -> ApplicantFacts:
    """Create applicant facts used only by the synthetic test rule."""
    return ApplicantFacts(
        al_results={},
        same_sitting=dummy_condition,
        al_attempts=1,
        common_general_paper_mark=50,
        previous_state_university_registration=False,
        ol_results={},
    )


def evaluate_dummy_rule(facts: ApplicantFacts) -> RuleResult:
    """Evaluate a synthetic condition that is not an admission requirement."""
    passed = facts.same_sitting
    return RuleResult(
        rule_id="TEST-01",
        rule_name="Synthetic Test Rule",
        passed=passed,
        message="Synthetic rule passed" if passed else "Synthetic rule failed",
        source=DUMMY_SOURCE,
        page=DUMMY_PAGE,
    )


def make_dummy_rule() -> Rule:
    """Build the synthetic rule used by these tests."""
    return Rule(
        id="TEST-01",
        name="Synthetic Test Rule",
        applies_to="tests only",
        source=DUMMY_SOURCE,
        page=DUMMY_PAGE,
        evaluation_function=evaluate_dummy_rule,
    )


def test_dummy_rule_can_pass() -> None:
    result = evaluate_rule(make_dummy_rule(), make_facts(dummy_condition=True))

    assert result.passed is True
    assert result.message == "Synthetic rule passed"


def test_dummy_rule_can_fail() -> None:
    result = evaluate_rule(make_dummy_rule(), make_facts(dummy_condition=False))

    assert result.passed is False
    assert result.message == "Synthetic rule failed"


def test_dummy_rule_returns_its_source() -> None:
    result = evaluate_rule(make_dummy_rule(), make_facts(dummy_condition=True))

    assert result.source == DUMMY_SOURCE


def test_dummy_rule_returns_its_page() -> None:
    result = evaluate_rule(make_dummy_rule(), make_facts(dummy_condition=True))

    assert result.page == DUMMY_PAGE


def test_multiple_rules_are_evaluated_in_order() -> None:
    rule = make_dummy_rule()

    results = evaluate_rules(
        [rule, rule],
        make_facts(dummy_condition=True),
    )

    assert [result.rule_id for result in results] == ["TEST-01", "TEST-01"]
