#!/usr/bin/env python3
"""Audit a `.codex/skills/<name>/SKILL.md` against agentskills.io spec + local style.

Usage:
    audit.py PATH [PATH ...]   # one or more SKILL.md files or skill dirs
    audit.py --all             # all skills under .codex/skills/
    audit.py --json            # machine-readable
    audit.py --strict          # treat spec-soft warnings as hard

Exit codes:
    0  clean — no hard findings (soft findings still print)
    1  hard findings — skill violates spec or sanity bounds
    2  IO / parse error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# --- limits ---------------------------------------------------------------

NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
DESC_SOFT_MAX = 1024          # agentskills.io specification cap
DESC_HARD_MAX = 8000          # sanity guardrail — beyond this, activation cost dominates
BODY_TOKENS_SOFT_MAX = 5000   # spec recommendation
BODY_TOKENS_HARD_MAX = 15000  # sanity guardrail
CHARS_PER_TOKEN = 4           # rough estimate; tiktoken not assumed present


# --- model ----------------------------------------------------------------

@dataclass
class Finding:
    check: str
    severity: str           # "hard" | "soft"
    status: str             # "pass" | "warn" | "fail"
    message: str


@dataclass
class SkillReport:
    path: str
    name: str = ""
    checks: list[Finding] = field(default_factory=list)
    hard_findings: int = 0
    soft_findings: int = 0


# --- frontmatter parser (no PyYAML dep) -----------------------------------

def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Empty dict if no frontmatter."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw_fm = text[4:end]
    body = text[end + 5:]
    return parse_simple_yaml(raw_fm), body


def parse_simple_yaml(raw: str) -> dict:
    """Tolerant parser for the SKILL.md frontmatter dialect.

    Handles:
      key: scalar
      key: "quoted scalar with : and other stuff"
      key: >        (folded block scalar — joined with spaces)
      key:          (mapping — children indented)
        sub: value
      key:          (sequence — children prefixed with `- `)
        - item

    Not a general YAML parser. Skill frontmatter rarely needs more.
    """
    out: dict = {}
    lines = raw.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if not re.match(r"^[a-zA-Z_-]", line):
            i += 1
            continue
        m = re.match(r"^([A-Za-z][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2).strip()
        if rest == ">" or rest == "|" or rest == ">-" or rest == "|-":
            # folded / literal block scalar
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            joined = " ".join(s.strip() for s in block if s.strip())
            out[key] = joined
            continue
        if rest == "":
            # nested mapping or sequence
            i += 1
            sub_lines: list[str] = []
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                sub_lines.append(lines[i])
                i += 1
            sub_text = "\n".join(s[2:] if s.startswith("  ") else s for s in sub_lines)
            if any(s.lstrip().startswith("- ") for s in sub_lines):
                items = [
                    s.lstrip()[2:].strip().strip('"').strip("'")
                    for s in sub_lines
                    if s.lstrip().startswith("- ")
                ]
                out[key] = items
            else:
                out[key] = parse_simple_yaml(sub_text)
            continue
        # inline scalar
        if (rest.startswith('"') and rest.endswith('"')) or (rest.startswith("'") and rest.endswith("'")):
            rest = rest[1:-1]
        out[key] = rest
        i += 1
    return out


# --- checks ---------------------------------------------------------------

def check_skill(skill_md: Path, strict: bool) -> SkillReport:
    rep = SkillReport(path=str(skill_md))
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as e:
        rep.checks.append(Finding("readable", "hard", "fail", f"cannot read: {e}"))
        rep.hard_findings = 1
        return rep

    fm, body = split_frontmatter(text)

    if not fm:
        rep.checks.append(Finding("frontmatter_present", "hard", "fail",
                                  "no YAML frontmatter found (must start with ---)"))
        rep.hard_findings = 1
        return rep
    rep.checks.append(Finding("frontmatter_present", "hard", "pass", "frontmatter parsed"))

    # name
    name = fm.get("name", "").strip()
    rep.name = name
    if not name:
        rep.checks.append(Finding("name_present", "hard", "fail", "`name:` is required"))
    else:
        rep.checks.append(Finding("name_present", "hard", "pass", name))
        if NAME_RE.match(name):
            rep.checks.append(Finding("name_kebab_case", "hard", "pass",
                                      "kebab-case valid"))
        else:
            rep.checks.append(Finding("name_kebab_case", "hard", "fail",
                                      f"`{name}` violates kebab-case: ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ "
                                      "(no uppercase, no leading/trailing hyphen, no consecutive hyphens)"))
        # name should match dir
        dir_name = skill_md.parent.name
        if name != dir_name:
            rep.checks.append(Finding("name_matches_dir", "soft", "warn",
                                      f"name `{name}` != directory `{dir_name}`"))
        else:
            rep.checks.append(Finding("name_matches_dir", "soft", "pass", "name == dir"))

    # description
    desc = fm.get("description", "")
    if isinstance(desc, list):
        desc = " ".join(desc)
    desc = desc.strip()
    if not desc:
        rep.checks.append(Finding("description_present", "hard", "fail",
                                  "`description:` is required (loaded at discovery)"))
    else:
        rep.checks.append(Finding("description_present", "hard", "pass",
                                  f"{len(desc)} chars"))
        # length
        if len(desc) > DESC_HARD_MAX:
            rep.checks.append(Finding("description_length", "hard", "fail",
                                      f"{len(desc)} chars > sanity max {DESC_HARD_MAX}"))
        elif len(desc) > DESC_SOFT_MAX:
            sev = "hard" if strict else "soft"
            rep.checks.append(Finding("description_length", sev,
                                      "fail" if strict else "warn",
                                      f"{len(desc)} chars > spec limit {DESC_SOFT_MAX} "
                                      "(local style permits — see references/description.md)"))
        else:
            rep.checks.append(Finding("description_length", "soft", "pass",
                                      f"{len(desc)} chars ≤ {DESC_SOFT_MAX}"))
        # heuristic — should contain a "use when" / "triggers" / activation hint
        low = desc.lower()
        has_trigger_phrase = any(
            kw in low for kw in (
                "use when", "use whenever", "triggers", "trigger:", "on invocation",
                "use this skill", "invoke", "fires when", "use as", "activate",
            )
        )
        if has_trigger_phrase:
            rep.checks.append(Finding("description_has_triggers", "soft", "pass",
                                      "trigger phrasing detected"))
        else:
            rep.checks.append(Finding("description_has_triggers", "soft", "warn",
                                      "description has no 'Use when …' / 'Triggers:' phrasing — "
                                      "may activate unreliably. See references/description.md."))

    # allowed-tools shape (optional)
    at = fm.get("allowed-tools")
    if at is not None:
        if isinstance(at, str):
            rep.checks.append(Finding("allowed_tools_shape", "soft", "pass",
                                      f"allowed-tools: {at}"))
        elif isinstance(at, list):
            rep.checks.append(Finding("allowed_tools_shape", "soft", "pass",
                                      f"allowed-tools list[{len(at)}]"))
        else:
            rep.checks.append(Finding("allowed_tools_shape", "soft", "warn",
                                      f"allowed-tools has unusual shape: {type(at).__name__}"))

    # body size
    body_tokens = max(1, len(body) // CHARS_PER_TOKEN)
    if body_tokens > BODY_TOKENS_HARD_MAX:
        rep.checks.append(Finding("body_token_budget", "hard", "fail",
                                  f"~{body_tokens} tokens > sanity max {BODY_TOKENS_HARD_MAX} "
                                  "— move bulk into references/ and link from body"))
    elif body_tokens > BODY_TOKENS_SOFT_MAX:
        sev = "hard" if strict else "soft"
        rep.checks.append(Finding("body_token_budget", sev,
                                  "fail" if strict else "warn",
                                  f"~{body_tokens} tokens > spec recommendation {BODY_TOKENS_SOFT_MAX} "
                                  "— consider splitting into references/"))
    else:
        rep.checks.append(Finding("body_token_budget", "soft", "pass",
                                  f"~{body_tokens} tokens ≤ {BODY_TOKENS_SOFT_MAX}"))

    # progressive disclosure — body should be a router, not a content dump
    rep.checks.append(check_progressive_disclosure(body, body_tokens))

    # self-validate directive — body must instruct the agent to re-validate after edits
    if _SELF_VALIDATE_DIRECTIVE_RE.search(body):
        rep.checks.append(Finding("self_validate_directive", "soft", "pass",
                                  "self-validate directive present"))
    else:
        rep.checks.append(Finding("self_validate_directive", "soft", "warn",
                                  "missing the canonical '> **Self-validate after edits.**' "
                                  "blockquote near the top of the body — agents that modify "
                                  "this skill won't be reminded to run scripts/validate.sh."))

    # referenced files exist
    missing = check_local_refs(body, skill_md.parent)
    if missing:
        rep.checks.append(Finding("referenced_files_exist", "soft", "warn",
                                  f"{len(missing)} missing local ref(s): {', '.join(missing[:5])}"))
    else:
        rep.checks.append(Finding("referenced_files_exist", "soft", "pass",
                                  "all local refs resolve"))

    rep.hard_findings = sum(1 for c in rep.checks if c.severity == "hard" and c.status == "fail")
    rep.soft_findings = sum(1 for c in rep.checks if c.severity == "soft" and c.status == "warn")
    return rep


# Match likely local-file references in skill body. Captures forms like:
#   `references/foo.md`, scripts/bar.py, [text](references/baz.md), ./templates/x
_REF_RE = re.compile(
    r"(?:\(|`|\s|^)((?:\.?/)?(?:references|scripts|templates|assets)/[A-Za-z0-9_./-]+)"
)

# Canonical lane-structure markers in this repo's skill convention.
# REPEATED occurrence of the same marker is the strong signal: each repetition
# represents a separate lane carrying its own procedure inline. Sequential
# "Step 1 / Step 2" headers in a single-flow skill don't trip this — each step
# is a different header, so no marker repeats.
_LANE_MARKERS = ("Preflight", "Do", "Closeout")
_LANE_HEADER_RES = {
    marker: re.compile(rf"^#{{2,4}}\s+{marker}\b", re.MULTILINE | re.IGNORECASE)
    for marker in _LANE_MARKERS
}

_REFERENCES_LINK_RE = re.compile(r"references/[A-Za-z0-9_-]+\.md", re.IGNORECASE)

# Canonical self-validate directive. Every SKILL.md must carry this blockquote
# near the top so the agent — on activation — already has the rule that any
# modification of the skill must be followed by ./scripts/validate.sh.
_SELF_VALIDATE_DIRECTIVE_RE = re.compile(
    r"^>\s+\*\*Self-validate after edits\.\*\*",
    re.MULTILINE,
)


def check_progressive_disclosure(body: str, body_tokens: int) -> Finding:
    """Flag bodies that carry multi-lane procedures inline instead of in references/.

    Always-loaded body should hold ONLY what every activation needs: lane routing,
    universal invariants, pointers. Per-lane Preflight/Do/Closeout content should
    live in references/<lane>.md and load on demand.

    Detection: the canonical lane-structure headers Preflight / Do / Closeout
    each appear at most ONCE in a properly progressive body — repeated occurrence
    means multiple lanes are carrying procedures inline. Sequential "Step 1 / Step 2"
    headers in single-flow skills don't trip this (each step is a unique header).
    """
    counts = {m: len(_LANE_HEADER_RES[m].findall(body)) for m in _LANE_MARKERS}
    max_count = max(counts.values())
    n_ref_links = len(set(_REFERENCES_LINK_RE.findall(body)))

    breakdown = ", ".join(f"{m}={counts[m]}" for m in _LANE_MARKERS)

    if max_count >= 2:
        return Finding(
            "progressive_disclosure", "soft", "warn",
            f"body has {breakdown} — repeated lane markers indicate multiple lanes inline. "
            "Move per-lane Preflight/Do/Closeout to references/<lane>.md; body should "
            "always-load only routing content.",
        )
    # Soft warn: large body even without lane repetition might still hide non-routing bulk.
    if body_tokens > 4000 and n_ref_links == 0:
        return Finding(
            "progressive_disclosure", "soft", "warn",
            f"body is ~{body_tokens} tokens with no references/ links. Even single-flow skills "
            "should split deep procedure into references/ when bulk isn't always needed.",
        )
    return Finding(
        "progressive_disclosure", "soft", "pass",
        f"{breakdown}, references/ links={n_ref_links} — router-shape OK",
    )


def _repo_root_for(skill_dir: Path) -> Path | None:
    """Walk up from skill_dir looking for the repo root (`.claude` parent)."""
    for parent in skill_dir.parents:
        if (parent / ".claude").is_dir() and parent != skill_dir:
            return parent
    return None


def check_local_refs(body: str, skill_dir: Path) -> list[str]:
    """Report refs that don't resolve against either the skill dir OR the repo root.

    SKILL.md bodies legitimately reference both skill-local files (`scripts/foo.py`
    in the skill's own `scripts/`) and repo-root files (`scripts/autoresearch/bar.py`
    living in `<repo>/scripts/autoresearch/`). A ref is only missing when neither
    resolution path finds it.
    """
    candidates = set(_REF_RE.findall(body))
    repo_root = _repo_root_for(skill_dir)
    missing: list[str] = []
    seen: set[str] = set()
    for ref in candidates:
        normalized = ref.lstrip("./").rstrip("/")
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        if (skill_dir / normalized).exists():
            continue
        if repo_root and (repo_root / normalized).exists():
            continue
        missing.append(normalized)
    return sorted(missing)


# --- driver ---------------------------------------------------------------

def resolve_targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        root = Path(args.skills_root)
        return sorted(p for p in root.glob("*/SKILL.md") if p.is_file())
    targets: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            targets.append(path / "SKILL.md")
        elif path.name == "SKILL.md":
            targets.append(path)
        else:
            targets.append(path / "SKILL.md")
    return targets


def render_human(reports: list[SkillReport]) -> str:
    lines = []
    for rep in reports:
        head = f"\n=== {rep.name or rep.path} ==="
        lines.append(head)
        for c in rep.checks:
            mark = {"pass": "✓", "warn": "!", "fail": "✗"}.get(c.status, "?")
            sev = c.severity.upper().ljust(4)
            lines.append(f"  [{sev}] {mark} {c.check}: {c.message}")
        lines.append(f"  → hard={rep.hard_findings}  soft={rep.soft_findings}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true", help="audit every skill under --skills-root")
    ap.add_argument("--skills-root", default=".claude/skills",
                    help="root directory when --all is used (default: .claude/skills)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="treat spec-soft warnings as hard (e.g., description > 1024 chars)")
    args = ap.parse_args(argv)

    targets = resolve_targets(args)
    if not targets:
        print("audit: no SKILL.md targets resolved", file=sys.stderr)
        return 2

    reports: list[SkillReport] = []
    for skill_md in targets:
        if not skill_md.exists():
            rep = SkillReport(path=str(skill_md))
            rep.checks.append(Finding("readable", "hard", "fail", "SKILL.md not found"))
            rep.hard_findings = 1
            reports.append(rep)
            continue
        reports.append(check_skill(skill_md, strict=args.strict))

    if args.json:
        payload = {
            "reports": [
                {
                    "path": r.path,
                    "name": r.name,
                    "hard_findings": r.hard_findings,
                    "soft_findings": r.soft_findings,
                    "checks": [asdict(c) for c in r.checks],
                }
                for r in reports
            ],
            "total_hard": sum(r.hard_findings for r in reports),
            "total_soft": sum(r.soft_findings for r in reports),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_human(reports))
        print(f"\nTotal: hard={sum(r.hard_findings for r in reports)} "
              f"soft={sum(r.soft_findings for r in reports)}")

    return 1 if any(r.hard_findings for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
