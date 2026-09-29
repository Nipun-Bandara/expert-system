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
git clone <repository-url>
cd <repository>
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
│   ├── sources.md                  # Source register
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

1. User input is stored as an `ApplicantFacts` working-memory object.
2. The engine evaluates all four general rules: R01-R04.
3. It selects the rules mapped to the requested course.
4. Every selected rule is evaluated; evaluation does not stop after the first
   failure.
5. A course is eligible only when every general rule and every mapped course
   rule passes.
6. The engine returns a structured `CourseEvaluation`, not only a Boolean.
7. The explanation facility reports the final result, general and course rule
   traces, failed requirements, and source references.

See [docs/architecture.txt](docs/architecture.txt) for the text architecture
diagram.

## Source documents

The knowledge base uses the handbook source identifiers supplied with the rule
requirements:

- `student_handbook_english_2025/2026.pdf`
- `student_handbook_english.pdf`

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
