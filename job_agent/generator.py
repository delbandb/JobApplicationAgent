from __future__ import annotations

from .models import ApplicationDraft, CandidateProfile, JobOffer, MatchResult


def create_application_draft(profile: CandidateProfile, job: JobOffer, match: MatchResult) -> ApplicationDraft:
    subject = f"Application for {job.title} at {job.company}"
    strengths = ", ".join(profile.core_strengths[:3])
    role_pitch = match.matched_track.lower()
    reasons = "; ".join(match.reasons[:3]) if match.reasons else "a strong overall fit"
    cover_letter = "\n".join(
        [
            f"Dear {job.company} hiring team,",
            "",
            f"I am applying for the {job.title} role in Madrid. Based on my background, this looks like one of my strongest matches in the {role_pitch} track because of {reasons}.",
            f"I bring {profile.years_experience} years of practical experience, with particular strengths in {strengths}.",
            profile.resume_summary,
            "",
            f"I would be excited to contribute to {job.company} and help deliver value quickly through reliable execution, curiosity, and collaboration.",
            "",
            "Best regards,",
            profile.name,
            profile.email,
            profile.phone,
        ]
    )
    payload = {
        "candidate_name": profile.name,
        "candidate_email": profile.email,
        "candidate_phone": profile.phone,
        "headline": profile.headline,
        "job_id": job.id,
        "company": job.company,
        "job_title": job.title,
        "matched_track": match.matched_track,
        "apply_url": job.apply_url,
        "match_score": match.score,
        "fit_label": match.fit_label,
        "resume_summary": profile.resume_summary,
    }
    return ApplicationDraft(job_id=job.id, subject=subject, cover_letter=cover_letter, payload=payload)
