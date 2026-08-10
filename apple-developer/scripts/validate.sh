#!/usr/bin/env bash
set -euo pipefail

skill_root=${1:-$(cd "$(dirname "$0")/.." && pwd)}
codex_root=$(cd "$(dirname "$0")/../../.." && pwd)
skill=$skill_root/SKILL.md
metadata=$skill_root/agents/openai.yaml

python3 "$codex_root/skills/.system/skill-creator/scripts/quick_validate.py" "$skill_root"
rumdl check --config "$codex_root/.rumdl.toml" "$skill"

for contract in \
  'For Xcode Cloud workflow design and operations, use the xcode-cloud skill' \
  'load `xcode-cloud` first'
do
  rg -Fq "$contract" "$skill" || {
    echo "FAIL: apple-developer must route Xcode Cloud work: $contract" >&2
    exit 1
  }
done

rg -Fq 'Configure Apple signing and distribution' "$metadata" || {
  echo "FAIL: Apple skill metadata must preserve its signing boundary" >&2
  exit 1
}

echo "PASS: apple-developer Xcode Cloud routing contract"
