# Sri Lankan University Course Eligibility Expert System

## Purpose

The Sri Lankan University Course Eligibility Expert System is a rule-based
Python command-line application that determines whether an applicant satisfies
published minimum eligibility requirements for selected Sri Lankan
state-university courses.

> **Important limitation:** This system does **not** predict actual admission or
> university selection. Passing its rules means only that the supplied facts
> satisfy the minimum requirements represented in the knowledge base.

## Prerequisites

- Python 3.11 or newer
- Git

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/Nipun-Bandara/expert-system.git
cd expert-system
python -m venv .venv
```

Activate the environment on Windows:

```text
.venv\Scripts\activate
```

Activate the environment on Linux or macOS:

```bash
source .venv/bin/activate
```

Install the dependency:

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

The menu can evaluate a specific supported course or every supported course.
The application prompts for applicant facts, delegates evaluation to the
inference engine, and displays rule traces, failed requirements, and source
references.

## Testing

```bash
pytest -v
```

## Project structure

```text
.
├── main.py                         # Executable entry point
├── expert_system/
│   ├── models.py                   # Applicant facts and result models
│   ├── grades.py                   # Grade normalization and comparison
│   ├── knowledge_base.py           # Rules R01-R21
│   ├── engine.py                   # General and course inference
│   ├── explanations.py             # Human-readable decision traces
│   └── cli.py                      # Input collection and result display
├── tests/                          # Unit and integration tests
├── docs/
│   ├── rules.md                    # Human-readable rule inventory
│   ├── sources.md                  # Source 
│   └── architecture.txt            # Text architecture diagram
├── requirements.txt
└── README.md
```

Rules remain separate from the CLI. The CLI collects facts and displays
results; it does not decide eligibility.

## Supported courses

- Medicine
- Dental Surgery
- Veterinary Science
- Engineering
- Nursing
- Pharmacy
- Information Technology
- Law
- Quantity Surveying

## How the inference engine works

The project implements two explicit, deliberately small inference workflows.
It is not Prolog, a RETE implementation, or a general-purpose inference engine.

### Backward chaining: one selected course

`backward_chaining()` starts with the goal `eligible for <selected course>`.
It identifies R01-R04 plus only the course-specific rules mapped to that goal,
then evaluates every required antecedent against the supplied `ApplicantFacts`.
Its trace records the goal, required and evaluated rule IDs, satisfied and
failed conditions, and the final conclusion. The CLI uses this mode when the
user checks one course.

### Forward chaining: all supported courses

`forward_chaining()` starts with the applicant facts, evaluates R01-R21 once,
and derives an eligible/not-eligible conclusion for every supported course.
Its trace records the mode, evaluated rules, all derived conclusions, and all
failed conditions. The CLI uses this mode when the user checks all courses.

The compatibility functions `evaluate_course()` and `evaluate_all_courses()`
remain available and delegate to backward and forward chaining respectively.
Every `CourseEvaluation` retains the existing rule results, failed-requirement
reporting, source references, and a reference to its inference trace.

See [docs/architecture.txt](docs/architecture.txt) for the text architecture
diagram.

## Source documents

Every rule uses one structured source record and the same identifier:

- `UGC-SL-ADMISSIONS-HANDBOOK-2025-2026`

The identifier represents the University Grants Commission Sri Lanka
publication *Admission to Undergraduate Courses of the Universities in Sri
Lanka, Academic Year 2025/2026*. The official handbook is available at
[ugc.ac.lk](https://www.ugc.ac.lk/downloads/admissions/Handbook_2025_26/student_handbook_english.pdf).

Exact page and section information is recorded in [docs/sources.md](docs/sources.md)
and beside every rule in [docs/rules.md](docs/rules.md).

## Limitations

- The system checks only the minimum eligibility rules represented in its
  knowledge base.
- It does not predict admission, selection, placement, ranking, or available
  university places.
- It does not calculate or interpret Z-scores, district quotas, or course
  cut-offs.
- Results depend on the accuracy and completeness of facts entered by the user.
- Subject names must match the documented names; the system does not invent or
  infer subject aliases.
- The Nursing physical-condition fact must be supplied by the applicant. The
  system does not perform a medical diagnosis.
- Handbook requirements may change. The implemented rules must be reviewed
  against the applicable official publication before use.
