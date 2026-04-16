from __future__ import annotations

from .apply import get_adapter
from .generator import create_application_draft
from .io_utils import (
    OUTPUT_DIR,
    ensure_output_dirs,
    load_application_queue,
    load_filters,
    load_jobs,
    load_profile,
    write_application_queue,
    write_draft_markdown,
    write_match_report,
    write_text,
)
from .models import ApplicationQueueItem
from .reporting import build_dashboard_html, build_portfolio_summary
from .scoring import score_job


def build_plan() -> tuple[list[dict], list[ApplicationQueueItem]]:
    ensure_output_dirs()
    profile = load_profile()
    filters = load_filters()
    jobs = load_jobs()

    results = [score_job(profile, filters, job) for job in jobs]
    results.sort(key=lambda item: item.score, reverse=True)
    write_match_report(results)

    queue: list[ApplicationQueueItem] = []
    job_lookup = {job.id: job for job in jobs}

    for result in results[: filters.limit]:
        job = job_lookup[result.job_id]
        draft = create_application_draft(profile, job, result)
        write_draft_markdown(draft)
        queue.append(
            ApplicationQueueItem(
                job_id=job.id,
                company=job.company,
                title=job.title,
                matched_track=result.matched_track,
                score=result.score,
                approved=not filters.auto_apply_requires_approval and result.recommended,
                submitted=False,
                submission_adapter=job.submission_adapter or filters.default_submission_adapter,
                notes=[result.summary, *result.reasons, *result.blockers],
            )
        )

    write_application_queue(queue)
    write_text(OUTPUT_DIR / "portfolio_summary.md", build_portfolio_summary(profile, results))
    write_text(OUTPUT_DIR / "dashboard.html", build_dashboard_html(profile, results, queue))
    return ([result.__dict__ for result in results], queue)


def approve_job(job_id: str) -> bool:
    queue = load_application_queue()
    changed = False
    for item in queue:
        if item.job_id == job_id:
            item.approved = True
            changed = True
            break
    if changed:
        write_application_queue(queue)
    return changed


def run_apply() -> list[str]:
    ensure_output_dirs()
    profile = load_profile()
    filters = load_filters()
    jobs = {job.id: job for job in load_jobs()}
    queue = load_application_queue()

    messages: list[str] = []
    for item in queue:
        if item.submitted:
            continue
        if not item.approved:
            messages.append(f"Skipped {item.job_id}: not approved")
            continue
        if filters.application_mode != "approved_auto_apply":
            messages.append(f"Skipped {item.job_id}: application mode is {filters.application_mode}")
            continue

        job = jobs.get(item.job_id)
        if job is None:
            messages.append(f"Skipped {item.job_id}: job definition missing")
            continue

        match = score_job(profile, filters, job)
        if match.score < filters.minimum_match_score:
            messages.append(f"Skipped {item.job_id}: score dropped to {match.score}")
            continue
        if match.blockers:
            messages.append(f"Skipped {item.job_id}: blockers present")
            continue

        draft = create_application_draft(profile, job, match)
        adapter = get_adapter(item.submission_adapter or filters.default_submission_adapter)
        result = adapter.submit(item, draft)
        item.submitted = True
        messages.append(result)

    write_application_queue(queue)
    refreshed_results = [score_job(profile, filters, job) for job in jobs.values()]
    refreshed_results.sort(key=lambda item: item.score, reverse=True)
    write_text(OUTPUT_DIR / "dashboard.html", build_dashboard_html(profile, refreshed_results, queue))
    return messages
