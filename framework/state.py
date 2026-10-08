"""Immutable YAML StateStore with exact references and atomic index CAS.

The file backend is a project-scoped durable Chat store, not conversation history.
GitStateStore uses the same contract under a dedicated control branch. Callers
must supply lifecycle-authorized payloads; storage never makes semantic decisions.
"""
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile

import jsonschema
import yaml

from .common import Blocked, canonical, digest, identifier, require, sha

KINDS = {
    "terminal-history": ("integration",),
    "phase-result": ("phase", "status"),
    "decisions": ("resolved", "material_unknowns", "decisions"),
    "authorization": ("phases", "withdrawn", "remote"),
    "spec": ("acceptance", "authority", "semantics"),
    "graph": ("responsibilities", "tickets", "dependencies"),
    "ticket": ("ticket_id", "scope", "claims", "dependencies", "frozen"),
    "integration": ("owner", "claims", "dependencies", "scope"),
    "structure-review": ("status", "graph_ref"),
    "contract": ("owner", "claims", "invariants", "preconditions", "status", "frozen_before_implementation"),
    "integration-contract": ("owner", "claims", "invariants", "preconditions", "status", "frozen_before_implementation"),
    "mapping": ("responsibilities", "locators"),
    "implementation-evidence": ("candidate", "claims", "dependencies", "observations", "conditions", "strength", "scope"),
    "review-evidence": ("candidate", "claims", "dependencies", "observations", "conditions", "strength", "scope"),
    "review-result": ("owner", "dispositions", "evidence", "candidate", "context", "reuse"),
    "execution": ("candidate", "validations", "role", "model", "effort", "runtime", "config_hash", "context"),
    "runtime-validation": ("kind", "status", "subject", "conditions", "observed_at"),
    "migration": ("old_pins", "new_pins", "comparison", "affected", "revalidated", "successful"),
    "integration-receipt": ("target", "candidate", "provenance", "verified"),
}
AUTHORS = {
    "terminal-history": "root",
    "phase-result": None,
    "decisions": "project-grill",
    "authorization": "user", "spec": "to-spec", "graph": "to-tickets", "ticket": "to-tickets",
    "integration": "to-tickets", "structure-review": "review-contract", "contract": "review-contract",
    "integration-contract": "review-contract", "mapping": "root", "implementation-evidence": "safe-implement",
    "review-evidence": "review", "review-result": "review", "execution": "safe-implement",
    "runtime-validation": "root", "migration": "root", "integration-receipt": "root",
}
REF_SCHEMA = {"type": "object", "additionalProperties": False,
              "required": ["work_id", "artifact_type", "artifact_version", "sha256"],
              "properties": {"work_id": {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$"},
                             "artifact_type": {"enum": list(KINDS)}, "artifact_version": {"type": "integer", "minimum": 1},
                             "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}}}
ARTIFACT_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
                   "additionalProperties": False,
                   "required": ["schema_version", "work_id", "artifact_type", "artifact_version", "bindings", "payload"],
                   "properties": {"schema_version": {"const": 1},
                                  **{k: v for k, v in REF_SCHEMA["properties"].items() if k != "sha256"},
                                  "bindings": {"type": "object", "additionalProperties": REF_SCHEMA},
                                  "payload": {"type": "object"}},
                   "allOf": [{"if": {"properties": {"artifact_type": {"const": k}}},
                              "then": {"properties": {"payload": {"required": list(fields),
                                       "additionalProperties": False, "properties": {f: {} for f in fields}}}}}
                             for k, fields in KINDS.items()]}
INDEX_KEYS = {"phase-result", "decisions", "authorization", "spec", "graph", "ticket", "integration", "structure-review", "contract",
              "integration-contract", "mapping", "implementation-evidence", "review-evidence", "review-result", "integration-receipt"}


class StrictLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    pairs = loader.construct_pairs(node, deep=deep)
    require(len({k for k, _ in pairs}) == len(pairs), detail="duplicate YAML key")
    return dict(pairs)


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def decode(raw):
    try:
        value = yaml.load(raw, Loader=StrictLoader)
        # Reject YAML-only types, aliases with cycles, NaNs and non-string keys.
        require(json.loads(canonical(value)) == value, detail="non-JSON YAML value")
        return value
    except (yaml.YAMLError, TypeError, ValueError, RecursionError) as error:
        raise Blocked("LIFECYCLE_STATE_INVALID", str(error)) from error


def validate(value):
    try:
        jsonschema.validate(value, ARTIFACT_SCHEMA)
    except jsonschema.ValidationError as error:
        raise Blocked("LIFECYCLE_STATE_INVALID", error.message) from error
    payload = value["payload"]
    kind = value["artifact_type"]
    array_fields = {"phases", "remote", "claims", "dependencies", "evidence", "validations", "affected", "revalidated", "scope"}
    boolean_fields = {"withdrawn", "frozen", "frozen_before_implementation", "successful", "verified", "resolved"}
    for key in array_fields & payload.keys():
        # Graph dependencies and mappings are dictionaries, other dependency lists are local.
        if key == "dependencies" and kind == "graph":
            require(isinstance(payload[key], dict), detail="graph dependency map")
        else:
            require(isinstance(payload[key], list), detail=f"{kind}.{key} must be a list")
    for key in boolean_fields & payload.keys():
        require(type(payload[key]) is bool, detail=f"{kind}.{key} must be boolean")
    if kind == "authorization":
        from .policy import PHASES
        require(set(payload["phases"]) <= set(PHASES) and len(set(payload["phases"])) == len(payload["phases"]), detail="authorization phases")
        for grant in payload["remote"]:
            require(isinstance(grant, dict) and set(grant) == {"remote", "branch", "sha"}, detail="separate exact remote grant")
    if kind == "decisions":
        require(type(payload["material_unknowns"]) is int and payload["material_unknowns"] >= 0, detail="material unknown count")
    if kind == "phase-result":
        from .policy import PHASES
        from .progression import STOPS
        require(payload["phase"] in PHASES and payload["status"] in STOPS | {"COMPLETE", "BLOCKED"}, detail="frozen phase result")
    if kind == "runtime-validation":
        require(payload["kind"] in {"role", "capability", "identity", "precondition", "evidence-reuse"}
                and payload["status"] in {"PASS", "FAIL", "UNKNOWN"}
                and isinstance(payload["conditions"], dict) and payload["subject"]
                and type(payload["observed_at"]) in {int, float}, detail="runtime validation fields")
    if kind == "graph":
        from .provenance import responsibility_graph
        responsibility_graph(payload)
    if kind == "review-result":
        require(isinstance(payload["dispositions"], dict)
                and set(payload["dispositions"].values()) <= {"PASS", "FAIL", "BLOCKED", "INSUFFICIENT_EVIDENCE", "CONTRACT_AMBIGUITY"}, detail="review dispositions")
    if kind in {"contract", "integration-contract"}:
        require(payload["status"] in {"APPROVED", "REJECTED", "CONDITIONALLY_APPROVED"}, detail="contract status")
        from .provenance import INVARIANTS
        inv = payload["invariants"]
        require(set(inv) == {"semantics_hash", "state_hash", "applicability"}
                and inv["semantics_hash"] == digest(INVARIANTS) and set(inv["applicability"]) == set(INVARIANTS), detail="pinned invariant semantics/applicability")
        require(set(inv["applicability"].values()) <= {"APPLICABLE", "NOT_APPLICABLE", "CONDITIONALLY_APPROVED", "NOT_APPROVED"}, detail="invariant trigger result")
        require(payload["status"] != "APPROVED" or "NOT_APPROVED" not in inv["applicability"].values(), detail="unresolved invariant cannot be approved")
        require(isinstance(payload["preconditions"], list), detail="frozen preconditions required")
        for condition in payload["preconditions"]:
            require(set(condition) == {"subject", "kind", "properties", "before_mutation"}
                    and condition["kind"] in {"role", "capability", "identity", "precondition"}
                    and isinstance(condition["properties"], list) and type(condition["before_mutation"]) is bool,
                    detail="precondition property contract")
    if kind in {"implementation-evidence", "review-evidence"}:
        require(payload["conditions"] and payload["observations"] and payload["strength"], detail="evidence observations and conditions required")


def reference(value, raw):
    return {k: value[k] for k in ("work_id", "artifact_type", "artifact_version")} | {"sha256": sha(raw)}


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, raw, *, immutable):
    missing = []
    ancestor = path.parent
    while not ancestor.exists():
        missing.append(ancestor)
        ancestor = ancestor.parent
    path.parent.mkdir(parents=True, exist_ok=True)
    for created in reversed(missing):
        fsync_dir(created.parent)
    fd, temp = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if immutable:
            os.link(temp, path)  # exclusive publication; never replace an artifact
        else:
            os.replace(temp, path)
        fsync_dir(path.parent)
    except FileExistsError as error:
        raise Blocked("LIFECYCLE_STATE_INVALID", "immutable version already exists") from error
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class ProjectStateStore:
    """Filesystem-backed durable project artifact provider usable from Chat tools.

    A Chat deployment exposes this API through its project-scoped file capability.
    The provider root and project ID are explicit and stable across sessions.
    """
    def __init__(self, root, project_id, work_id):
        require(root is not None, "DURABLE_STATE_STORE_UNAVAILABLE", "project store required")
        self.root = Path(root).resolve() / identifier(project_id) / identifier(work_id)
        self.work_id = work_id

    @contextmanager
    def locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / ".lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def _path(self, kind, version):
        require(kind in KINDS and type(version) is int and version > 0, detail="artifact locator")
        require(not (self.root / kind).is_symlink(), detail="symlink artifact family")
        return self.root / kind / f"{version}.yaml"

    def _read(self, path):
        try:
            require(not path.is_symlink(), detail="symlink artifact")
            return path.read_bytes()
        except OSError as error:
            raise Blocked("LIFECYCLE_STATE_INVALID", f"unavailable {path.name}: {error}") from error

    def _publish(self, path, raw, immutable):
        atomic(path, raw, immutable=immutable)

    def _terminal(self):
        p = self.root / "terminal-history" / "1.yaml"
        if p.exists():
            raw = self._read(p)
            marker = decode(raw)
            validate(marker)
            require(marker["artifact_type"] == "terminal-history" and marker["artifact_version"] == 1
                    and marker["work_id"] == self.work_id, detail="terminal identity")
            self.read(reference(marker, raw))
            receipt = self.read(marker["payload"]["integration"])
            require(receipt["artifact_type"] == "integration-receipt" and receipt["payload"]["verified"] is True, detail="invalid terminal receipt")
            return True
        return False

    def read(self, ref, expected_bindings=None, _seen=None):
        try:
            jsonschema.validate(ref, REF_SCHEMA)
        except jsonschema.ValidationError as error:
            raise Blocked("LIFECYCLE_STATE_INVALID", error.message) from error
        require(ref["work_id"] == self.work_id, detail="wrong work_id")
        raw = self._read(self._path(ref["artifact_type"], ref["artifact_version"]))
        require(sha(raw) == ref["sha256"], detail="SHA mismatch")
        obj = decode(raw)
        validate(obj)
        require(reference(obj, raw) == ref, detail="identity mismatch")
        if expected_bindings is not None:
            require(obj["bindings"] == expected_bindings, detail="parent-binding mismatch")
        seen = set() if _seen is None else set(_seen)
        require(ref["sha256"] not in seen, detail="cyclic binding")
        seen.add(ref["sha256"])
        for parent in obj["bindings"].values():
            self.read(parent, _seen=seen)
        return obj

    def create(self, kind, payload, bindings, *, author, version=None, exact_bytes=None):
        expected_author = payload.get("phase") if kind == "phase-result" else AUTHORS.get(kind)
        require(expected_author is not None and expected_author == author, "BLOCKED", "wrong semantic authority")
        with self.locked():
            require(not self._terminal(), "BLOCKED", "completed work item is terminal")
            existing = self.versions(kind)
            number = version if version is not None else (max(existing, default=0) + 1)
            obj = {"schema_version": 1, "work_id": self.work_id, "artifact_type": kind,
                   "artifact_version": number, "bindings": deepcopy(bindings), "payload": deepcopy(payload)}
            validate(obj)
            for ref in bindings.values():
                self.read(ref)
            if kind == "review-result":
                from .provenance import blocking_review_evidence
                blocking_review_evidence(self, payload)
                require("contract" in bindings and "execution" in bindings, detail="review must bind contract and execution")
                contract = self.read(bindings["contract"])["payload"]
                execution = self.read(bindings["execution"])["payload"]
                from .policy import independent_review
                independent_review(payload["context"], execution["context"])
                require(contract["status"] in {"APPROVED", "CONDITIONALLY_APPROVED"} and contract["frozen_before_implementation"] is True
                        and set(payload["dispositions"]) == {c["id"] for c in contract["claims"]}
                        and payload["owner"] == contract["owner"] and execution["candidate"] == payload["candidate"], detail="review standard/candidate mismatch")
            if kind == "terminal-history":
                require(number == 1 and bindings.get("integration") == payload["integration"], detail="terminal provenance binding")
            raw = yaml.safe_dump(obj, sort_keys=True, allow_unicode=True).encode() if exact_bytes is None else exact_bytes
            require(decode(raw) == obj, "HANDOFF_NOT_READY", "serialization would change exact packet")
            self._publish(self._path(kind, number), raw, True)
            return reference(obj, raw)

    def versions(self, kind):
        require(kind in KINDS, detail="unknown artifact family")
        return sorted(int(p.stem) for p in (self.root / kind).glob("*.yaml") if p.stem.isdecimal())

    def index(self):
        raw = self._read(self.root / "state.yaml")
        obj = decode(raw)
        self._validate_index(obj)
        return obj, sha(raw)

    def _validate_index(self, obj):
        require(set(obj) == {"work_id", "pins", "bindings"} and obj["work_id"] == self.work_id, detail="index fields")
        pins = obj["pins"]
        require(set(pins) == {"repository", "release", "commit", "schemas", "policy", "profile", "capability_policy"}, detail="incomplete framework pins")
        require(pins["schemas"] == dict.fromkeys(KINDS, 1), detail="unsupported schema pin; explicit migration required")
        require(all(isinstance(pins[k], str) and pins[k] for k in ("repository", "release", "commit")), detail="framework identity")
        require(re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", pins["commit"]), detail="exact framework commit required")
        from .policy import project_policy
        require(project_policy(pins["policy"]["snapshot"]) == pins["policy"], detail="policy identity")
        require(pins["profile"] == pins["policy"]["snapshot"]["profile"] and pins["capability_policy"] == pins["policy"]["snapshot"], detail="resolved policy differs")
        for name, ref in obj["bindings"].items():
            require(name.split(":")[0] in INDEX_KEYS and ref["artifact_type"] == name.split(":")[0], detail="forbidden index binding")
            self.read(ref)

    def update_index(self, obj, expected_hash, *, operator, migration=None):
        require(operator == "root", "BLOCKED", "root persistence only")
        with self.locked():
            require(not self._terminal(), "BLOCKED", "terminal work item")
            path = self.root / "state.yaml"
            previous, actual = self.index() if path.exists() else (None, None)
            require(actual == expected_hash, detail="index changed concurrently")
            self._validate_index(obj)
            if previous and previous["pins"] != obj["pins"]:
                require(migration is not None, "BLOCKED", "explicit migration required")
                m = self.read(migration)["payload"]
                require(migration["artifact_type"] == "migration" and m["successful"] is True
                        and m["old_pins"] == previous["pins"] and m["new_pins"] == obj["pins"]
                        and m["comparison"] and set(m["affected"]) <= set(m["revalidated"]), "BLOCKED", "incomplete migration transaction")
            self._publish(path, yaml.safe_dump(obj, sort_keys=True).encode(), False)
            return self.index()[1]

    def persist_spec(self, exact_packet):
        obj = decode(exact_packet)
        from .policy import handoff
        handoff(obj)
        return self.create("spec", obj["payload"], obj["bindings"], author="to-spec",
                           version=obj["artifact_version"], exact_bytes=exact_packet)


class GitStateStore(ProjectStateStore):
    """Local Git control-branch store. Never invokes remote operations."""
    def __init__(self, repository, work_id):
        self.repo = Path(repository).resolve()
        self.work_id = identifier(work_id)
        self.root = self.repo / ".engineering" / self.work_id
        require(self.git("branch", "--show-current") == f"work/{work_id}", "BLOCKED", "dedicated control branch required")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.repo), *args], text=True, capture_output=True)
        require(result.returncode == 0, detail=result.stderr.strip())
        return result.stdout.strip()

    @contextmanager
    def locked(self):
        # Synchronization is operational Git metadata, never untracked source or
        # authoritative lifecycle content that would contaminate integration.
        path = Path(self.git("rev-parse", "--git-path", f"ews-state-lock-{self.work_id}"))
        if not path.is_absolute():
            path = self.repo / path
        self.root.mkdir(parents=True, exist_ok=True)
        with path.open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def _read(self, path):
        raw = super()._read(path)
        relative = path.relative_to(self.repo).as_posix()
        result = subprocess.run(["git", "-C", str(self.repo), "show", f"HEAD:{relative}"], capture_output=True)
        require(result.returncode == 0 and result.stdout == raw, detail="Git store uncommitted/different content")
        return raw

    def _publish(self, path, raw, immutable):
        require(self.git("branch", "--show-current") == f"work/{self.work_id}", "BLOCKED", "control branch drift")
        require(not self.git("diff", "--cached", "--name-only") and not self.git("diff", "--name-only"), detail="Git store dirty tracked state")
        super()._publish(path, raw, immutable)
        relative = path.relative_to(self.repo).as_posix()
        self.git("add", "--", relative)
        self.git("commit", "-m", f"state: {self.work_id} {relative}", "--", relative)
