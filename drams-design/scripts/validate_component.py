#!/usr/bin/env python3
"""
Validate component against Dieter Rams' 10 principles.

Usage:
  python3 validate_component.py path/to/component.tsx
"""

import sys
import re
from pathlib import Path

# Rams' principles with validation patterns
PRINCIPLES = {
    "Useful": {
        "patterns": [
            r"(aria-label|label|htmlFor)",  # Clear labels
            r"placeholder=",  # Helpful placeholders
        ],
        "anti_patterns": [
            r"className.*animate-pulse.*(?!loading)",  # Decorative animation
        ],
        "description": "Solves real problem, clear purpose"
    },
    "Understandable": {
        "patterns": [
            r"(aria-label|aria-describedby)",  # Screen reader support
            r"htmlFor=\w",  # Label association
        ],
        "anti_patterns": [
            r"<button[^>]*>\s*<[A-Z]",  # Icon-only without aria-label
        ],
        "description": "Self-explanatory, intuitive"
    },
    "Aesthetic": {
        "patterns": [
            r"(slate|gray|zinc)-",  # Neutral palette
            r"(space-y|gap|p-\d|m-\d)",  # Generous spacing
        ],
        "anti_patterns": [
            r"(pink|purple|gradient|animate-bounce)",  # Trendy/vibrant
        ],
        "description": "Minimal, timeless"
    },
    "Unobtrusive": {
        "patterns": [
            r"hover:(scale-\d|opacity-)",  # Subtle hover
            r"transition-(all|colors|duration)",  # Smooth transitions
        ],
        "anti_patterns": [
            r"(animate-bounce|animate-shake|shake)",  # Jarring animations
        ],
        "description": "Doesn't compete with content"
    },
    "Honest": {
        "patterns": [
            r"(isLoading|loading|error|disabled)",  # Real states
            r"aria-invalid",  # Validation state
            r"aria-busy",  # Loading state
        ],
        "anti_patterns": [
            r"setTimeout.*loading",  # Fake loading delays
        ],
        "description": "Accurate states, no deception"
    },
    "Thorough": {
        "patterns": [
            r"\{isLoading.*\{.*error",  # Handle loading/error
            r"disabled.*\{",  # Handle disabled state
            r"\{isEmpty",  # Handle empty state
        ],
        "anti_patterns": [
            r"className.*bg-slate-900.*(?!error|loading|disabled)",  # Only happy path
        ],
        "description": "Edge cases handled"
    },
    "Environmentally friendly": {
        "patterns": [
            r'from ["\']@/components',  # Local imports
            r'from ["\']framer-motion["\']',  # Tree-shakeable
        ],
        "anti_patterns": [
            r'from ["\']huge-lib["\']',  # Heavy dependencies
        ],
        "description": "Lightweight, tree-shakeable"
    },
    "Little design": {
        "patterns": [],
        "anti_patterns": [
            r"variant.*(size|color|shadow|border).*\{",  # Over-configurable
        ],
        "description": "Essential only"
    }
}


def validate_component(content: str, filepath: str) -> dict:
    """Validate component against Rams' principles."""
    results = {
        "file": filepath,
        "principles": {},
        "score": 0,
        "max_score": len(PRINCIPLES),
        "issues": [],
        "passes": []
    }

    for principle, rules in PRINCIPLES.items():
        passed = False
        principle_issues = []
        principle_passes = []

        # Check for positive patterns
        for pattern in rules["patterns"]:
            if re.search(pattern, content):
                principle_passes.append(f"✓ Found: {pattern}")
                passed = True

        # Check for anti-patterns
        for anti_pattern in rules["anti_patterns"]:
            if re.search(anti_pattern, content):
                principle_issues.append(f"✗ Avoid: {anti_pattern}")
                passed = False

        results["principles"][principle] = {
            "passed": passed,
            "description": rules["description"],
            "issues": principle_issues,
            "passes": principle_passes
        }

        if passed:
            results["score"] += 1
            results["passes"].append(principle)
        else:
            results["issues"].append(principle)

    return results


def print_results(results: dict):
    """Print validation results."""
    print(f"\n{'='*60}")
    print(f"Validating: {results['file']}")
    print(f"{'='*60}")

    print(f"\nScore: {results['score']}/{results['max_score']}")

    if results["passes"]:
        print(f"\n✓ Passed ({len(results['passes'])}):")
        for principle in results["passes"]:
            print(f"  • {principle}: {results['principles'][principle]['description']}")
            for pass_msg in results['principles'][principle]['passes']:
                print(f"    {pass_msg}")

    if results["issues"]:
        print(f"\n✗ Failed ({len(results['issues'])}):")
        for principle in results["issues"]:
            print(f"  • {principle}: {results['principles'][principle]['description']}")
            for issue in results['principles'][principle]['issues']:
                print(f"    {issue}")

    # Overall assessment
    print(f"\n{'='*60}")
    if results["score"] >= results["max_score"] * 0.7:
        print("✓ Component follows Rams' principles")
        return 0
    else:
        print("✗ Component needs improvement")
        return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_component.py <component.tsx>")
        sys.exit(1)

    filepath = sys.argv[1]
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    content = path.read_text()
    results = validate_component(content, filepath)
    exit_code = print_results(results)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
