#!/usr/bin/env python3
"""
CLAUDE.md Auto-Fixer

Automatically fixes common CLAUDE.md issues.

Usage:
    python auto-fix-claude-md.py <path>
    python auto-fix-claude-md.py <path> --dry-run
    python auto-fix-claude-md.py <path> --category structure
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def create_backup(file_path):
    """Create backup with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(str(file_path) + f".backup_{timestamp}")
    shutil.copy2(file_path, backup_path)
    return backup_path


def fix_frontmatter(content, detected_type):
    """Add missing frontmatter."""
    if content.startswith("---"):
        return content, False  # Already has frontmatter
    
    frontmatter = f"""---
name: {detected_type}
description: CLAUDE.md for {detected_type} configuration
---

"""
    
    return frontmatter + content, True


def fix_empty_sections(content):
    """Remove empty sections (headers with no content)."""
    lines = content.split("\n")
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # Check if this is a section header
        if line.strip().startswith("##"):
            # Look ahead to see if section is empty
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            
            # If next non-empty line is another header, this section is empty
            if j < len(lines) and lines[j].strip().startswith("##"):
                # Skip the empty section (don't add it to fixed_lines)
                fixed_lines.pop()
                i = j - 1  # Will increment to j
        
        i += 1
    
    return "\n".join(fixed_lines), True


def fix_blank_lines(content):
    """Collapse multiple blank lines to single."""
    # Replace 3+ newlines with double newline
    fixed = re.sub(r'\n\n\n+', '\n\n', content)
    return fixed, fixed != content


def fix_tables(content):
    """Convert pipe-separated lists to tables."""
    lines = content.split("\n")
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detect list items with pipe separators that look like tables
        if re.match(r'^\s*-\s*\|.+?\|\s*$', line):
            # Convert to table row
            table_row = " " + line.lstrip().lstrip("-").strip()
            fixed_lines.append(table_row)
            
            # Check if previous line was also a table row
            if i > 0 and fixed_lines and "|" in fixed_lines[-1]:
                # We might need a separator row
                prev = fixed_lines[-2] if len(fixed_lines) > 1 else ""
                if prev and not re.match(r'^\s*\|[\s\-:]+\|\s*$', prev):
                    # Count columns and insert separator
                    cols = fixed_lines[-1].count("|") - 1
                    separator = "|" + "---|" * cols
                    fixed_lines.insert(-1, separator)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return "\n".join(fixed_lines), True


def normalize_headings(content):
    """Normalize heading levels (ensure H2 for main sections)."""
    lines = content.split("\n")
    fixed_lines = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            fixed_lines.append(line)
        elif in_code_block:
            fixed_lines.append(line)
        elif line.strip().startswith("####"):
            # Convert H4+ to H3
            fixed_lines.append(re.sub(r'^#+\s*', '### ', line))
        elif line.strip().startswith("# ") and not line.strip().startswith("##"):
            # Convert H1 to H2
            fixed_lines.append(re.sub(r'^#\s', '## ', line))
        else:
            fixed_lines.append(line)
    
    return "\n".join(fixed_lines), True


def apply_fixes(file_path, category=None, dry_run=False):
    """Apply auto-fixes to file."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return 1
    
    content = path.read_text()
    original = content
    fixes_applied = []
    
    # Detect type from path
    if ".claude/rules" in str(path):
        detected_type = "rules"
    elif path.name == "CLAUDE.local.md":
        detected_type = "local"
    elif path.parent == Path.home() / ".claude":
        detected_type = "global"
    else:
        detected_type = "project"
    
    # Apply fixes based on category
    if category in [None, "frontmatter"]:
        content, was_fixed = fix_frontmatter(content, detected_type)
        if was_fixed:
            fixes_applied.append("Added frontmatter")
    
    if category in [None, "structure"]:
        content, was_fixed = fix_empty_sections(content)
        if was_fixed:
            fixes_applied.append("Removed empty sections")
        
        content, was_fixed = normalize_headings(content)
        if was_fixed:
            fixes_applied.append("Normalized heading levels")
    
    if category in [None, "formatting"]:
        content, was_fixed = fix_blank_lines(content)
        if was_fixed:
            fixes_applied.append("Collapsed blank lines")
        
        content, was_fixed = fix_tables(content)
        if was_fixed:
            fixes_applied.append("Converted lists to tables")
    
    if content == original:
        print("✅ No fixes needed")
        return 0
    
    # Report what would change
    print(f"Fixes to apply: {len(fixes_applied)}")
    for fix in fixes_applied:
        print(f"  - {fix}")
    
    if dry_run:
        print("\n🔍 Dry run mode - no changes made")
        print(f"\nWould change {len(original)} lines to {len(content.split(chr(10)))} lines")
        return 0
    
    # Create backup and write
    backup = create_backup(path)
    path.write_text(content)
    print(f"\n✅ Fixed {file_path}")
    print(f"   Backup: {backup}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Auto-fix CLAUDE.md issues")
    parser.add_argument("file", help="Path to CLAUDE.md file")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--category", choices=["frontmatter", "structure", "formatting"],
                       help="Only fix specific category")
    args = parser.parse_args()
    
    return apply_fixes(args.file, args.category, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
