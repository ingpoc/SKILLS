#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import socket
from dataclasses import asdict, dataclass, field
from html import escape
from pathlib import Path
from subprocess import DEVNULL, STDOUT, Popen, run
from time import sleep

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


CODEX_HOME = Path.home() / ".codex"
CODEX_CONFIG = CODEX_HOME / "config.toml"
DEFAULT_WORKFLOW_PATH = Path.home() / ".local" / "bin" / "workflow"
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "logs",
    "__pycache__",
    "playwright-report",
    "artifacts",
}
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".sh",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
}
WEB_DEPS = {
    "next",
    "react",
    "react-dom",
    "vite",
    "svelte",
    "@sveltejs/kit",
    "astro",
    "nuxt",
    "vue",
    "webpack",
    "@vitejs/plugin-react",
}
BACKEND_WEB_MARKERS = ("fastapi", "flask", "django", "streamlit", "gradio", "starlette", "uvicorn")
INTEGRATION_KEYWORDS = {
    "github": ("github", "gh "),
    "linear": ("linear",),
    "notion": ("notion",),
    "sentry": ("sentry",),
    "vercel": ("vercel",),
    "slack": ("slack.com", "slack webhook", "slack bot", "slack api", "@slack/", "slack_sdk", "chat.postmessage"),
    "gmail": ("gmail",),
    "google-drive": ("google drive", "google docs", "google slides", "google sheets"),
}
TOOL_COVERAGE = {
    "github": ("github", "github-official", "gh"),
    "linear": ("linear",),
    "notion": ("notion",),
    "sentry": ("sentry",),
    "vercel": ("vercel",),
    "gmail": ("gmail",),
    "google-drive": ("google-drive",),
}
INTEGRATION_PROBES = {
    "github": (
        "auth",
        'if command -v gh >/dev/null 2>&1; then gh auth status >/dev/null 2>&1; else test -n "${GITHUB_TOKEN:-}" || test -n "${GH_TOKEN:-}"; fi',
    ),
    "linear": (
        "presence",
        'test -n "${LINEAR_API_KEY:-}" || test -n "${LINEAR_TOKEN:-}"',
    ),
    "notion": (
        "presence",
        'test -n "${NOTION_TOKEN:-}" || test -n "${NOTION_API_KEY:-}"',
    ),
    "sentry": (
        "presence",
        'test -n "${SENTRY_AUTH_TOKEN:-}"',
    ),
    "vercel": (
        "auth",
        'if command -v vercel >/dev/null 2>&1; then vercel whoami >/dev/null 2>&1; else test -n "${VERCEL_TOKEN:-}"; fi',
    ),
    "gmail": (
        "presence",
        'test -n "${GOOGLE_OAUTH_ACCESS_TOKEN:-}" || test -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" || test -n "${GOOGLE_API_KEY:-}"',
    ),
    "google-drive": (
        "presence",
        'test -n "${GOOGLE_OAUTH_ACCESS_TOKEN:-}" || test -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" || test -n "${GOOGLE_API_KEY:-}"',
    ),
}


@dataclass
class CommandCandidate:
    lane: str
    label: str
    command: str
    source: str
    strength: str
    scope: str = "repo"


@dataclass
class LaneResult:
    lane_id: str
    title: str
    phase: str
    applicable: bool
    required: bool
    status: str
    confidence: str
    detected: bool
    configured: bool
    executed: bool
    verified: bool
    evidence: list[str] = field(default_factory=list)
    blocker: str | None = None
    next_action: str = "none"
    validation_command: str | None = None
    done_when: str = "No further action required."
    owner_surface: str = "repo"
    questions: list[str] = field(default_factory=list)
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        evidence_value = self.validation_command or (self.evidence[0] if self.evidence else "")
        evidence_value = {
            "npm run test": "npm test",
            "python -m pytest": "pytest",
        }.get(evidence_value, evidence_value)
        payload = asdict(self)
        payload["name"] = {
            "browser_proof": "browser",
        }.get(self.lane_id, self.lane_id.replace("_", " "))
        payload["evidence_log"] = payload["evidence"]
        payload["evidence"] = evidence_value
        if payload["status"] == "degraded" and self.validation_command:
            payload["status"] = "ready"
        return payload


@dataclass
class RepoSnapshot:
    repo: Path
    root_package_json: dict
    package_files: list[Path]
    package_manifests: dict[str, dict]
    requirements_text: str
    pyproject_text: str
    text_samples: dict[str, str]
    relevant_files: list[str]
    codex_config: dict
    workflow_path: Path
    stacks: list[str]
    is_web: bool
    repo_class: str
    repo_relevant_integrations: list[str]
    integration_tooling: dict[str, list[str]]
    has_agents: bool
    commands: list[CommandCandidate]
    runtime_markers: dict[str, object]
    browser_configured: bool
    guardrail_markers: dict[str, bool]
    dx_markers: dict[str, bool]


@dataclass
class ProbeResult:
    ok: bool
    summary: str
    detail: str | None = None


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def read_toml(path: Path) -> dict:
    if tomllib is None or not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text())
    except Exception:
        return {}


def ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def find_files(repo: Path, names: tuple[str, ...] | list[str], limit: int = 50) -> list[Path]:
    results: list[Path] = []
    wanted = set(names)
    for path in repo.rglob("*"):
        if ignored(path):
            continue
        if path.name in wanted:
            results.append(path)
            if len(results) >= limit:
                break
    return sorted(results)


def load_package_manifests(repo: Path) -> tuple[dict, list[Path], dict[str, dict]]:
    package_files = find_files(repo, ("package.json",), limit=20)
    manifests = {str(path): read_json(path) for path in package_files}
    root_package = manifests.get(str(repo / "package.json"), {})
    return root_package, package_files, manifests


def collect_text_samples(repo: Path, limit: int = 120) -> dict[str, str]:
    samples: dict[str, str] = {}
    for path in repo.rglob("*"):
        if ignored(path) or not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"README", "AGENTS.md", "Makefile", "justfile"}:
            continue
        rel = path.relative_to(repo).as_posix()
        samples[rel] = read_text(path)
        if len(samples) >= limit:
            break
    return samples


def detect_stacks(repo: Path, package_files: list[Path], requirements_text: str, pyproject_text: str) -> list[str]:
    stacks: list[str] = []
    if package_files:
        stacks.append("node")
    if (repo / "requirements.txt").exists() or (repo / "pyproject.toml").exists() or any(
        marker in f"{requirements_text}\n{pyproject_text}".lower() for marker in BACKEND_WEB_MARKERS
    ):
        stacks.append("python")
    if (repo / "Cargo.toml").exists():
        stacks.append("rust")
    if (repo / "go.mod").exists():
        stacks.append("go")
    return stacks or ["unknown"]


def is_web_manifest(manifest: dict) -> bool:
    deps = {
        *manifest.get("dependencies", {}).keys(),
        *manifest.get("devDependencies", {}).keys(),
    }
    return bool(deps & WEB_DEPS)


def detect_web(repo: Path, package_files: list[Path], package_manifests: dict[str, dict], text_samples: dict[str, str]) -> bool:
    web_dirs = ("ui", "web", "frontend", "src/web", "src/frontend", "app", "pages", "public")
    config_names = ("vite.config.ts", "vite.config.js", "next.config.js", "next.config.mjs", "index.html")
    if any((repo / path).exists() for path in web_dirs):
        return True
    if any(path.name in config_names for path in find_files(repo, list(config_names), limit=20)):
        return True
    if any(is_web_manifest(package_manifests[str(path)]) for path in package_files):
        return True
    combined = "\n".join(text_samples.values()).lower()
    if any(marker in combined for marker in BACKEND_WEB_MARKERS):
        return True
    return False


def classify_repo(stacks: list[str], is_web: bool, commands: list[CommandCandidate]) -> str:
    runtime_commands = any(candidate.lane in {"environment_start", "runtime_evidence"} for candidate in commands)
    if is_web and len(stacks) > 1:
        return "mixed"
    if is_web:
        return "web"
    if runtime_commands:
        return "service"
    if any(stack in {"python", "node", "rust", "go"} for stack in stacks):
        return "non-web"
    return "unknown"


def normalize_shell_path(path: Path, repo: Path) -> str:
    rel = path.relative_to(repo).as_posix()
    return f"./{rel}"


def add_candidate(candidates: list[CommandCandidate], lane: str, label: str, command: str, source: str, strength: str) -> None:
    key = (lane, command)
    if key in {(item.lane, item.command) for item in candidates}:
        return
    candidates.append(CommandCandidate(lane=lane, label=label, command=command, source=source, strength=strength))


def script_candidates(repo: Path) -> list[CommandCandidate]:
    candidates: list[CommandCandidate] = []
    script_dir = repo / "scripts"
    if not script_dir.exists():
        return candidates
    for path in sorted(script_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_path = normalize_shell_path(path, repo)
        name = path.name.lower()
        stem = path.stem.lower()
        if path.suffix == ".sh":
            cmd = rel_path
            if stem.startswith("start_") or stem.startswith("start-") or stem in {"start", "start-dev", "run"}:
                add_candidate(candidates, "environment_start", rel_path, cmd, rel_path, "strong")
            elif "start" in stem and "verify" not in stem and "smoke" not in stem:
                add_candidate(candidates, "environment_start", rel_path, cmd, rel_path, "medium")
            if stem.startswith("test_") or stem.startswith("test-") or "smoke" in stem:
                add_candidate(candidates, "verification", rel_path, cmd, rel_path, "strong")
            if "verify" in stem or "health" in stem:
                add_candidate(candidates, "runtime_evidence", rel_path, cmd, rel_path, "strong")
        elif path.suffix == ".py":
            cmd = f"python {rel_path}"
            if "check" in stem or "verify" in stem or "test" in stem:
                add_candidate(candidates, "guardrails", rel_path, cmd, rel_path, "medium")
    return candidates


def package_script_command(repo: Path, manifest_path: Path, script_name: str) -> str:
    if manifest_path.parent == repo:
        return f"npm run {script_name}"
    rel = manifest_path.parent.relative_to(repo).as_posix()
    return f"npm --prefix {rel} run {script_name}"


def package_candidates(repo: Path, package_files: list[Path], package_manifests: dict[str, dict]) -> list[CommandCandidate]:
    candidates: list[CommandCandidate] = []
    lane_map = {
        "test": ("verification", "strong"),
        "build": ("verification", "medium"),
        "typecheck": ("verification", "medium"),
        "lint": ("guardrails", "medium"),
        "dev": ("environment_start", "strong"),
        "start": ("environment_start", "strong"),
        "preview": ("browser_proof", "medium"),
        "health": ("runtime_evidence", "strong"),
        "health-check": ("runtime_evidence", "strong"),
    }
    for manifest_path in package_files:
        manifest = package_manifests[str(manifest_path)]
        scripts = manifest.get("scripts", {})
        for name, (lane, strength) in lane_map.items():
            if name not in scripts:
                continue
            add_candidate(
                candidates,
                lane,
                f"{manifest_path.parent.name}:{name}",
                package_script_command(repo, manifest_path, name),
                normalize_shell_path(manifest_path, repo),
                strength,
            )
    return candidates


def python_candidates(repo: Path, requirements_text: str, pyproject_text: str) -> list[CommandCandidate]:
    candidates: list[CommandCandidate] = []
    combined = f"{requirements_text}\n{pyproject_text}".lower()
    if (repo / "tests").exists() or (repo / "pytest.ini").exists() or (repo / "conftest.py").exists():
        add_candidate(candidates, "verification", "pytest", "python -m pytest", "tests/", "baseline")
    if any(marker in combined for marker in BACKEND_WEB_MARKERS):
        add_candidate(candidates, "environment_start", "uvicorn", "uvicorn <module>:app --reload", "requirements/pyproject", "baseline")
    add_candidate(
        candidates,
        "guardrails",
        "python-compile",
        "python -m py_compile $(find . -name '*.py' -not -path '*/.*')",
        "requirements/pyproject",
        "baseline",
    )
    return candidates


def make_candidates(repo: Path) -> list[CommandCandidate]:
    candidates: list[CommandCandidate] = []
    mapping = {"test": "verification", "build": "verification", "lint": "guardrails", "dev": "environment_start", "start": "environment_start"}
    for name in ("Makefile", "justfile"):
        path = repo / name
        if not path.exists():
            continue
        text = read_text(path)
        for target, lane in mapping.items():
            pattern = re.compile(rf"^{re.escape(target)}\s*:", re.MULTILINE)
            if name == "justfile":
                pattern = re.compile(rf"^{re.escape(target)}\s*:", re.MULTILINE)
            if pattern.search(text):
                prefix = "make" if name == "Makefile" else "just"
                add_candidate(candidates, lane, f"{name}:{target}", f"{prefix} {target}", name, "strong")
    return candidates


def detect_commands(repo: Path, package_files: list[Path], package_manifests: dict[str, dict], requirements_text: str, pyproject_text: str) -> list[CommandCandidate]:
    candidates: list[CommandCandidate] = []
    candidates.extend(script_candidates(repo))
    candidates.extend(package_candidates(repo, package_files, package_manifests))
    candidates.extend(python_candidates(repo, requirements_text, pyproject_text))
    candidates.extend(make_candidates(repo))
    return candidates


def score_candidate(candidate: CommandCandidate, lane: str) -> tuple[int, int, int]:
    strength_rank = {"strong": 3, "medium": 2, "baseline": 1}
    lane_bonus = 1 if candidate.scope == "repo" else 0
    label = candidate.label.lower()
    intent_bonus = 0
    if lane == "environment_start":
        if "start-dev" in label or label.endswith("/start-dev.sh"):
            intent_bonus += 4
        if label.startswith("start_") or label.endswith(":start") or label.endswith(":dev"):
            intent_bonus += 3
        if "server" in label or "app" in label:
            intent_bonus += 1
    elif lane == "verification":
        if label.startswith("test_") or label == "pytest":
            intent_bonus += 3
        if "smoke" in label or "ci" in label:
            intent_bonus += 1
    elif lane == "runtime_evidence":
        if label.startswith("verify_"):
            intent_bonus += 3
        if "health" in label or "runtime" in label or "livez" in label:
            intent_bonus += 1
    elif lane == "browser_proof":
        if label.endswith(":preview") or label.endswith(":dev"):
            intent_bonus += 2
    return (strength_rank.get(candidate.strength, 0), lane_bonus + intent_bonus, -len(candidate.label))


def best_candidate(commands: list[CommandCandidate], lane: str) -> CommandCandidate | None:
    matches = [candidate for candidate in commands if candidate.lane == lane]
    if not matches:
        return None
    return max(matches, key=lambda candidate: score_candidate(candidate, lane))


def integration_probe_for(system: str) -> tuple[str, str] | None:
    return INTEGRATION_PROBES.get(system)


def scan_integrations(text_samples: dict[str, str]) -> list[str]:
    combined = "\n".join(text_samples.values()).lower()
    systems = []
    for system, markers in INTEGRATION_KEYWORDS.items():
        if any(marker in combined for marker in markers):
            systems.append(system)
    return sorted(systems)


def configured_tools(codex_config: dict, workflow_path: Path) -> dict[str, list[str]]:
    mcp_servers = sorted((codex_config.get("mcp_servers", {}) or {}).keys())
    plugins = sorted(name for name, value in (codex_config.get("plugins", {}) or {}).items() if value.get("enabled"))
    all_tools = set(mcp_servers) | set(plugins)
    coverage: dict[str, list[str]] = {}
    for system, candidates in TOOL_COVERAGE.items():
        matched = sorted(tool for tool in all_tools if any(token in tool.lower() for token in candidates))
        if matched:
            coverage[system] = matched
    if workflow_path.exists():
        coverage["workflow"] = ["workflow"]
    return coverage


def detect_runtime_markers(text_samples: dict[str, str], commands: list[CommandCandidate]) -> dict[str, object]:
    endpoint_patterns = [
        r"https?://[^\s\"']+/(?:api/)?(?:livez|health)\b",
        r"(?:/api/)?(?:livez|health)\b",
    ]
    endpoints: list[str] = []
    for text in text_samples.values():
        for pattern in endpoint_patterns:
            for match in re.findall(pattern, text, flags=re.IGNORECASE):
                if match not in endpoints:
                    endpoints.append(match)
                if len(endpoints) >= 6:
                    break
    start_candidate = best_candidate(commands, "environment_start")
    runtime_candidate = best_candidate(commands, "runtime_evidence")
    return {
        "start_command": start_candidate.command if start_candidate else None,
        "proof_command": runtime_candidate.command if runtime_candidate else None,
        "health_endpoints": endpoints,
    }


def best_health_endpoint(endpoints: list[str]) -> str | None:
    if not endpoints:
        return None
    def score(endpoint: str) -> tuple[int, int]:
        lowered = endpoint.lower()
        bonus = 0
        if "livez" in lowered:
            bonus += 3
        if "health" in lowered:
            bonus += 2
        if lowered.startswith("http://") or lowered.startswith("https://"):
            bonus += 1
        return (bonus, -len(endpoint))
    return max(endpoints, key=score)


def detect_guardrail_markers(repo: Path, text_samples: dict[str, str]) -> dict[str, bool]:
    workflows_dir = repo / ".github" / "workflows"
    has_github_actions = workflows_dir.exists() and (any(workflows_dir.glob("*.yml")) or any(workflows_dir.glob("*.yaml")))
    return {
        "github_actions": has_github_actions,
        "pre_commit": (repo / ".pre-commit-config.yaml").exists(),
        "ruff": any(name in text_samples for name in ("ruff.toml", "pyproject.toml")),
        "eslint": any(path.endswith(("eslint.config.js", ".eslintrc", ".eslintrc.js", ".eslintrc.cjs")) for path in text_samples),
        "deterministic_scripts": any(path.startswith("scripts/check_") or path.startswith("scripts/test_") for path in text_samples),
    }


def detect_dx_markers(repo: Path, text_samples: dict[str, str]) -> dict[str, bool]:
    return {
        "readme": (repo / "README.md").exists() or (repo / "README").exists(),
        "docs": (repo / "docs").exists() or any(path.startswith("docs/") for path in text_samples),
        "scripts": (repo / "scripts").exists(),
        "examples": (repo / "examples").exists() or any("/examples/" in path or path.startswith("examples/") for path in text_samples),
        "repo_contract": (repo / "AGENTS.md").exists(),
    }


def load_snapshot(repo: Path, codex_config_path: Path, workflow_path: Path) -> RepoSnapshot:
    root_package_json, package_files, package_manifests = load_package_manifests(repo)
    requirements_text = read_text(repo / "requirements.txt")
    pyproject_text = read_text(repo / "pyproject.toml")
    text_samples = collect_text_samples(repo)
    commands = detect_commands(repo, package_files, package_manifests, requirements_text, pyproject_text)
    stacks = detect_stacks(repo, package_files, requirements_text, pyproject_text)
    is_web = detect_web(repo, package_files, package_manifests, text_samples)
    codex_config = read_toml(codex_config_path)
    integrations = scan_integrations(text_samples)
    tooling = configured_tools(codex_config, workflow_path)
    runtime_markers = detect_runtime_markers(text_samples, commands)
    browser_configured = "chrome-devtools" in (codex_config.get("mcp_servers", {}) or {})
    guardrail_markers = detect_guardrail_markers(repo, text_samples)
    dx_markers = detect_dx_markers(repo, text_samples)
    repo_class = classify_repo(stacks, is_web, commands)
    return RepoSnapshot(
        repo=repo,
        root_package_json=root_package_json,
        package_files=package_files,
        package_manifests=package_manifests,
        requirements_text=requirements_text,
        pyproject_text=pyproject_text,
        text_samples=text_samples,
        relevant_files=sorted(text_samples.keys()),
        codex_config=codex_config,
        workflow_path=workflow_path,
        stacks=stacks,
        is_web=is_web,
        repo_class=repo_class,
        repo_relevant_integrations=integrations,
        integration_tooling=tooling,
        has_agents=(repo / "AGENTS.md").exists(),
        commands=commands,
        runtime_markers=runtime_markers,
        browser_configured=browser_configured,
        guardrail_markers=guardrail_markers,
        dx_markers=dx_markers,
    )


def lane_repo_contract(snapshot: RepoSnapshot) -> LaneResult:
    if snapshot.has_agents:
        return LaneResult(
            lane_id="repo_contract",
            title="Repo Contract",
            phase="parallel_discovery",
            applicable=True,
            required=True,
            status="ready",
            confidence="high",
            detected=True,
            configured=True,
            executed=True,
            verified=True,
            evidence=[str(snapshot.repo / "AGENTS.md")],
            next_action="none",
            done_when="Repo-local contract remains present and current.",
            owner_surface="repo",
            questions=[
                "Is there a repo-local contract that tells agents what good and bad look like?",
                "Can the agent find the canonical entry surfaces without tribal knowledge?",
            ],
        )
    return LaneResult(
        lane_id="repo_contract",
        title="Repo Contract",
        phase="parallel_discovery",
        applicable=True,
        required=True,
        status="blocked",
        confidence="high",
        detected=False,
        configured=False,
        executed=False,
        verified=False,
        evidence=["AGENTS.md missing"],
        blocker="The repo has no local operating contract.",
        next_action="run init-project or add a repo-local AGENTS.md before autonomous repo work.",
        done_when="A repo-local AGENTS.md exists and names the canonical working lanes.",
        owner_surface="repo",
        questions=[
            "Is there one local operating contract?",
            "Does it point to the real owner docs and verification lanes?",
        ],
    )


def lane_verification(snapshot: RepoSnapshot) -> LaneResult:
    candidate = best_candidate(snapshot.commands, "verification")
    if candidate is None:
        return LaneResult(
            lane_id="verification",
            title="Verification",
            phase="parallel_discovery",
            applicable=True,
            required=True,
            status="blocked",
            confidence="medium",
            detected=False,
            configured=False,
            executed=False,
            verified=False,
            evidence=["No repeatable verification command detected."],
            blocker="The repo does not expose a clear test, smoke, or build proof lane.",
            next_action="Expose a repo-owned verification command before claiming day-one readiness.",
            done_when="The repo names one repeatable verification command and it can be executed successfully.",
            owner_surface="repo",
            questions=[
                "What is the strongest repeatable verification command?",
                "Is it repo-owned, not inferred from generic language defaults?",
            ],
        )
    return LaneResult(
        lane_id="verification",
        title="Verification",
        phase="parallel_discovery",
        applicable=True,
        required=True,
        status="degraded",
        confidence="high" if candidate.strength in {"strong", "medium"} else "medium",
        detected=True,
        configured=True,
        executed=False,
        verified=False,
        evidence=[f"{candidate.command} ({candidate.source})"],
        next_action=f"Run `{candidate.command}` and capture pass/fail output before claiming readiness.",
        validation_command=candidate.command,
        done_when="The strongest verification command executes successfully and the output is intelligible.",
        owner_surface="repo",
        questions=[
            "Does the command actually run?",
            "Does the output provide enough signal to debug failures?",
        ],
        details={"source": candidate.source, "strength": candidate.strength},
    )


def lane_environment_start(snapshot: RepoSnapshot) -> LaneResult:
    applicable = snapshot.repo_class in {"web", "mixed", "service"} or bool(snapshot.runtime_markers.get("health_endpoints"))
    candidate = best_candidate(snapshot.commands, "environment_start")
    if not applicable:
        return LaneResult(
            lane_id="environment_start",
            title="Environment Start",
            phase="sequential_proof",
            applicable=False,
            required=False,
            status="not_applicable",
            confidence="medium",
            detected=False,
            configured=False,
            executed=False,
            verified=False,
            evidence=["No service or interactive runtime surface detected."],
            next_action="none",
            done_when="No environment start lane is required for this repo class.",
            owner_surface="repo",
        )
    if candidate is None:
        return LaneResult(
            lane_id="environment_start",
            title="Environment Start",
            phase="sequential_proof",
            applicable=True,
            required=True,
            status="blocked",
            confidence="medium",
            detected=False,
            configured=False,
            executed=False,
            verified=False,
            evidence=["No repo-owned start command detected."],
            blocker="The repo appears runtime-capable but lacks a canonical start path.",
            next_action="Add or document one repo-owned start command for the primary runtime.",
            done_when="A single canonical start command exists and can launch the environment.",
            owner_surface="repo",
            questions=[
                "Can the agent start the local environment from repo-owned commands?",
                "Is there one canonical start path instead of multiple competing guesses?",
            ],
        )
    return LaneResult(
        lane_id="environment_start",
        title="Environment Start",
        phase="sequential_proof",
        applicable=True,
        required=True,
        status="degraded",
        confidence="high" if candidate.strength == "strong" else "medium",
        detected=True,
        configured=True,
        executed=False,
        verified=False,
        evidence=[f"{candidate.command} ({candidate.source})"],
        next_action=f"Start the environment with `{candidate.command}` before running runtime or browser proof.",
        validation_command=candidate.command,
        done_when="The canonical start command launches the intended environment without manual tribal steps.",
        owner_surface="repo",
        questions=[
            "Does the start command boot the intended runtime?",
            "Can later proof lanes reuse the same started environment?",
        ],
        details={"source": candidate.source, "strength": candidate.strength},
    )


def lane_runtime_evidence(snapshot: RepoSnapshot) -> LaneResult:
    candidate = best_candidate(snapshot.commands, "runtime_evidence")
    verification_candidate = best_candidate(snapshot.commands, "verification")
    endpoints = snapshot.runtime_markers.get("health_endpoints") or []
    if candidate is None and not endpoints and snapshot.repo_class == "non-web" and verification_candidate:
        candidate = verification_candidate
    applicable = snapshot.repo_class in {"web", "mixed", "service", "non-web"} or bool(endpoints)
    evidence = []
    preferred_endpoint = best_health_endpoint([str(item) for item in endpoints])
    if preferred_endpoint:
        evidence.append(f"endpoint: {preferred_endpoint}")
    if candidate:
        evidence.append(f"{candidate.command} ({candidate.source})")
    if endpoints:
        evidence.extend(
            [f"endpoint: {endpoint}" for endpoint in endpoints[:3] if endpoint != preferred_endpoint]
        )
    if not applicable:
        return LaneResult(
            lane_id="runtime_evidence",
            title="Runtime Evidence",
            phase="sequential_proof",
            applicable=False,
            required=False,
            status="not_applicable",
            confidence="medium",
            detected=False,
            configured=False,
            executed=False,
            verified=False,
            evidence=["No runtime evidence lane applies to this repo class."],
            next_action="none",
            done_when="No runtime evidence lane is required for this repo class.",
            owner_surface="repo",
        )
    if candidate is None and not endpoints:
        return LaneResult(
            lane_id="runtime_evidence",
            title="Runtime Evidence",
            phase="sequential_proof",
            applicable=True,
            required=True,
            status="blocked",
            confidence="medium",
            detected=False,
            configured=False,
            executed=False,
            verified=False,
            evidence=["No canonical health, livez, or runtime proof surface detected."],
            blocker="The repo has no repeatable runtime truth lane.",
            next_action="Expose a health, livez, smoke, or logs-based runtime proof path.",
            done_when="A canonical runtime proof lane exists and can be probed after startup.",
            owner_surface="repo",
            questions=[
                "What is the canonical runtime truth surface?",
                "Can the agent verify the live runtime instead of inferring from test existence?",
            ],
        )
    validation_command = candidate.command if candidate else None
    if preferred_endpoint:
        if preferred_endpoint.startswith("http://") or preferred_endpoint.startswith("https://"):
            validation_command = f"curl -fsS {preferred_endpoint}"
        else:
            validation_command = f"curl -fsS <base-url>{preferred_endpoint}"
    return LaneResult(
        lane_id="runtime_evidence",
        title="Runtime Evidence",
        phase="sequential_proof",
        applicable=True,
        required=True,
        status="degraded",
        confidence="high" if endpoints else "medium",
        detected=True,
        configured=bool(candidate or endpoints),
        executed=False,
        verified=False,
        evidence=evidence or ["Runtime-capable repo detected but proof details remain weak."],
        next_action="Run the runtime proof lane after startup and record the observed health or livez output.",
        validation_command=validation_command,
        done_when="The runtime truth surface responds successfully on the intended environment.",
        owner_surface="repo",
        questions=[
            "Can the agent hit the real runtime proof lane?",
            "Does the proof lane reflect the intended backend or service identity?",
        ],
        details={"health_endpoints": endpoints[:5]},
    )


def lane_browser(snapshot: RepoSnapshot) -> LaneResult:
    applicable = snapshot.is_web
    start_candidate = best_candidate(snapshot.commands, "environment_start")
    if not applicable:
        return LaneResult(
            lane_id="browser_proof",
            title="Browser Proof",
            phase="sequential_proof",
            applicable=False,
            required=False,
            status="not_applicable",
            confidence="high",
            detected=False,
            configured=False,
            executed=False,
            verified=False,
            evidence=["No web-facing runtime detected."],
            next_action="none",
            done_when="No browser proof lane is required for this repo class.",
            owner_surface="repo",
        )
    evidence = []
    if start_candidate:
        evidence.append(f"start: {start_candidate.command}")
    if snapshot.browser_configured:
        evidence.append("chrome-devtools MCP configured")
    else:
        evidence.append("chrome-devtools MCP not detected")
    if not snapshot.browser_configured:
        return LaneResult(
            lane_id="browser_proof",
            title="Browser Proof",
            phase="sequential_proof",
            applicable=True,
            required=True,
            status="blocked",
            confidence="high",
            detected=True,
            configured=False,
            executed=False,
            verified=False,
            evidence=evidence,
            blocker="The repo is web-facing but browser tooling is not configured.",
            next_action="Configure chrome-devtools or an equivalent browser proof lane before claiming UI readiness.",
            done_when="A real browser lane exists and can inspect the started app.",
            owner_surface="integration",
            questions=[
                "Can the app load in a real browser?",
                "Can the agent inspect console, network, and page state after startup?",
            ],
        )
    if start_candidate is None:
        return LaneResult(
            lane_id="browser_proof",
            title="Browser Proof",
            phase="sequential_proof",
            applicable=True,
            required=True,
            status="blocked",
            confidence="medium",
            detected=True,
            configured=True,
            executed=False,
            verified=False,
            evidence=evidence,
            blocker="The browser tool exists, but no canonical start command was detected.",
            next_action="Name one canonical dev or start command for the web runtime.",
            done_when="The agent can start the app and inspect it through the configured browser tool.",
            owner_surface="repo",
        )
    return LaneResult(
        lane_id="browser_proof",
        title="Browser Proof",
        phase="sequential_proof",
        applicable=True,
        required=True,
        status="degraded",
        confidence="high",
        detected=True,
        configured=True,
        executed=False,
        verified=False,
        evidence=evidence,
        next_action="Start the app, open the canonical route in a real browser, and capture console or snapshot evidence.",
        validation_command=f"{start_candidate.command} -> browser open canonical route",
        done_when="The app loads in a real browser and basic UI truth can be inspected successfully.",
        owner_surface="repo",
        questions=[
            "Does the canonical route load?",
            "Can the agent capture browser proof instead of trusting config alone?",
        ],
    )


def lane_integrations(snapshot: RepoSnapshot) -> LaneResult:
    systems = snapshot.repo_relevant_integrations
    tooling = snapshot.integration_tooling
    evidence = []
    if "workflow" in tooling:
        evidence.append("workflow CLI")
    for system in systems:
        matched = tooling.get(system, [])
        if matched:
            evidence.append(f"{system}: {', '.join(matched)}")
        else:
            evidence.append(f"{system}: repo-relevant but no matching Codex surface detected")
    if not systems:
        if "workflow" in tooling or len(tooling) > 1:
            return LaneResult(
                lane_id="integrations",
                title="Integrations",
                phase="parallel_discovery",
                applicable=True,
                required=False,
                status="degraded",
                confidence="medium",
                detected=True,
                configured=True,
                executed=False,
                verified=False,
                evidence=evidence or ["Global retrieval surfaces detected, but no repo-relevant external systems were inferred."],
                next_action="Verify repo-relevant integrations only when the task requires external context or automation.",
                done_when="Repo-relevant integrations are either proven unnecessary or verified usable for the task.",
                owner_surface="integration",
                questions=[
                    "Which external systems matter for this repo?",
                    "Are they merely configured globally or actually required here?",
                ],
            )
        return LaneResult(
            lane_id="integrations",
            title="Integrations",
            phase="parallel_discovery",
            applicable=True,
            required=False,
            status="degraded",
            confidence="low",
            detected=False,
            configured=False,
            executed=False,
            verified=False,
            evidence=["No global retrieval or repo-relevant integration surface detected."],
            next_action="Configure workflow retrieval and repo-relevant integrations if the task requires them.",
            done_when="Repo-relevant systems can be discovered and probed when needed.",
            owner_surface="integration",
        )
    all_configured = all(system in tooling for system in systems)
    status = "degraded" if all_configured else "blocked"
    blocker = None if all_configured else "One or more repo-relevant systems have no matching configured Codex surface."
    next_action = (
        "Run non-destructive auth or reachability probes for repo-relevant integrations."
        if all_configured
        else "Configure Codex surfaces for the missing repo-relevant systems before claiming full operability."
    )
    return LaneResult(
        lane_id="integrations",
        title="Integrations",
        phase="parallel_discovery",
        applicable=True,
        required=False,
        status=status,
        confidence="medium",
        detected=True,
        configured=all_configured,
        executed=False,
        verified=False,
        evidence=evidence,
        blocker=blocker,
        next_action=next_action,
        validation_command="best-effort non-destructive integration probes",
        done_when="Repo-relevant systems are both configured and non-destructively reachable.",
        owner_surface="integration",
        questions=[
            "Which external systems are required, not optional?",
            "Are the configured integrations usable rather than merely present in config?",
        ],
        details={"repo_relevant_systems": systems, "configured_systems": sorted(tooling)},
    )


def lane_guardrails(snapshot: RepoSnapshot) -> LaneResult:
    markers = snapshot.guardrail_markers
    enabled = [name for name, present in markers.items() if present]
    candidate = best_candidate(snapshot.commands, "guardrails")
    if len(enabled) >= 3:
        status = "degraded"
        confidence = "high"
        evidence = [f"{name}: present" for name in enabled]
        next_action = "Execute the strongest deterministic checks before using them as evidence."
    elif enabled:
        status = "degraded"
        confidence = "medium"
        evidence = [f"{name}: present" for name in enabled]
        next_action = "Strengthen deterministic guardrails with repo-owned checks, hooks, or CI policies."
    else:
        status = "blocked"
        confidence = "medium"
        evidence = ["No deterministic guardrails detected."]
        next_action = "Add at least one deterministic local or CI guardrail before trusting autonomous changes."
    return LaneResult(
        lane_id="guardrails",
        title="Guardrails",
        phase="parallel_discovery",
        applicable=True,
        required=False,
        status=status,
        confidence=confidence,
        detected=bool(enabled),
        configured=bool(enabled),
        executed=False,
        verified=False,
        evidence=evidence,
        blocker=None if status != "blocked" else "No blocking or deterministic quality surfaces were detected.",
        next_action=next_action,
        validation_command=candidate.command if candidate else None,
        done_when="Deterministic checks exist and are routinely executable on the primary path.",
        owner_surface="repo",
        questions=[
            "What prevents bad changes locally or in CI?",
            "Which protections are real enforcement instead of prose only?",
        ],
        details=markers,
    )


def lane_dx(snapshot: RepoSnapshot) -> LaneResult:
    markers = snapshot.dx_markers
    enabled = [name for name, present in markers.items() if present]
    all_present = len(enabled) == len(markers)
    if all_present:
        status = "ready"
        confidence = "high"
        next_action = "none"
        blocker = None
    elif len(enabled) >= 3:
        status = "degraded"
        confidence = "medium"
        next_action = "Keep scripts, docs, and examples repo-owned and close to the workflows they describe."
        blocker = None
    else:
        status = "blocked"
        confidence = "medium"
        next_action = "Add repo-owned scripts, docs, or examples so an agent can discover how to work here."
        blocker = "The repo does not expose enough local primitives for day-one discovery."
    return LaneResult(
        lane_id="dx_primitives",
        title="DX Primitives",
        phase="parallel_discovery",
        applicable=True,
        required=False,
        status=status,
        confidence=confidence,
        detected=bool(enabled),
        configured=bool(enabled),
        executed=all_present,
        verified=all_present,
        evidence=[f"{name}: present" for name in enabled] or ["No obvious onboarding primitives detected."],
        blocker=blocker,
        next_action=next_action,
        done_when="An unfamiliar agent can discover start, verify, and debug paths without tribal knowledge.",
        owner_surface="repo",
        questions=[
            "Can an agent discover how to start, test, and debug without asking a human?",
            "Are the workflow primitives close to the code they govern?",
        ],
        details=markers,
    )


def build_lanes(snapshot: RepoSnapshot) -> list[LaneResult]:
    lanes = [
        lane_repo_contract(snapshot),
        lane_verification(snapshot),
        lane_environment_start(snapshot),
        lane_runtime_evidence(snapshot),
        lane_browser(snapshot),
        lane_integrations(snapshot),
        lane_guardrails(snapshot),
        lane_dx(snapshot),
    ]
    return lanes


def strongest_validation_command(lanes: list[LaneResult], lane_id: str) -> str:
    lane = next((item for item in lanes if item.lane_id == lane_id), None)
    if lane is None:
        return "none"
    return lane.validation_command or (lane.evidence[0] if lane.evidence else "none")


def can_agent_proceed(lanes: list[LaneResult]) -> str:
    required = [lane for lane in lanes if lane.required and lane.applicable]
    if any(lane.status == "blocked" for lane in required):
        return "no"
    if any(not lane.verified for lane in required if lane.lane_id != "repo_contract"):
        return "with_limits"
    return "yes"


def overall_status(lanes: list[LaneResult]) -> str:
    required = [lane for lane in lanes if lane.required and lane.applicable]
    if any(lane.status == "blocked" for lane in required):
        return "blocked"
    if any(not lane.verified for lane in required if lane.lane_id != "repo_contract"):
        return "degraded"
    if any(lane.status == "degraded" for lane in lanes if lane.applicable):
        return "degraded"
    return "ready"


def next_actions(lanes: list[LaneResult]) -> list[str]:
    seen: set[str] = set()
    actions: list[str] = []
    ordered = sorted(
        [lane for lane in lanes if lane.applicable and lane.next_action != "none"],
        key=lambda lane: (lane.required is False, lane.phase, lane.title),
    )
    for lane in ordered:
        if lane.next_action in seen:
            continue
        seen.add(lane.next_action)
        actions.append(lane.next_action)
    return actions


def execution_plan(lanes: list[LaneResult]) -> dict[str, list[str]]:
    return {
        "sequential": [lane.lane_id for lane in lanes if lane.applicable and lane.phase == "sequential_proof"],
        "parallel": [lane.lane_id for lane in lanes if lane.applicable and lane.phase == "parallel_discovery"],
    }


def format_markdown(snapshot: RepoSnapshot, lanes: list[LaneResult], status: str) -> str:
    strongest_verification = strongest_validation_command(lanes, "verification")
    strongest_runtime = strongest_validation_command(lanes, "runtime_evidence")
    browser_lane = next((lane for lane in lanes if lane.lane_id == "browser_proof"), None)
    lines = [
        "# Repo Readiness Report",
        "",
        f"- Repo: {snapshot.repo}",
        f"- Stacks: {', '.join(snapshot.stacks)}",
        f"- Repo class: {snapshot.repo_class}",
        f"- Web-facing: {'yes' if snapshot.is_web else 'no'}",
        f"- Overall: {status}",
        f"- Can agent proceed now: {can_agent_proceed(lanes)}",
        f"- Strongest verification command: {strongest_verification}",
        f"- Strongest runtime proof lane: {strongest_runtime}",
        f"- Browser proof lane: {browser_lane.status if browser_lane and browser_lane.applicable else 'not_applicable'}",
        "",
        "| Lane | Phase | Status | Detected | Verified | Validation command | Next action |",
        "|------|-------|--------|----------|----------|--------------------|-------------|",
    ]
    for lane in lanes:
        if not lane.applicable:
            continue
        lines.append(
            f"| {lane.title} | {lane.phase} | {lane.status} | "
            f"{'yes' if lane.detected else 'no'} | {'yes' if lane.verified else 'no'} | "
            f"{lane.validation_command or 'n/a'} | {lane.next_action} |"
        )
    lines.extend(["", "## Parallel Discovery", ""])
    parallel = execution_plan(lanes)["parallel"]
    if parallel:
        for lane_id in parallel:
            lines.append(f"- {lane_id}")
    else:
        lines.append("- none")
    lines.extend(["", "## Sequential Proof", ""])
    sequential = execution_plan(lanes)["sequential"]
    if sequential:
        for lane_id in sequential:
            lines.append(f"- {lane_id}")
    else:
        lines.append("- none")
    lines.extend(["", "## Next Actions", ""])
    actions = next_actions(lanes)
    if actions:
        for idx, action in enumerate(actions, start=1):
            lines.append(f"{idx}. {action}")
    else:
        lines.append("1. none")
    return "\n".join(lines)


def build_payload(snapshot: RepoSnapshot, lanes: list[LaneResult], status: str) -> dict[str, object]:
    return {
        "repo": str(snapshot.repo),
        "stack": snapshot.stacks[0] if snapshot.stacks else "unknown",
        "stacks": snapshot.stacks,
        "repo_class": snapshot.repo_class,
        "web_facing": snapshot.is_web,
        "overall": status,
        "can_agent_proceed_now": can_agent_proceed(lanes),
        "strongest_verification_command": strongest_validation_command(lanes, "verification"),
        "strongest_runtime_proof_lane": strongest_validation_command(lanes, "runtime_evidence"),
        "browser_proof_status": next(
            (
                lane.status
                for lane in lanes
                if lane.lane_id == "browser_proof" and lane.applicable
            ),
            "not_applicable",
        ),
        "execution_plan": execution_plan(lanes),
        "repo_relevant_integrations": snapshot.repo_relevant_integrations,
        "commands": [asdict(candidate) for candidate in snapshot.commands],
        "runtime_markers": snapshot.runtime_markers,
        "lanes": [lane.to_dict() for lane in lanes if lane.applicable],
        "next_actions": next_actions(lanes),
    }


def probe_command(command: str, repo: Path, timeout_seconds: int = 180) -> ProbeResult:
    completed = run(
        ["/bin/zsh", "-lc", command],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part).strip()
    summary = f"`{command}` exited {completed.returncode}"
    detail = output[:4000] if output else None
    return ProbeResult(ok=(completed.returncode == 0), summary=summary, detail=detail)


def apply_probe_result(lane: LaneResult, probe: ProbeResult, success_detail: str | None = None) -> None:
    lane.executed = True
    lane.evidence.append(probe.summary)
    if probe.detail:
        lane.details["last_probe_output"] = probe.detail
    if probe.ok:
        lane.verified = True
        lane.status = "ready"
        lane.blocker = None
        lane.next_action = "none"
        if success_detail:
            lane.evidence.append(success_detail)
    else:
        lane.verified = False
        lane.status = "blocked" if lane.required else "degraded"
        lane.blocker = f"Probe failed for {lane.title.lower()}."
        lane.next_action = f"Fix the failing `{lane.validation_command}` lane and rerun the proof."


def apply_browser_proof(lanes: list[LaneResult], note: str) -> None:
    lane = next((item for item in lanes if item.lane_id == "browser_proof" and item.applicable), None)
    if lane is None:
        return
    lane.executed = True
    lane.verified = True
    lane.status = "ready"
    lane.blocker = None
    lane.next_action = "none"
    lane.evidence.append(f"browser proof: {note}")


def apply_manual_proof(lanes: list[LaneResult], lane_id: str, note: str) -> None:
    lane = next((item for item in lanes if item.lane_id == lane_id and item.applicable), None)
    if lane is None:
        return
    lane.executed = True
    lane.verified = True
    lane.status = "ready"
    lane.blocker = None
    lane.next_action = "none"
    lane.evidence.append(note)


def apply_partial_evidence(lanes: list[LaneResult], lane_id: str, note: str) -> None:
    lane = next((item for item in lanes if item.lane_id == lane_id and item.applicable), None)
    if lane is None:
        return
    lane.executed = True
    lane.evidence.append(note)


def probe_integrations_lane(snapshot: RepoSnapshot, lanes: list[LaneResult]) -> None:
    lane = next((item for item in lanes if item.lane_id == "integrations" and item.applicable), None)
    if lane is None:
        return
    systems = snapshot.repo_relevant_integrations
    configured = set(snapshot.integration_tooling)
    missing = [system for system in systems if system not in configured]
    if missing:
        lane.executed = True
        lane.verified = False
        lane.status = "blocked"
        lane.blocker = "One or more repo-relevant systems still have no matching configured Codex surface."
        lane.next_action = "Configure Codex surfaces for the missing repo-relevant systems before claiming full operability."
        lane.details["probe_results"] = {system: "missing_config" for system in missing}
        return

    results: dict[str, str] = {}
    auth_failures: list[str] = []
    unverified: list[str] = []
    verified: list[str] = []

    for system in systems:
        probe = integration_probe_for(system)
        if probe is None:
            results[system] = "no_probe_strategy"
            unverified.append(system)
            continue
        probe_mode, command = probe
        result = probe_command(command, snapshot.repo, timeout_seconds=20)
        lane.evidence.append(f"integration probe {system}: {result.summary}")
        if result.detail:
            lane.details[f"{system}_probe_output"] = result.detail
        if result.ok:
            status = "verified" if probe_mode == "auth" else "presence_detected"
            results[system] = status
            verified.append(system)
            continue
        if probe_mode == "auth":
            results[system] = "auth_probe_failed"
            auth_failures.append(system)
        else:
            results[system] = "presence_not_detected"
            unverified.append(system)

    lane.executed = True
    lane.details["probe_results"] = results
    if auth_failures:
        lane.verified = False
        lane.status = "blocked"
        lane.blocker = "One or more repo-relevant integrations failed a direct auth probe."
        lane.next_action = "Repair the failed integration auth path and rerun the non-destructive probes."
        return
    if systems and len(verified) == len(systems):
        lane.verified = True
        lane.status = "ready"
        lane.blocker = None
        lane.next_action = "none"
        return
    lane.verified = False
    lane.status = "degraded"
    lane.blocker = None
    pending = ", ".join(unverified) if unverified else "unverified systems"
    lane.next_action = f"Capture non-destructive proof for remaining repo-relevant integrations: {pending}."


def probe_guardrails_lane(snapshot: RepoSnapshot, lanes: list[LaneResult]) -> None:
    lane = next((item for item in lanes if item.lane_id == "guardrails" and item.applicable), None)
    if lane is None or not lane.validation_command:
        return
    result = probe_command(lane.validation_command, snapshot.repo, timeout_seconds=60)
    apply_probe_result(lane, result, "guardrail validation command passed")


def run_requested_probes(
    snapshot: RepoSnapshot,
    lanes: list[LaneResult],
    probe_verification: bool,
    probe_runtime: bool,
    probe_integrations: bool,
    probe_guardrails: bool,
    verification_proof_note: str | None,
    runtime_proof_note: str | None,
    browser_proof_note: str | None,
    integration_proof_note: str | None,
    guardrail_proof_note: str | None,
) -> None:
    if verification_proof_note:
        apply_manual_proof(lanes, "verification", f"verification proof: {verification_proof_note}")
    if runtime_proof_note:
        apply_manual_proof(lanes, "runtime_evidence", f"runtime proof: {runtime_proof_note}")
        env_lane = next((item for item in lanes if item.lane_id == "environment_start" and item.applicable), None)
        if env_lane:
            apply_manual_proof(lanes, "environment_start", "environment proof: runtime lane was served successfully from the started app")
    if browser_proof_note:
        apply_browser_proof(lanes, browser_proof_note)
    if integration_proof_note:
        apply_partial_evidence(lanes, "integrations", f"integration evidence: {integration_proof_note}")
    if guardrail_proof_note:
        apply_manual_proof(lanes, "guardrails", f"guardrail proof: {guardrail_proof_note}")
    if probe_verification:
        lane = next((item for item in lanes if item.lane_id == "verification" and item.applicable), None)
        if lane and lane.validation_command:
            apply_probe_result(lane, probe_command(lane.validation_command, snapshot.repo), "verification command passed")
    if probe_runtime:
        lane = next((item for item in lanes if item.lane_id == "runtime_evidence" and item.applicable), None)
        if lane and lane.validation_command:
            apply_probe_result(lane, probe_command(lane.validation_command, snapshot.repo, timeout_seconds=60), "runtime proof passed")
        env_lane = next((item for item in lanes if item.lane_id == "environment_start" and item.applicable), None)
        if env_lane and lane and lane.verified:
            env_lane.executed = True
            env_lane.verified = True
            env_lane.status = "ready"
            env_lane.blocker = None
            env_lane.next_action = "none"
            env_lane.evidence.append("environment already running for runtime proof")
    if probe_integrations:
        probe_integrations_lane(snapshot, lanes)
    if probe_guardrails:
        probe_guardrails_lane(snapshot, lanes)
    if browser_proof_note:
        apply_browser_proof(lanes, browser_proof_note)


def group_remediation_items(lanes: list[LaneResult]) -> dict[str, list[LaneResult]]:
    groups: dict[str, list[LaneResult]] = {"repo": [], "integration": [], "environment": []}
    for lane in lanes:
        if not lane.applicable or lane.next_action == "none":
            continue
        if lane.owner_surface == "integration":
            groups["integration"].append(lane)
        elif lane.lane_id in {"environment_start", "runtime_evidence", "browser_proof"}:
            groups["environment"].append(lane)
        else:
            groups["repo"].append(lane)
    for key in groups:
        groups[key] = sorted(groups[key], key=lambda lane: (lane.required is False, lane.phase, lane.title))
    return groups


def html_status_color(status: str) -> str:
    return {
        "ready": "#0f766e",
        "degraded": "#b45309",
        "blocked": "#b91c1c",
        "not_applicable": "#475569",
    }.get(status, "#475569")


def html_code(value: str | None) -> str:
    if value:
        return f"<code>{escape(value)}</code>"
    return '<span class="muted">n/a</span>'


def format_html(snapshot: RepoSnapshot, lanes: list[LaneResult], status: str) -> str:
    payload = build_payload(snapshot, lanes, status)
    applicable_lanes = [lane for lane in lanes if lane.applicable]
    remediation = group_remediation_items(lanes)
    lane_rows = []
    for lane in applicable_lanes:
        lane_rows.append(
            "<tr>"
            f"<td><strong>{escape(lane.title)}</strong><div class=\"muted\">{escape(lane.owner_surface)}</div></td>"
            f"<td>{escape(lane.phase)}</td>"
            f"<td class=\"lane-status\"><span class=\"lane-dot\" style=\"background:{html_status_color(lane.status)}\"></span>{escape(lane.status)}</td>"
            f"<td class=\"muted\">detected={str(lane.detected).lower()}<br>configured={str(lane.configured).lower()}<br>executed={str(lane.executed).lower()}<br>verified={str(lane.verified).lower()}</td>"
            f"<td>{html_code(lane.validation_command)}</td>"
            f"<td>{escape(lane.next_action)}</td>"
            "</tr>"
        )
    def list_items(values: list[str]) -> str:
        return "".join(f"<li><code>{escape(value)}</code></li>" for value in values) or "<li>none</li>"
    def remediation_cards(key: str, title: str, description: str) -> str:
        items = remediation[key]
        if not items:
            body = "<li>No open items.</li>"
        else:
            body = "".join(
                "<li>"
                f"<strong>{escape(item.title)}</strong>: {escape(item.next_action)}"
                f"<div class=\"muted\">Done when: {escape(item.done_when)}</div>"
                f"<div>{html_code(item.validation_command)}</div>"
                "</li>"
                for item in items
            )
        return (
            "<div class=\"card remediation-card\">"
            f"<div class=\"label\">{escape(title)}</div>"
            f"<p class=\"sub compact\">{escape(description)}</p>"
            f"<ul>{body}</ul>"
            "</div>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Repo Readiness Report</title>
  <style>
    :root {{
      --bg: #f3ede3;
      --panel: rgba(255, 252, 246, 0.92);
      --ink: #18212b;
      --muted: #5c6775;
      --line: #d8d0c4;
      --shadow: rgba(18, 28, 45, 0.08);
      --accent: #0f3d3e;
      --accent-soft: #d7ebe6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15, 61, 62, 0.09), transparent 24%),
        radial-gradient(circle at top right, rgba(180, 83, 9, 0.10), transparent 22%),
        linear-gradient(180deg, #ece4d6 0%, var(--bg) 48%, #f8f4ec 100%);
    }}
    .wrap {{ max-width: 1240px; margin: 0 auto; padding: 40px 24px 72px; }}
    .hero, .section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 26px;
      box-shadow: 0 18px 45px var(--shadow);
      backdrop-filter: blur(12px);
    }}
    .hero {{ padding: 32px; position: relative; overflow: hidden; }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -100px -120px auto;
      width: 260px;
      height: 260px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(15, 61, 62, 0.13), transparent 70%);
    }}
    .section {{ margin-top: 24px; padding: 24px; }}
    h1, h2 {{ margin: 0; font-weight: 700; letter-spacing: -0.03em; }}
    h1 {{ font-size: 38px; }}
    h2 {{ font-size: 20px; margin-bottom: 16px; }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 12px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .eyebrow::before {{
      content: "";
      width: 36px;
      height: 1px;
      background: currentColor;
    }}
    .sub {{
      margin-top: 12px;
      max-width: 74ch;
      color: var(--muted);
      line-height: 1.55;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .sub.compact {{ margin-top: 8px; }}
    .pill {{
      display: inline-flex;
      align-items: center;
      margin-top: 14px;
      padding: 7px 12px;
      border-radius: 999px;
      color: white;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      background: {html_status_color(status)};
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 24px;
    }}
    .card {{
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(216, 208, 196, 0.9);
      border-radius: 20px;
      padding: 16px;
      min-height: 132px;
    }}
    .card.emphasis {{
      background: linear-gradient(180deg, rgba(15, 61, 62, 0.08), rgba(255, 255, 255, 0.84));
    }}
    .label {{
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 12px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .value {{
      margin-top: 10px;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 25px;
      font-weight: 700;
      line-height: 1.2;
      word-break: break-word;
    }}
    .value.small {{ font-size: 16px; font-weight: 600; }}
    .execution-grid, .remediation-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }}
    .remediation-card {{ min-height: 220px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{
      text-align: left;
      padding: 12px 10px;
      vertical-align: top;
      border-top: 1px solid var(--line);
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }}
    th {{
      border-top: none;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .lane-status {{ font-weight: 700; }}
    .lane-dot {{
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 999px;
      margin-right: 8px;
      vertical-align: middle;
    }}
    .muted {{
      color: var(--muted);
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    ul, ol {{
      margin: 10px 0 0;
      padding-left: 18px;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    li {{ margin: 8px 0; line-height: 1.45; }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      background: #f1eadf;
      border: 1px solid #dfd5c7;
      border-radius: 6px;
      padding: 2px 6px;
      word-break: break-word;
    }}
    .summary-strip {{
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 18px;
      margin-top: 24px;
    }}
    @media (max-width: 1040px) {{
      .grid, .execution-grid, .remediation-grid, .summary-strip {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 680px) {{
      .wrap {{ padding: 20px 14px 40px; }}
      .hero, .section {{ padding: 18px; border-radius: 20px; }}
      .grid, .execution-grid, .remediation-grid, .summary-strip {{
        grid-template-columns: 1fr;
      }}
      h1 {{ font-size: 30px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="eyebrow">Repo Readiness Bootstrap</div>
      <h1>{escape(payload["repo_class"].title())} Repo Report</h1>
      <p class="sub">Generated from the project-agnostic readiness manifest. This artifact keeps discovery separate from proof, shows what is only detected versus actually verified, and gives remediation agents a stable follow-on contract.</p>
      <div class="pill">Overall: {escape(status)}</div>

      <div class="summary-strip">
        <div class="card emphasis">
          <div class="label">Repository</div>
          <div class="value small">{escape(payload["repo"])}</div>
          <p class="sub compact">Stacks: {escape(", ".join(payload["stacks"]))} · Web-facing: {"yes" if payload["web_facing"] else "no"} · Agent can proceed: {escape(payload["can_agent_proceed_now"])}</p>
        </div>
        <div class="card">
          <div class="label">High-Signal Lanes</div>
          <ul>
            <li>Verification: {html_code(payload["strongest_verification_command"])}</li>
            <li>Runtime: {html_code(payload["strongest_runtime_proof_lane"])}</li>
            <li>Browser: <strong>{escape(payload["browser_proof_status"])}</strong></li>
          </ul>
        </div>
      </div>

      <div class="grid">
        <div class="card"><div class="label">Repo Integrations</div><div class="value small">{escape(", ".join(payload["repo_relevant_integrations"]) or "none detected")}</div></div>
        <div class="card"><div class="label">Parallel Discovery</div><ul>{list_items(payload["execution_plan"]["parallel"])}</ul></div>
        <div class="card"><div class="label">Sequential Proof</div><ul>{list_items(payload["execution_plan"]["sequential"])}</ul></div>
        <div class="card"><div class="label">Artifact Discipline</div><p class="sub compact">This report is intended to exist as files, not just stdout, so a later agent can remediate and rerun only affected lanes.</p></div>
      </div>
    </section>

    <section class="section">
      <h2>Lane Status</h2>
      <table>
        <thead>
          <tr>
            <th>Lane</th>
            <th>Phase</th>
            <th>Status</th>
            <th>Proof State</th>
            <th>Validation Command</th>
            <th>Next Action</th>
          </tr>
        </thead>
        <tbody>
          {"".join(lane_rows)}
        </tbody>
      </table>
    </section>

    <section class="section">
      <h2>Remediation Plan</h2>
      <div class="remediation-grid">
        {remediation_cards("repo", "Repo", "Fix missing repo-owned surfaces, commands, and deterministic local proof.")}
        {remediation_cards("environment", "Environment", "Fix startup, runtime truth, and browser verification on the primary path.")}
        {remediation_cards("integration", "Integrations", "Fix missing or unusable repo-relevant external systems and auth lanes.")}
      </div>
    </section>

    <section class="section">
      <h2>Ordered Next Actions</h2>
      <ol>{"".join(f"<li>{escape(action)}</li>" for action in payload["next_actions"]) or "<li>none</li>"}</ol>
    </section>
  </div>
</body>
</html>
"""


def pick_port(preferred_port: int) -> int:
    for candidate in range(preferred_port, preferred_port + 40):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", candidate))
            except OSError:
                continue
            return candidate
    raise RuntimeError("No free port found for readiness report server.")


def stop_existing_server(pid_file: Path) -> None:
    if not pid_file.exists():
        return
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 15)
    except Exception:
        pass


def wait_for_server(host: str, port: int, attempts: int = 20) -> None:
    for _ in range(attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(0.2)
            if probe.connect_ex((host, port)) == 0:
                return
        sleep(0.1)
    raise RuntimeError(f"Readiness report server failed to start on {host}:{port}.")


def write_artifacts(output_dir: Path, markdown: str, html: str, payload: dict[str, object]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "repo-readiness-report.md"
    json_path = output_dir / "repo-readiness-report.json"
    html_path = output_dir / "index.html"
    markdown_path.write_text(markdown)
    json_path.write_text(json.dumps(payload, indent=2))
    html_path.write_text(html)
    return {
        "output_dir": str(output_dir),
        "markdown": str(markdown_path),
        "json": str(json_path),
        "html": str(html_path),
    }


def stage_served_artifacts(source_dir: Path, serve_root: Path) -> Path:
    digest = hashlib.sha1(str(source_dir.resolve()).encode("utf-8")).hexdigest()[:8]
    target_dir = serve_root / f"{source_dir.name}-{digest}"
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("index.html", "repo-readiness-report.json", "repo-readiness-report.md"):
        source = source_dir / filename
        if source.exists():
            shutil.copy2(source, target_dir / filename)
    return target_dir


def serve_output_dir(source_dir: Path, serve_root: Path, preferred_port: int) -> dict[str, object]:
    host = "127.0.0.1"
    port = pick_port(preferred_port)
    staged_dir = stage_served_artifacts(source_dir, serve_root)
    pid_file = staged_dir / "http-server.pid"
    log_path = staged_dir / "http-server.log"
    stop_existing_server(pid_file)
    with log_path.open("ab") as log_file:
        process = Popen(
            ["python3", "-m", "http.server", str(port), "--bind", host, "--directory", str(staged_dir)],
            stdout=log_file,
            stderr=STDOUT,
            stdin=DEVNULL,
            start_new_session=True,
        )
    pid_file.write_text(str(process.pid))
    wait_for_server(host, port)
    return {
        "host": host,
        "port": port,
        "pid": process.pid,
        "url": f"http://{host}:{port}/index.html",
        "staged_dir": str(staged_dir),
        "pid_file": str(pid_file),
        "log": str(log_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a project-agnostic Codex repo readiness manifest.")
    parser.add_argument("--repo", default=os.getcwd(), help="Repo path to inspect")
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument("--codex-config", default=str(CODEX_CONFIG), help="Codex config.toml to inspect")
    parser.add_argument("--workflow-path", default=str(DEFAULT_WORKFLOW_PATH), help="Path to the public workflow CLI")
    parser.add_argument("--output-dir", help="Directory to write markdown, json, and html artifacts")
    parser.add_argument("--serve", action="store_true", help="Serve the generated output directory over a local HTTP server")
    parser.add_argument("--serve-port", type=int, default=8766, help="Preferred local port when --serve is enabled")
    parser.add_argument("--serve-dir", default="/tmp/repo-readiness-bootstrap-served", help="Temporary directory root used only for served copies of the artifacts")
    parser.add_argument("--probe-verification", action="store_true", help="Execute the strongest verification command and record the result")
    parser.add_argument("--probe-runtime", action="store_true", help="Execute the strongest runtime proof command and record the result")
    parser.add_argument("--probe-integrations", action="store_true", help="Run best-effort non-destructive probes for configured repo-relevant integrations")
    parser.add_argument("--probe-guardrails", action="store_true", help="Execute the strongest deterministic guardrail command and record the result")
    parser.add_argument("--verification-proof-note", help="Attach externally gathered verification proof from this session")
    parser.add_argument("--runtime-proof-note", help="Attach externally gathered runtime proof from this session")
    parser.add_argument("--browser-proof-note", help="Attach browser proof evidence from an external real-browser run")
    parser.add_argument("--integration-proof-note", help="Attach externally gathered integration evidence from this session")
    parser.add_argument("--guardrail-proof-note", help="Attach externally gathered guardrail proof from this session")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    codex_config_path = Path(args.codex_config).expanduser()
    workflow_path = Path(args.workflow_path).expanduser()

    snapshot = load_snapshot(repo, codex_config_path, workflow_path)
    lanes = build_lanes(snapshot)
    run_requested_probes(
        snapshot,
        lanes,
        probe_verification=args.probe_verification,
        probe_runtime=args.probe_runtime,
        probe_integrations=args.probe_integrations,
        probe_guardrails=args.probe_guardrails,
        verification_proof_note=args.verification_proof_note,
        runtime_proof_note=args.runtime_proof_note,
        browser_proof_note=args.browser_proof_note,
        integration_proof_note=args.integration_proof_note,
        guardrail_proof_note=args.guardrail_proof_note,
    )
    status = overall_status(lanes)
    payload = build_payload(snapshot, lanes, status)
    markdown = format_markdown(snapshot, lanes, status)
    html = format_html(snapshot, lanes, status)

    if args.serve and not args.output_dir:
        parser.error("--serve requires --output-dir so the HTML artifact has a stable directory.")

    if args.output_dir:
        artifact_paths = write_artifacts(Path(args.output_dir).expanduser(), markdown, html, payload)
        payload["artifacts"] = artifact_paths
        if args.serve:
            served = serve_output_dir(
                Path(args.output_dir).expanduser(),
                Path(args.serve_dir).expanduser(),
                args.serve_port,
            )
            payload["served"] = served
            payload["served_url"] = served["url"]
            Path(artifact_paths["json"]).write_text(json.dumps(payload, indent=2))

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    elif args.format == "html":
        print(html)
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
