#!/usr/bin/env bash
set -euo pipefail

skill_path="${1:-}"
if [[ -z "$skill_path" ]]; then
  echo "Usage: audit.sh <skill-path>" >&2
  exit 2
fi

skill_file="$skill_path/SKILL.md"
if [[ ! -f "$skill_file" ]]; then
  echo "SKILL.md not found in $skill_path" >&2
  exit 2
fi

gcount() {
  local pattern="$1"
  local file="$2"
  grep -E -c "$pattern" "$file" 2>/dev/null || true
}

gmatch() {
  local pattern="$1"
  local file="$2"
  if grep -Eq "$pattern" "$file" 2>/dev/null; then
    echo true
  else
    echo false
  fi
}

count_tree_files() {
  local dir="$1"
  if [[ -d "$dir" ]]; then
    find "$dir" -type f | wc -l | tr -d ' '
  else
    echo 0
  fi
}

count_section_items() {
  local header="$1"
  local file="$2"
  awk -v header="$header" '
    BEGIN { in_section=0; bullets=0; tables=0 }
    $0 == header { in_section=1; next }
    in_section && /^## / { in_section=0 }
    in_section && /^- / { bullets++ }
    in_section && /^\|/ { tables++ }
    END {
      if (tables >= 2) {
        tables -= 2
      } else {
        tables = 0
      }
      print bullets + tables
    }
  ' "$file"
}

count_fenced_block_lines() {
  local opener="$1"
  local file="$2"
  awk -v opener="$opener" '
    BEGIN { in_block=0; lines=0 }
    $0 == opener { in_block=1; next }
    in_block && /^```/ { in_block=0; next }
    in_block { lines++ }
    END { print lines }
  ' "$file"
}

extract_frontmatter_keys() {
  awk '
    BEGIN { fence=0; in_frontmatter=0 }
    /^---$/ {
      fence++
      if (fence == 1) {
        in_frontmatter=1
        next
      }
      if (fence == 2) {
        exit
      }
    }
    in_frontmatter && /^[A-Za-z0-9_-]+:/ {
      key=$0
      sub(/:.*/, "", key)
      print key
    }
  ' "$skill_file"
}

count_missing_references() {
  local prefix="$1"
  local count=0
  local refs
  refs="$(perl -ne 'while (m{(^|[^/[:alnum:]_.-])('"$prefix"'/[A-Za-z0-9._/-]+)}g) { print "$2\n" }' "$skill_file" | sort -u || true)"
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    if [[ ! -e "$skill_path/$ref" ]]; then
      count=$((count + 1))
    fi
  done <<< "$refs"
  echo "$count"
}

total_lines="$(wc -l < "$skill_file" | tr -d ' ')"
description_line="$(grep '^description:' "$skill_file" | head -n 1 || true)"
description_value="${description_line#description:}"
description_words="$(printf '%s\n' "$description_value" | wc -w | tr -d ' ')"

script_count="$(count_tree_files "$skill_path/scripts")"
reference_count="$(count_tree_files "$skill_path/references")"
section_count="$(gcount '^## ' "$skill_file")"
workflow_step_count="$(gcount '^### Step ' "$skill_file")"
inline_bash_blocks="$(gcount '^```bash' "$skill_file")"
inline_bash_lines="$(count_fenced_block_lines '```bash' "$skill_file")"
why_explanations="$(gcount '\b(why|because|so that|in order to)\b' "$skill_file")"
imperative_total="$(gcount '\b(MUST|NEVER|ALWAYS|Do NOT|Do not|must|never|always)\b' "$skill_file")"
imperative_density_pct="$(awk -v total="$imperative_total" -v lines="$total_lines" 'BEGIN { if (lines == 0) { printf "0.0" } else { printf "%.1f", (total / lines) * 100 } }')"
has_gotchas_section="$(gmatch '^## Gotchas' "$skill_file")"
gotcha_item_count="$(count_section_items '## Gotchas' "$skill_file")"
has_usage_section="$(gmatch '^## Usage' "$skill_file")"
has_workflow_section="$(gmatch '^## Workflow' "$skill_file")"
has_context_fork="$(gmatch 'context: ?fork' "$skill_file")"
has_agent_field="$(gmatch '^agent:' "$skill_file")"
has_metadata_field="$(gmatch '^metadata:' "$skill_file")"
missing_script_references="$(count_missing_references 'scripts')"
missing_reference_references="$(count_missing_references 'references')"

unexpected_frontmatter_keys=0
while IFS= read -r key; do
  [[ -z "$key" ]] && continue
  case "$key" in
    name|description|license|allowed-tools|metadata) ;;
    *) unexpected_frontmatter_keys=$((unexpected_frontmatter_keys + 1)) ;;
  esac
done < <(extract_frontmatter_keys)

quick_validate_script="/Users/gurusharan/.codex/skills/.system/skill-creator/scripts/quick_validate.py"
quick_validate_available=false
quick_validate_passed=false
if [[ -f "$quick_validate_script" ]]; then
  quick_validate_available=true
  if python3 "$quick_validate_script" "$skill_path" >/dev/null 2>&1; then
    quick_validate_passed=true
  fi
fi

cat <<EOF
{
  "skill_path": "$skill_path",
  "skill_file": "$skill_file",
  "total_lines": $total_lines,
  "section_count": $section_count,
  "workflow_step_count": $workflow_step_count,
  "description_words": $description_words,
  "script_count": $script_count,
  "reference_count": $reference_count,
  "inline_bash_blocks": $inline_bash_blocks,
  "inline_bash_lines": $inline_bash_lines,
  "why_explanations": $why_explanations,
  "has_gotchas_section": $has_gotchas_section,
  "gotcha_item_count": $gotcha_item_count,
  "has_usage_section": $has_usage_section,
  "has_workflow_section": $has_workflow_section,
  "has_context_fork": $has_context_fork,
  "has_agent_field": $has_agent_field,
  "has_metadata_field": $has_metadata_field,
  "unexpected_frontmatter_keys": $unexpected_frontmatter_keys,
  "missing_script_references": $missing_script_references,
  "missing_reference_references": $missing_reference_references,
  "quick_validate_available": $quick_validate_available,
  "quick_validate_passed": $quick_validate_passed,
  "imperative": {
    "total": $imperative_total,
    "density_pct": $imperative_density_pct
  }
}
EOF
