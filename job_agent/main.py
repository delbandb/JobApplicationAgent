from __future__ import annotations

import argparse
import json

from .ingest import import_jobs
from .pipeline import approve_job, build_plan, run_apply


def main() -> None:
    parser = argparse.ArgumentParser(description="Job application agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("plan", help="Score jobs and generate application drafts")

    approve_parser = subparsers.add_parser("approve", help="Approve one job for submission")
    approve_parser.add_argument("--job-id", required=True)

    subparsers.add_parser("apply", help="Submit approved applications")

    import_parser = subparsers.add_parser("import-jobs", help="Import jobs from CSV or JSON into data/jobs.json")
    import_parser.add_argument("--source", required=True, help="Path to a CSV or JSON file")

    args = parser.parse_args()

    if args.command == "plan":
        results, queue = build_plan()
        print(json.dumps({"results": results, "queue": [item.to_dict() for item in queue]}, indent=2))
        return

    if args.command == "approve":
        success = approve_job(args.job_id)
        print(f"approved={success}")
        return

    if args.command == "apply":
        messages = run_apply()
        print(json.dumps(messages, indent=2))
        return

    if args.command == "import-jobs":
        result = import_jobs(args.source)
        print(json.dumps(result, indent=2))
        return


if __name__ == "__main__":
    main()
