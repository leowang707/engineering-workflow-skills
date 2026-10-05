#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_HOME="$CODEX_HOME/skills"
STATE_HOME="$CODEX_HOME/.engineering-workflow-skills"
BACKUP_HOME="$STATE_HOME/backups"
MANIFEST="$STATE_HOME/manifest.tsv"
SKILLS=(project-grill to-spec to-tickets review-contract safe-implement review)

"$ROOT/scripts/validate.sh"
mkdir -p "$SKILLS_HOME" "$BACKUP_HOME"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="$BACKUP_HOME/$STAMP"
mkdir -p "$BACKUP_DIR"

printf 'skill\tsource_sha256\tinstalled_path\n' > "$MANIFEST.tmp"
for skill in "${SKILLS[@]}"; do
  src="$ROOT/skills/$skill"
  dst="$SKILLS_HOME/$skill"

  if [[ -e "$dst" || -L "$dst" ]]; then
    cp -a "$dst" "$BACKUP_DIR/"
  fi

  rm -rf "$dst"
  mkdir -p "$dst"
  cp -a "$src/." "$dst/"

  sha="$(sha256sum "$src/SKILL.md" | awk '{print $1}')"
  installed_sha="$(sha256sum "$dst/SKILL.md" | awk '{print $1}')"
  if [[ "$sha" != "$installed_sha" ]]; then
    echo "Hash verification failed for $skill" >&2
    exit 1
  fi
  printf '%s\t%s\t%s\n' "$skill" "$sha" "$dst" >> "$MANIFEST.tmp"
done
mv "$MANIFEST.tmp" "$MANIFEST"

# Remove an empty backup created when nothing existed previously.
rmdir "$BACKUP_DIR" 2>/dev/null || true

echo "INSTALL=PASS"
echo "VERSION=$(cat "$ROOT/VERSION")"
echo "CODEX_HOME=$CODEX_HOME"
echo "SKILLS_HOME=$SKILLS_HOME"
echo "MANIFEST=$MANIFEST"
