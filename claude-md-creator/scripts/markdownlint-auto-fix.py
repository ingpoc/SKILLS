#!/usr/bin/env python3
"""Markdownlint Auto-Fixer - Run after any .md file edit/create"""

import re
import sys
from pathlib import Path

def fix_markdownlint(content):
    """Apply all markdownlint fixes."""
    fixes = []

    # MD022: Blanks around headings
    def fix_headings(c):
        lines = c.split("\n")
        fixed = []
        in_code = False
        for i, line in enumerate(lines):
            if "```" in line:
                in_code = not in_code
                fixed.append(line)
                continue
            # Check if this is a heading
            is_heading = not in_code and re.match(r'^##+\s', line)
            # Add blank before heading if needed
            if is_heading and fixed and fixed[-1].strip():
                fixed.append("")
            fixed.append(line)
            # Add blank after heading if needed and next line exists
            if is_heading and i + 1 < len(lines) and lines[i + 1].strip():
                fixed.append("")
        return "\n".join(fixed)

    # MD031: Blanks around fences  
    def fix_fences(c):
        lines = c.split("\n")
        fixed = []
        for i, line in enumerate(lines):
            # Add blank before opening fence
            if line.strip().startswith("```") and fixed and fixed[-1].strip():
                # Only if not already blank or another fence
                if not fixed[-1].strip().startswith("```"):
                    fixed.append("")
            fixed.append(line)
            # Add blank after closing fence
            if line.strip().startswith("```") and i + 1 < len(lines) and lines[i + 1].strip():
                # Only if this is closing fence (next line is not fence)
                if not lines[i + 1].strip().startswith("```"):
                    fixed.append("")
        return "\n".join(fixed)

    # MD040: Fenced code language
    def fix_language(c):
        lines = c.split("\n")
        fixed = []
        fence_count = 0
        for i, line in enumerate(lines):
            if re.match(r'^\s*```\s*$', line):
                fence_count += 1
                # Opening fence (odd count) if next line exists and has content
                if fence_count % 2 == 1 and i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith("```"):
                    fixed.append(re.sub(r'^(\s*)```(\s*)$', r'\1```text\2', line))
                else:
                    fixed.append(line)
            else:
                fixed.append(line)
        return "\n".join(fixed)

    # MD060: Table spacing
    def fix_tables(c):
        lines = c.split("\n")
        fixed = []
        for line in lines:
            if "|" in line and not line.strip().startswith("#"):
                line = re.sub(r'\|(\S)', r'| \1', line)
                line = re.sub(r'(\S)\|', r'\1 |', line)
                line = re.sub(r'\|-+\|', '| --- |', line)
            fixed.append(line)
        return "\n".join(fixed)

    # Apply in order
    for name, func in [("MD060", fix_tables), ("MD040", fix_language), ("MD022", fix_headings), ("MD031", fix_fences)]:
        before = content
        content = func(content)
        if content != before:
            fixes.append(name)
    
    return content, fixes

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)
    
    file_path = Path(sys.argv[1])
    if file_path.suffix != ".md" or not file_path.exists():
        sys.exit(0)
    
    content = file_path.read_text()
    fixed, applied = fix_markdownlint(content)
    
    if applied:
        file_path.write_text(fixed)
        print(f"🔧 markdownlint-auto-fix: {file_path.name} ({', '.join(applied)})", file=sys.stderr)
    
    sys.exit(0)
