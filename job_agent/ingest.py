from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .io_utils import DATA_DIR, write_json


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "id": ("id", "job_id", "job id"),
    "title": ("title", "job_title", "job title", "position", "role"),
    "company": ("company", "company_name", "company name"),
    "location": ("location", "city"),
    "remote_mode": ("remote_mode", "remote mode", "workplace", "remote", "mode"),
    "employment_type": ("employment_type", "employment type", "type"),
    "salary_min": ("salary_min", "salary min", "min_salary", "minimum salary"),
    "salary_max": ("salary_max", "salary max", "max_salary", "maximum salary"),
    "salary_currency": ("salary_currency", "currency", "salary currency"),
    "years_experience_min": (
        "years_experience_min",
        "years experience min",
        "experience",
        "experience_years",
        "minimum experience",
    ),
    "skills": ("skills", "stack", "technologies", "requirements"),
    "description": ("description", "summary", "job description"),
    "apply_url": ("apply_url", "apply url", "url", "link", "application_url"),
    "submission_adapter": ("submission_adapter", "submission adapter", "adapter"),
}


DEFAULTS: dict[str, Any] = {
    "location": "Madrid",
    "remote_mode": "hybrid",
    "employment_type": "full-time",
    "salary_min": None,
    "salary_max": None,
    "salary_currency": "EUR",
    "years_experience_min": 1,
    "skills": [],
    "description": "",
    "apply_url": "",
    "submission_adapter": "email_draft",
}


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("_", " ")


def _lookup(row: dict[str, Any], field_name: str) -> Any:
    for alias in FIELD_ALIASES[field_name]:
        for key, value in row.items():
            if _normalize_key(key) == alias:
                return value
    return None


def _parse_int(value: Any) -> int | None:
    if value in (None, "", "null"):
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip().replace(",", "")
    digits = "".join(char for char in text if char.isdigit())
    return int(digits) if digits else None


def _parse_skills(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value)
    separators = ["|", ";", ","]
    for separator in separators:
        if separator in text:
            return [item.strip() for item in text.split(separator) if item.strip()]
    return [text.strip()] if text.strip() else []


def _slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts)


def _build_id(title: str, company: str, index: int) -> str:
    return f"import-{index:03d}-{_slugify(company)}-{_slugify(title)}"[:80]


def normalize_row(row: dict[str, Any], index: int) -> dict[str, Any]:
    title = str(_lookup(row, "title") or "").strip()
    company = str(_lookup(row, "company") or "").strip()
    if not title or not company:
        raise ValueError("Each imported job needs at least title and company.")

    normalized = {
        "id": str(_lookup(row, "id") or _build_id(title, company, index)),
        "title": title,
        "company": company,
        "location": str(_lookup(row, "location") or DEFAULTS["location"]).strip(),
        "remote_mode": str(_lookup(row, "remote_mode") or DEFAULTS["remote_mode"]).strip().lower(),
        "employment_type": str(_lookup(row, "employment_type") or DEFAULTS["employment_type"]).strip().lower(),
        "salary_min": _parse_int(_lookup(row, "salary_min")),
        "salary_max": _parse_int(_lookup(row, "salary_max")),
        "salary_currency": str(_lookup(row, "salary_currency") or DEFAULTS["salary_currency"]).strip().upper(),
        "years_experience_min": _parse_int(_lookup(row, "years_experience_min")),
        "skills": _parse_skills(_lookup(row, "skills")),
        "description": str(_lookup(row, "description") or DEFAULTS["description"]).strip(),
        "apply_url": str(_lookup(row, "apply_url") or DEFAULTS["apply_url"]).strip(),
        "submission_adapter": str(_lookup(row, "submission_adapter") or DEFAULTS["submission_adapter"]).strip(),
    }

    if normalized["years_experience_min"] is None:
        normalized["years_experience_min"] = DEFAULTS["years_experience_min"]

    if normalized["salary_min"] is None and normalized["salary_max"] is None:
        normalized["salary_currency"] = DEFAULTS["salary_currency"]

    return normalized


def load_source(source: Path) -> list[dict[str, Any]]:
    suffix = source.suffix.lower()
    if suffix == ".json":
        items = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise ValueError("JSON import file must contain a list of job objects.")
        return [dict(item) for item in items]

    if suffix == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]

    raise ValueError(f"Unsupported import format: {source.suffix}")


def import_jobs(source_path: str, destination: Path | None = None) -> dict[str, Any]:
    source = Path(source_path).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Import source not found: {source}")

    rows = load_source(source)
    normalized_jobs: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, row in enumerate(rows, start=1):
        try:
            normalized_jobs.append(normalize_row(row, index))
        except ValueError as exc:
            errors.append(f"row {index}: {exc}")

    target = destination or DATA_DIR / "jobs.json"
    write_json(target, normalized_jobs)

    return {
        "source": str(source),
        "target": str(target),
        "imported": len(normalized_jobs),
        "failed": len(errors),
        "errors": errors,
    }
