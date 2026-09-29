"""Reusable examination-grade normalization and comparison utilities."""

from collections.abc import Iterable


_GRADE_RANK = {
    "A": 4,
    "B": 3,
    "C": 2,
    "S": 1,
    "F": 0,
}


def normalize_grade(value: str) -> str:
    """Return a supported grade in canonical uppercase form.

    Surrounding whitespace is ignored. Unsupported values raise ``ValueError``.
    """
    if not isinstance(value, str):
        raise ValueError(f"Invalid grade: {value!r}")

    normalized = value.strip().upper()
    if normalized not in _GRADE_RANK:
        raise ValueError(f"Invalid grade: {value!r}")
    return normalized


def grade_at_least(actual: str, required: str) -> bool:
    """Return whether ``actual`` is equal to or higher than ``required``."""
    actual_grade = normalize_grade(actual)
    required_grade = normalize_grade(required)
    return _GRADE_RANK[actual_grade] >= _GRADE_RANK[required_grade]


def count_grades_at_least(grades: Iterable[str], required: str) -> int:
    """Count grades that are equal to or higher than ``required``."""
    required_grade = normalize_grade(required)
    required_rank = _GRADE_RANK[required_grade]
    return sum(
        _GRADE_RANK[normalize_grade(grade)] >= required_rank for grade in grades
    )
