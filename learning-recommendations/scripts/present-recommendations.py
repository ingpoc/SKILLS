#!/usr/bin/env python3
"""
Present pending learning recommendations to user.

Outputs formatted text for Claude to use with AskUserQuestion.
"""

import json
import sys
from pathlib import Path


def load_recommendations(store_dir: Path) -> list:
    """Load all pending recommendations."""
    recommendations = []
    rec_files = []

    for rec_file in sorted(store_dir.glob('recommendations_*.json')):
        try:
            data = json.loads(rec_file.read_text())
            recs = data.get('recommendations', [])
            recommendations.extend(recs)
            rec_files.append(rec_file)
        except Exception as e:
            print(f"⚠️  Error reading {rec_file}: {e}", file=sys.stderr)

    return recommendations, rec_files


def format_for_ask_user(recommendations: list) -> str:
    """
    Format recommendations for use with AskUserQuestion.

    Returns Python code that constructs AskUserQuestion calls.
    """
    if not recommendations:
        return "# No pending recommendations"

    lines = [
        "# Learning Recommendations",
        "# Use AskUserQuestion with these questions:",
        ""
    ]

    for i, rec in enumerate(recommendations[:5], 1):  # Max 5 at a time
        lines.extend([
            f"# Recommendation {i}: {rec['title']}",
            "AskUserQuestion(",
            '    questions=[{',
            f'        "question": """{rec["description"]}""",',
            f'        "header": "{rec["title"]}",',
            '        "options": [',
        ])

        for opt in rec['actions']:
            lines.extend([
                '            {',
                f'                "label": "{opt["label"]}",',
                f'                "description": "{opt.get("description", "")}"',
                '            },'
            ])

        lines.extend([
            '        ],',
            '        "multiSelect": false',
            '    }]',
            ')',
            ''
        ])

    return '\n'.join(lines)


def main():
    store_dir = Path.home() / '.claude' / 'learning-recommendations'

    recommendations, rec_files = load_recommendations(store_dir)

    if not recommendations:
        print("ℹ️  No pending recommendations")
        sys.exit(0)

    print(f"📊 Found {len(recommendations)} recommendation(s) from {len(rec_files)} file(s)", file=sys.stderr)

    # Output formatted for AskUserQuestion
    print(format_for_ask_user(recommendations))


if __name__ == '__main__':
    main()
