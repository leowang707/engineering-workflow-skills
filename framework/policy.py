"""Frozen authority, profiles and capability-property selection (R1–R20)."""
from copy import deepcopy
from pathlib import PurePosixPath

from .common import Blocked, digest, require

PHASES = ("project-grill", "to-spec", "to-tickets", "review-contract", "safe-implement", "review")
PROFILES = {
    "hybrid_engineering": dict(zip(PHASES, ("Chat", "Chat", "Codex", "Codex", "Codex", "Codex"))),
    "chat_engineering_full": dict.fromkeys(PHASES, "Chat"),
    "none": {},
}
ROLES = {
    "root": frozenset({"coordinate", "persist", "route", "integrate", "remote", "review"}),
    "codex_explorer": frozenset({"read"}),
    "codex_fast_worker": frozenset({"read", "implement", "candidate"}),
    "codex_complex_worker": frozenset({"read", "implement", "candidate"}),
}
POLICY_KEYS = {"profile", "native_baseline", "custom_allowed", "framework_default", "preferences"}


def project_policy(value):
    require(set(value) == POLICY_KEYS, detail="project policy fields")
    require(value["profile"] in PROFILES and isinstance(value["native_baseline"], bool), detail="profile/baseline")
    require(isinstance(value["custom_allowed"], list) and len(set(value["custom_allowed"])) == len(value["custom_allowed"]), detail="opt-in")
    require(isinstance(value["preferences"], list) and len(set(value["preferences"])) == len(value["preferences"]), detail="preferences")
    require(set(value["framework_default"]) == {"repository", "release", "commit"}, detail="framework default")
    return {"hash": digest(value), "snapshot": deepcopy(value)}


def surface(profile, phase, actual):
    require(profile in PROFILES and phase in PHASES and actual in {"Chat", "Codex"} and PROFILES[profile].get(phase) == actual,
            "HANDOFF_NOT_READY", "phase is not enabled on this surface")


def handoff(packet):
    require(packet.get("artifact_type") == "spec" and packet.get("payload", {}).get("acceptance") == "FROZEN"
            and packet["payload"].get("authority") == "Chat/to-spec",
            "HANDOFF_NOT_READY", "exact Chat Frozen Spec required")
    return deepcopy(packet)


def authority(phase, actor, action, surface_name, profile):
    surface(profile, phase, surface_name)
    require(actor == phase and action == {
        "project-grill": "resolve-decisions", "to-spec": "freeze-spec",
        "to-tickets": "freeze-boundaries", "review-contract": "freeze-contract",
        "safe-implement": "implement-frozen-boundary", "review": "grade-frozen-contract",
    }[phase], "BLOCKED", "six-core authority required")


def permission(role, operation, paths=(), allowed_roots=()):
    require(operation in ROLES.get(role, ()), "BLOCKED", "role has no operation authority")
    for raw in paths:
        p = PurePosixPath(raw)
        require(not p.is_absolute() and ".." not in p.parts and bool(p.parts), "BLOCKED", "unsafe mutation path")
        if operation in {"implement", "candidate"}:
            require(p.parts[0] not in {".engineering", ".serena"}, "BLOCKED", "worker control/runtime mutation")
            require(any(p == PurePosixPath(r) or PurePosixPath(r) in p.parents for r in allowed_roots),
                    "BLOCKED", "outside frozen scope")
        elif operation == "persist":
            require(p.parts[0] == ".engineering", "BLOCKED", "root production mutation")


class CapabilityRegistry:
    """Registry declarations are limits; a provider probe must verify actual properties."""
    def __init__(self, definitions, probes):
        self.definitions = deepcopy(definitions)
        self.probes = dict(probes)

    def resolve(self, policy, properties, *, exact_provider=None, tool_specific=False):
        project_policy(policy)
        require(not exact_provider or tool_specific, "REQUIRED_CAPABILITY_UNSATISFIED", "unjustified exact-tool pin")
        required = set(properties)
        require(bool(required), "REQUIRED_CAPABILITY_UNSATISFIED", "empty requirement")
        eligible = {}
        for name, definition in sorted(self.definitions.items()):
            if exact_provider and name != exact_provider:
                continue
            allowed = policy["native_baseline"] if definition["origin"] == "native" else name in policy["custom_allowed"]
            if not allowed or name not in self.probes:
                continue
            try:
                observed = self.probes[name]()
                valid = (observed["provider"] == name and bool(observed["version"])
                         and observed["mode"] in definition["modes"]
                         and observed["status"] == "PASS"
                         and required <= set(observed["properties"]) <= set(definition["properties"]))
                if name == "serena":
                    valid = valid and definition["origin"] == "third-party" and observed["mode"] == "project-read-only" and observed.get("global") is False and observed.get("write_enabled") is False
                if valid:
                    eligible[name] = deepcopy(observed)
            except (KeyError, TypeError, ValueError, OSError):
                continue
        order = list(dict.fromkeys(policy["preferences"] + sorted(eligible)))
        for name in order:
            if name in eligible:
                return {"required": sorted(required), "policy_hash": digest(policy), "observed": eligible[name]}
        raise Blocked("REQUIRED_CAPABILITY_UNSATISFIED", "no verified allowed provider")


def route(complexity, resources, *, boundary_valid=True):
    require(boundary_valid, "STRUCTURAL_CHANGE", "frozen boundary no longer sufficient")
    require(complexity in {"read", "fast", "complex"}, "BLOCKED", "unknown execution complexity")
    role = {"read": "codex_explorer", "fast": "codex_fast_worker", "complex": "codex_complex_worker"}[complexity]
    require(role in resources and set(resources[role]) == {"model", "effort"}, "ROLE_CONFIG_INVALID", "resource policy")
    return {"role": role, **deepcopy(resources[role])}


def escalate(execution, frozen_boundary_hash):
    require(execution["role"] == "codex_fast_worker" and execution["escalations"] == 0
            and execution["boundary_hash"] == frozen_boundary_hash and execution["reason"] == "execution_complexity",
            "BLOCKED", "only one unchanged-boundary fast-to-complex escalation")
    return {**deepcopy(execution), "role": "codex_complex_worker", "escalations": 1}


def validate_role(role, config, session):
    require(role in ROLES and set(config) == {"permissions", "router", "model", "effort", "runtime"}, "ROLE_CONFIG_INVALID", "unknown role/config")
    require(set(config["permissions"]) == ROLES[role] and config["router"] == "codex-native",
            "ROLE_CONFIG_INVALID", "authority drift or duplicate router")
    require(all(isinstance(config[k], str) and config[k] for k in ("model", "effort", "runtime")), "ROLE_CONFIG_INVALID", "missing runtime provenance")
    return {"role": role, "config_hash": digest(config), "session": session, "status": "PASS",
            "model": config["model"], "effort": config["effort"], "runtime": config["runtime"]}


def use_role(validation, config, session):
    require(validation.get("status") == "PASS" and validation.get("session") == session,
            "ROLE_CONFIG_INVALID", "session-start validation required")
    require(validation["config_hash"] == digest(config), "CONFIG_DRIFT_DETECTED", "revalidate before use")
    return deepcopy(validation)


def independent_review(context, implementation_context):
    require(context.get("fresh") is True and context.get("id") != implementation_context
            and context.get("implementer_history") is False and context.get("role") == "root",
            "REVIEW_PRECONDITION_UNSATISFIED", "fresh independent root context required")
