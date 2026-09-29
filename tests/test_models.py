"""Tests for applicant fact validation and normalization."""

import pytest

from expert_system.models import ApplicantFacts


def make_applicant(**overrides: object) -> ApplicantFacts:
    """Create valid applicant facts with optional field overrides."""
    values = {
        "al_results": {"Biology": "A", "  General   Chemistry ": "B"},
        "same_sitting": True,
        "al_attempts": 1,
        "common_general_paper_mark": 50.0,
        "previous_state_university_registration": False,
        "ol_results": {"English Language": "A"},
    }
    values.update(overrides)
    return ApplicantFacts(**values)  # type: ignore[arg-type]


def test_valid_applicant_facts_are_created() -> None:
    applicant = make_applicant(
        height_cm=165.5,
        nursing_physical_condition_met=True,
    )

    assert applicant.al_attempts == 1
    assert applicant.height_cm == 165.5
    assert applicant.nursing_physical_condition_met is True


def test_subject_names_are_normalized_for_case_and_whitespace() -> None:
    applicant = make_applicant()

    assert applicant.al_results == {"biology": "A", "general chemistry": "B"}
    assert applicant.ol_results == {"english language": "A"}


@pytest.mark.parametrize("attempts", [0, -1])
def test_al_attempts_cannot_be_below_one(attempts: int) -> None:
    with pytest.raises(ValueError, match="attempts"):
        make_applicant(al_attempts=attempts)


@pytest.mark.parametrize("mark", [-0.01, 100.01])
def test_common_general_paper_mark_must_be_between_zero_and_one_hundred(
    mark: float,
) -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        make_applicant(common_general_paper_mark=mark)


@pytest.mark.parametrize("mark", [0.0, 100.0])
def test_common_general_paper_mark_accepts_boundaries(mark: float) -> None:
    applicant = make_applicant(common_general_paper_mark=mark)

    assert applicant.common_general_paper_mark == mark


@pytest.mark.parametrize("height", [0.0, -0.01])
def test_height_must_be_positive_when_supplied(height: float) -> None:
    with pytest.raises(ValueError, match="positive"):
        make_applicant(height_cm=height)


def test_optional_nursing_facts_may_be_omitted() -> None:
    applicant = make_applicant()

    assert applicant.height_cm is None
    assert applicant.nursing_physical_condition_met is None
