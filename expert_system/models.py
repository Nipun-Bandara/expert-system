"""Domain models containing facts supplied to the expert system."""

from dataclasses import dataclass


def _normalize_subject_name(subject: str) -> str:
    """Normalize a subject name without applying subject aliases."""
    return " ".join(subject.split()).casefold()


def _normalize_results(results: dict[str, str]) -> dict[str, str]:
    """Return results keyed by normalized subject names."""
    return {_normalize_subject_name(subject): grade for subject, grade in results.items()}


@dataclass
class ApplicantFacts:
    """Facts supplied about an applicant for later rule evaluation."""

    al_results: dict[str, str]
    same_sitting: bool
    al_attempts: int
    common_general_paper_mark: float
    previous_state_university_registration: bool
    ol_results: dict[str, str]
    height_cm: float | None = None
    nursing_physical_condition_met: bool | None = None

    def __post_init__(self) -> None:
        """Normalize subject names and validate numeric fact ranges."""
        if self.al_attempts < 1:
            raise ValueError("A/L attempts cannot be below 1")
        if not 0 <= self.common_general_paper_mark <= 100:
            raise ValueError("Common General Paper mark must be between 0 and 100")
        if self.height_cm is not None and not self.height_cm > 0:
            raise ValueError("Height must be positive when supplied")

        self.al_results = _normalize_results(self.al_results)
        self.ol_results = _normalize_results(self.ol_results)
