#!/usr/bin/env python3
"""
CLAUDE.md Validator

Validates CLAUDE.md structure and best practices.

Usage:
    python validate-claude-md.py <path>
    python validate-claude-md.py <path> --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Validation rules by type
LINE_COUNT_TARGETS = {
    "global": (50, 150),
    "project": (100, 300),
    "local": (0, 50),
    "rules": (20, 100),
}

REQUIRED_SECTIONS = {
    "global": [],
    "project": [],
    "local": [],
    "rules": ["## Purpose"],
}


class ValidationIssue:
    def __init__(self, category, level, message, location=None):
        self.category = category
        self.level = level  # "error" or "warning"
        self.message = message
        self.location = location

    def to_dict(self):
        return {
            "category": self.category,
            "level": self.level,
            "message": self.message,
            "location": self.location
        }


def validate_frontmatter(content, issues):
    """Validate YAML frontmatter."""
    lines = content.split("\n")
    
    # Check for YAML fence
    if not content.startswith("---"):
        issues.append(ValidationIssue(
            "frontmatter", "error",
            "Missing opening YAML fence (---)",
            "line 1"
        ))
        return False
    
    # Find closing fence
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break
    
    if frontmatter_end == -1:
        issues.append(ValidationIssue(
            "frontmatter", "error",
            "Missing closing YAML fence (---)",
            "frontmatter"
        ))
        return False
    
    # Extract frontmatter content
    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter = "\n".join(frontmatter_lines)
    
    # Check for required fields (for SKILL.md style)
    if "name:" not in frontmatter:
        issues.append(ValidationIssue(
            "frontmatter", "warning",
            "Missing 'name' field in frontmatter",
            "frontmatter"
        ))
    
    if "description:" not in frontmatter:
        issues.append(ValidationIssue(
            "frontmatter", "warning",
            "Missing 'description' field in frontmatter",
            "frontmatter"
        ))
    
    # Check for angle brackets (security risk)
    if "<" in frontmatter or ">" in frontmatter:
        issues.append(ValidationIssue(
            "frontmatter", "warning",
            "Angle brackets detected in frontmatter (use &lt; or &gt; instead)",
            "frontmatter"
        ))
    
    return True


def validate_structure(content, claude_type, issues):
    """Validate document structure."""
    lines = content.split("\n")
    
    # Count headings
    headings = [i for i, line in enumerate(lines) if line.startswith("##")]
    
    if not headings:
        issues.append(ValidationIssue(
            "structure", "warning",
            "No section headings (##) found",
            "entire file"
        ))
    
    # Check for required sections based on type
    required = REQUIRED_SECTIONS.get(claude_type, [])
    for section in required:
        if section not in content:
            issues.append(ValidationIssue(
                "structure", "warning",
                f"Missing required section: {section}",
                "sections"
            ))


def validate_best_practices(content, claude_type, issues):
    """Validate best practices."""
    lines = content.split("\n")
    line_count = len(lines)
    
    # Check line count
    min_lines, max_lines = LINE_COUNT_TARGETS.get(claude_type, (0, 500))
    
    if line_count > max_lines:
        issues.append(ValidationIssue(
            "best_practices", "warning",
            f"Line count: {line_count} (target: {min_lines}-{max_lines}). Consider using references/ for detailed content.",
            "entire file"
        ))
    
    # Check for tables vs lists
    # Look for bullet lists that could be tables
    bullet_sections = []
    current_section = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        elif in_code_block:
            continue
        elif line.strip().startswith("- ") and "|" in line:
            current_section.append(line)
        elif current_section:
            if len(current_section) >= 3:
                bullet_sections.append(current_section)
            current_section = []
    
    if bullet_sections:
        issues.append(ValidationIssue(
            "best_practices", "info",
            f"Found {len(bullet_sections)} sections with bullet lists containing pipes - consider using Markdown tables instead",
            "formatting"
        ))


def validate_content(content, issues):
    """Validate content (paths, commands)."""
    lines = content.split("\n")
    
    # Check for referenced paths
    path_refs = re.findall(r'`[^`]*?/([^`]+?)`', content)
    for path_ref in path_refs:
        # Skip common non-file paths
        if any(x in path_ref for x in ["npm run", "pip install", "cargo", "go run", "pytest", "npm test"]):
            continue
        
        # Check if path exists
        test_path = Path(path_ref.split()[0])  # Take first part before any space
        if not test_path.exists():
            issues.append(ValidationIssue(
                "content", "info",
                f"Referenced path does not exist: {path_ref}",
                "references"
            ))


def detect_claude_type_from_content(content, file_path):
    """Detect CLAUDE.md type from content and path."""
    path = Path(file_path)
    
    # Check path
    if path == Path.home() / ".claude" / "CLAUDE.md":
        return "global"
    elif ".claude/rules" in str(path):
        return "rules"
    elif path.name == "CLAUDE.local.md":
        return "local"
    else:
        return "project"


def validate_file(file_path, json_output=False):
    """Validate a CLAUDE.md file."""
    path = Path(file_path)
    
    if not path.exists():
        result = {
            "valid": False,
            "errors": 1,
            "warnings": 0,
            "info": 0,
            "issues": [{
                "category": "file",
                "level": "error",
                "message": f"File not found: {file_path}",
                "location": "filesystem"
            }]
        }
        if json_output:
            print(json.dumps(result, indent=2))
        return 2
    
    content = path.read_text()
    issues = []
    
    # Detect type
    claude_type = detect_claude_type_from_content(content, path)
    
    # Run validations
    validate_frontmatter(content, issues)
    validate_structure(content, claude_type, issues)
    validate_best_practices(content, claude_type, issues)
    validate_content(content, issues)
    
    # Count by level
    errors = sum(1 for i in issues if i.level == "error")
    warnings = sum(1 for i in issues if i.level == "warning")
    infos = sum(1 for i in issues if i.level == "info")
    
    result = {
        "valid": errors == 0,
        "type": claude_type,
        "errors": errors,
        "warnings": warnings,
        "info": infos,
        "issues": [i.to_dict() for i in issues]
    }
    
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        if errors == 0 and warnings == 0:
            print(f"✅ Valid {claude_type} CLAUDE.md")
        else:
            print(f"{'❌' if errors > 0 else '⚠️  '} {claude_type} CLAUDE.md validation")
            print(f"   Errors: {errors}, Warnings: {warnings}, Info: {infos}")
            print()
            
            # Group by level
            for level in ["error", "warning", "info"]:
                level_issues = [i for i in issues if i.level == level]
                if not level_issues:
                    continue
                
                icon = {"error": "❌", "warning": "⚠️ ", "info": "ℹ️  "}[level]
                print(f"{icon} {level.capitalize()}s:")
                for issue in level_issues:
                    print(f"   - {issue.message}")
                    if issue.location:
                        print(f"     Location: {issue.location}")
    
    return 0 if errors == 0 else (2 if errors > 0 else 1)


def main():
    parser = argparse.ArgumentParser(description="Validate CLAUDE.md structure")
    parser.add_argument("file", help="Path to CLAUDE.md file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    return validate_file(args.file, args.json)


if __name__ == "__main__":
    sys.exit(main())
