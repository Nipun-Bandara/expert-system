# Rule Inventory

This document describes the implemented rules in human-readable form. Grade
order is `A > B > C > S > F`. “At least” includes the named grade.

## General eligibility rules

### R01 — Minimum Grade & Sitting

- **IF:** Exactly three supplied A/L subjects each have grade S or better, and
  all three results were obtained in one sitting.
- **THEN:** The basic grade and sitting requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 9

### R02 — Maximum Attempt Limit

- **IF:** The number of A/L attempts is 3 or fewer.
- **THEN:** The attempt-limit requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 9

### R03 — Common General Paper

- **IF:** The Common General Paper mark is at least 30.
- **THEN:** The Common General Paper requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 9

### R04 — Prior Registration

- **IF:** The applicant has not previously registered as an internal student in
  a Sri Lankan state university.
- **THEN:** The prior-registration rule passes. If prior registration is true,
  this rule fails and disqualifies the applicant.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 13

## Medicine, Dental Surgery, Veterinary Science, and Engineering

### R05 — Medicine Subject/Grade

- **IF:** Biology, Chemistry, and Physics are all present; all three have grade
  S or better; and at least two of the three have grade C or better.
- **THEN:** The Medicine course requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 50

### R06 — Dental Surgery Subject/Grade

- **IF:** Biology, Chemistry, and Physics are all present and each has grade S
  or better.
- **THEN:** The Dental Surgery course requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 51

### R07 — Veterinary Science Subject/Grade

- **IF:** Biology, Chemistry, and Physics are all present and each has grade S
  or better.
- **THEN:** The Veterinary Science course requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 51

### R08 — Engineering Subject/Grade

- **IF:** Chemistry, Combined Mathematics, and Physics are all present and each
  has grade S or better.
- **THEN:** The Engineering course requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 68

## Nursing and Pharmacy

### R09 — Nursing A/L Subject

- **IF:** Biology, Chemistry, and Physics are all present and each has grade S
  or better.
- **THEN:** The Nursing A/L subject requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 57

### R10 — Nursing O/L English

- **IF:** O/L English has grade S or better.
- **THEN:** The Nursing O/L English requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 57

### R11 — Nursing Physical

- **IF:** The supplied height is at least 147.32 cm (the exact conversion of
  4 feet 10 inches), and the supplied
  `nursing_physical_condition_met` fact is true.
- **THEN:** The Nursing physical requirement passes.
- **Missing facts:** If height or the physical-condition fact is not supplied,
  the pass/fail model records a failure with an insufficient-information
  explanation.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 57

### R12 — Pharmacy A/L Grades

- **IF:** Chemistry has grade C or better, Physics has grade S or better, and
  Biology has grade S or better.
- **THEN:** The Pharmacy A/L grade requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 58

### R13 — Pharmacy O/L English

- **IF:** O/L English has grade S or better.
- **THEN:** The Pharmacy O/L English requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 58

## Information Technology and Law

### R14 — Information Technology A/L Grades

- **IF:** At least three supplied A/L subjects have grade S or better, **AND** at
  least one of the following has grade C or better:
  - Higher Mathematics
  - Combined Mathematics
  - Mathematics
  - Physics
- **THEN:** The Information Technology A/L requirement passes.
- **Source:** `student_handbook_english.pdf`
- **Page:** 83, Section 2.2.8.1

### R15 — Law A/L Grade

**List A:**

- Accounting
- Agricultural Science
- Biology
- Business Statistics
- Business Studies
- Chemistry
- Political Science
- Geography
- Higher Mathematics
- History
- Logic & Scientific Method
- Economics
- Physics
- Communication & Media Studies
- Mathematics
- Combined Mathematics
- Information & Communication Technology

**List B:**

- Buddhism
- Buddhist Civilization
- Islam
- Islamic Civilization
- Christianity
- Christian Civilization
- Chinese
- Greek & Roman Civilization
- English
- Japanese
- French
- Pali
- German
- Sanskrit
- Arabic
- Sinhala
- Hindi
- Tamil
- Russian
- Hinduism
- Hindu Civilization
- Korean

- **IF:** Either all three subjects are in List A, **OR** one or two subjects are
  in List A and the number from List B equals `3 - number from List A`; **AND**
  at least two supplied grades are C or better; **AND** exactly three supplied
  grades are S or better.
- **THEN:** The Law A/L requirement passes.
- **Source:** `student_handbook_english.pdf`
- **Page:** 90, Section 2.2.8.10

### R16 — Law O/L English

- **IF:** O/L English has grade C or better.
- **THEN:** The Law O/L English requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 90

### R17 — Law O/L Sinhala/Tamil

- **IF:** O/L Sinhala has grade C or better **OR** O/L Tamil has grade C or
  better.
- **THEN:** The Law O/L Sinhala/Tamil requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 90

## Quantity Surveying

### R18 — Quantity Surveying A/L

**Mathematics list:**

- Combined Mathematics
- Higher Mathematics

**Other-subject list:**

- Accounting
- Economics
- Business Statistics
- Business Studies
- Physics
- Chemistry
- Information & Communication Technology

- **IF:** At least one supplied subject is in the mathematics list; **AND** the
  count of subjects in the other-subject list equals
  `3 - mathematics-list subject count`; **AND** exactly three supplied grades
  are S or better.
- **THEN:** The Quantity Surveying A/L requirement passes.
- **Source:** `student_handbook_english.pdf`
- **Page:** 84, Section 2.2.8.3

### R19 — Quantity Surveying O/L Mathematics

- **IF:** O/L Mathematics has grade C or better.
- **THEN:** The Quantity Surveying O/L Mathematics requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 84

### R20 — Quantity Surveying O/L Science

- **IF:** O/L Science has grade S or better.
- **THEN:** The Quantity Surveying O/L Science requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 84

### R21 — Quantity Surveying O/L English

- **IF:** O/L English has grade C or better.
- **THEN:** The Quantity Surveying O/L English requirement passes.
- **Source:** `student_handbook_english_2025/2026.pdf`
- **Page:** 84
