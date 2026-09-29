"""Sourced general eligibility rules for the expert system knowledge base."""

from collections.abc import Callable
from dataclasses import dataclass

from expert_system.grades import count_grades_at_least
from expert_system.models import ApplicantFacts, RuleResult


RuleEvaluationFunction = Callable[[ApplicantFacts], RuleResult]
SOURCE = "student_handbook_english_2025/2026.pdf"


@dataclass
class Rule:
    """A sourced rule and the function used to evaluate it."""

    id: str
    name: str
    applies_to: str
    source: str
    page: int
    evaluation_function: RuleEvaluationFunction

    def evaluate(self, facts: ApplicantFacts) -> RuleResult:
        """Evaluate this rule against supplied applicant facts."""
        return self.evaluation_function(facts)


def _evaluate_r01(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the minimum grade and one-sitting requirement."""
    has_three_results = len(facts.al_results) == 3
    all_at_least_s = (
        count_grades_at_least(facts.al_results.values(), "S") == 3
        if has_three_results
        else False
    )
    passed = has_three_results and all_at_least_s and facts.same_sitting

    if passed:
        message = (
            "Exactly three A/L subjects have grade S or better and were obtained "
            "in one sitting."
        )
    elif not has_three_results:
        message = "Exactly three A/L subject results must be supplied."
    elif not all_at_least_s:
        message = "All three A/L subjects must have grade S or better."
    else:
        message = "The three A/L results were not obtained in one sitting."

    return RuleResult(
        rule_id="R01",
        rule_name="Minimum Grade & Sitting",
        passed=passed,
        message=message,
        source=SOURCE,
        page=9,
    )


def _evaluate_r02(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the maximum A/L attempt limit."""
    passed = facts.al_attempts <= 3
    message = (
        f"A/L attempt count {facts.al_attempts} is within the maximum of 3."
        if passed
        else f"A/L attempt count {facts.al_attempts} exceeds the maximum of 3."
    )
    return RuleResult(
        rule_id="R02",
        rule_name="Maximum Attempt Limit",
        passed=passed,
        message=message,
        source=SOURCE,
        page=9,
    )


def _evaluate_r03(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Common General Paper minimum mark."""
    passed = facts.common_general_paper_mark >= 30
    mark = f"{facts.common_general_paper_mark:g}"
    message = (
        f"Common General Paper mark {mark} satisfies the required minimum of 30%."
        if passed
        else f"Common General Paper mark {mark} is below the required minimum of 30%."
    )
    return RuleResult(
        rule_id="R03",
        rule_name="Common General Paper",
        passed=passed,
        message=message,
        source=SOURCE,
        page=9,
    )


def _evaluate_r04(facts: ApplicantFacts) -> RuleResult:
    """Disqualify an applicant who has previously registered internally."""
    passed = not facts.previous_state_university_registration
    message = (
        "Applicant has not previously registered as an internal student in a Sri "
        "Lankan state university, so this rule is satisfied."
        if passed
        else "Applicant has previously registered as an internal student in a Sri "
        "Lankan state university and is disqualified by this rule."
    )
    return RuleResult(
        rule_id="R04",
        rule_name="Prior Registration",
        passed=passed,
        message=message,
        source=SOURCE,
        page=13,
    )


R01 = Rule(
    id="R01",
    name="Minimum Grade & Sitting",
    applies_to="All applicants",
    source=SOURCE,
    page=9,
    evaluation_function=_evaluate_r01,
)

R02 = Rule(
    id="R02",
    name="Maximum Attempt Limit",
    applies_to="All applicants",
    source=SOURCE,
    page=9,
    evaluation_function=_evaluate_r02,
)

R03 = Rule(
    id="R03",
    name="Common General Paper",
    applies_to="All applicants",
    source=SOURCE,
    page=9,
    evaluation_function=_evaluate_r03,
)

R04 = Rule(
    id="R04",
    name="Prior Registration",
    applies_to="All applicants",
    source=SOURCE,
    page=13,
    evaluation_function=_evaluate_r04,
)

GENERAL_RULES = (R01, R02, R03, R04)


MEDICAL_SCIENCE_SUBJECTS = ("Biology", "Chemistry", "Physics")
ENGINEERING_SUBJECTS = ("Chemistry", "Combined Mathematics", "Physics")


def _relevant_grades(
    facts: ApplicantFacts,
    required_subjects: tuple[str, ...],
) -> dict[str, str]:
    """Return supplied grades for required subjects using their exact names."""
    return {
        subject: facts.al_results[subject.casefold()]
        for subject in required_subjects
        if subject.casefold() in facts.al_results
    }


def _subject_details(
    required_subjects: tuple[str, ...],
    supplied_grades: dict[str, str],
) -> str:
    """Format required subjects and supplied relevant grades for an explanation."""
    required = ", ".join(required_subjects)
    supplied = ", ".join(
        f"{subject}={grade}" for subject, grade in supplied_grades.items()
    )
    return (
        f"Required subjects: {required}. "
        f"Supplied relevant grades: {supplied or 'none'}."
    )


def _evaluate_three_subject_s_requirement(
    facts: ApplicantFacts,
    *,
    rule_id: str,
    rule_name: str,
    required_subjects: tuple[str, ...],
    page: int,
) -> RuleResult:
    """Evaluate a requirement for three named subjects at grade S or better."""
    supplied = _relevant_grades(facts, required_subjects)
    missing = [subject for subject in required_subjects if subject not in supplied]
    details = _subject_details(required_subjects, supplied)

    if missing:
        passed = False
        reason = (
            f"FAIL: missing required subjects: {', '.join(missing)}."
        )
    else:
        passed = count_grades_at_least(supplied.values(), "S") == 3
        reason = (
            "PASS: all three required subjects have grade S or better."
            if passed
            else "FAIL: at least one required subject has a grade below S."
        )

    return RuleResult(
        rule_id=rule_id,
        rule_name=rule_name,
        passed=passed,
        message=f"{details} {reason}",
        source=SOURCE,
        page=page,
    )


def _evaluate_r05(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Medicine subject and grade requirement."""
    supplied = _relevant_grades(facts, MEDICAL_SCIENCE_SUBJECTS)
    missing = [
        subject for subject in MEDICAL_SCIENCE_SUBJECTS if subject not in supplied
    ]
    details = _subject_details(MEDICAL_SCIENCE_SUBJECTS, supplied)

    if missing:
        passed = False
        reason = f"FAIL: missing required subjects: {', '.join(missing)}."
    else:
        all_at_least_s = count_grades_at_least(supplied.values(), "S") == 3
        at_least_two_c = count_grades_at_least(supplied.values(), "C") >= 2
        passed = all_at_least_s and at_least_two_c
        if passed:
            reason = (
                "PASS: all three required subjects have grade S or better and at "
                "least two have grade C or better."
            )
        elif not all_at_least_s:
            reason = "FAIL: at least one required subject has a grade below S."
        else:
            reason = (
                "FAIL: fewer than two required subjects have grade C or better."
            )

    return RuleResult(
        rule_id="R05",
        rule_name="Medicine Subject/Grade",
        passed=passed,
        message=f"{details} {reason}",
        source=SOURCE,
        page=50,
    )


def _evaluate_r06(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Dental Surgery subject and grade requirement."""
    return _evaluate_three_subject_s_requirement(
        facts,
        rule_id="R06",
        rule_name="Dental Surgery Subject/Grade",
        required_subjects=MEDICAL_SCIENCE_SUBJECTS,
        page=51,
    )


def _evaluate_r07(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Veterinary Science subject and grade requirement."""
    return _evaluate_three_subject_s_requirement(
        facts,
        rule_id="R07",
        rule_name="Veterinary Science Subject/Grade",
        required_subjects=MEDICAL_SCIENCE_SUBJECTS,
        page=51,
    )


def _evaluate_r08(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Engineering subject and grade requirement."""
    return _evaluate_three_subject_s_requirement(
        facts,
        rule_id="R08",
        rule_name="Engineering Subject/Grade",
        required_subjects=ENGINEERING_SUBJECTS,
        page=68,
    )


R05 = Rule(
    id="R05",
    name="Medicine Subject/Grade",
    applies_to="Medicine",
    source=SOURCE,
    page=50,
    evaluation_function=_evaluate_r05,
)

R06 = Rule(
    id="R06",
    name="Dental Surgery Subject/Grade",
    applies_to="Dental Surgery",
    source=SOURCE,
    page=51,
    evaluation_function=_evaluate_r06,
)

R07 = Rule(
    id="R07",
    name="Veterinary Science Subject/Grade",
    applies_to="Veterinary Science",
    source=SOURCE,
    page=51,
    evaluation_function=_evaluate_r07,
)

R08 = Rule(
    id="R08",
    name="Engineering Subject/Grade",
    applies_to="Engineering",
    source=SOURCE,
    page=68,
    evaluation_function=_evaluate_r08,
)

COURSE_RULES = (R05, R06, R07, R08)


def _evaluate_r09(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Nursing A/L subject requirement."""
    return _evaluate_three_subject_s_requirement(
        facts,
        rule_id="R09",
        rule_name="Nursing A/L Subject",
        required_subjects=MEDICAL_SCIENCE_SUBJECTS,
        page=57,
    )


def _evaluate_ol_english_requirement(
    facts: ApplicantFacts,
    *,
    rule_id: str,
    rule_name: str,
    page: int,
) -> RuleResult:
    """Evaluate an O/L English requirement of grade S or better."""
    english_grade = facts.ol_results.get("english")
    supplied = f"English={english_grade}" if english_grade is not None else "none"

    if english_grade is None:
        passed = False
        reason = "FAIL: the required O/L English result was not supplied."
    else:
        passed = count_grades_at_least([english_grade], "S") == 1
        reason = (
            "PASS: O/L English has grade S or better."
            if passed
            else "FAIL: O/L English has a grade below S."
        )

    return RuleResult(
        rule_id=rule_id,
        rule_name=rule_name,
        passed=passed,
        message=f"Required subject: O/L English. Supplied relevant grade: {supplied}. {reason}",
        source=SOURCE,
        page=page,
    )


def _evaluate_r10(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Nursing O/L English requirement."""
    return _evaluate_ol_english_requirement(
        facts,
        rule_id="R10",
        rule_name="Nursing O/L English",
        page=57,
    )


def _evaluate_r11(facts: ApplicantFacts) -> RuleResult:
    """Evaluate supplied Nursing height and physical-condition facts."""
    minimum_height_cm = 147.32
    missing: list[str] = []
    if facts.height_cm is None:
        missing.append("height_cm")
    if facts.nursing_physical_condition_met is None:
        missing.append("nursing_physical_condition_met")

    details = (
        f"Required height: at least {minimum_height_cm:.2f} cm. "
        f"Supplied height: {facts.height_cm if facts.height_cm is not None else 'not supplied'}. "
        "Published physical-condition requirement supplied as satisfied: "
        f"{facts.nursing_physical_condition_met if facts.nursing_physical_condition_met is not None else 'not supplied'}."
    )

    if missing:
        passed = False
        reason = (
            "FAIL: insufficient information; required facts not supplied: "
            f"{', '.join(missing)}."
        )
    else:
        height_met = facts.height_cm >= minimum_height_cm
        condition_met = facts.nursing_physical_condition_met is True
        passed = height_met and condition_met
        if passed:
            reason = (
                "PASS: the supplied height meets the minimum and the published "
                "physical-condition requirement is recorded as satisfied."
            )
        elif not height_met and not condition_met:
            reason = (
                "FAIL: the supplied height is below the minimum and the published "
                "physical-condition requirement is not recorded as satisfied."
            )
        elif not height_met:
            reason = "FAIL: the supplied height is below the minimum."
        else:
            reason = (
                "FAIL: the published physical-condition requirement is not recorded "
                "as satisfied."
            )

    return RuleResult(
        rule_id="R11",
        rule_name="Nursing Physical",
        passed=passed,
        message=f"{details} {reason}",
        source=SOURCE,
        page=57,
    )


def _evaluate_r12(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Pharmacy A/L grade requirements."""
    supplied = _relevant_grades(facts, MEDICAL_SCIENCE_SUBJECTS)
    missing = [
        subject for subject in MEDICAL_SCIENCE_SUBJECTS if subject not in supplied
    ]
    details = _subject_details(MEDICAL_SCIENCE_SUBJECTS, supplied)

    if missing:
        passed = False
        reason = f"FAIL: missing required subjects: {', '.join(missing)}."
    else:
        chemistry_met = count_grades_at_least([supplied["Chemistry"]], "C") == 1
        physics_met = count_grades_at_least([supplied["Physics"]], "S") == 1
        biology_met = count_grades_at_least([supplied["Biology"]], "S") == 1
        passed = chemistry_met and physics_met and biology_met
        failed_requirements: list[str] = []
        if not chemistry_met:
            failed_requirements.append("Chemistry must have grade C or better")
        if not physics_met:
            failed_requirements.append("Physics must have grade S or better")
        if not biology_met:
            failed_requirements.append("Biology must have grade S or better")
        reason = (
            "PASS: Chemistry has grade C or better, and Physics and Biology each "
            "have grade S or better."
            if passed
            else f"FAIL: {'; '.join(failed_requirements)}."
        )

    return RuleResult(
        rule_id="R12",
        rule_name="Pharmacy A/L Grades",
        passed=passed,
        message=f"{details} {reason}",
        source=SOURCE,
        page=58,
    )


def _evaluate_r13(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Pharmacy O/L English requirement."""
    return _evaluate_ol_english_requirement(
        facts,
        rule_id="R13",
        rule_name="Pharmacy O/L English",
        page=58,
    )


R09 = Rule(
    id="R09",
    name="Nursing A/L Subject",
    applies_to="Nursing",
    source=SOURCE,
    page=57,
    evaluation_function=_evaluate_r09,
)

R10 = Rule(
    id="R10",
    name="Nursing O/L English",
    applies_to="Nursing",
    source=SOURCE,
    page=57,
    evaluation_function=_evaluate_r10,
)

R11 = Rule(
    id="R11",
    name="Nursing Physical",
    applies_to="Nursing",
    source=SOURCE,
    page=57,
    evaluation_function=_evaluate_r11,
)

R12 = Rule(
    id="R12",
    name="Pharmacy A/L Grades",
    applies_to="Pharmacy",
    source=SOURCE,
    page=58,
    evaluation_function=_evaluate_r12,
)

R13 = Rule(
    id="R13",
    name="Pharmacy O/L English",
    applies_to="Pharmacy",
    source=SOURCE,
    page=58,
    evaluation_function=_evaluate_r13,
)

COURSE_RULES += (R09, R10, R11, R12, R13)


def _evaluate_single_ol_subject_requirement(
    facts: ApplicantFacts,
    *,
    rule_id: str,
    rule_name: str,
    course: str,
    subject: str,
    required_grade: str,
    page: int,
) -> RuleResult:
    """Evaluate one exact O/L subject against a minimum grade."""
    grade = facts.ol_results.get(subject.casefold())
    supplied = f"{subject}={grade}" if grade is not None else "none"

    if grade is None:
        passed = False
        reason = f"FAIL: the required O/L {subject} result was not supplied."
    else:
        passed = count_grades_at_least([grade], required_grade) == 1
        reason = (
            f"PASS: O/L {subject} has grade {required_grade} or better."
            if passed
            else f"FAIL: O/L {subject} has a grade below {required_grade}."
        )

    return RuleResult(
        rule_id=rule_id,
        rule_name=rule_name,
        passed=passed,
        message=(
            f"Course: {course}. Required subject: O/L {subject} at grade "
            f"{required_grade} or better. Supplied relevant grade: {supplied}. "
            f"{reason}"
        ),
        source=SOURCE,
        page=page,
    )


def _evaluate_r16(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Law O/L English requirement."""
    return _evaluate_single_ol_subject_requirement(
        facts,
        rule_id="R16",
        rule_name="Law O/L English",
        course="Law",
        subject="English",
        required_grade="C",
        page=90,
    )


def _evaluate_r17(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Law O/L Sinhala-or-Tamil requirement."""
    sinhala = facts.ol_results.get("sinhala")
    tamil = facts.ol_results.get("tamil")
    supplied_parts = []
    if sinhala is not None:
        supplied_parts.append(f"Sinhala={sinhala}")
    if tamil is not None:
        supplied_parts.append(f"Tamil={tamil}")
    supplied = ", ".join(supplied_parts) or "none"

    sinhala_met = (
        count_grades_at_least([sinhala], "C") == 1 if sinhala is not None else False
    )
    tamil_met = (
        count_grades_at_least([tamil], "C") == 1 if tamil is not None else False
    )
    passed = sinhala_met or tamil_met

    if passed:
        qualifying_subjects = []
        if sinhala_met:
            qualifying_subjects.append("Sinhala")
        if tamil_met:
            qualifying_subjects.append("Tamil")
        reason = (
            "PASS: O/L "
            f"{' and '.join(qualifying_subjects)} has grade C or better, satisfying "
            "the Sinhala OR Tamil requirement."
        )
    elif sinhala is None and tamil is None:
        reason = "FAIL: neither an O/L Sinhala nor an O/L Tamil result was supplied."
    else:
        reason = (
            "FAIL: neither supplied O/L Sinhala nor O/L Tamil has grade C or better."
        )

    return RuleResult(
        rule_id="R17",
        rule_name="Law O/L Sinhala/Tamil",
        passed=passed,
        message=(
            "Course: Law. Required subjects: O/L Sinhala at grade C or better OR "
            "O/L Tamil at grade C or better. Supplied relevant grades: "
            f"{supplied}. {reason}"
        ),
        source=SOURCE,
        page=90,
    )


def _evaluate_r19(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Quantity Surveying O/L Mathematics requirement."""
    return _evaluate_single_ol_subject_requirement(
        facts,
        rule_id="R19",
        rule_name="Quantity Surveying O/L Mathematics",
        course="Quantity Surveying",
        subject="Mathematics",
        required_grade="C",
        page=84,
    )


def _evaluate_r20(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Quantity Surveying O/L Science requirement."""
    return _evaluate_single_ol_subject_requirement(
        facts,
        rule_id="R20",
        rule_name="Quantity Surveying O/L Science",
        course="Quantity Surveying",
        subject="Science",
        required_grade="S",
        page=84,
    )


def _evaluate_r21(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Quantity Surveying O/L English requirement."""
    return _evaluate_single_ol_subject_requirement(
        facts,
        rule_id="R21",
        rule_name="Quantity Surveying O/L English",
        course="Quantity Surveying",
        subject="English",
        required_grade="C",
        page=84,
    )


R16 = Rule(
    id="R16",
    name="Law O/L English",
    applies_to="Law",
    source=SOURCE,
    page=90,
    evaluation_function=_evaluate_r16,
)

R17 = Rule(
    id="R17",
    name="Law O/L Sinhala/Tamil",
    applies_to="Law",
    source=SOURCE,
    page=90,
    evaluation_function=_evaluate_r17,
)

R19 = Rule(
    id="R19",
    name="Quantity Surveying O/L Mathematics",
    applies_to="Quantity Surveying",
    source=SOURCE,
    page=84,
    evaluation_function=_evaluate_r19,
)

R20 = Rule(
    id="R20",
    name="Quantity Surveying O/L Science",
    applies_to="Quantity Surveying",
    source=SOURCE,
    page=84,
    evaluation_function=_evaluate_r20,
)

R21 = Rule(
    id="R21",
    name="Quantity Surveying O/L English",
    applies_to="Quantity Surveying",
    source=SOURCE,
    page=84,
    evaluation_function=_evaluate_r21,
)

COURSE_RULES += (R16, R17, R19, R20, R21)


SOURCE_R14_R15_R18 = "student_handbook_english.pdf"

IT_GRADE_C_SUBJECTS = (
    "Higher Mathematics",
    "Combined Mathematics",
    "Mathematics",
    "Physics",
)

LAW_LIST_A = (
    "Accounting",
    "Agricultural Science",
    "Biology",
    "Business Statistics",
    "Business Studies",
    "Chemistry",
    "Political Science",
    "Geography",
    "Higher Mathematics",
    "History",
    "Logic & Scientific Method",
    "Economics",
    "Physics",
    "Communication & Media Studies",
    "Mathematics",
    "Combined Mathematics",
    "Information & Communication Technology",
)

LAW_LIST_B = (
    "Buddhism",
    "Buddhist Civilization",
    "Islam",
    "Islamic Civilization",
    "Christianity",
    "Christian Civilization",
    "Chinese",
    "Greek & Roman Civilization",
    "English",
    "Japanese",
    "French",
    "Pali",
    "German",
    "Sanskrit",
    "Arabic",
    "Sinhala",
    "Hindi",
    "Tamil",
    "Russian",
    "Hinduism",
    "Hindu Civilization",
    "Korean",
)

QS_MATH_LIST = ("Combined Mathematics", "Higher Mathematics")
QS_OTHER_LIST = (
    "Accounting",
    "Economics",
    "Business Statistics",
    "Business Studies",
    "Physics",
    "Chemistry",
    "Information & Communication Technology",
)


def _format_grades(grades: dict[str, str]) -> str:
    """Format an exact-name subject-to-grade mapping for rule explanations."""
    return ", ".join(f"{subject}={grade}" for subject, grade in grades.items()) or "none"


def _evaluate_r14(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Information Technology A/L grade requirement."""
    passed_subject_count = count_grades_at_least(facts.al_results.values(), "S")
    relevant = _relevant_grades(facts, IT_GRADE_C_SUBJECTS)
    qualifying = {
        subject: grade
        for subject, grade in relevant.items()
        if count_grades_at_least([grade], "C") == 1
    }
    enough_passed_subjects = passed_subject_count >= 3
    has_required_c_grade = bool(qualifying)
    passed = enough_passed_subjects and has_required_c_grade

    if passed:
        reason = (
            "PASS: at least three A/L subjects have grade S or better and at least "
            "one listed subject has grade C or better."
        )
    elif not enough_passed_subjects and not has_required_c_grade:
        reason = (
            "FAIL: fewer than three A/L subjects have grade S or better and none "
            "of the listed subjects has grade C or better."
        )
    elif not enough_passed_subjects:
        reason = "FAIL: fewer than three A/L subjects have grade S or better."
    else:
        reason = "FAIL: none of the listed subjects has grade C or better."

    return RuleResult(
        rule_id="R14",
        rule_name="Information Technology A/L Grades",
        passed=passed,
        message=(
            f"Passed A/L subjects: {passed_subject_count}. Grade-C OR subjects: "
            f"{', '.join(IT_GRADE_C_SUBJECTS)}. Supplied relevant grades: "
            f"{_format_grades(relevant)}. {reason}"
        ),
        source=SOURCE_R14_R15_R18,
        page=83,
    )


def _evaluate_r15(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Law A/L subject-list and grade requirements."""
    list_a_grades = _relevant_grades(facts, LAW_LIST_A)
    list_b_grades = _relevant_grades(facts, LAW_LIST_B)
    list_a_count = len(list_a_grades)
    list_b_count = len(list_b_grades)
    subject_pattern_met = list_a_count == 3 or (
        1 <= list_a_count <= 2 and list_b_count == 3 - list_a_count
    )
    grades_at_least_c = count_grades_at_least(facts.al_results.values(), "C")
    grades_at_least_s = count_grades_at_least(facts.al_results.values(), "S")
    grade_pattern_met = grades_at_least_c >= 2 and grades_at_least_s == 3
    passed = subject_pattern_met and grade_pattern_met

    failures = []
    if not subject_pattern_met:
        failures.append(
            "the supplied subjects do not satisfy either the three-from-List-A "
            "branch or the one/two-from-List-A plus List-B branch"
        )
    if grades_at_least_c < 2:
        failures.append("fewer than two grades are C or better")
    if grades_at_least_s != 3:
        failures.append("the number of grades S or better is not exactly three")
    reason = (
        "PASS: the subject-list condition is satisfied, at least two grades are C "
        "or better, and exactly three grades are S or better."
        if passed
        else f"FAIL: {'; '.join(failures)}."
    )

    return RuleResult(
        rule_id="R15",
        rule_name="Law A/L Grade",
        passed=passed,
        message=(
            f"Supplied List A grades: {_format_grades(list_a_grades)}. Supplied "
            f"List B grades: {_format_grades(list_b_grades)}. List A count: "
            f"{list_a_count}; List B count: {list_b_count}; grades C or better: "
            f"{grades_at_least_c}; grades S or better: {grades_at_least_s}. {reason}"
        ),
        source=SOURCE_R14_R15_R18,
        page=90,
    )


def _evaluate_r18(facts: ApplicantFacts) -> RuleResult:
    """Evaluate the Quantity Surveying A/L subject and grade requirements."""
    math_grades = _relevant_grades(facts, QS_MATH_LIST)
    other_grades = _relevant_grades(facts, QS_OTHER_LIST)
    math_count = len(math_grades)
    other_count = len(other_grades)
    grades_at_least_s = count_grades_at_least(facts.al_results.values(), "S")
    math_condition_met = math_count >= 1
    other_condition_met = other_count == 3 - math_count
    grade_condition_met = grades_at_least_s == 3
    passed = math_condition_met and other_condition_met and grade_condition_met

    failures = []
    if not math_condition_met:
        failures.append("no subject from the Quantity Surveying mathematics list")
    if not other_condition_met:
        failures.append(
            f"the other-list count is {other_count}, not {3 - math_count}"
        )
    if not grade_condition_met:
        failures.append("the number of grades S or better is not exactly three")
    reason = (
        "PASS: at least one mathematics-list subject is supplied, the required "
        "number of other-list subjects is supplied, and exactly three grades are S "
        "or better."
        if passed
        else f"FAIL: {'; '.join(failures)}."
    )

    return RuleResult(
        rule_id="R18",
        rule_name="Quantity Surveying A/L",
        passed=passed,
        message=(
            f"Supplied mathematics-list grades: {_format_grades(math_grades)}. "
            f"Supplied other-list grades: {_format_grades(other_grades)}. "
            f"Mathematics-list count: {math_count}; other-list count: {other_count}; "
            f"grades S or better: {grades_at_least_s}. {reason}"
        ),
        source=SOURCE_R14_R15_R18,
        page=84,
    )


R14 = Rule(
    id="R14",
    name="Information Technology A/L Grades",
    applies_to="Information Technology",
    source=SOURCE_R14_R15_R18,
    page=83,
    evaluation_function=_evaluate_r14,
)

R15 = Rule(
    id="R15",
    name="Law A/L Grade",
    applies_to="Law",
    source=SOURCE_R14_R15_R18,
    page=90,
    evaluation_function=_evaluate_r15,
)

R18 = Rule(
    id="R18",
    name="Quantity Surveying A/L",
    applies_to="Quantity Surveying",
    source=SOURCE_R14_R15_R18,
    page=84,
    evaluation_function=_evaluate_r18,
)

COURSE_RULES = tuple(
    sorted(COURSE_RULES + (R14, R15, R18), key=lambda rule: int(rule.id[1:]))
)
