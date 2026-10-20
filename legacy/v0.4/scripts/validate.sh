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

cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python3 -B - <<'PY'
import json
from pathlib import Path
from framework.common import sha
from framework.state import ARTIFACT_SCHEMA, REF_SCHEMA
root = Path('.')
assert json.loads((root/'schemas/artifact-v1.schema.json').read_text()) == ARTIFACT_SCHEMA
assert json.loads((root/'schemas/reference-v1.schema.json').read_text()) == REF_SCHEMA
for name, expected in json.loads((root/'policies/kernel-hashes.json').read_text()).items():
    assert sha((root/name).read_bytes()) == expected, name
assert (root/'VERSION').read_text().strip() == json.loads((root/'plugin.json').read_text())['version'] == '0.4.0'
print('SOURCE_IDENTITIES=VERIFIED')
PY
FIXTURE_ROOT="$(mktemp -d /tmp/ews-framework-validation.XXXXXXXX)"
python3 -B -m pytest -q -p no:cacheprovider --basetemp="$FIXTURE_ROOT" tests/test_framework.py
sha256sum -c SHA256SUMS
