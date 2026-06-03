---
name: "github-ci-fix"
description: "Use when a user asks to publish, debug, or fix a GitHub change until the PR is ready to merge. Create or reuse the PR, diagnose GitHub Actions failures with `gh`, address active merge-blocking review comments autonomously when safe, and stay in a PR-to-mergeable loop until required checks are green and no fixable blocker remains. After the PR is ready to merge, run `session-introspection` to capture anti-recurrence controls."
---

# GitHub CI Fix

This skill is the single GitHub branch-to-merge skill. Use it when the work is anywhere on the path from local branch state to a merge-ready PR.

It has two modes:

- `inspect` mode: diagnose current PR state, summarize blockers, and stop.
- `fix` mode: create or reuse the PR, then stay in a closed PR-to-mergeable loop until required checks are green and no fixable merge blocker remains.

When the user says to publish a GitHub PR, `fix CI`, `fix failing checks`, `get the PR green`, `make the PR mergeable`, or equivalent, default to `fix` mode. Also use this skill immediately after opening or materially updating a PR when CI and review state are expected to gate merge. Do not stop after one patch if the PR is still blocked.

## Prerequisites

- Require `gh` authentication: run `gh auth status`.
- Use GitHub Actions logs for GitHub-hosted checks.
- For non-GitHub Actions providers, report the external URL only.
- Treat unresolved review threads and review comments as part of the same repair lane when they are still active and plausibly blocking merge.

## Inputs

- `repo`: path inside the repo (default `.`)
- `pr`: PR number or URL (optional; defaults to current branch PR)
- user intent: `inspect` or `fix`
- optional publish intent: stage/commit/push/open PR if a PR does not already exist, or if the branch has unpublished local changes that must be pushed before status can be trusted

## Quick Start

- Preferred inspection command:
  - `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
- Add `--json` for machine-friendly output.
- Review-thread inspection fallback:
  - `gh api graphql -F query=@query.graphql ...`
  - or use an existing repo-local/bundled review-thread fetcher when available.

## Workflow

1. Verify `gh` authentication.
   - Run `gh auth status`.
   - If unauthenticated, stop and ask the user to authenticate.
2. Ensure the branch is publishable.
   - Check `git status -sb`.
   - If on the default branch and the task implies publishing, create a branch such as `codex/{description}`.
   - If local changes are part of the requested PR fix, stage and commit them intentionally.
   - Push the current branch if the remote branch is missing or behind the local branch.
3. Resolve or create the PR.
   - If the user provided a PR number or URL, use it directly.
   - Otherwise try the current branch PR: `gh pr view --json number,url,mergeable,mergeStateStatus,isDraft,reviewDecision,statusCheckRollup`.
   - If no PR exists and the task implies publish/fix-to-merge, create one with `gh pr create`, then continue in the same loop.
4. Inspect the full merge state, not just CI.
   - Read:
     - `gh pr view <pr> --json mergeable,mergeStateStatus,isDraft,reviewDecision,statusCheckRollup,latestReviews,url`
   - Distinguish:
     - required check failures or pending runs
     - unresolved active review threads/comments
     - draft state
     - branch conflicts
     - policy blocks you cannot change from the branch
5. Inspect current failing checks.
   - Preferred: use the bundled inspection script.
   - Manual fallback:
     - `gh pr view <pr> --json statusCheckRollup`
     - `gh run view <run_id> --json name,workflowName,conclusion,status,url,event,headBranch,headSha,jobs`
     - `gh run view <run_id> --log`
     - If logs are not available yet, fetch the job archive with:
       - `gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs"`
6. Inspect unresolved review threads/comments whenever the PR is still blocked after CI is green, or when review feedback is clearly part of the merge gate.
   - Prefer the bundled review-thread fetcher:
     - `python "<path-to-skill>/scripts/fetch_comments.py"`
   - Manual fallback: fetch review threads and review comments with `gh api graphql`.
   - Ignore outdated threads unless the same issue still exists in the current diff.
   - Prefer the smallest active, high-confidence fix first.
   - Do not ask the user to choose among routine comment fixes unless the comments are ambiguous, mutually incompatible, or materially change product direction.
7. Classify each blocker.
   - `branch regression`: caused by the current diff or by a new control introduced on this branch.
   - `stale test`: assertion or fixture no longer matches current behavior.
   - `environment/startup gap`: runtime or integration path issue not covered by local lightweight checks.
   - `review-blocker`: active review feedback that can be resolved safely from the branch.
   - `merge-conflict`: branch is not mergeable until base-branch drift is repaired.
   - `policy-blocker`: draft status, missing approval, or repo settings the agent cannot satisfy by editing code.
   - `external`: non-GitHub Actions or provider outside this skill's scope.
8. If in `inspect` mode:
   - Summarize the current merge blockers, whether they are CI, review, conflicts, or policy, and the smallest likely fix.
   - Stop.
9. If in `fix` mode:
   - Pick the highest-leverage fixable blocker autonomously.
   - Priority order:
     1. merge conflicts
     2. failing required checks
     3. active review comments that are still applicable and safe to address
     4. pending required checks after a push
     5. missing PR publication steps needed before status can be trusted
   - Implement the smallest fix that addresses the chosen blocker.
   - Run the closest local verification that matches the touched surface.
   - Push the branch.
   - Wait for the fresh required checks to complete.
   - Recheck the live PR state.
   - If the push created new review comments, new conflicts, or new failing checks, keep looping.
   - Do not stop after push while required checks are pending, failing, or while an active fixable review blocker remains.
   - Stop only when the PR is ready for the user to merge, or when the only remaining blocker is a real non-code blocker you cannot resolve from the branch.
10. Determine merge readiness before exit.
   - Success means all of the following:
     - `mergeable` is not `CONFLICTING`
     - required checks are green
     - no active applicable review thread remains that you should reasonably fix from the branch
     - the branch is not waiting on a fixable code change
   - If the PR is still blocked only because it is draft, missing external approval, or protected-branch policy that requires a human action, state that explicitly and stop.
11. After the PR is ready in `fix` mode:
   - Run `session-introspection`.
   - Capture only preventable friction from the PR-to-mergeable loop.
   - Prefer the narrowest anti-recurrence control: `script`, `lint`, `hook`, `workflow-doc`, or `AGENTS-trigger`.
   - Apply obvious safe controls immediately when practical.

## Guardrails

- Do not treat `fix CI` as `inspect and stop`.
- Do not split PR publication, CI repair, and routine review-comment repair across separate skills.
- Do not claim CI is green without checking the live PR status.
- Do not stop at a green subset of jobs while required checks are still pending.
- Do not stop at green CI if unresolved active review feedback still leaves the PR not ready to merge.
- Do not ask the user which routine review comment to fix first; choose autonomously unless the comments conflict or require product judgment.
- Do not turn one-time external outages into repo policy.
- Prefer repo-owned parity scripts when they exist instead of improvising new local commands.
- If a new control introduced on the branch breaks CI, fix that control before continuing.
- Ignore outdated review comments unless the same defect still exists in the current diff.
- Keep looping until the PR is merge-ready unless a real blocker requires surfacing to the user.
- If the PR is blocked only by human approval or draft status, say that clearly instead of pretending more code changes are needed.

## Bundled Resources

### scripts/inspect_pr_checks.py

Fetch failing PR checks, pull GitHub Actions logs, and extract a failure snippet. Exits non-zero when failures remain so it can be used in automation.

Usage examples:
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "123"`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "https://github.com/org/repo/pull/123" --json`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --max-lines 200 --context 40`

### scripts/fetch_comments.py

Fetch all top-level PR comments, reviews, and inline review threads for the current branch PR. Use this to inspect active review blockers without asking the user to enumerate them manually.

Usage examples:
- `python "<path-to-skill>/scripts/fetch_comments.py"`
- `python "<path-to-skill>/scripts/fetch_comments.py" > pr_comments.json`

## Exit Criteria

Do not exit `fix` mode until one of these is true:

1. The PR is ready for the user to merge.
2. The only remaining blocker is a human/policy action outside branch-edit scope, and that blocker is stated explicitly.
3. A real blocker was found and clearly surfaced with evidence.
