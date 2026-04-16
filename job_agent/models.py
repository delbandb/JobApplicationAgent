from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RoleTrack:
    name: str
    titles: list[str]
    core_skills: list[str]
    bonus_skills: list[str]
    keywords: list[str] = field(default_factory=list)


@dataclass
class CandidateProfile:
    name: str
    email: str
    phone: str
    location: str
    remote_ok: bool
    work_authorization: str
    years_experience: int
    headline: str
    resume_summary: str
    salary_expectation_min: int
    salary_expectation_currency: str
    preferred_locations: list[str]
    disallowed_keywords: list[str]
    core_strengths: list[str]
    role_tracks: list[RoleTrack]


@dataclass
class SearchFilters:
    minimum_match_score: int
    limit: int
    allowed_employment_types: list[str]
    allowed_remote_modes: list[str]
    application_mode: str
    default_submission_adapter: str
    auto_apply_requires_approval: bool


@dataclass
class JobOffer:
    id: str
    title: str
    company: str
    location: str
    remote_mode: str
    employment_type: str
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    years_experience_min: int | None
    skills: list[str]
    description: str
    apply_url: str
    submission_adapter: str | None = None


@dataclass
class MatchResult:
    job_id: str
    company: str
    title: str
    matched_track: str
    score: int
    fit_label: str
    reasons: list[str]
    blockers: list[str]
    summary: str
    recommended: bool


@dataclass
class ApplicationDraft:
    job_id: str
    subject: str
    cover_letter: str
    payload: dict[str, Any]


@dataclass
class ApplicationQueueItem:
    job_id: str
    company: str
    title: str
    matched_track: str
    score: int
    approved: bool = False
    submitted: bool = False
    submission_adapter: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
