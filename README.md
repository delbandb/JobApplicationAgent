# JobApplicationAgent

JobApplicationAgent is a Python workflow for organizing job leads, scoring them against a candidate profile, generating application drafts, and keeping a human approval step before anything is submitted.

It is not a spam bot. The project is designed around a more realistic job-search workflow: import roles, understand fit, explain the score, prepare drafts, and only move forward when the application is worth reviewing.

## Why I Built It

Job hunting becomes admin work very quickly. After a few open leads, it is easy to lose track of which roles match your profile, which ones fail on salary or location, and which ones deserve a tailored message. I built this project to make that process structured without pretending every job should be applied to automatically.

The main value is transparency: every score includes reasons and blockers, so the output can be reviewed instead of blindly trusted.

## What It Does

- Imports job leads from CSV or JSON.
- Normalizes common job fields such as title, company, location, salary, skills, description, and application URL.
- Loads a candidate profile and search filters from YAML files.
- Scores each job against multiple role tracks.
- Explains each match with positive signals and blockers.
- Generates an application queue ordered by fit.
- Creates draft application notes in Markdown.
- Builds a visual HTML dashboard and JSON match report.
- Requires approval before the apply step can submit or generate final output.

## Scoring Signals

The scoring system considers:

- Role-title alignment.
- Core-skill overlap.
- Bonus-skill overlap.
- Keywords in the job description.
- Preferred locations and remote mode.
- Employment type.
- Experience requirements.
- Salary expectations.
- Disallowed keywords or deal breakers.

Scores are capped at 100 and converted into labels such as `Excellent`, `Strong`, `Possible`, or `Weak`.

## Tech Stack

| Area | Tools |
| --- | --- |
| Language | Python |
| Configuration | YAML |
| Inputs | CSV, JSON |
| Outputs | Markdown, JSON, HTML |
| Interface | CLI |

## Project Structure

```text
job-application-agent/
|-- data/
|   |-- jobs.json                # Demo or imported job leads
|   |-- job_import_template.csv  # CSV template for new leads
|   |-- profile.yaml             # Candidate profile and role tracks
|   `-- search_filters.yaml      # Rules for filtering and scoring
|-- job_agent/
|   |-- apply.py                 # Submission adapters and approval handling
|   |-- generator.py             # Draft generation helpers
|   |-- ingest.py                # CSV and JSON import logic
|   |-- io_utils.py              # File loading and writing helpers
|   |-- main.py                  # CLI entry point
|   |-- models.py                # Domain models
|   |-- pipeline.py              # Main workflow orchestration
|   |-- reporting.py             # HTML and summary outputs
|   `-- scoring.py               # Match scoring logic
|-- output/
|   |-- dashboard.html           # Visual review dashboard
|   |-- match_report.json        # Scored jobs with reasons and blockers
|   |-- application_queue.json   # Approved, blocked, and pending applications
|   `-- drafts/                  # Generated Markdown drafts
|-- requirements.txt
`-- README.md
```

## Run Locally

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

## Typical Workflow

Import leads from a CSV file:

```bash
python -m job_agent.main import-jobs --source data/job_import_template.csv
```

Score jobs and generate drafts:

```bash
python -m job_agent.main plan
```

Approve one job for submission:

```bash
python -m job_agent.main approve --job-id import-001-madrid-digital-studio-junior-frontend-developer
```

Run the apply step:

```bash
python -m job_agent.main apply
```

## Outputs

- `output/dashboard.html` gives a quick visual overview of the application queue.
- `output/match_report.json` stores scoring details for every job.
- `output/application_queue.json` tracks which jobs are approved, skipped, or submitted.
- `output/drafts/` contains generated Markdown application drafts.
- `output/email_drafts/` can hold final email-style drafts depending on the adapter.

## What It Does Not Do Yet

- It does not scrape job boards directly.
- It does not log into websites or auto-click forms.
- It does not rewrite a CV automatically.
- It does not use a database yet.
- It does not have a web UI or API yet.

Those limits are intentional for this version. The project is built around a reviewable workflow, not uncontrolled automation.

## What I Would Improve Next

- Add tests for scoring edge cases and import normalization.
- Add deduplication when importing jobs from multiple sources.
- Add a lightweight web dashboard for reviewing the queue.
- Add CV parsing from PDF or DOCX.
- Add a small SQLite database for persistence.
- Add role-specific draft templates to make generated text less generic.
