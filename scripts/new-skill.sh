#!/usr/bin/env bash
# Scaffold a new skill that works in both Claude Code and Codex.
# Usage: scripts/new-skill.sh <name> <model|user> "<Display Name>" "<short description>"
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
name="${1:?skill name (kebab-case)}"
mode="${2:?model or user}"
display="${3:?display name}"
short="${4:?short description}"

if ! [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error: name must be lowercase kebab-case" >&2; exit 1
fi
dir="$ROOT/skills/$name"
if [ -e "$dir" ]; then
  echo "error: $dir already exists" >&2; exit 1
fi

case "$mode" in
  model) invocation=""; description="$short. Use when ..." ;;
  user)  invocation="disable-model-invocation: true"$'\n'; description="$short." ;;
  *) echo "error: mode must be model or user" >&2; exit 1 ;;
esac

mkdir -p "$dir/agents"
python3 - "$ROOT/templates/SKILL.md" "$dir/SKILL.md" "$name" "$description" "$invocation" <<'PY'
import sys
src, dst, name, desc, inv = sys.argv[1:]
text = open(src, encoding="utf-8").read()
text = text.replace("__NAME__", name).replace("__DESCRIPTION__", desc).replace("__INVOCATION__", inv)
open(dst, "w", encoding="utf-8").write(text)
PY

{
  printf 'interface:\n  display_name: "%s"\n  short_description: "%s"\n' "$display" "$short"
  if [ "$mode" = user ]; then
    printf 'policy:\n  allow_implicit_invocation: false\n'
  fi
} > "$dir/agents/openai.yaml"

echo "created $dir"
echo "next: write the body, register it in skills/workflow/SKILL.md and README.md, then run python3 scripts/validate.py"
