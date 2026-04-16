from __future__ import annotations

import html
from collections import Counter

from .models import ApplicationQueueItem, CandidateProfile, MatchResult


def build_portfolio_summary(profile: CandidateProfile, results: list[MatchResult]) -> str:
    recommended = [result for result in results if result.recommended]
    top_results = results[:3]
    tracks = ", ".join(track.name for track in profile.role_tracks)

    lines = [
        "# Candidate Match Snapshot",
        "",
        f"**Candidate:** {profile.name}",
        f"**Headline:** {profile.headline}",
        f"**Madrid Focus:** {', '.join(profile.preferred_locations)}",
        f"**Tracks Covered:** {tracks}",
        "",
        "## Why This Project Exists",
        "",
        "This repository demonstrates a personal job-matching workflow that evaluates openings against a multi-track profile rather than a single static resume.",
        "",
        "## Current Snapshot",
        "",
        f"- Total jobs reviewed: {len(results)}",
        f"- Recommended matches: {len(recommended)}",
    ]

    for result in top_results:
        lines.append(
            f"- {result.title} at {result.company}: {result.score}/100, {result.fit_label}, track={result.matched_track}"
        )

    lines.extend(["", "## Core Strengths", ""])
    for strength in profile.core_strengths:
        lines.append(f"- {strength}")

    return "\n".join(lines) + "\n"


def build_dashboard_html(profile: CandidateProfile, results: list[MatchResult], queue: list[ApplicationQueueItem]) -> str:
    track_counts = Counter(result.matched_track for result in results)
    recommended_count = sum(1 for result in results if result.recommended)
    submitted_count = sum(1 for item in queue if item.submitted)

    cards = []
    for result in results:
        reasons = "".join(f"<li>{html.escape(reason)}</li>" for reason in result.reasons[:4])
        blockers = "".join(f"<li>{html.escape(blocker)}</li>" for blocker in result.blockers[:2]) or "<li>None</li>"
        cards.append(
            f"""
            <article class="card">
              <div class="score">{result.score}</div>
              <div class="content">
                <p class="eyebrow">{html.escape(result.matched_track)} • {html.escape(result.fit_label)}</p>
                <h3>{html.escape(result.title)}</h3>
                <p class="company">{html.escape(result.company)} • {html.escape(result.summary)}</p>
                <div class="grid">
                  <section>
                    <h4>Positive signals</h4>
                    <ul>{reasons}</ul>
                  </section>
                  <section>
                    <h4>Blockers</h4>
                    <ul>{blockers}</ul>
                  </section>
                </div>
              </div>
            </article>
            """
        )

    track_pills = "".join(
        f'<span class="pill">{html.escape(track)}: {count}</span>' for track, count in track_counts.items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Madrid Job Match Dashboard</title>
  <style>
    :root {{
      --panel: rgba(255, 252, 247, 0.86);
      --ink: #1f2430;
      --muted: #6a6f7d;
      --accent: #cc5c2b;
      --line: rgba(31, 36, 48, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(204, 92, 43, 0.18), transparent 30%),
        linear-gradient(135deg, #f8f1e7, #efe6d8 42%, #f8f5ee);
    }}
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 40px 20px 64px; }}
    .hero {{
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: 0 18px 40px rgba(70, 43, 21, 0.08);
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(2.2rem, 5vw, 4.4rem); line-height: 0.95; }}
    .lede {{ max-width: 760px; font-size: 1.05rem; color: var(--muted); }}
    .stats, .tracks {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 18px; }}
    .stat, .pill {{
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.65);
      font-size: 0.95rem;
    }}
    .cards {{ display: grid; gap: 18px; margin-top: 28px; }}
    .card {{
      display: grid;
      grid-template-columns: 92px 1fr;
      gap: 18px;
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: rgba(255,255,255,0.78);
    }}
    .score {{
      width: 92px;
      height: 92px;
      border-radius: 24px;
      display: grid;
      place-items: center;
      background: linear-gradient(145deg, var(--accent), #8c3e1c);
      color: white;
      font-size: 2rem;
      font-weight: bold;
    }}
    .eyebrow {{ margin: 0; color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.75rem; }}
    h3 {{ margin: 8px 0 4px; font-size: 1.6rem; }}
    .company {{ margin: 0 0 12px; color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    section {{
      padding: 14px;
      border-radius: 18px;
      background: #fffaf4;
      border: 1px solid rgba(31, 36, 48, 0.08);
    }}
    h4 {{ margin: 0 0 8px; font-size: 0.95rem; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); }}
    @media (max-width: 720px) {{
      .card {{ grid-template-columns: 1fr; }}
      .score {{ width: 72px; height: 72px; border-radius: 18px; }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <p class="eyebrow">Personal Job-Matching Agent</p>
      <h1>{html.escape(profile.name)}</h1>
      <p class="lede">{html.escape(profile.headline)} Focused on Madrid opportunities across data, design, frontend, backend, and IT-adjacent roles.</p>
      <div class="stats">
        <span class="stat">{len(results)} jobs scored</span>
        <span class="stat">{recommended_count} recommended</span>
        <span class="stat">{submitted_count} submitted</span>
        <span class="stat">{html.escape(profile.location)}</span>
      </div>
      <div class="tracks">{track_pills}</div>
    </section>
    <section class="cards">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>
"""
