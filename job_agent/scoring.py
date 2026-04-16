from __future__ import annotations

import re

from .models import CandidateProfile, JobOffer, MatchResult, RoleTrack, SearchFilters


def _normalize(values: list[str]) -> set[str]:
    return {value.strip().lower() for value in values}


def _tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9\+\#\.]+", value.lower()))


def _overlap_score(left: set[str], right: set[str], max_points: int) -> tuple[int, int]:
    if not left:
        return 0, 0
    overlap = len(left & right)
    score = round((overlap / len(left)) * max_points)
    return score, overlap


def _track_score(track: RoleTrack, job: JobOffer) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0
    job_title = job.title.lower()
    job_tokens = _tokenize(job.title + " " + job.description + " " + " ".join(job.skills))

    if any(title.lower() in job_title for title in track.titles):
        score += 20
        reasons.append("Strong title alignment")

    core_skill_score, core_overlap = _overlap_score(_normalize(track.core_skills), _normalize(job.skills), 28)
    if core_skill_score:
        score += core_skill_score
        reasons.append(f"{core_overlap} core skills matched")

    bonus_skill_score, bonus_overlap = _overlap_score(_normalize(track.bonus_skills), _normalize(job.skills), 10)
    if bonus_skill_score:
        score += bonus_skill_score
        reasons.append(f"{bonus_overlap} bonus skills matched")

    keyword_hits = len(_normalize(track.keywords) & job_tokens)
    if keyword_hits:
        score += min(keyword_hits * 4, 12)
        reasons.append("Relevant keywords found in job description")

    return score, reasons


def score_job(profile: CandidateProfile, filters: SearchFilters, job: JobOffer) -> MatchResult:
    best_track = profile.role_tracks[0]
    best_track_score = -1
    best_track_reasons: list[str] = []

    for track in profile.role_tracks:
        track_score, track_reasons = _track_score(track, job)
        if track_score > best_track_score:
            best_track = track
            best_track_score = track_score
            best_track_reasons = track_reasons

    score = max(best_track_score, 0)
    reasons = list(best_track_reasons)
    blockers: list[str] = []

    if job.remote_mode.lower() in [mode.lower() for mode in filters.allowed_remote_modes]:
        score += 8
        reasons.append(f"Remote mode allowed: {job.remote_mode}")
    else:
        blockers.append(f"Remote mode not allowed: {job.remote_mode}")

    if job.employment_type.lower() in [mode.lower() for mode in filters.allowed_employment_types]:
        score += 6
    else:
        blockers.append(f"Employment type not allowed: {job.employment_type}")

    preferred_locations = _normalize(profile.preferred_locations)
    if job.location.lower() in preferred_locations:
        score += 10
        reasons.append(f"Location fit: {job.location}")
    elif profile.remote_ok and job.remote_mode.lower() == "remote":
        score += 8
        reasons.append("Remote-friendly role")
    else:
        blockers.append(f"Location outside focus area: {job.location}")

    if job.years_experience_min is not None:
        if profile.years_experience >= job.years_experience_min:
            score += 8
            reasons.append("Experience requirement met")
        else:
            blockers.append(
                f"Experience gap: requires {job.years_experience_min}+ years, profile has {profile.years_experience}"
            )

    if (
        job.salary_min is not None
        and job.salary_currency
        and job.salary_currency.upper() == profile.salary_expectation_currency.upper()
    ):
        if (job.salary_max and job.salary_max >= profile.salary_expectation_min) or (
            job.salary_min >= profile.salary_expectation_min
        ):
            score += 8
            reasons.append("Salary range meets expectation")
        else:
            blockers.append("Salary below expectation")

    description = job.description.lower()
    for keyword in _normalize(profile.disallowed_keywords):
        if keyword in description:
            score -= 25
            blockers.append(f"Disallowed keyword found: {keyword}")

    score = max(0, min(score, 100))
    if score >= 80:
        fit_label = "Excellent"
    elif score >= filters.minimum_match_score:
        fit_label = "Strong"
    elif score >= 50:
        fit_label = "Possible"
    else:
        fit_label = "Weak"

    recommended = score >= filters.minimum_match_score and len(blockers) == 0
    summary = (
        f"Best track: {best_track.name}. "
        f"Score {score}/100 with {len(reasons)} positive signals"
        f"{' and no blockers.' if not blockers else f' but {len(blockers)} blocker(s).'}"
    )

    return MatchResult(
        job_id=job.id,
        company=job.company,
        title=job.title,
        matched_track=best_track.name,
        score=score,
        fit_label=fit_label,
        reasons=reasons,
        blockers=blockers,
        summary=summary,
        recommended=recommended,
    )
