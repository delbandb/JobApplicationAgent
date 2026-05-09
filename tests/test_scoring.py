from __future__ import annotations

import unittest

from job_agent.models import CandidateProfile, JobOffer, RoleTrack, SearchFilters
from job_agent.scoring import score_job


def make_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Delband Behdadfar",
        email="delband@example.com",
        phone="",
        location="Madrid",
        remote_ok=True,
        work_authorization="EU",
        years_experience=2,
        headline="Junior data and frontend candidate",
        resume_summary="Python, SQL, and frontend projects.",
        salary_expectation_min=24000,
        salary_expectation_currency="EUR",
        preferred_locations=["Madrid"],
        disallowed_keywords=["senior only"],
        core_strengths=["Python", "SQL"],
        role_tracks=[
            RoleTrack(
                name="Data Analyst",
                titles=["Data Analyst"],
                core_skills=["Python", "SQL"],
                bonus_skills=["Power BI"],
                keywords=["dashboard", "analytics"],
            )
        ],
    )


def make_filters() -> SearchFilters:
    return SearchFilters(
        minimum_match_score=70,
        limit=10,
        allowed_employment_types=["full-time", "internship"],
        allowed_remote_modes=["remote", "hybrid"],
        application_mode="draft",
        default_submission_adapter="email_draft",
        auto_apply_requires_approval=True,
    )


def make_job(**overrides: object) -> JobOffer:
    values = {
        "id": "job-001",
        "title": "Junior Data Analyst",
        "company": "Insight Madrid",
        "location": "Madrid",
        "remote_mode": "hybrid",
        "employment_type": "full-time",
        "salary_min": 24000,
        "salary_max": 30000,
        "salary_currency": "EUR",
        "years_experience_min": 1,
        "skills": ["Python", "SQL", "Power BI"],
        "description": "Build analytics dashboard reports for operations.",
        "apply_url": "https://example.com/apply",
        "submission_adapter": "email_draft",
    }
    values.update(overrides)
    return JobOffer(**values)


class ScoringTests(unittest.TestCase):
    def test_recommends_strong_matching_job_without_blockers(self) -> None:
        result = score_job(make_profile(), make_filters(), make_job())

        self.assertTrue(result.recommended)
        self.assertGreaterEqual(result.score, 80)
        self.assertEqual(result.fit_label, "Excellent")
        self.assertEqual(result.blockers, [])
        self.assertIn("Data Analyst", result.summary)

    def test_blocks_disallowed_or_out_of_scope_jobs(self) -> None:
        result = score_job(
            make_profile(),
            make_filters(),
            make_job(
                location="Berlin",
                remote_mode="onsite",
                employment_type="contract",
                description="Senior only onsite support role.",
            ),
        )

        self.assertFalse(result.recommended)
        self.assertLess(result.score, 70)
        self.assertTrue(any("Remote mode not allowed" in item for item in result.blockers))
        self.assertTrue(any("Employment type not allowed" in item for item in result.blockers))
        self.assertTrue(any("Disallowed keyword" in item for item in result.blockers))


if __name__ == "__main__":
    unittest.main()
