"""Domain models containing facts and traceable inference results."""

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


@dataclass
class RuleResult:
    """Recorded outcome of evaluating one rule."""

    rule_id: str
    rule_name: str
    passed: bool
    message: str
    source: str
    page: int


@dataclass(frozen=True)
class EligibilityConclusion:
    """A conclusion derived for one supported course."""

    course_name: str
    eligible: bool

    @property
    def statement(self) -> str:
        """Return the conclusion in readable goal form."""
        status = "eligible" if self.eligible else "not eligible"
        return f"{status} for {self.course_name}"


@dataclass
class InferenceTrace:
    """Trace produced by the deliberately small course inference layer."""

    inference_mode: str
    goal: str | None
    required_rule_ids: list[str]
    evaluated_rule_results: list[RuleResult]
    derived_conclusions: list[EligibilityConclusion]
    failed_conditions: list[RuleResult]
    final_conclusion: EligibilityConclusion | None = None

    @property
    def evaluated_rule_ids(self) -> list[str]:
        """Return evaluated rule IDs in evaluation order."""
        return [result.rule_id for result in self.evaluated_rule_results]

    @property
    def satisfied_antecedents(self) -> list[RuleResult]:
        """Return required antecedents established by the supplied facts."""
        return [result for result in self.evaluated_rule_results if result.passed]

    @property
    def failed_antecedents(self) -> list[RuleResult]:
        """Return required antecedents not established by the supplied facts."""
        return self.failed_conditions


@dataclass
class CourseEvaluation:
    """Combined general and course-specific results for one course."""

    course_name: str
    eligible: bool
    general_rule_results: list[RuleResult]
    course_rule_results: list[RuleResult]
    explanation: str
    inference_trace: InferenceTrace | None = None

    @property
    def inference_mode(self) -> str | None:
        """Expose the mode directly while retaining the complete trace."""
        return self.inference_trace.inference_mode if self.inference_trace else None


@dataclass
class ForwardChainingResult:
    """All course evaluations and the trace that produced them."""

    evaluations: list[CourseEvaluation]
    trace: InferenceTrace


@dataclass
class BackwardChainingResult:
    """One goal-directed course evaluation and its trace."""

    evaluation: CourseEvaluation
    trace: InferenceTrace
