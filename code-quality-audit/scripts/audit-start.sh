#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: audit-start.sh [options]

Create an isolated code-quality audit worktree and render GOAL.md/PROGRESS.md.

Options:
  --repo PATH                 Target Git repo. Default: current directory.
  --branch NAME               Audit branch name. Default: codex/audit/<repo>-<timestamp>.
  --worktree PATH             Audit worktree path. Default: <repo-parent>/.codex-audits/<repo>-<timestamp>.
  --worktree-parent PATH      Parent directory for default worktree path.
  --allow-dirty-base          Allow setup when the source repo has uncommitted changes.
                              Dirty changes are not copied into the audit worktree.
  --launch                    Launch Codex in the audit worktree after setup.
  --no-launch                 Print the Codex launch command only. Default.
  -h, --help                  Show this help.
USAGE
}

repo="."
branch=""
worktree=""
worktree_parent=""
allow_dirty_base=0
launch=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      repo="${2:?missing value for --repo}"
      shift 2
      ;;
    --branch)
      branch="${2:?missing value for --branch}"
      shift 2
      ;;
    --worktree)
      worktree="${2:?missing value for --worktree}"
      shift 2
      ;;
    --worktree-parent)
      worktree_parent="${2:?missing value for --worktree-parent}"
      shift 2
      ;;
    --allow-dirty-base)
      allow_dirty_base=1
      shift
      ;;
    --launch)
      launch=1
      shift
      ;;
    --no-launch)
      launch=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
skill_dir="$(CDPATH= cd -- "$script_dir/.." && pwd)"
template_dir="$skill_dir/templates"

root="$(git -C "$repo" rev-parse --show-toplevel)"
root="$(CDPATH= cd -- "$root" && pwd)"
repo_name="$(basename "$root")"
repo_slug="$(printf '%s' "$repo_name" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9._-' '-' | sed 's/^-//;s/-$//')"
timestamp="$(date -u '+%Y%m%dT%H%M%SZ')"
iso_timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
commit="$(git -C "$root" rev-parse HEAD)"
base_branch="$(git -C "$root" branch --show-current)"
if [[ -z "$base_branch" ]]; then
  base_branch="detached-$(git -C "$root" rev-parse --short HEAD)"
fi

dirty=0
if ! git -C "$root" diff --quiet; then
  dirty=1
fi
if ! git -C "$root" diff --cached --quiet; then
  dirty=1
fi
if [[ -n "$(git -C "$root" ls-files --others --exclude-standard)" ]]; then
  dirty=1
fi

if [[ "$dirty" -eq 1 && "$allow_dirty_base" -ne 1 ]]; then
  cat >&2 <<EOF
Source repo has uncommitted changes. Commit/stash them, or rerun with
--allow-dirty-base if auditing HEAD without dirty changes is intentional.

Repo: $root
EOF
  exit 1
fi

if [[ -z "$branch" ]]; then
  branch="codex/audit/${repo_slug}-${timestamp}"
fi

if [[ -z "$worktree_parent" ]]; then
  worktree_parent="$(dirname "$root")/.codex-audits"
fi

if [[ -z "$worktree" ]]; then
  worktree="$worktree_parent/${repo_slug}-${timestamp}"
fi

if git -C "$root" show-ref --verify --quiet "refs/heads/$branch"; then
  echo "Branch already exists: $branch" >&2
  exit 1
fi

if [[ -e "$worktree" ]]; then
  echo "Worktree path already exists: $worktree" >&2
  exit 1
fi

mkdir -p "$(dirname "$worktree")"
git -C "$root" worktree add -b "$branch" "$worktree" HEAD

python3 "$script_dir/render_audit_files.py" \
  --repo-root "$root" \
  --worktree "$worktree" \
  --base-branch "$base_branch" \
  --audit-branch "$branch" \
  --commit "$commit" \
  --iso-timestamp "$iso_timestamp" \
  --template-dir "$template_dir"

prompt="Set this as the active goal: read GOAL.md, perform the audit-only code quality review, and maintain PROGRESS.md as the durable handoff artifact. During audit mode, do not modify code and write only PROGRESS.md. Use read-only subagents for bounded parallel inspection when useful."

cat <<EOF
Audit worktree ready.

Source repo: $root
Base branch: $base_branch
Audit branch: $branch
Worktree: $worktree
Goal: $worktree/GOAL.md
Progress: $worktree/PROGRESS.md

Launch command:
codex --enable goals -C "$worktree" "$prompt"
EOF

if [[ "$launch" -eq 1 ]]; then
  exec codex --enable goals -C "$worktree" "$prompt"
fi
