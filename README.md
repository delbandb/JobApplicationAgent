# Madrid Career Match Agent

A personal AI-assisted job-matching project built to support one real candidate while also serving as a recruiter-facing portfolio artifact.

This repository scores opportunities in Madrid against a multi-track profile that can span:

- data analyst
- UI / product design
- frontend engineering
- backend engineering
- IT support / systems roles

It then generates:

- a structured match report
- role-specific application drafts
- an approval queue before submission
- a visual HTML dashboard that is easier for recruiters to review on GitHub
- a real import path for CSV or JSON job leads

## Publishing note

This repository is intentionally published with sanitized candidate data and curated demo outputs so recruiters can review the workflow without exposing private application history.

## Why this is a strong portfolio project

This is not just a script that sends applications. It shows:

- product thinking around a real workflow
- data modeling for candidates, jobs, and match signals
- scoring logic with transparent reasoning and blockers
- output generation for both personal use and public presentation
- safe automation boundaries instead of blind spam

## Project structure

- `data/profile.yaml`: candidate profile and role tracks
- `data/jobs.json`: jobs to evaluate
- `data/job_import_template.csv`: starter CSV template for real job exports
- `data/search_filters.yaml`: search rules and application controls
- `job_agent/`: matching engine, reporting, application queue, and CLI
- `output/dashboard.html`: recruiter-friendly visual report
- `output/portfolio_summary.md`: short written project snapshot

## Quick start

```powershell
python -m job_agent.main import-jobs --source data\job_import_template.csv
python -m job_agent.main plan
python -m job_agent.main approve --job-id import-001-madrid-digital-studio-junior-frontend-developer
python -m job_agent.main apply
```

## Import real jobs

You can now import leads from CSV or JSON before running the matcher.

Supported CSV headers are flexible and include common variants such as:

- `title` / `job_title`
- `company` / `company_name`
- `location`
- `remote_mode` / `workplace`
- `employment_type`
- `salary_min` / `salary_max`
- `skills`
- `description`
- `apply_url`

Example:

```powershell
python -m job_agent.main import-jobs --source "C:\path\to\madrid_jobs.csv"
python -m job_agent.main plan
```

## Current behavior

The project is designed for personal use, so it is intentionally conservative:

- it only auto-submits jobs you explicitly approve
- it stores the reasoning behind every score
- it keeps submission adapters simple and auditable

## Portfolio outputs

The repository includes a curated demo set in `output/`:

- `dashboard.html` for a visual recruiter-friendly snapshot
- `portfolio_summary.md` for a concise written overview
- `match_report.json` and `application_queue.json` for transparent machine-readable outputs

## Future work

- parse PDF or DOCX CV files directly into the candidate profile
- support merge and deduplicate modes for repeated imports
- add board-specific adapters for selected job platforms
- generate stronger role-specific cover letter variants
