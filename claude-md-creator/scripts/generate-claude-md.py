#!/usr/bin/env python3
"""
CLAUDE.md Generator

Creates CLAUDE.md files from templates with project detection.
"""

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def load_template(template_name):
    template_path = ASSETS_DIR / template_name
    if not template_path.exists():
        return None
    return template_path.read_text()


def load_framework_template(framework):
    framework_map = {
        "next.js": "nodejs.md", "react": "nodejs.md", "vite": "nodejs.md",
        "fastapi": "python.md", "django": "python.md", "flask": "python.md",
        "rust": "rust.md", "go": "go.md",
    }
    template_name = framework_map.get(framework.lower(), "general.md")
    return load_template(f"framework-templates/{template_name}")


def detect_project_data():
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "detect-project.py"), "--json"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return {}


def generate_project(output_path=None, project_data=None):
    template = load_template("project.template.md")
    if not template:
        return None
    
    project_data = project_data or detect_project_data()
    framework = project_data.get("framework", "general")
    framework_content = load_framework_template(framework) or ""
    
    content = template.format(
        project_description=project_data.get("name", "Project"),
        dev_command=project_data.get("dev_command", "# dev"),
        test_command=project_data.get("test_command", "# test"),
        build_command=project_data.get("build_command", "# build"),
        entry_point_dir="src/",
        additional_configs="- `.mcp.json` - MCP config",
        language=project_data.get("language", "Unknown"),
        framework=framework,
        package_manager=project_data.get("package_manager", "Unknown"),
    )
    
    if framework_content:
        content += "\n" + framework_content.format(
            python_entry_points="", node_entry_points="", rust_entry_points="",
            go_entry_points="", entry_points="", build_command="",
            test_command="", run_command="", framework_specific_commands="",
            general_notes="",
        )
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content)
        return str(output_path)
    return content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["global", "project", "local", "rules"])
    parser.add_argument("--output", "-o")
    parser.add_argument("--auto", action="store_true")
    args = parser.parse_args()
    
    if args.auto:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "detect-claude-type.py"), "--json"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            detection = json.loads(result.stdout)
            args.type = detection.get("type", "project")
            if not args.output:
                args.output = detection.get("path")
    
    if not args.type:
        parser.print_help()
        return 1
    
    project_data = detect_project_data()
    
    if args.type == "project":
        result = generate_project(args.output, project_data)
    elif args.type == "global":
        template = load_template("global.template.md")
        result = Path(args.output).write_text(template) if args.output else template
    else:
        print(f"Type {args.type} not yet implemented")
        return 1
    
    if result:
        print(f"Generated: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
