#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_HOME="$CODEX_HOME/skills"
STATE_HOME="$CODEX_HOME/.engineering-workflow-skills"
MANIFEST="$STATE_HOME/manifest.tsv"

if [[ ! -f "$MANIFEST" ]]; then
  echo "UNINSTALL=NO_MANIFEST"
  echo "Nothing removed. Expected manifest: $MANIFEST"
  exit 0
fi

removed=0
while IFS=$'\t' read -r skill expected_sha installed_path; do
  [[ "$skill" == "skill" ]] && continue
  [[ -z "$skill" ]] && continue
  target="$SKILLS_HOME/$skill"
  if [[ ! -f "$target/SKILL.md" ]]; then
    continue
  fi
  current_sha="$(sha256sum "$target/SKILL.md" | awk '{print $1}')"
  if [[ "$current_sha" != "$expected_sha" ]]; then
    echo "SKIP_MODIFIED=$skill path=$target" >&2
    continue
  fi
  rm -rf "$target"
  echo "REMOVED=$skill"
  removed=$((removed + 1))
done < "$MANIFEST"

rm -f "$MANIFEST"
echo "UNINSTALL=PASS removed=$removed"
echo "Backups, if any, remain under $STATE_HOME/backups"
