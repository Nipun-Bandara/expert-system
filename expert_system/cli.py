"""Command-line input and output for the expert system."""

from collections.abc import Callable, Iterable

from expert_system.engine import COURSE_RULE_MAP, evaluate_all_courses, evaluate_course
from expert_system.grades import normalize_grade
from expert_system.models import ApplicantFacts, CourseEvaluation


APPLICATION_TITLE = "Sri Lankan University Course Eligibility Expert System"

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]

COURSE_OL_SUBJECTS: dict[str, tuple[str, ...]] = {
    "Nursing": ("English",),
    "Pharmacy": ("English",),
    "Law": ("English", "Sinhala", "Tamil"),
    "Quantity Surveying": ("Mathematics", "Science", "English"),
}


def parse_yes_no(value: str) -> bool:
    """Parse a user-friendly yes/no response or raise ``ValueError``."""
    normalized = value.strip().casefold()
    if normalized in {"y", "yes"}:
        return True
    if normalized in {"n", "no"}:
        return False
    raise ValueError("Please enter y, yes, n, or no.")


def parse_grade(value: str) -> str:
    """Parse and normalize one supported examination grade."""
    return normalize_grade(value)


def parse_positive_integer(value: str) -> int:
    """Parse an integer greater than or equal to one."""
    try:
        parsed = int(value.strip())
    except ValueError as error:
        raise ValueError("Please enter a whole number.") from error
    if parsed < 1:
        raise ValueError("The value must be at least 1.")
    return parsed


def parse_mark(value: str) -> float:
    """Parse a mark in the inclusive range zero to one hundred."""
    try:
        parsed = float(value.strip())
    except ValueError as error:
        raise ValueError("Please enter a numeric mark.") from error
    if not 0 <= parsed <= 100:
        raise ValueError("The mark must be between 0 and 100.")
    return parsed


def parse_positive_float(value: str) -> float:
    """Parse a positive floating-point value."""
    try:
        parsed = float(value.strip())
    except ValueError as error:
        raise ValueError("Please enter a numeric value.") from error
    if not parsed > 0:
        raise ValueError("The value must be positive.")
    return parsed


def _prompt_until_valid(
    prompt: str,
    parser: Callable[[str], object],
    input_fn: InputFunction,
    output_fn: OutputFunction,
) -> object:
    """Prompt repeatedly until the parser accepts the supplied value."""
    while True:
        try:
            return parser(input_fn(prompt))
        except ValueError as error:
            output_fn(f"Invalid input: {error}")


def prompt_grade(
    prompt: str,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> str:
    """Prompt until a supported grade is entered."""
    result = _prompt_until_valid(prompt, parse_grade, input_fn, output_fn)
    assert isinstance(result, str)
    return result


def prompt_optional_grade(
    prompt: str,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> str | None:
    """Prompt for a grade while allowing a blank missing value."""
    while True:
        value = input_fn(prompt)
        if not value.strip():
            return None
        try:
            return parse_grade(value)
        except ValueError as error:
            output_fn(f"Invalid input: {error}")


def prompt_yes_no(
    prompt: str,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> bool:
    """Prompt until a valid yes/no response is entered."""
    result = _prompt_until_valid(prompt, parse_yes_no, input_fn, output_fn)
    assert isinstance(result, bool)
    return result


def prompt_optional_yes_no(
    prompt: str,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> bool | None:
    """Prompt for yes/no while allowing a blank unknown value."""
    while True:
        value = input_fn(prompt)
        if not value.strip():
            return None
        try:
            return parse_yes_no(value)
        except ValueError as error:
            output_fn(f"Invalid input: {error}")


def _collect_al_results(
    input_fn: InputFunction,
    output_fn: OutputFunction,
) -> dict[str, str]:
    """Collect exactly three distinct A/L subject results."""
    output_fn("\nEnter the three A/L subject results using official subject names.")
    results: dict[str, str] = {}
    normalized_subjects: set[str] = set()
    while len(results) < 3:
        position = len(results) + 1
        subject = input_fn(f"A/L subject {position}: ").strip()
        normalized_subject = " ".join(subject.split()).casefold()
        if not normalized_subject:
            output_fn("Invalid input: subject name cannot be blank.")
            continue
        if normalized_subject in normalized_subjects:
            output_fn("Invalid input: that subject has already been entered.")
            continue
        grade = prompt_grade(
            f"Grade for {subject} (A/B/C/S/F): ", input_fn, output_fn
        )
        results[subject] = grade
        normalized_subjects.add(normalized_subject)
    return results


def _ol_subjects_for_courses(course_names: Iterable[str]) -> list[str]:
    """Return de-duplicated O/L input fields needed for selected courses."""
    subjects: list[str] = []
    for course_name in course_names:
        for subject in COURSE_OL_SUBJECTS.get(course_name, ()):
            if subject not in subjects:
                subjects.append(subject)
    return subjects


def _collect_ol_results(
    course_names: Iterable[str],
    input_fn: InputFunction,
    output_fn: OutputFunction,
) -> dict[str, str]:
    """Collect relevant O/L facts, preserving blank fields as missing."""
    subjects = _ol_subjects_for_courses(course_names)
    if not subjects:
        return {}

    output_fn("\nEnter relevant O/L results. Leave blank if not supplied.")
    results = {}
    for subject in subjects:
        grade = prompt_optional_grade(
            f"O/L {subject} grade (A/B/C/S/F, or blank): ",
            input_fn,
            output_fn,
        )
        if grade is not None:
            results[subject] = grade
    return results


def _collect_optional_height(
    input_fn: InputFunction,
    output_fn: OutputFunction,
) -> float | None:
    """Collect an optional positive height in centimetres."""
    while True:
        value = input_fn("Height in centimetres (or blank if not supplied): ")
        if not value.strip():
            return None
        try:
            return parse_positive_float(value)
        except ValueError as error:
            output_fn(f"Invalid input: {error}")


def collect_applicant_facts(
    course_names: Iterable[str],
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> ApplicantFacts:
    """Collect applicant facts needed for the selected courses."""
    selected_courses = tuple(course_names)
    al_results = _collect_al_results(input_fn, output_fn)
    same_sitting = prompt_yes_no(
        "Were all three A/L results obtained in one sitting? (y/n): ",
        input_fn,
        output_fn,
    )
    attempts_result = _prompt_until_valid(
        "Number of A/L attempts: ", parse_positive_integer, input_fn, output_fn
    )
    mark_result = _prompt_until_valid(
        "Common General Paper mark (0-100): ", parse_mark, input_fn, output_fn
    )
    assert isinstance(attempts_result, int)
    assert isinstance(mark_result, float)
    previous_registration = prompt_yes_no(
        "Previously registered internally at a Sri Lankan state university? (y/n): ",
        input_fn,
        output_fn,
    )
    ol_results = _collect_ol_results(selected_courses, input_fn, output_fn)

    height_cm = None
    physical_condition_met = None
    if "Nursing" in selected_courses:
        output_fn("\nNursing-related facts")
        height_cm = _collect_optional_height(input_fn, output_fn)
        physical_condition_met = prompt_optional_yes_no(
            "Published Nursing physical-condition requirement satisfied? "
            "(y/n, or blank if unknown): ",
            input_fn,
            output_fn,
        )

    return ApplicantFacts(
        al_results=al_results,
        same_sitting=same_sitting,
        al_attempts=attempts_result,
        common_general_paper_mark=mark_result,
        previous_state_university_registration=previous_registration,
        ol_results=ol_results,
        height_cm=height_cm,
        nursing_physical_condition_met=physical_condition_met,
    )


def display_course_evaluation(
    evaluation: CourseEvaluation,
    output_fn: OutputFunction = print,
) -> None:
    """Display the complete explanation prepared by the inference layer."""
    output_fn("\n" + evaluation.explanation)


def _parse_menu_choice(value: str) -> str:
    """Parse a main-menu choice."""
    choice = value.strip()
    if choice not in {"1", "2", "3"}:
        raise ValueError("Please choose 1, 2, or 3.")
    return choice


def _prompt_menu_choice(
    input_fn: InputFunction,
    output_fn: OutputFunction,
) -> str:
    """Display the main menu and return a valid choice."""
    output_fn("\n1. Check a specific course")
    output_fn("2. Check all supported courses")
    output_fn("3. Exit")
    result = _prompt_until_valid(
        "Choose an option: ", _parse_menu_choice, input_fn, output_fn
    )
    assert isinstance(result, str)
    return result


def _prompt_course(
    input_fn: InputFunction,
    output_fn: OutputFunction,
) -> str:
    """Display supported courses and return the selected canonical name."""
    courses = tuple(COURSE_RULE_MAP)
    output_fn("\nSupported courses")
    for number, course_name in enumerate(courses, start=1):
        output_fn(f"{number}. {course_name}")

    def parse_course_number(value: str) -> str:
        try:
            index = int(value.strip()) - 1
        except ValueError as error:
            raise ValueError("Please enter a course number.") from error
        if not 0 <= index < len(courses):
            raise ValueError(f"Please choose a number from 1 to {len(courses)}.")
        return courses[index]

    result = _prompt_until_valid(
        "Choose a course: ", parse_course_number, input_fn, output_fn
    )
    assert isinstance(result, str)
    return result


def run(
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> None:
    """Run the interactive command-line application."""
    output_fn(APPLICATION_TITLE)
    try:
        while True:
            choice = _prompt_menu_choice(input_fn, output_fn)
            if choice == "3":
                output_fn("Goodbye.")
                return

            if choice == "1":
                course_name = _prompt_course(input_fn, output_fn)
                applicant = collect_applicant_facts(
                    [course_name], input_fn, output_fn
                )
                display_course_evaluation(
                    evaluate_course(applicant, course_name), output_fn
                )
            else:
                course_names = tuple(COURSE_RULE_MAP)
                applicant = collect_applicant_facts(
                    course_names, input_fn, output_fn
                )
                for evaluation in evaluate_all_courses(applicant):
                    display_course_evaluation(evaluation, output_fn)
    except (EOFError, KeyboardInterrupt):
        output_fn("\nInput cancelled. Goodbye.")
