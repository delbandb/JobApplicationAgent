from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from job_agent.ingest import import_jobs, normalize_row


class IngestTests(unittest.TestCase):
    def test_normalize_row_accepts_common_aliases(self) -> None:
        row = {
            "Job Title": " Junior Data Analyst ",
            "Company Name": " Insight Madrid ",
            "City": "Madrid",
            "Workplace": "Hybrid",
            "Minimum Salary": "28,000 EUR",
            "Technologies": "Python; SQL; Power BI",
            "Application URL": "https://example.com/apply",
        }

        normalized = normalize_row(row, 1)

        self.assertEqual(normalized["title"], "Junior Data Analyst")
        self.assertEqual(normalized["company"], "Insight Madrid")
        self.assertEqual(normalized["remote_mode"], "hybrid")
        self.assertEqual(normalized["salary_min"], 28000)
        self.assertEqual(normalized["skills"], ["Python", "SQL", "Power BI"])
        self.assertTrue(normalized["id"].startswith("import-001-insight-madrid"))

    def test_import_jobs_reports_invalid_rows_without_stopping_import(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "jobs.csv"
            target = Path(temp_dir) / "jobs.json"

            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["title", "company"])
                writer.writeheader()
                writer.writerow({"title": "Frontend Developer", "company": "Madrid Studio"})
                writer.writerow({"title": "", "company": "Missing Title LLC"})

            result = import_jobs(str(source), destination=target)

            self.assertEqual(result["imported"], 1)
            self.assertEqual(result["failed"], 1)
            self.assertTrue(target.exists())
            self.assertIn("row 2", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
