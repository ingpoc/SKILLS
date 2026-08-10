---
name: xcode-cloud
description: Design, configure, audit, and verify Xcode Cloud CI/CD for Apple-platform projects, including private source repositories, generated Xcode projects, custom ci_scripts, managed signing, build numbering, compute usage, TestFlight delivery, and App Store Connect readback. Use when setting up Xcode Cloud, choosing an Apple CI runner, repairing cloud builds, controlling cost, or separating archive/upload success from TestFlight and device acceptance.
---

# Xcode Cloud

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill.

Use Xcode Cloud as an Apple-native CI/CD control plane without promoting a
cloud action into evidence it cannot prove. Read
[references/apple-guidance.md](references/apple-guidance.md) before setup or
when cost, roles, supported behavior, or Apple UI may have changed.

## Ownership

| Concern | Owner |
| --- | --- |
| Xcode Cloud workflows, clean-clone bootstrap, compute, and evidence gates | **this skill** |
| Team, certificates, profiles, entitlements, and App IDs | `apple-developer` |
| Product-specific commands, targets, and release acceptance | Repository skill or release owner |
| Mutable build, review, tester, and usage state | Authoritative Xcode/App Store Connect readback |

Do not duplicate bundle IDs, teams, live build status, or product-specific
commands here.

## Classify the lane

Choose one before acting:

- **audit** — read workflows, usage, roles, build state, and evidence;
- **feasibility** — connect source and prove one non-distribution clean clone;
- **validation** — build/test changes without TestFlight delivery;
- **distribution** — archive and deliver a selected revision;
- **operations** — inspect failures, usage, processing, or tester availability.

An earlier lane never proves a later one.

## Gate 1: cost and authority

1. Recheck Apple's current included compute allowance and the account's active
   plan. Never activate paid compute automatically.
2. Confirm the operator has the required Apple and source-control role.
3. Grant the Xcode Cloud GitHub App access only to the required repository.
4. Prefer Apple cloud-managed signing. Do not export `.p12` identities,
   provisioning profiles, or API keys merely to move signing into another CI.
5. Keep App Store Connect API access optional. Initial Xcode/SCM onboarding
   remains interactive; API credentials do not replace it.

Treat prices, included hours, available Xcode images, and plan entitlements as
mutable facts. Report the readback date and source.

## Gate 2: prove a clean clone

Before creating release automation:

1. Open a locally buildable project or workspace with shared, archive-enabled
   schemes and automatic signing.
2. Connect Xcode Cloud interactively and authorize the narrowest repository.
3. If a generator owns the project, keep its configuration authoritative.
4. Put bootstrap work in executable `ci_scripts/ci_post_clone.sh`; pin and checksum downloaded tools, avoid `sudo`, and make the script idempotent.
   Assume only Apple runner system tools: do not require Homebrew, `rg`, or a newer Bash.
   Exercise the check lane with `/usr/bin:/bin` and `/bin/bash` before spending
   cloud compute.
5. Run one infrastructure-validation build with distribution disabled.
6. Record the exact failure if onboarding or generated files do not survive the
   cloud lifecycle. A local generated project is not cloud proof.

Only `ci_post_clone.sh`, `ci_pre_xcodebuild.sh`, and
`ci_post_xcodebuild.sh` are recognized at the top of `ci_scripts`. Treat the
post-build hook as cleanup/reporting because it runs even after build failure.

## Gate 3: design lean workflows

- Validation: default-branch changes and pull requests that target it; cancel
  superseded work and avoid unneeded device, clean-build, and archive matrices.
- Distribution: manually start an archive workflow from a selected clean
  revision unless the repository explicitly owns an approved automatic policy.
- Multi-product release: use separate product workflows when app records have
  distinct bundle IDs. Build the intended set from the same revision/version,
  but preflight and number each record independently.
- External TestFlight: choose an App-Review-eligible destination and use the
  required clean environment. Do not use an Internal-Only archive if external
  testing or App Store submission may be required.
- Restrict workflow editing for distribution workflows where Xcode Cloud offers
  that control.

Measure task compute, not wall-clock time: parallel actions consume their
aggregate execution time. Expand triggers or matrices only after usage readback.

## Gate 4: distribute and read back

Keep these statuses independent:

1. validation passed;
2. signed archive exists with the expected team, identifiers, and entitlements;
3. upload or Xcode Cloud delivery completed;
4. App Store Connect processing completed for the expected app record;
5. the intended TestFlight group received an eligible build;
6. Beta App Review completed when required;
7. TestFlight installed the expected build on the target device;
8. runtime and visible product acceptance passed.

For a paired release, withhold tester-group assignment until every required
build completes processing and signed-artifact inspection. One successful
platform must not silently promote an incomplete release set.

Upload, processing, group assignment, APNs delivery, or a simulator run is not
TestFlight installation or rendered-device proof.

## Failure and recovery

- Generated-project onboarding fails: preserve the generator owner, record the
  cloud error, and keep the existing trusted release lane while fixing the
  smallest clean-clone defect.
- Signing fails: use `apple-developer`; do not create/revoke certificates or
  profiles without the required authorization.
- Compute is exhausted: cancel obsolete builds and reduce triggers; do not buy
  a tier without explicit approval.
- One product fails: hold the release set and rerun only the failed product from
  the same source revision when possible.
- Processing or review stalls: inspect App Store Connect status; do not rebuild
  merely because upload returned success.

Report every gate as `PASS`, `BLOCKED`, or `NOT VERIFIED`, with the readback
surface and remaining user/device action.
