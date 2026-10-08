"""Frozen T01 boundary tests. All writes stay in pytest's explicit temp root."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml

from framework.common import Blocked, canonical, digest, sha
from framework import policy as p
from framework import provenance as v
from framework import progression as g
from framework.state import KINDS, ProjectStateStore, GitStateStore, decode
from framework.gitops import GitLifecycle, terminalize
from framework.delivery import distribution, migration_next, MIGRATION_STAGES

ROOT = Path(__file__).resolve().parents[1]


def frozen_invariants():
    return v.freeze_invariants({"preimplementation": True, "facts": {"bounded": True}},
                               {name: {"fact": "bounded", "runtime_resolvable": False, "semantic": False} for name in v.INVARIANTS})


def policy(profile="hybrid_engineering"):
    return {"profile": profile, "native_baseline": True, "custom_allowed": [],
            "framework_default": {"repository": "framework", "release": "0.4.0", "commit": "a" * 40}, "preferences": []}


def pins(pol=None):
    pol = policy() if pol is None else pol
    return {**pol["framework_default"], "schemas": dict.fromkeys(KINDS, 1),
            "policy": p.project_policy(pol), "profile": pol["profile"], "capability_policy": pol}


def git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def repo_at(path):
    path.mkdir()
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Fixture")
    git(path, "config", "user.email", "fixture@invalid.example")
    git(path, "config", "commit.gpgsign", "false")
    git(path, "config", "core.hooksPath", "/dev/null")
    (path / "base").write_text("baseline\n")
    git(path, "add", "base")
    git(path, "commit", "-m", "base")
    return path


@pytest.fixture(params=["chat", "git"])
def store(request, tmp_path):
    if request.param == "chat":
        return ProjectStateStore(tmp_path, "project", "W")
    repo = repo_at(tmp_path / "repo")
    git(repo, "checkout", "-b", "work/W")
    return GitStateStore(repo, "W")


def bootstrap(store):
    auth = store.create("authorization", {"phases": list(p.PHASES), "withdrawn": False, "remote": []}, {}, author="user")
    idx = {"work_id": "W", "pins": pins(), "bindings": {"authorization": auth}}
    store.update_index(idx, None, operator="root")
    return idx


def spec(store):
    return store.create("spec", {"acceptance": "FROZEN", "authority": "Chat/to-spec", "semantics": {"unknown": "UNKNOWN", "claims": ["RQ-1"]}}, {}, author="to-spec")


def blocked(code, call):
    with pytest.raises(Blocked) as caught:
        call()
    assert caught.value.code == code


def test_c01_authority_surface_and_handoff():
    for phase in p.PHASES:
        actual = p.PROFILES["hybrid_engineering"][phase]
        p.surface("hybrid_engineering", phase, actual)
        blocked("HANDOFF_NOT_READY", lambda: p.surface("hybrid_engineering", phase, "Chat" if actual == "Codex" else "Codex"))
        p.surface("chat_engineering_full", phase, "Chat")
        blocked("HANDOFF_NOT_READY", lambda: p.surface("none", phase, actual))
    p.authority("to-spec", "to-spec", "freeze-spec", "Chat", "hybrid_engineering")
    for actor in ("root", "tool", "codex_complex_worker", "validator"):
        blocked("BLOCKED", lambda: p.authority("to-spec", actor, "freeze-spec", "Chat", "hybrid_engineering"))
    blocked("HANDOFF_NOT_READY", lambda: p.surface("codex_engineering_full", "to-spec", "Codex"))
    blocked("HANDOFF_NOT_READY", lambda: p.handoff({"artifact_type": "EVIDENCE_PACKET"}))


def test_c02_capability_runtime_eligibility_optin_and_order():
    definitions = {n: {"origin": "native", "modes": ["read"], "properties": ["symbols", "readonly"]} for n in ("a", "b")}
    observations = {n: {"provider": n, "version": "1", "mode": "read", "status": "PASS", "properties": ["symbols", "readonly"]} for n in definitions}
    registry = p.CapabilityRegistry(definitions, {n: lambda n=n: observations[n] for n in definitions})
    pol = policy()
    assert registry.resolve(pol, ["symbols"])["observed"]["provider"] == "a"
    pol["preferences"] = ["b", "a"]
    assert registry.resolve(pol, ["symbols"])["observed"]["provider"] == "b"
    observations["b"]["properties"] = []
    assert registry.resolve(pol, ["symbols"])["observed"]["provider"] == "a"
    observations["a"]["status"] = "UNKNOWN"
    blocked("REQUIRED_CAPABILITY_UNSATISFIED", lambda: registry.resolve(pol, ["symbols"]))
    blocked("REQUIRED_CAPABILITY_UNSATISFIED", lambda: registry.resolve(pol, ["symbols"], exact_provider="a"))
    definitions = {"serena": {"origin": "third-party", "modes": ["project-read-only"], "properties": ["symbols", "readonly"]}}
    observed = {"provider": "serena", "version": "1", "mode": "project-read-only", "status": "PASS", "properties": ["symbols", "readonly"], "global": False, "write_enabled": False}
    registry = p.CapabilityRegistry(definitions, {"serena": lambda: observed})
    blocked("REQUIRED_CAPABILITY_UNSATISFIED", lambda: registry.resolve(pol, ["symbols"]))
    pol["custom_allowed"] = ["serena"]
    assert registry.resolve(pol, ["symbols"])["observed"]["provider"] == "serena"
    for key in ("global", "write_enabled"):
        observed[key] = True
        blocked("REQUIRED_CAPABILITY_UNSATISFIED", lambda: registry.resolve(pol, ["symbols"]))
        observed[key] = False
    blocked("LIFECYCLE_STATE_INVALID", lambda: p.project_policy(policy() | {"phase": "review"}))


def test_c03_roles_drift_escalation_independence():
    config = {"permissions": sorted(p.ROLES["codex_fast_worker"]), "router": "codex-native", "model": "fixture-model", "effort": "medium", "runtime": "fixture-runtime"}
    receipt = p.validate_role("codex_fast_worker", config, "S")
    assert p.use_role(receipt, config, "S") == receipt
    changed = config | {"model": "replacement-model"}
    blocked("CONFIG_DRIFT_DETECTED", lambda: p.use_role(receipt, changed, "S"))
    assert p.validate_role("codex_fast_worker", changed, "S")["status"] == "PASS"
    for changed in (config | {"permissions": ["remote"]}, config | {"router": "hermes"}):
        blocked("ROLE_CONFIG_INVALID", lambda: p.validate_role("codex_fast_worker", changed, "S"))
    blocked("ROLE_CONFIG_INVALID", lambda: p.use_role(receipt, config, "new-session"))
    execution = {"role": "codex_fast_worker", "escalations": 0, "boundary_hash": "frozen", "reason": "execution_complexity"}
    escalated = p.escalate(execution, "frozen")
    blocked("BLOCKED", lambda: p.escalate(escalated, "frozen"))
    blocked("BLOCKED", lambda: p.escalate(execution, "changed"))
    for role, action in (("root", "implement"), ("codex_fast_worker", "persist"), ("codex_complex_worker", "remote"), ("codex_explorer", "candidate"), ("codex_fast_worker", "delegate")):
        blocked("BLOCKED", lambda: p.permission(role, action))
    p.permission("codex_fast_worker", "implement", ["src/module.py"], ["src"])
    for path in (".engineering/state.yaml", "../outside", ".serena/project.yml", "unowned/file"):
        blocked("BLOCKED", lambda: p.permission("codex_fast_worker", "implement", [path], ["src"]))
    p.permission("root", "persist", [".engineering/W/state.yaml"])
    blocked("BLOCKED", lambda: p.permission("root", "persist", ["src/module.py"]))
    context = {"fresh": True, "id": "review", "implementer_history": False, "role": "root"}
    p.independent_review(context, "implementation")
    for altered in (context | {"id": "implementation"}, context | {"implementer_history": True}, context | {"role": "review-agent"}):
        blocked("REVIEW_PRECONDITION_UNSATISFIED", lambda: p.independent_review(altered, "implementation"))


def test_c04_both_stores_reconstruct_exact_versions_and_atomic_index(store):
    idx = bootstrap(store)
    ref = spec(store)
    idx["bindings"]["spec"] = ref
    _, old_hash = store.index()
    store.update_index(idx, old_hash, operator="root")
    assert store.read(ref)["payload"]["semantics"]["unknown"] == "UNKNOWN"
    blocked("LIFECYCLE_STATE_INVALID", lambda: store.update_index(idx, old_hash, operator="root"))
    blocked("LIFECYCLE_STATE_INVALID", lambda: store.create("spec", store.read(ref)["payload"], {}, author="to-spec", version=1))
    assert store.versions("spec") == [1]
    # A separate interpreter reconstructs state without session memory.
    if isinstance(store, GitStateStore):
        constructor = f"GitStateStore({str(store.repo)!r}, 'W')"
    else:
        constructor = f"ProjectStateStore({str(store.root.parents[1])!r}, 'project', 'W')"
    code = f"from framework.state import *; s={constructor}; i,h=s.index(); print(s.read(i['bindings']['spec'])['payload']['acceptance'])"
    result = subprocess.run(["python3", "-B", "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "FROZEN"
    before = store.index()
    for extra in ("current_phase", "PASS", "runtime-validation"):
        bad = deepcopy(idx)
        bad[extra] = "forbidden"
        blocked("LIFECYCLE_STATE_INVALID", lambda: store.update_index(bad, before[1], operator="root"))
    assert store.index() == before
    for badref in (ref | {"work_id": "other"}, ref | {"sha256": "0" * 64}, ref | {"artifact_version": 99}, ref | {"artifact_type": "ticket"}):
        blocked("LIFECYCLE_STATE_INVALID", lambda: store.read(badref))
    blocked("LIFECYCLE_STATE_INVALID", lambda: store.read(ref, {"unexpected": ref}))


def test_c04_authorization_migration_and_spec_bytes(store):
    idx = bootstrap(store)
    obj = {"schema_version": 1, "work_id": "W", "artifact_type": "spec", "artifact_version": 1,
           "bindings": {}, "payload": {"acceptance": "FROZEN", "authority": "Chat/to-spec", "semantics": "UNKNOWN stays UNKNOWN"}}
    raw = yaml.safe_dump(obj, sort_keys=False).encode()
    ref = store.persist_spec(raw)
    assert store._read(store._path("spec", 1)) == raw
    assert store.read(ref) == obj
    newpol = policy("chat_engineering_full")
    changed = deepcopy(idx)
    changed["pins"] = pins(newpol)
    old_hash = store.index()[1]
    blocked("BLOCKED", lambda: store.update_index(changed, old_hash, operator="root"))
    migration = store.create("migration", {"old_pins": idx["pins"], "new_pins": changed["pins"], "comparison": "surface changes", "affected": ["surface"], "revalidated": ["surface"], "successful": True}, {}, author="root")
    store.update_index(changed, old_hash, operator="root", migration=migration)
    assert store.index()[0]["pins"]["profile"] == "chat_engineering_full"
    withdrawn = store.create("authorization", {"phases": [], "withdrawn": True, "remote": []}, {}, author="user")
    changed["bindings"]["authorization"] = withdrawn
    store.update_index(changed, store.index()[1], operator="root")
    assert g.derive(store, {"stops": [], "outcomes": {}, "terminal": False})["stop"] == "AUTHORIZATION_WITHDRAWN"
    assert store.read(idx["bindings"]["authorization"])["payload"]["withdrawn"] is False


def test_c04_integrity_corruption_does_not_repair(tmp_path):
    s = ProjectStateStore(tmp_path, "P", "W")
    ref = spec(s)
    path = s._path("spec", 1)
    path.write_bytes(b"broken: [")
    blocked("LIFECYCLE_STATE_INVALID", lambda: s.read(ref))
    assert path.read_bytes() == b"broken: ["
    blocked("LIFECYCLE_STATE_INVALID", lambda: decode(b"a: 1\na: 2\n"))
    blocked("LIFECYCLE_STATE_INVALID", lambda: s.create("spec", {"acceptance": "FROZEN"}, {}, author="to-spec"))
    blocked("DURABLE_STATE_STORE_UNAVAILABLE", lambda: ProjectStateStore(None, "P", "W"))


def test_c05_ownership_mapping_selective_reuse():
    graph = {"responsibilities": [{"id": "A", "owner": "T1", "meaning": "alpha", "boundary": "A-only", "kind": "local"}, {"id": "B", "owner": "T2", "meaning": "beta", "boundary": "B-only", "kind": "local"}], "tickets": ["T1", "T2"], "dependencies": {"T1": [], "T2": []}}
    assert v.responsibility_graph(graph) == graph
    duplicate = deepcopy(graph)
    duplicate["responsibilities"].append(graph["responsibilities"][0])
    blocked("STRUCTURAL_CHANGE", lambda: v.responsibility_graph(duplicate))
    cyclic = graph | {"dependencies": {"T1": ["T2"], "T2": ["T1"]}}
    blocked("STRUCTURAL_CHANGE", lambda: v.responsibility_graph(cyclic))
    old = {"responsibilities": graph["responsibilities"], "locators": {"A": "old", "B": "b"}}
    new = old | {"locators": {"A": "new", "B": "b"}}
    assert v.refine_mapping(old, new, "root") == new
    blocked("BLOCKED", lambda: v.refine_mapping(old, new, "codex_fast_worker"))
    bad = deepcopy(new)
    bad["responsibilities"][0]["owner"] = "T2"
    blocked("STRUCTURAL_CHANGE", lambda: v.refine_mapping(old, bad, "root"))
    assert v.affected(["A"], ["A"], [], True) == "STALE"
    assert v.affected(["B"], ["A"], ["B"], True) == "REUSABLE"
    assert v.affected(["B"], ["A"], [], True) == "STALE"
    assert v.affected(["B"], [], ["B"], False) == "STALE"
    boundary = dict.fromkeys(("scope", "claims", "dependencies", "contract", "shared_contracts"), "frozen")
    assert v.remediation(boundary, boundary) == "SAME_TICKET_AND_CONTRACT"
    blocked("STRUCTURAL_CHANGE", lambda: v.remediation(boundary, boundary | {"claims": "changed"}))


def test_c06_identity_and_prefrozen_triggers(tmp_path):
    repo = repo_at(tmp_path / "repo")
    commit = git(repo, "rev-parse", "HEAD")
    provider = v.git_identity_provider(repo)
    registry = v.IdentityRegistry({"git": provider})
    candidate = {"provider": "git", "id": commit, "sha256": sha(provider(commit)["bytes"]), "execution": "E1"}
    assert registry.validate(candidate)["status"] == "PASS"
    for bad in (candidate | {"id": "HEAD"}, candidate | {"sha256": "0" * 64}, candidate | {"execution": ""}, candidate | {"provider": "unregistered"}):
        blocked("IMPLEMENTATION_IDENTITY_INVALID", lambda: registry.validate(bad))
    triggers = {name: {"fact": "bounded", "runtime_resolvable": False, "semantic": False} for name in v.INVARIANTS}
    state = {"preimplementation": True, "facts": {"bounded": True}}
    assert set(v.freeze_invariants(state, triggers)["applicability"].values()) == {"APPLICABLE"}
    for value, expected in ((False, "NOT_APPLICABLE"), (None, "NOT_APPROVED")):
        assert set(v.freeze_invariants(state | {"facts": {"bounded": value}}, triggers)["applicability"].values()) == {expected}
    conditional = {k: val | {"runtime_resolvable": True} for k, val in triggers.items()}
    assert set(v.freeze_invariants(state | {"facts": {"bounded": None}}, conditional)["applicability"].values()) == {"CONDITIONALLY_APPROVED"}
    blocked("BLOCKED", lambda: v.freeze_invariants(state | {"diff": []}, triggers))


def test_c06_runtime_gates_and_timing(store):
    conditions = {"role": {"config_hash": "h"}}
    ref = store.create("runtime-validation", {"kind": "precondition", "status": "PASS", "subject": "role", "conditions": conditions["role"], "observed_at": 10}, {}, author="root")
    v.resolve_preconditions(store, [ref], conditions, 11)
    blocked("BLOCKED", lambda: v.resolve_preconditions(store, [ref], conditions, 9))
    blocked("BLOCKED", lambda: v.resolve_preconditions(store, [ref], {"role": {"config_hash": "changed"}}, 11))
    execution = store.create("execution", {"candidate": "candidate", "validations": [ref], "role": "codex_fast_worker", "model": "fixture", "effort": "fixture", "runtime": "fixture", "config_hash": "h", "context": "implementation"}, {"precondition": ref}, author="safe-implement")
    assert v.provenance_gate(store, execution, {"precondition": ref}, conditions, ["precondition"])
    blocked("REVIEW_PRECONDITION_UNSATISFIED", lambda: v.provenance_gate(store, execution, {"precondition": ref}, {}, ["precondition"]))
    blocked("REVIEW_PRECONDITION_UNSATISFIED", lambda: v.provenance_gate(store, execution, {"precondition": ref}, conditions, ["identity"]))


def test_c07_exact_packet_evidence_and_durable_review(store):
    claims = [{"id": "C1", "requirements": ["R1"], "strengths": ["behavior"], "invalidation": "affected-or-unknown-stale"}]
    ticket = store.create("ticket", {"ticket_id": "T1", "scope": ["A"], "claims": claims, "dependencies": [], "frozen": True}, {}, author="to-tickets")
    contract = store.create("contract", {"owner": "T1", "claims": claims, "invariants": frozen_invariants(), "preconditions": [], "status": "APPROVED", "frozen_before_implementation": True}, {"ticket": ticket}, author="review-contract")
    payload = {"candidate": "c1", "claims": ["C1"], "dependencies": ["A"], "observations": ["expected rejection observed"], "conditions": {"fixture": 1}, "strength": "behavior", "scope": ["A"]}
    evidence = store.create("implementation-evidence", payload, {"contract": contract}, author="safe-implement")
    packet = v.review_packet(store, contract, ticket, "c1", [evidence])
    assert packet == v.review_packet(store, contract, ticket, "c1", [evidence])
    assert packet["standards"] == store.read(contract)["payload"]
    assert packet["authoritative"] is False and packet["durable"] is False
    kwargs = {"bindings": {"contract": contract}, "allowed_scope": ["A"], "requirement": {"claim": "C1", "strengths": ["behavior"]}}
    assert v.evidence_resolve(store, evidence, **kwargs)["payload"] == payload
    blocked("EVIDENCE_REFERENCE_INVALID", lambda: v.evidence_resolve(store, evidence | {"sha256": "0" * 64}, **kwargs))
    blocked("EVIDENCE_REFERENCE_INVALID", lambda: v.evidence_resolve(store, evidence, **(kwargs | {"allowed_scope": []})))
    blocked("EVIDENCE_REFERENCE_INVALID", lambda: v.evidence_resolve(store, evidence, **(kwargs | {"requirement": {"claim": "C1", "strengths": ["runtime"]}})))
    acquired = store.create("review-evidence", payload, {"contract": contract}, author="review")
    v.blocking_review_evidence(store, {"evidence": [acquired], "candidate": "c1"})
    blocked("EVIDENCE_REFERENCE_INVALID", lambda: v.blocking_review_evidence(store, {"evidence": [acquired], "candidate": "c2"}))


def test_c08_git_isolation_mechanical_integration_and_conflict(tmp_path):
    repo = repo_at(tmp_path / "main")
    lifecycle = GitLifecycle(repo)
    base = git(repo, "rev-parse", "HEAD")
    lifecycle.control("W", base, operator="root")
    git(repo, "checkout", "work/W")
    provenance = repo / ".engineering/W"
    provenance.mkdir(parents=True)
    (provenance / "record.yaml").write_text("frozen: true\n")
    git(repo, "add", ".engineering")
    git(repo, "commit", "-m", "control")
    control = git(repo, "rev-parse", "HEAD")
    one = lifecycle.isolate("W", "T1", control, tmp_path / "t1", operator="root")
    two = lifecycle.isolate("W", "T2", control, tmp_path / "t2", operator="root")
    (Path(one["worktree"]) / "feature").write_text("bounded\n")
    assert not (Path(two["worktree"]) / "feature").exists()
    worker = GitLifecycle(one["worktree"])
    candidate = worker.candidate(one, ["feature"], ["feature"], operator="codex_fast_worker")
    assert git(Path(two["worktree"]), "rev-parse", "HEAD") == control
    # Later control bookkeeping does not enter the candidate.
    (provenance / "later.yaml").write_text("later: true\n")
    git(repo, "add", ".engineering/W/later.yaml")
    git(repo, "commit", "-m", "later control")
    assert git(Path(one["worktree"]), "rev-parse", "HEAD") == candidate
    current = git(repo, "rev-parse", "HEAD")
    tree = git(repo, "merge-tree", "--write-tree", current, candidate).splitlines()[0]
    blocked("BLOCKED", lambda: lifecycle.integrate(candidate, control, tree, operator="root", reviewed=candidate, provenance_path=".engineering/W"))
    receipt = lifecycle.integrate(candidate, current, tree, operator="root", reviewed=candidate, provenance_path=".engineering/W", frozen_checks=[lambda gitops, tree: bool(gitops.git("ls-tree", tree, "feature").stdout)])
    assert receipt["verified"] and git(repo, "show", "HEAD:feature") == "bounded"
    assert git(repo, "show", "HEAD:.engineering/W/later.yaml") == "later: true"
    # Competing edits require engineering; integration must preserve HEAD.
    conflict_base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-b", "conflicting")
    (repo / "feature").write_text("other\n")
    git(repo, "commit", "-am", "other")
    other = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "work/W")
    (repo / "feature").write_text("ours\n")
    git(repo, "commit", "-am", "ours")
    before = git(repo, "rev-parse", "HEAD")
    blocked("INTEGRATION_REQUIRED", lambda: lifecycle.integrate(other, before, "unknown", operator="root", reviewed=other, provenance_path=".engineering/W"))
    assert git(repo, "rev-parse", "HEAD") == before


def test_c08_completion_remote_cleanup_terminal(store):
    assert g.complete(["C1", "I1"], {"C1": "PASS", "I1": "PASS"}, valid_state=True, stale=False)
    for disposition in ("FAIL", "BLOCKED", "INSUFFICIENT_EVIDENCE", "CONTRACT_AMBIGUITY"):
        assert not g.complete(["C1"], {"C1": disposition}, valid_state=True, stale=False)
    assert not g.complete(["C1"], {"C1": "PASS"}, valid_state=True, stale=True)
    kwargs = {"reviewed_sha": "sha", "actual_sha": "sha", "remote": "origin", "branch": "main", "reviews_current": True, "bindings_valid": True}
    auth = {"remote": "origin", "branch": "main", "sha": "sha"}
    g.remote_gate("root", auth, **kwargs)
    blocked("REMOTE_OPERATION_BLOCKED", lambda: g.remote_gate("codex_fast_worker", auth, **kwargs))
    blocked("REMOTE_OPERATION_BLOCKED", lambda: g.remote_gate("root", None, **kwargs))
    for flag in ("conflict", "divergence", "judgment"):
        blocked("REMOTE_OPERATION_BLOCKED", lambda: g.remote_gate("root", auth, **kwargs, **{flag: True}))
    cleanup = dict(derived_complete=True, verified_integration=True, provenance_in_target=True, remote_required=True, remote_completed=True)
    g.cleanup_gate(**cleanup)
    for flag in ("derived_complete", "verified_integration", "provenance_in_target", "remote_completed"):
        blocked("BLOCKED", lambda: g.cleanup_gate(**(cleanup | {flag: False})))
    receipt = store.create("integration-receipt", {"target": "t", "candidate": "c", "provenance": ".engineering/W", "verified": True}, {}, author="root")
    terminalize(store, derived_complete=True, integration_ref=receipt, operator="root")
    blocked("BLOCKED", lambda: spec(store))


def test_c09_authorized_progression_and_all_stops(store):
    bootstrap(store)
    gates = {"stops": [], "outcomes": {}, "terminal": False}
    before = store.index()
    assert g.derive(store, gates)["next"] == "project-grill"
    assert store.index() == before
    called = []
    g.sequence(store, gates, "Chat", lambda phase, receipt: called.append(phase))
    assert called == ["project-grill"]
    blocked("HANDOFF_NOT_READY", lambda: g.sequence(store, gates, "Codex", lambda *args: None))
    for stop in g.STOPS:
        assert g.derive(store, gates | {"stops": [stop]})["stop"] == stop
    blocked("HANDOFF_NOT_READY", lambda: g.derive(store, gates | {"outcomes": {"project-grill": "COMPLETE", "to-spec": "COMPLETE"}}))
    g.chat_implementation(frozen_ticket=True, allowed_capability=True, preconditions=True, identity_available=True)
    for key in ("frozen_ticket", "allowed_capability", "preconditions", "identity_available"):
        args = dict.fromkeys(("frozen_ticket", "allowed_capability", "preconditions", "identity_available"), True)
        args[key] = False
        blocked("BLOCKED", lambda: g.chat_implementation(**args))


def test_c10_distribution_and_migration():
    chat = distribution(ROOT, "hybrid_engineering", "Chat")
    codex = distribution(ROOT, "hybrid_engineering", "Codex")
    assert set(chat["skills"]) == {"project-grill", "to-spec"}
    assert set(codex["skills"]) == set(p.PHASES[2:])
    assert chat["semantic_source"] == codex["semantic_source"]
    assert len(distribution(ROOT, "chat_engineering_full", "Chat")["skills"]) == 6
    assert not distribution(ROOT, "none", "Codex")["skills"]
    receipts = []
    for stage in MIGRATION_STAGES:
        assert migration_next(receipts, baseline_ready=True, framework_validated=True) == stage
        receipts.append({"stage": stage, "accepted": True, "rollback_validated": True, "blocking_findings": 0})
    assert migration_next(receipts, baseline_ready=True, framework_validated=True) is None
    blocked("BLOCKED", lambda: migration_next(receipts[::-1], baseline_ready=True, framework_validated=True))
    blocked("BLOCKED", lambda: migration_next([], baseline_ready=False, framework_validated=True))
    blocked("BLOCKED", lambda: migration_next(receipts[:1], baseline_ready=True, framework_validated=False))


def test_c04_atomic_failure_and_competing_writers(tmp_path, monkeypatch):
    from framework import state
    s = ProjectStateStore(tmp_path, "P", "W")
    idx = bootstrap(s)
    before = s.index()
    real_replace = state.os.replace
    def failure(*args):
        raise OSError("simulated storage interruption before publication")
    monkeypatch.setattr(state.os, "replace", failure)
    with pytest.raises(OSError, match="storage interruption"):
        s.update_index(idx, before[1], operator="root")
    monkeypatch.setattr(state.os, "replace", real_replace)
    assert s.index() == before
    assert not list(s.root.glob(".pending-*"))
    # Two independent processes requesting the same immutable version: exactly one wins.
    code = f"""from framework.state import ProjectStateStore
from framework.common import Blocked
s=ProjectStateStore({str(tmp_path)!r},'P','W')
try:
 s.create('spec',{{'acceptance':'FROZEN','authority':'Chat/to-spec','semantics':'fixed'}},{{}},author='to-spec',version=1)
 print('created')
except Blocked:
 print('rejected')
"""
    processes = [subprocess.Popen(["python3", "-B", "-c", code], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    outputs = []
    for process in processes:
        out, err = process.communicate(timeout=20)
        assert process.returncode == 0, err
        outputs.append(out.strip())
    assert sorted(outputs) == ["created", "rejected"]
    assert s.versions("spec") == [1]


def test_c03_resource_routing_does_not_change_boundary():
    resources = {role: {"model": "fixture", "effort": "medium"} for role in p.ROLES if role != "root"}
    assert p.route("read", resources)["role"] == "codex_explorer"
    assert p.route("complex", resources)["role"] == "codex_complex_worker"
    blocked("STRUCTURAL_CHANGE", lambda: p.route("complex", resources, boundary_valid=False))
    blocked("BLOCKED", lambda: p.route("unresolved", resources))


@pytest.mark.parametrize("conditional", [False, True])
def test_c09_durable_end_to_end_and_c07_review_gates(store, conditional):
    idx = bootstrap(store)
    def bind(name, ref):
        idx["bindings"][name] = ref
        store.update_index(idx, store.index()[1], operator="root")
    def next_phase(expected):
        assert g.derive_current(store)["next"] == expected
    next_phase("project-grill")
    decisions = store.create("decisions", {"resolved": True, "material_unknowns": 0, "decisions": ["frozen choice"]}, {}, author="project-grill")
    bind("decisions", decisions)
    next_phase("to-spec")
    specification = spec(store)
    bind("spec", specification)
    next_phase("to-tickets")
    graph = store.create("graph", {"responsibilities": [{"id": "A", "meaning": "local feature", "owner": "T1", "boundary": "A", "kind": "local"}], "tickets": ["T1"], "dependencies": {"T1": []}}, {"spec": specification}, author="to-tickets")
    bind("graph", graph)
    claims = [{"id": "C1", "requirements": ["R1"], "strengths": ["behavior"], "invalidation": "affected-or-unknown-stale"}]
    ticket = store.create("ticket", {"ticket_id": "T1", "scope": ["A"], "claims": claims, "dependencies": [], "frozen": True}, {}, author="to-tickets")
    bind("ticket:T1", ticket)
    next_phase("review-contract")
    structure = store.create("structure-review", {"status": "APPROVED", "graph_ref": graph}, {"graph": graph}, author="review-contract")
    bind("structure-review", structure)
    invariants = frozen_invariants()
    if conditional:
        invariants["applicability"]["RI-6"] = "CONDITIONALLY_APPROVED"
    contract = store.create("contract", {"owner": "T1", "claims": claims, "invariants": invariants, "preconditions": [], "status": "CONDITIONALLY_APPROVED" if conditional else "APPROVED", "frozen_before_implementation": True}, {"ticket": ticket}, author="review-contract")
    bind("contract:T1", contract)
    next_phase("safe-implement")
    validations, conditions = [], {}
    for kind in ("role", "capability", "identity", "precondition"):
        conditions[kind] = {"observed": "fixture-" + kind}
        validations.append(store.create("runtime-validation", {"kind": kind, "status": "PASS", "subject": kind, "conditions": conditions[kind], "observed_at": 1}, {}, author="root"))
    if conditional:
        blocked("BLOCKED", lambda: v.pre_mutation_gate(store, contract, ticket, validations, conditions, 2))
        conditions["RI-6"] = {"properties": ["resolved-before-mutation"]}
        validations.append(store.create("runtime-validation", {"kind": "precondition", "status": "PASS", "subject": "RI-6", "conditions": conditions["RI-6"], "observed_at": 1}, {}, author="root"))
        assert v.pre_mutation_gate(store, contract, ticket, validations, conditions, 2)
    execution = store.create("execution", {"candidate": "revision-1", "validations": validations,
                            "role": "codex_fast_worker", "model": "fixture", "effort": "high", "runtime": "fixture", "config_hash": "hash", "context": "implementation"}, {"contract": contract}, author="safe-implement")
    # Provider adapter for an immutable durable artifact revision; executable source
    # and document providers use the same identity contract.
    provider = v.artifact_identity_provider(store, {"revision-1": specification})
    identity = {"provider": "artifact", "id": "revision-1", "sha256": sha(provider("revision-1")["bytes"]), "execution": execution}
    registry = v.IdentityRegistry({"artifact": provider})
    payload = {"candidate": "revision-1", "claims": ["C1"], "dependencies": ["A"], "observations": ["required fixture behavior observed"], "conditions": {"isolated": True}, "strength": "behavior", "scope": ["A"]}
    evidence = store.create("implementation-evidence", payload, {"contract": contract}, author="safe-implement")
    bind("implementation-evidence:T1", evidence)
    next_phase("review")
    args = dict(contract_ref=contract, ticket_ref=ticket, candidate=identity, identity_registry=registry,
                execution_ref=execution, expected_execution_bindings={"contract": contract}, current_conditions=conditions,
                required_validation_kinds=["role", "capability", "identity", "precondition"], review_context={"fresh": True, "id": "review", "implementer_history": False, "role": "root"}, evidence_refs=[evidence])
    packet = v.prepare_review(store, **args)
    assert packet["standards"]["claims"] == claims
    blocked("REVIEW_PRECONDITION_UNSATISFIED", lambda: v.prepare_review(store, **(args | {"current_conditions": {}})))
    blocked("REVIEW_PRECONDITION_UNSATISFIED", lambda: v.prepare_review(store, **(args | {"review_context": args["review_context"] | {"id": "implementation"}})))
    blocked("IMPLEMENTATION_IDENTITY_INVALID", lambda: v.prepare_review(store, **(args | {"candidate": identity | {"execution": specification}})))
    acquired = store.create("review-evidence", payload, {"contract": contract}, author="review")
    review = store.create("review-result", {"owner": "T1", "dispositions": {"C1": "PASS"}, "evidence": [evidence, acquired], "candidate": "revision-1", "context": args["review_context"], "reuse": {}}, {"contract": contract, "execution": execution}, author="review")
    bind("review-result:T1", review)
    assert g.derive_current(store) == {"next": None, "derived_complete": True, "authoritative": False}
    # A revised local contract never silently reuses old review bindings.
    revised = store.create("contract", store.read(contract)["payload"], {"ticket": ticket}, author="review-contract")
    bind("contract:T1", revised)
    blocked("LIFECYCLE_STATE_INVALID", lambda: g.derive_current(store))


def test_c09_authorization_reduction_is_immediate(store):
    idx = bootstrap(store)
    assert g.derive_current(store)["next"] == "project-grill"
    reduced = store.create("authorization", {"phases": ["review"], "withdrawn": False, "remote": []}, {}, author="user")
    idx["bindings"]["authorization"] = reduced
    store.update_index(idx, store.index()[1], operator="root")
    assert g.derive_current(store)["stop"] == "NOT_AUTHORIZED"
    blocked("LIFECYCLE_STATE_INVALID", lambda: store.create("authorization", {"phases": ["invented"], "withdrawn": False, "remote": []}, {}, author="user"))


def test_c10_payload_and_helpers_only_explicit_destinations(tmp_path):
    from framework.__main__ import build
    destination = tmp_path / "payload"
    manifest = build(ROOT, destination, "hybrid_engineering", "Codex")
    assert set(manifest["skills"]) == set(p.PHASES[2:])
    assert not (destination / ".serena").exists()
    assert not (destination / ".engineering").exists()
    assert not (destination / "skills/project-grill").exists()
    env = os.environ | {"TARGET_FRAMEWORK_HOME": str(destination)}
    verified = subprocess.run(["bash", "scripts/verify-codex-user.sh"], cwd=ROOT, env=env, capture_output=True, text=True)
    assert verified.returncode == 0, verified.stderr
    (destination / "VERSION").write_text("drift\n")
    drift = subprocess.run(["bash", "scripts/verify-codex-user.sh"], cwd=ROOT, env=env, capture_output=True, text=True)
    assert drift.returncode != 0 and "payload drift" in drift.stderr
    blocked("BLOCKED", lambda: build(ROOT, destination, "hybrid_engineering", "Codex"))


def test_c05_durable_reuse_preserves_identity_and_rejects_unknown(store):
    payload = {"candidate": "old", "claims": ["C1"], "dependencies": ["B"], "observations": ["B verified"], "conditions": {"fixture": True}, "strength": "behavior", "scope": ["B"]}
    evidence = store.create("implementation-evidence", payload, {}, author="safe-implement")
    original = store.read(evidence)
    conditions = {"old_candidate": "old", "new_candidate": "new", "changed": ["A"], "proven_unaffected": ["B"], "known_impact": True}
    proof = store.create("runtime-validation", {"kind": "evidence-reuse", "status": "PASS", "subject": evidence["sha256"], "conditions": conditions, "observed_at": 1}, {"evidence": evidence}, author="root")
    assert v.reuse_evidence(store, evidence, "new", proof) == original
    v.blocking_review_evidence(store, {"candidate": "new", "evidence": [evidence], "reuse": {evidence["sha256"]: proof}})
    assert store.read(evidence) == original
    for change in ({"known_impact": None}, {"changed": ["B"]}, {"proven_unaffected": []}):
        invalid = store.create("runtime-validation", {"kind": "evidence-reuse", "status": "PASS", "subject": evidence["sha256"], "conditions": conditions | change, "observed_at": 2}, {"evidence": evidence}, author="root")
        blocked("EVIDENCE_REFERENCE_INVALID", lambda: v.reuse_evidence(store, evidence, "new", invalid))


def test_c05_local_artifacts_do_not_invalidate_unrelated_contracts(store):
    refs = []
    for owner in ("T1", "T2"):
        claims = [{"id": owner + ".C1", "requirements": ["R1"], "strengths": ["behavior"], "invalidation": "affected-or-unknown-stale"}]
        ticket = store.create("ticket", {"ticket_id": owner, "scope": [owner], "claims": claims, "dependencies": [], "frozen": True}, {}, author="to-tickets")
        contract = store.create("contract", {"owner": owner, "claims": claims, "invariants": frozen_invariants(), "preconditions": [], "status": "APPROVED", "frozen_before_implementation": True}, {"ticket": ticket}, author="review-contract")
        refs.append((ticket, contract))
    unchanged = store.read(refs[1][1])
    store.create("ticket", store.read(refs[0][0])["payload"] | {"scope": ["new-scope"]}, {}, author="to-tickets")
    assert store.read(refs[1][1]) == unchanged
    assert store.read(refs[1][1])["bindings"]["ticket"] == refs[1][0]


def test_c07_integration_packet_has_own_contract(store):
    claims = [{"id": "I1", "requirements": ["R1"], "strengths": ["behavior"], "invalidation": "affected-or-unknown-stale"}]
    definition = store.create("integration", {"owner": "JOIN", "claims": claims, "dependencies": ["A", "B"], "scope": ["JOIN"]}, {}, author="to-tickets")
    contract = store.create("integration-contract", {"owner": "JOIN", "claims": claims, "invariants": frozen_invariants(), "preconditions": [], "status": "APPROVED", "frozen_before_implementation": True}, {"integration": definition}, author="review-contract")
    assert v.review_packet(store, contract, definition, "candidate", [])["standards"]["claims"] == claims


def test_c06_frozen_mutation_preconditions_fail_closed(store):
    claims = [{"id": "C1", "strengths": ["behavior"], "invalidation": "affected-or-unknown-stale"}]
    ticket = store.create("ticket", {"ticket_id": "T1", "scope": ["A"], "claims": claims, "dependencies": [], "frozen": True}, {}, author="to-tickets")
    cp = {"owner": "T1", "claims": claims, "invariants": frozen_invariants(), "preconditions": [{"subject": "storage", "kind": "precondition", "properties": ["durable"], "before_mutation": True}], "status": "APPROVED", "frozen_before_implementation": True}
    contract = store.create("contract", cp, {"ticket": ticket}, author="review-contract")
    conditions = {"storage": {"properties": ["durable"], "configuration": "original"}}
    resolution = store.create("runtime-validation", {"kind": "precondition", "subject": "storage", "status": "PASS", "conditions": conditions["storage"], "observed_at": 10}, {}, author="root")
    assert v.pre_mutation_gate(store, contract, ticket, [resolution], conditions, 11)["resolutions"] == [resolution]
    blocked("BLOCKED", lambda: v.pre_mutation_gate(store, contract, ticket, [], conditions, 11))
    blocked("BLOCKED", lambda: v.pre_mutation_gate(store, contract, ticket, [resolution], {}, 11))
    blocked("BLOCKED", lambda: v.pre_mutation_gate(store, contract, ticket, [resolution], conditions, 9))


def test_c09_durable_phase_stops_cannot_be_overridden(store):
    idx = bootstrap(store)
    for stop in sorted(g.STOPS | {"BLOCKED"}):
        result = store.create("phase-result", {"phase": "safe-implement", "status": stop}, {}, author="safe-implement")
        idx["bindings"]["phase-result:safe-implement"] = result
        store.update_index(idx, store.index()[1], operator="root")
        calls = []
        assert g.sequence_current(store, "Chat", lambda *args: calls.append(args))["stop"] == stop
        assert calls == []


def test_c08_git_store_and_execution_integration_compose(tmp_path):
    repo = repo_at(tmp_path / "repo")
    lifecycle = GitLifecycle(repo)
    lifecycle.control("W", git(repo, "rev-parse", "HEAD"), operator="root")
    git(repo, "checkout", "work/W")
    state = GitStateStore(repo, "W")
    bootstrap(state)
    assert git(repo, "status", "--porcelain") == ""
    base = git(repo, "rev-parse", "HEAD")
    instance = lifecycle.isolate("W", "T1", base, tmp_path / "worker", operator="root")
    (Path(instance["worktree"]) / "source").write_text("implementation\n")
    candidate = GitLifecycle(instance["worktree"]).candidate(instance, ["source"], ["source"], operator="codex_complex_worker")
    state.create("runtime-validation", {"kind": "identity", "status": "PASS", "subject": candidate, "conditions": {"fixture": True}, "observed_at": 1}, {}, author="root")
    before = state.index()
    current = git(repo, "rev-parse", "HEAD")
    tree = git(repo, "merge-tree", "--write-tree", current, candidate).splitlines()[0]
    receipt = lifecycle.integrate(candidate, current, tree, operator="root", reviewed=candidate, provenance_path=".engineering/W")
    assert receipt["verified"] and state.index() == before
    assert git(repo, "status", "--porcelain") == ""
