#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPECTED=(project-grill to-spec to-tickets review-contract safe-implement review)

python3 - "$ROOT" "${EXPECTED[@]}" <<'PY'
from pathlib import Path
import json, re, sys
root = Path(sys.argv[1])
expected = sys.argv[2:]
errors = []

try:
    manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
except Exception as e:
    errors.append(f"plugin.json invalid: {e}")
else:
    if manifest.get("name") != "engineering-workflow-skills":
        errors.append("plugin.json name must be engineering-workflow-skills")

version = (root / "VERSION").read_text(encoding="utf-8").strip()
if not version:
    errors.append("VERSION is empty")

for name in expected:
    p = root / "skills" / name / "SKILL.md"
    if not p.is_file():
        errors.append(f"missing {p.relative_to(root)}")
        continue
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{name}: missing YAML front matter")
        continue
    m = re.search(r"^name:\s*([^\n]+)$", text, re.M)
    d = re.search(r"^description:\s*([^\n]+)$", text, re.M)
    if not m or m.group(1).strip() != name:
        errors.append(f"{name}: front matter name mismatch")
    if not d or not d.group(1).strip():
        errors.append(f"{name}: missing description")

actual = sorted(p.parent.name for p in (root / "skills").glob("*/SKILL.md"))
if actual != sorted(expected):
    errors.append(f"unexpected skill set: {actual}")

if errors:
    print("VALIDATION=FAIL")
    for e in errors:
        print(f"- {e}")
    raise SystemExit(1)
print(f"VALIDATION=PASS version={version} skills={len(expected)}/{len(expected)}")
PY
