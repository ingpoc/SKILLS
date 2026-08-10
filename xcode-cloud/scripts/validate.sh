#!/usr/bin/env bash
set -euo pipefail

skill_root=${1:-$(cd "$(dirname "$0")/.." && pwd)}
codex_root=$(cd "$(dirname "$0")/../../.." && pwd)
skill=$skill_root/SKILL.md
guidance=$skill_root/references/apple-guidance.md
metadata=$skill_root/agents/openai.yaml
catalog=$codex_root/skills/apple-developer/references/apple-skill-catalog.md

python3 "$codex_root/skills/.system/skill-creator/scripts/quick_validate.py" "$skill_root"
rumdl check --config "$codex_root/.rumdl.toml" "$skill" "$guidance"

for contract in \
  'use the xcode-cloud skill' \
  'load `xcode-cloud` first'
do
  rg -Fq "$contract" "$codex_root/skills/apple-developer/SKILL.md" || {
    echo "FAIL: apple-developer must route Xcode Cloud to its owner: $contract" >&2
    exit 1
  }
done

rg -Fq '| `xcode-cloud` | Apple-native CI/CD' "$catalog" || {
  echo "FAIL: Apple skill catalog must route Xcode Cloud to its owner" >&2
  exit 1
}

for contract in \
  'Never activate paid compute automatically.' \
  'Prefer Apple cloud-managed signing.' \
  'prove a clean clone' \
  'pin and checksum downloaded tools' \
  'do not require Homebrew, `rg`, or a newer Bash' \
  'Distribution: manually start' \
  'withhold tester-group assignment' \
  'runtime and visible product acceptance passed' \
  'PASS`, `BLOCKED`, or `NOT VERIFIED`'
do
  rg -Fqi "$contract" "$skill" || {
    echo "FAIL: Xcode Cloud skill contract is missing: $contract" >&2
    exit 1
  }
done

for source in \
  'https://developer.apple.com/xcode-cloud/get-started/' \
  'https://developer.apple.com/documentation/xcode/writing-custom-build-scripts' \
  'https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution' \
  'https://developer.apple.com/help/account/certificates/cloud-managed-certificates/' \
  'https://docs.github.com/en/actions/reference/security/secure-use'
do
  rg -Fq "$source" "$guidance" || {
    echo "FAIL: Xcode Cloud guidance source is missing: $source" >&2
    exit 1
  }
done

rg -Fq 'Configure safe Apple CI/CD and TestFlight delivery' "$metadata" || {
  echo "FAIL: Xcode Cloud skill metadata is stale" >&2
  exit 1
}

echo "PASS: xcode-cloud skill contracts"
