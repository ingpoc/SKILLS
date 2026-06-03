#!/usr/bin/env python3
"""Render LLM Council artifacts from a structured JSON payload.

Input JSON shape:
{
  "question": "...",
  "framed_question": "...",
  "chairman_verdict": {
    "where_agrees": "...",
    "where_clashes": "...",
    "blind_spots": "...",
    "recommendation": "...",
    "first_step": "..."
  },
  "advisors": [
    {"name": "The Contrarian", "stance": "...", "response": "..."}
  ],
  "peer_reviews": [
    {"reviewer": "Review 1", "text": "..."}
  ],
  "anonymization_mapping": {
    "A": "The Contrarian"
  }
}
"""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any


SECTION_TITLES = [
    ("where_agrees", "Where the Council Agrees"),
    ("where_clashes", "Where the Council Clashes"),
    ("blind_spots", "Blind Spots the Council Caught"),
    ("recommendation", "The Recommendation"),
    ("first_step", "The One Thing to Do First"),
]


def render_rich_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    parts: list[str] = []
    bullets: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            joined = " ".join(chunk.strip() for chunk in paragraph if chunk.strip())
            parts.append(f"<p>{html.escape(joined)}</p>")
            paragraph.clear()

    def flush_bullets() -> None:
        if bullets:
            items = "".join(f"<li>{html.escape(item)}</li>" for item in bullets)
            parts.append(f"<ul>{items}</ul>")
            bullets.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_bullets()
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            bullets.append(stripped[2:].strip())
            continue
        flush_bullets()
        paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()
    return "".join(parts) or "<p></p>"


def build_html(payload: dict[str, Any], timestamp: str, generated_at: str) -> str:
    question = html.escape(payload["question"])
    framed_question = render_rich_text(payload["framed_question"])
    verdict = payload["chairman_verdict"]
    advisors = payload["advisors"]
    peer_reviews = payload["peer_reviews"]

    alignment_cards = "".join(
        f"""
        <article class="card advisor-card">
          <div class="eyebrow">{html.escape(advisor['name'])}</div>
          <p>{html.escape(advisor.get('stance') or 'No stance summary provided.')}</p>
        </article>
        """
        for advisor in advisors
    )

    verdict_sections = "".join(
        f"""
        <section class="verdict-block">
          <h3>{html.escape(title)}</h3>
          {render_rich_text(verdict[key])}
        </section>
        """
        for key, title in SECTION_TITLES
    )

    advisor_details = "".join(
        f"""
        <details class="detail card">
          <summary>{html.escape(advisor['name'])}</summary>
          <div class="detail-meta">{html.escape(advisor.get('stance') or '')}</div>
          {render_rich_text(advisor['response'])}
        </details>
        """
        for advisor in advisors
    )

    peer_review_details = "".join(
        f"""
        <details class="detail card">
          <summary>{html.escape(review.get('reviewer') or 'Peer Review')}</summary>
          {render_rich_text(review['text'])}
        </details>
        """
        for review in peer_reviews
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LLM Council Report</title>
  <style>
    :root {{
      --bg: #f6f7f4;
      --panel: #ffffff;
      --ink: #161616;
      --muted: #5d645f;
      --line: #d7ddd6;
      --accent: #0f766e;
      --accent-soft: #d8f1ed;
      --shadow: 0 12px 30px rgba(16, 24, 40, 0.08);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.55;
    }}
    main {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 40px 20px 64px;
    }}
    h1, h2, h3, p {{
      margin-top: 0;
    }}
    h1 {{
      font-size: clamp(2rem, 4vw, 3rem);
      letter-spacing: -0.03em;
      margin-bottom: 12px;
    }}
    h2 {{
      font-size: 1.2rem;
      margin-bottom: 16px;
    }}
    .hero {{
      margin-bottom: 28px;
    }}
    .hero p {{
      max-width: 760px;
      color: var(--muted);
      font-size: 1.02rem;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      box-shadow: var(--shadow);
    }}
    .question {{
      padding: 24px;
      margin-bottom: 24px;
    }}
    .question blockquote {{
      margin: 0;
      padding-left: 18px;
      border-left: 3px solid var(--accent);
      color: var(--ink);
      font-size: 1.05rem;
    }}
    .verdict {{
      padding: 28px;
      margin-bottom: 24px;
      border-top: 6px solid var(--accent);
    }}
    .verdict-grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}
    .verdict-block {{
      background: linear-gradient(180deg, #ffffff 0%, #f8fbfa 100%);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 18px;
    }}
    .verdict-block h3 {{
      font-size: 1rem;
      margin-bottom: 10px;
    }}
    .alignment {{
      margin-bottom: 24px;
    }}
    .alignment-grid {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    }}
    .advisor-card {{
      padding: 16px;
      border-radius: 16px;
      border-color: #c7ddd9;
      background: linear-gradient(180deg, #ffffff 0%, var(--accent-soft) 140%);
    }}
    .eyebrow {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--accent);
      margin-bottom: 8px;
      font-weight: 700;
    }}
    .detail-stack {{
      display: grid;
      gap: 14px;
    }}
    .detail {{
      padding: 0 18px;
      overflow: hidden;
    }}
    summary {{
      cursor: pointer;
      list-style: none;
      padding: 18px 0;
      font-weight: 700;
    }}
    summary::-webkit-details-marker {{
      display: none;
    }}
    .detail[open] summary {{
      border-bottom: 1px solid var(--line);
    }}
    .detail > *:not(summary) {{
      padding-top: 14px;
      padding-bottom: 18px;
    }}
    .detail-meta {{
      color: var(--muted);
      font-size: 0.92rem;
      margin-bottom: 8px;
    }}
    footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    ul {{
      margin: 0 0 0 1.1rem;
      padding: 0;
    }}
    p:last-child, ul:last-child {{
      margin-bottom: 0;
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="eyebrow">LLM Council</div>
      <h1>Council Report</h1>
      <p>Five independent advisors analyzed the decision, challenged one another anonymously, and a chairman synthesized the final verdict.</p>
    </section>

    <section class="question card">
      <h2>The Question</h2>
      <blockquote>{question}</blockquote>
      <details class="detail">
        <summary>View framed question</summary>
        {framed_question}
      </details>
    </section>

    <section class="verdict card">
      <h2>Chairman&apos;s Verdict</h2>
      <div class="verdict-grid">
        {verdict_sections}
      </div>
    </section>

    <section class="alignment">
      <h2>Agreement and Divergence</h2>
      <div class="alignment-grid">
        {alignment_cards}
      </div>
    </section>

    <section>
      <h2>Advisor Responses</h2>
      <div class="detail-stack">
        {advisor_details}
      </div>
    </section>

    <section>
      <h2>Peer Review Highlights</h2>
      <div class="detail-stack">
        {peer_review_details}
      </div>
    </section>

    <footer>
      Generated {html.escape(generated_at)}. Session timestamp: {html.escape(timestamp)}.
      What was counciled: {question}
    </footer>
  </main>
</body>
</html>
"""


def build_transcript(payload: dict[str, Any], timestamp: str, generated_at: str) -> str:
    verdict = payload["chairman_verdict"]
    advisors = payload["advisors"]
    peer_reviews = payload["peer_reviews"]
    mapping = payload["anonymization_mapping"]

    advisor_sections = "\n\n".join(
        f"## {advisor['name']}\n\n**Stance:** {advisor.get('stance') or 'Not provided'}\n\n{advisor['response']}"
        for advisor in advisors
    )

    peer_review_sections = "\n\n".join(
        f"## {review.get('reviewer') or 'Peer Review'}\n\n{review['text']}"
        for review in peer_reviews
    )

    mapping_lines = "\n".join(
        f"- Response {label}: {name}" for label, name in sorted(mapping.items())
    )

    verdict_sections = "\n\n".join(
        f"## {title}\n\n{verdict[key]}" for key, title in SECTION_TITLES
    )

    return f"""# LLM Council Transcript

Generated: {generated_at}
Timestamp: {timestamp}

## Original Question

{payload['question']}

## Framed Question

{payload['framed_question']}

## Advisor Responses

{advisor_sections}

## Peer Review Mapping

{mapping_lines}

## Peer Reviews

{peer_review_sections}

## Chairman Verdict

{verdict_sections}
"""


def validate_payload(payload: dict[str, Any]) -> None:
    required_top_level = {
        "question",
        "framed_question",
        "chairman_verdict",
        "advisors",
        "peer_reviews",
        "anonymization_mapping",
    }
    missing = sorted(required_top_level - payload.keys())
    if missing:
        raise ValueError(f"Missing payload key(s): {', '.join(missing)}")

    if len(payload["advisors"]) != 5:
        raise ValueError("Payload must include exactly 5 advisors.")
    if len(payload["peer_reviews"]) != 5:
        raise ValueError("Payload must include exactly 5 peer reviews.")

    for key, _ in SECTION_TITLES:
        if key not in payload["chairman_verdict"]:
            raise ValueError(f"Missing chairman_verdict field: {key}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render LLM Council HTML and transcript artifacts.")
    parser.add_argument("--input", required=True, help="Path to input JSON payload")
    parser.add_argument("--output-dir", required=True, help="Directory for generated artifacts")
    parser.add_argument(
        "--timestamp",
        help="Optional timestamp override for filenames (default: current local time as YYYYmmdd-HHMMSS)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(input_path.read_text())
    validate_payload(payload)

    now = datetime.now()
    timestamp = args.timestamp or now.strftime("%Y%m%d-%H%M%S")
    generated_at = now.strftime("%Y-%m-%d %H:%M:%S")

    html_path = output_dir / f"council-report-{timestamp}.html"
    transcript_path = output_dir / f"council-transcript-{timestamp}.md"

    html_path.write_text(build_html(payload, timestamp, generated_at))
    transcript_path.write_text(build_transcript(payload, timestamp, generated_at))

    print(json.dumps({"report": str(html_path), "transcript": str(transcript_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
