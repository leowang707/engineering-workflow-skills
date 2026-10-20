#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${TARGET_FRAMEWORK_HOME:?Set the explicit distribution directory}"
cd "$ROOT"
python3 -B - "$TARGET_FRAMEWORK_HOME" <<'PYTHON'
import json,sys
from pathlib import Path
from framework.common import require,sha
root=Path(sys.argv[1]).resolve()
manifest=json.loads((root/'distribution.json').read_text())
require(manifest['release']=='0.4.0',detail='release mismatch')
for name,expected in manifest['payload_sha256'].items():
    p=root/name
    require(p.resolve().is_relative_to(root) and not p.is_symlink(),detail='unsafe payload path')
    require(sha(p.read_bytes())==expected,detail='payload drift: '+name)
print('DISTRIBUTION_VERIFIED=YES')
PYTHON
