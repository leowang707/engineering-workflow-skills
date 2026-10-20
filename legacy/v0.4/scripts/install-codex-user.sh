#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${TARGET_FRAMEWORK_HOME:?Set an explicit NEW distribution directory; no global default is provided}"
cd "$ROOT"
exec python3 -B -m framework build-distribution --source "$ROOT" --destination "$TARGET_FRAMEWORK_HOME" --profile "${LIFECYCLE_PROFILE:-hybrid_engineering}" --surface Codex
