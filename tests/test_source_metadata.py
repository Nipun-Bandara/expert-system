"""Tests for the single authoritative handbook source."""

from expert_system.knowledge_base import (
    COURSE_RULES,
    GENERAL_RULES,
    HANDBOOK_2025_2026,
)


def test_all_rules_use_official_2025_2026_handbook_and_verified_pages() -> None:
    rules = (*GENERAL_RULES, *COURSE_RULES)
    expected_pages = {
        **{rule_id: 9 for rule_id in ("R01", "R02", "R03")},
        "R04": 13,
        "R05": 50,
        "R06": 51,
        "R07": 51,
        "R08": 68,
        **{rule_id: 57 for rule_id in ("R09", "R10", "R11")},
        "R12": 58,
        "R13": 58,
        "R14": 83,
        **{rule_id: 90 for rule_id in ("R15", "R16", "R17")},
        **{rule_id: 84 for rule_id in ("R18", "R19", "R20", "R21")},
    }

    assert len(rules) == 21
    assert {rule.source for rule in rules} == {HANDBOOK_2025_2026.identifier}
    assert {rule.id: rule.page for rule in rules} == expected_pages
    assert HANDBOOK_2025_2026.title == (
        "Admission to Undergraduate Courses of the Universities in Sri Lanka, "
        "Academic Year 2025/2026"
    )
    assert HANDBOOK_2025_2026.url == (
        "https://www.ugc.ac.lk/downloads/admissions/Handbook_2025_26/"
        "student_handbook_english.pdf"
    )
