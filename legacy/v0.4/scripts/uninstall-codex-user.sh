#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${TARGET_FRAMEWORK_HOME:?Set the explicit distribution directory}"
"$ROOT/scripts/verify-codex-user.sh"
python3 -B - "$TARGET_FRAMEWORK_HOME" <<'PYTHON'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
manifest=json.loads((root/'distribution.json').read_text())
# Remove only verified managed files; leave unrelated files and directories.
for name in manifest['payload_sha256']:
    (root/name).unlink()
(root/'distribution.json').unlink()
print('MANAGED_PAYLOAD_REMOVED=YES')
PYTHON
