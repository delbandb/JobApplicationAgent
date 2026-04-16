from __future__ import annotations

from pathlib import Path

from .io_utils import EMAIL_DRAFTS_DIR
from .models import ApplicationDraft, ApplicationQueueItem


class SubmissionError(RuntimeError):
    """Raised when a submission cannot be completed."""


class SubmissionAdapter:
    def submit(self, item: ApplicationQueueItem, draft: ApplicationDraft) -> str:
        raise NotImplementedError


class ConsoleAdapter(SubmissionAdapter):
    def submit(self, item: ApplicationQueueItem, draft: ApplicationDraft) -> str:
        return f"Printed payload for {item.job_id}: {draft.payload}"


class EmailDraftAdapter(SubmissionAdapter):
    def submit(self, item: ApplicationQueueItem, draft: ApplicationDraft) -> str:
        target = Path(EMAIL_DRAFTS_DIR) / f"{item.job_id}.txt"
        content = "\n".join(
            [
                f"Subject: {draft.subject}",
                "",
                draft.cover_letter,
                "",
            ]
        )
        target.write_text(content, encoding="utf-8")
        return f"Wrote email draft to {target}"


def get_adapter(name: str | None) -> SubmissionAdapter:
    normalized = (name or "console").lower()
    if normalized == "console":
        return ConsoleAdapter()
    if normalized == "email_draft":
        return EmailDraftAdapter()
    raise SubmissionError(f"Unsupported submission adapter: {name}")
