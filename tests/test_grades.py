"""Tests for reusable examination-grade utilities."""

import pytest

from expert_system.grades import (
    count_grades_at_least,
    grade_at_least,
    normalize_grade,
)


SUPPORTED_GRADES = ("A", "B", "C", "S", "F")


@pytest.mark.parametrize("grade", SUPPORTED_GRADES)
def test_normalize_grade_accepts_every_supported_grade(grade: str) -> None:
    assert normalize_grade(grade) == grade


@pytest.mark.parametrize(
    ("value", "expected"),
    [("a", "A"), ("c", "C"), (" s ", "S"), ("\tf\n", "F")],
)
def test_normalize_grade_is_case_insensitive_and_ignores_surrounding_whitespace(
    value: str,
    expected: str,
) -> None:
    assert normalize_grade(value) == expected


@pytest.mark.parametrize("value", ["", "D", "AA", "pass", "A+"])
def test_normalize_grade_rejects_invalid_grades(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid grade"):
        normalize_grade(value)


@pytest.mark.parametrize("value", [None, 1])
def test_normalize_grade_rejects_non_string_values(value: object) -> None:
    with pytest.raises(ValueError, match="Invalid grade"):
        normalize_grade(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("actual", "required", "expected"),
    [
        (actual, required, actual_index <= required_index)
        for actual_index, actual in enumerate(SUPPORTED_GRADES)
        for required_index, required in enumerate(SUPPORTED_GRADES)
    ],
)
def test_grade_at_least_follows_the_complete_grade_ranking(
    actual: str,
    required: str,
    expected: bool,
) -> None:
    assert grade_at_least(actual, required) is expected


def test_grade_at_least_is_case_insensitive() -> None:
    assert grade_at_least("a", "c") is True
    assert grade_at_least("s", "C") is False


@pytest.mark.parametrize(
    ("actual", "required"),
    [("D", "C"), ("A", "D")],
)
def test_grade_at_least_rejects_invalid_actual_or_required_grade(
    actual: str,
    required: str,
) -> None:
    with pytest.raises(ValueError, match="Invalid grade"):
        grade_at_least(actual, required)


def test_count_grades_at_least_counts_matching_and_higher_grades() -> None:
    assert count_grades_at_least(["A", "B", "C", "S", "F"], "C") == 3


def test_count_grades_at_least_accepts_any_iterable_and_is_case_insensitive() -> None:
    grades = (grade for grade in ["a", "c", "s", "f"])

    assert count_grades_at_least(grades, "s") == 3


def test_count_grades_at_least_returns_zero_for_an_empty_iterable() -> None:
    assert count_grades_at_least([], "A") == 0


@pytest.mark.parametrize(
    ("grades", "required"),
    [(["A", "D"], "C"), (["A", "B"], "D")],
)
def test_count_grades_at_least_rejects_invalid_input_grades(
    grades: list[str],
    required: str,
) -> None:
    with pytest.raises(ValueError, match="Invalid grade"):
        count_grades_at_least(grades, required)
