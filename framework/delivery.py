"""Source-only distribution and migration support. No active-runtime writes."""
from pathlib import Path
import json

from .common import require, sha
from .policy import PHASES, PROFILES

MIGRATION_STAGES = (
    "freeze-backup", "validated-framework", "surface-distribution", "execution-roles",
    "remove-duplicate-routing-review", "serena-boundary", "coexistence-end-to-end", "seal",
)
DISPOSITIONS = {
    "keep": [*PHASES, "review-agent:evidence-only", "openai-docs", "native-specialists",
             "serena:project-opt-in-read-only", "root", "codex_explorer", "codex_fast_worker", "codex_complex_worker"],
    "remove_from_codex_integration": ["hermes-local-delegator", "hermes_reviewer", "hermes-routing", "rtk-routing"],
    "do_not_add": ["model-router-skill", "Atlas", "repo-mapper", "second-router"],
}


def distribution(root, profile, surface):
    require(profile in PROFILES and surface in {"Chat", "Codex"}, "BLOCKED", "unknown distribution")
    root = Path(root)
    version = (root / "VERSION").read_text().strip()
    require(version == "0.4.0" and json.loads((root / "plugin.json").read_text())["version"] == version, detail="release metadata mismatch")
    kernels = {phase: {"source": f"skills/{phase}/SKILL.md", "sha256": sha((root / "skills" / phase / "SKILL.md").read_bytes())} for phase in PHASES}
    return {"release": version, "profile": profile, "surface": surface,
            "skills": {p: kernels[p] for p in PHASES if PROFILES[profile].get(p) == surface},
            "semantic_source": kernels}


def migration_next(receipts, *, baseline_ready, framework_validated):
    require(baseline_ready, "BLOCKED", "verified known-good recovery prerequisite")
    require(len(receipts) <= len(MIGRATION_STAGES), "BLOCKED", "extra migration stage")
    for number, receipt in enumerate(receipts):
        require(receipt["stage"] == MIGRATION_STAGES[number] and receipt["accepted"] is True
                and receipt["rollback_validated"] is True and receipt["blocking_findings"] == 0,
                "BLOCKED", "phase order/gate/recovery failed")
    if len(receipts) >= 1:
        require(framework_validated, "BLOCKED", "accepted framework required")
    return MIGRATION_STAGES[len(receipts)] if len(receipts) < len(MIGRATION_STAGES) else None
