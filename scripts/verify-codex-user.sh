#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_SKILLS_HOME="${TARGET_SKILLS_HOME:-$HOME/.agents/skills}"

SKILLS=(
  project-grill
  to-spec
  to-tickets
  review-contract
  safe-implement
  review
)

fail=0

for skill in "${SKILLS[@]}"; do
  src="$ROOT/skills/$skill/SKILL.md"
  dst="$TARGET_SKILLS_HOME/$skill/SKILL.md"

  if [[ ! -f "$dst" ]]; then
    echo "MISSING=$skill"
    fail=1
    continue
  fi

  a="$(sha256sum "$src" | awk '{print $1}')"
  b="$(sha256sum "$dst" | awk '{print $1}')"

  if [[ "$a" == "$b" ]]; then
    echo "OK=$skill"
  else
    echo "DRIFT=$skill"
    fail=1
  fi
done

if [[ "$fail" -ne 0 ]]; then
  echo "VERIFY=FAIL"
  exit 1
fi

echo "VERIFY=PASS skills=6/6"