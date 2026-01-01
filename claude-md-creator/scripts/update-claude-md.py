#!/usr/bin/env python3
"""
CLAUDE.md Updater

Updates existing CLAUDE.md files with new project data while preserving custom content.

Usage:
    python update-claude-md.py <path>
    python update-claude-md.py <path> --refresh-project
"""

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"


def parse_sections(content):
    """Parse content into sections by heading."""
    lines = content.split("\n")
    sections = {}
    current_section = "header"
    current_content = []
    
    for line in lines:
        if line.strip().startswith("##"):
            # Save previous section
            sections[current_section] = "\n".join(current_content)
            
            # Start new section
            current_section = line.strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    sections[current_section] = "\n".join(current_content)
    
    return sections


def update_common_commands_section(section_content, project_data):
    """Update Common Commands section with new project data."""
    new_commands = []
    
    # Add detected commands
    if project_data.get("test_command"):
        new_commands.append(f"# Testing\n{project_data['test_command']}")
    
    if project_data.get("dev_command"):
        new_commands.append(f"# Development\n{project_data['dev_command']}")
    
    if project_data.get("build_command"):
        new_commands.append(f"# Building\n{project_data['build_command']}")
    
    # Preserve existing custom commands
    existing_lines = section_content.split("\n")
    custom_commands = []
    skip_standard = ["test", "dev", "build", "install", "lint"]
    
    for line in existing_lines:
        is_standard = False
        for cmd in skip_standard:
            if cmd in line.lower():
                is_standard = True
                break
        if not is_standard and line.strip() and not line.strip().startswith("#"):
            custom_commands.append(line)
    
    if custom_commands:
        new_commands.append("\n# Custom Commands")
        new_commands.extend(custom_commands)
    
    return "\n".join(new_commands)


def update_claude_md(file_path, refresh_project=False):
    """Update existing CLAUDE.md file."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return 1
    
    # Detect project data
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "detect-project.py"), "--json"],
        capture_output=True, text=True
    )
    
    project_data = {}
    if result.returncode == 0:
        project_data = json.loads(result.stdout)
    
    content = path.read_text()
    sections = parse_sections(content)
    
    # Check what to update
    updates_made = []
    
    # Update Common Commands section
    for section_name, section_content in sections.items():
        if "Common Commands" in section_name or "Quick Commands" in section_name:
            updated = update_common_commands_section(section_content, project_data)
            if updated != section_content:
                sections[section_name] = updated
                updates_made.append("Common Commands")
    
    # Add detected dev port if missing
    if project_data.get("dev_port") and "dev_port" not in content.lower():
        # Add to relevant section
        for section_name in sections:
            if "Development" in section_name or "Config" in section_name:
                sections[section_name] += f"\n- Dev Port: {project_data['dev_port']}"
                updates_made.append("Dev port")
                break
    
    if not updates_made:
        print("✅ No updates needed - file is current")
        return 0
    
    # Reconstruct file
    updated_content = "\n".join(sections.values())
    
    # Create backup
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = Path(str(path) + f".backup_{timestamp}")
    path.rename(backup)
    
    # Write updated content
    path.write_text(updated_content)
    
    print(f"✅ Updated {file_path}")
    print(f"   Updates: {', '.join(updates_made)}")
    print(f"   Backup: {backup}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Update existing CLAUDE.md")
    parser.add_argument("file", help="Path to CLAUDE.md file")
    parser.add_argument("--refresh-project", action="store_true",
                       help="Re-detect all project data")
    args = parser.parse_args()
    
    return update_claude_md(args.file, args.refresh_project)


if __name__ == "__main__":
    sys.exit(main())
