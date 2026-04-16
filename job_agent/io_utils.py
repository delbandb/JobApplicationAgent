from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from .models import (
    ApplicationDraft,
    ApplicationQueueItem,
    CandidateProfile,
    JobOffer,
    MatchResult,
    RoleTrack,
    SearchFilters,
)


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DRAFTS_DIR = OUTPUT_DIR / "drafts"
EMAIL_DRAFTS_DIR = OUTPUT_DIR / "email_drafts"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def load_profile() -> CandidateProfile:
    raw_profile = load_yaml(DATA_DIR / "profile.yaml")
    raw_tracks = raw_profile.pop("role_tracks", [])
    role_tracks = [RoleTrack(**track) for track in raw_tracks]
    return CandidateProfile(role_tracks=role_tracks, **raw_profile)


def load_filters() -> SearchFilters:
    return SearchFilters(**load_yaml(DATA_DIR / "search_filters.yaml"))


def load_jobs() -> list[JobOffer]:
    with (DATA_DIR / "jobs.json").open("r", encoding="utf-8") as handle:
        items = json.load(handle)
    return [JobOffer(**item) for item in items]


def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    EMAIL_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)


def write_text(path: Path, payload: str) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write(payload)


def write_match_report(results: list[MatchResult]) -> None:
    write_json(OUTPUT_DIR / "match_report.json", [asdict(result) for result in results])


def write_application_queue(items: list[ApplicationQueueItem]) -> None:
    write_json(OUTPUT_DIR / "application_queue.json", [item.to_dict() for item in items])


def load_application_queue() -> list[ApplicationQueueItem]:
    path = OUTPUT_DIR / "application_queue.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        raw_items = json.load(handle)
    return [ApplicationQueueItem(**item) for item in raw_items]


def write_draft_markdown(draft: ApplicationDraft) -> None:
    body = "\n".join(
        [
            f"# {draft.subject}",
            "",
            draft.cover_letter,
            "",
            "## Payload",
            "",
            "```json",
            json.dumps(draft.payload, indent=2, ensure_ascii=True),
            "```",
            "",
        ]
    )
    write_text(DRAFTS_DIR / f"{draft.job_id}.md", body)
