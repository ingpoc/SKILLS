#!/usr/bin/env python3
"""
Project Type Detection

Scans for project markers (package.json, requirements.txt, etc.) to determine
language, framework, and extract common commands.

Usage:
    python detect-project.py [--json] [--path <dir>]
"""

import json
import sys
from pathlib import Path


PROJECT_MARKERS = {
    "package.json": {"language": "TypeScript/JavaScript", "package_manager": "npm"},
    "requirements.txt": {"language": "Python", "package_manager": "pip"},
    "pyproject.toml": {"language": "Python", "package_manager": "uv/pip"},
    "Cargo.toml": {"language": "Rust", "package_manager": "cargo"},
    "go.mod": {"language": "Go", "package_manager": "go"},
    "Gemfile": {"language": "Ruby", "package_manager": "bundle"},
    "pom.xml": {"language": "Java", "package_manager": "maven"},
    "build.gradle": {"language": "Java/Kotlin", "package_manager": "gradle"},
    "composer.json": {"language": "PHP", "package_manager": "composer"},
}


def detect_project(path=None):
    """Detect project type and extract metadata."""
    cwd = Path(path or Path.cwd())

    result = {
        "name": cwd.name,
        "path": str(cwd),
        "language": None,
        "framework": None,
        "package_manager": None,
        "test_command": None,
        "dev_command": None,
        "dev_port": None,
        "entry_points": [],
        "markers_found": []
    }

    # Check for project markers
    for marker, info in PROJECT_MARKERS.items():
        marker_path = cwd / marker
        if marker_path.exists():
            result["markers_found"].append(marker)
            if not result["language"]:
                result["language"] = info["language"]
                result["package_manager"] = info["package_manager"]

            # Extract metadata from specific files
            if marker == "package.json":
                extract_from_package_json(marker_path, result)
            elif marker == "requirements.txt":
                extract_from_requirements_txt(marker_path, result)

    return result


def extract_from_package_json(package_json, result):
    """Extract commands and framework from package.json."""
    try:
        import json
        data = json.loads(package_json.read_text())

        # Detect framework from dependencies
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

        if "next" in deps:
            result["framework"] = "Next.js"
        elif "vite" in deps and "react" in deps:
            result["framework"] = "Vite React"
        elif "react" in deps:
            result["framework"] = "React"
        elif "vue" in deps:
            result["framework"] = "Vue"

        # Extract commands
        scripts = data.get("scripts", {})
        if "test" in scripts:
            result["test_command"] = f"npm run test"
        if "dev" in scripts:
            result["dev_command"] = f"npm run dev"
        if "build" in scripts:
            result["build_command"] = f"npm run build"

    except Exception:
        pass


def extract_from_requirements_txt(requirements, result):
    """Extract framework from requirements.txt."""
    try:
        content = requirements.read_text().lower()

        if "fastapi" in content or "starlette" in content:
            result["framework"] = "FastAPI"
        elif "django" in content:
            result["framework"] = "Django"
        elif "flask" in content:
            result["framework"] = "Flask"

        result["test_command"] = "pytest"
    except Exception:
        pass


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Detect project type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--path", help="Directory to check")
    args = parser.parse_args()

    result = detect_project(args.path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Project: {result['name']}")
        print(f"Language: {result['language'] or 'Unknown'}")
        print(f"Framework: {result['framework'] or 'None'}")
        print(f"Package Manager: {result['package_manager'] or 'None'}")
        print(f"Markers: {', '.join(result['markers_found']) or 'None'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
