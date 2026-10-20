#!/usr/bin/env bash
# Link every skill in this repo into the local skill folders:
#   ~/.claude/skills  (Claude Code)
#   ~/.agents/skills  (Codex and other Agent Skills harnesses)
# Each entry is a symlink into this checkout, so `git pull` keeps them current.
# Re-run after adding, removing or renaming a skill.
# Use this OR the plugin install, not both, or every skill shows up twice.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESTS=("${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}" "${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}")

for DEST in "${DESTS[@]}"; do
  if [ -L "$DEST" ]; then
    case "$(readlink -f "$DEST")" in
      "$REPO"|"$REPO"/*) echo "error: $DEST points into this repo; remove it and re-run" >&2; exit 1 ;;
    esac
  fi
  mkdir -p "$DEST"
  for src in "$REPO"/skills/*/; do
    src="${src%/}"
    [ -f "$src/SKILL.md" ] || continue
    name="$(basename "$src")"
    target="$DEST/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "skip $target: a real folder is there, not a link from this repo" >&2
      continue
    fi
    ln -sfn "$src" "$target"
    echo "linked $name -> $DEST"
  done
done
