"""Formatting of completed inference results for human-readable explanations."""

from expert_system.models import RuleResult


def _format_rule_trace(results: list[RuleResult]) -> list[str]:
    """Format rule outcomes without evaluating any rule conditions."""
    lines: list[str] = []
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"{status} {result.rule_id} - {result.rule_name}")
        lines.append(f"  {result.message}")
    return lines


def _format_failed_requirements(results: list[RuleResult]) -> list[str]:
    """Format all failed results or state that none failed."""
    failed = [result for result in results if not result.passed]
    if not failed:
        return ["None."]
    return [
        f"- {result.rule_id} - {result.rule_name}: {result.message}"
        for result in failed
    ]


def _format_source_references(results: list[RuleResult]) -> list[str]:
    """Group rule IDs that cite the same source and page."""
    references: dict[tuple[str, int], list[str]] = {}
    for result in results:
        reference = (result.source, result.page)
        references.setdefault(reference, []).append(result.rule_id)

    return [
        f"- {source}, page {page} ({', '.join(rule_ids)})"
        for (source, page), rule_ids in references.items()
    ]


def build_course_explanation(
    course_name: str,
    eligible: bool,
    general_results: list[RuleResult],
    course_results: list[RuleResult],
) -> str:
    """Build a complete trace from already evaluated rule results."""
    all_results = [*general_results, *course_results]
    final_status = "ELIGIBLE" if eligible else "NOT ELIGIBLE"
    lines = [
        "=" * 50,
        course_name,
        f"FINAL RESULT: {final_status}",
        "=" * 50,
        "",
        "GENERAL RULE TRACE",
        *_format_rule_trace(general_results),
        "",
        "COURSE RULE TRACE",
        *_format_rule_trace(course_results),
        "",
        "FAILED REQUIREMENTS",
        *_format_failed_requirements(all_results),
        "",
        "SOURCE REFERENCES",
        *_format_source_references(all_results),
    ]
    return "\n".join(lines)
