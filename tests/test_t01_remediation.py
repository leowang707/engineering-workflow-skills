"""Behavioral regressions for frozen R21, R27, R54 and R68-R69.

The standard validation entry point imports these tests without changing its
checks. Fixtures and killed child processes operate only in pytest's temp root.
"""
from copy import deepcopy
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import time

import pytest
import yaml

from framework.common import Blocked, sha
from framework.state import KINDS, GitStateStore, ProjectStateStore
from framework import policy as p, progression as g, provenance as v

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def make_store(root, backend):
    if backend == "chat":
        return ProjectStateStore(root, "project", "W")
    repo = root / "repo"
    repo.mkdir(parents=True)
    for args in [("init", "-b", "main"), ("config", "user.name", "Fixture"),
                 ("config", "user.email", "fixture@invalid.example"),
                 ("config", "commit.gpgsign", "false"), ("config", "core.hooksPath", "/dev/null")]:
        git(repo, *args)
    (repo / "base").write_text("baseline\n")
    git(repo, "add", "base")
    git(repo, "commit", "-m", "baseline")
    git(repo, "checkout", "-b", "work/W")
    return GitStateStore(repo, "W")


@pytest.fixture(params=["chat", "git"])
def remediation_store(request, tmp_path):
    return make_store(tmp_path, request.param)


def bootstrap(store):
    pol = {"profile": "hybrid_engineering", "native_baseline": True, "custom_allowed": [],
           "framework_default": {"repository": "fixture", "release": "0.4.0", "commit": "a" * 40}, "preferences": []}
    auth = store.create("authorization", {"phases": list(p.PHASES), "withdrawn": False, "remote": []}, {}, author="user")
    idx = {"work_id": "W", "pins": {**pol["framework_default"], "schemas": dict.fromkeys(KINDS, 1),
           "policy": p.project_policy(pol), "profile": pol["profile"], "capability_policy": pol}, "bindings": {"authorization": auth}}
    store.update_index(idx, None, operator="root")
    return idx


def observations(value):
    path = os.environ.get("T01_OBSERVATIONS")
    if path:
        with open(path, "a") as stream:
            stream.write(json.dumps(value, sort_keys=True) + "\n")


def definition(store, owner, dependencies):
    claims = [{"id": owner + ".C1", "requirements": ["R1"], "strengths": ["behavior"], "invalidation": "affected-or-unknown-stale"}]
    ticket = store.create("ticket", {"ticket_id": owner, "scope": [owner], "claims": claims,
                          "dependencies": dependencies, "frozen": True}, {}, author="to-tickets")
    inv = v.freeze_invariants({"preimplementation": True, "facts": {"bounded": True}},
          {name: {"fact": "bounded", "runtime_resolvable": False, "semantic": False} for name in v.INVARIANTS})
    contract = store.create("contract", {"owner": owner, "claims": claims, "invariants": inv, "preconditions": [],
                            "status": "APPROVED", "frozen_before_implementation": True}, {"ticket": ticket}, author="review-contract")
    return ticket, contract


def review_setup(store, ticket, contract):
    validations, conditions = [], {}
    for kind in ("role", "identity"):
        conditions[kind] = {"fixture": kind}
        validations.append(store.create("runtime-validation", {"kind": kind, "status": "PASS", "subject": kind,
            "conditions": conditions[kind], "observed_at": 1}, {}, author="root"))
    execution = store.create("execution", {"candidate": "revision-1", "validations": validations, "role": "codex_fast_worker",
        "model": "fixture", "effort": "high", "runtime": "fixture", "config_hash": "hash", "context": "implementation"},
        {"contract": contract}, author="safe-implement")
    provider = v.artifact_identity_provider(store, {"revision-1": ticket})
    candidate = {"provider": "artifact", "id": "revision-1", "sha256": sha(provider("revision-1")["bytes"]), "execution": execution}
    owner = store.read(ticket)["payload"]["ticket_id"]
    payload = {"candidate": "revision-1", "claims": [owner + ".C1"], "dependencies": [owner],
        "observations": ["controlled fixture behavior"], "conditions": {"fixture": True}, "strength": "behavior", "scope": [owner]}
    evidence = store.create("implementation-evidence", payload, {"contract": contract}, author="safe-implement")
    context = {"fresh": True, "id": "review", "implementer_history": False, "role": "root"}
    args = dict(contract_ref=contract, ticket_ref=ticket, candidate=candidate, identity_registry=v.IdentityRegistry({"artifact": provider}),
        execution_ref=execution, expected_execution_bindings={"contract": contract}, current_conditions=conditions,
        required_validation_kinds=["role", "identity"], review_context=context, evidence_refs=[evidence])
    assert v.prepare_review(store, **args)["evidence"] == [evidence]
    return args, execution, evidence, payload, context


@pytest.mark.parametrize("stage", ["commit-tree", "before-ref", "after-ref", "after-file", "after-index"])
@pytest.mark.parametrize("operation", ["index", "immutable"])
def test_t01_git_process_interruption_restart(tmp_path, stage, operation):
    store = make_store(tmp_path, "git")
    idx = bootstrap(store)
    next_auth = store.create("authorization", {"phases": [], "withdrawn": True, "remote": []}, {}, author="user")
    before = store.index()
    old_head = git(store.repo, "rev-parse", "HEAD")
    idx["bindings"]["authorization"] = next_auth
    code = f"""
import os, signal
from pathlib import Path
from framework import state
from framework.state import GitStateStore
s = GitStateStore({str(store.repo)!r}, 'W')
original = s.git
def interrupted(*args):
    if ({stage!r} == 'commit-tree' and args[0] == 'commit-tree') or ({stage!r} == 'before-ref' and args[0] == 'update-ref'):
        os.kill(os.getpid(), signal.SIGKILL)
    result = original(*args)
    if ({stage!r} == 'after-ref' and args[0] == 'update-ref') or ({stage!r} == 'after-index' and args[0] == 'update-index'):
        os.kill(os.getpid(), signal.SIGKILL)
    return result
s.git = interrupted
atomic = state.atomic
def interrupted_file(path, raw, **kwargs):
    atomic(path, raw, **kwargs)
    if {stage!r} == 'after-file' and path.name != 'ews-state-transaction.json':
        os.kill(os.getpid(), signal.SIGKILL)
state.atomic = interrupted_file
if {operation!r} == 'index':
    s.update_index({idx!r}, {before[1]!r}, operator='root')
else:
    s.create('spec', {{'acceptance':'FROZEN','authority':'Chat/to-spec','semantics':'fixed'}}, {{}}, author='to-spec', version=1)
raise AssertionError('kill point not reached')
"""
    result = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == -9, result.stderr
    published = stage in {"after-ref", "after-file", "after-index"}
    interrupted_head = git(store.repo, "rev-parse", "HEAD")
    assert (interrupted_head != old_head) == published
    # Fresh-process reconstruction, not an exception handler in the killed writer.
    check = f"""
import json
from framework.state import GitStateStore
s=GitStateStore({str(store.repo)!r},'W')
print(json.dumps({{'index':s.index(), 'versions':s.versions('spec')}}))
"""
    restart = subprocess.run([sys.executable, "-B", "-c", check], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert restart.returncode == 0, restart.stderr
    rebuilt = json.loads(restart.stdout)
    assert rebuilt["index"][0] == (idx if operation == "index" and published else before[0])
    assert rebuilt["versions"] == ([1] if operation == "immutable" and published else [])
    if operation == "immutable" and published:
        refs = store.versions("spec")
        assert refs == [1]
        assert git(store.repo, "show", "HEAD:.engineering/W/spec/1.yaml")
    assert git(store.repo, "status", "--porcelain") == ""
    observations({"test": "F01-process-restart", "stage": stage, "operation": operation, "killed_returncode": result.returncode,
                  "old_head": old_head, "interrupted_head": interrupted_head, "restarted_head": git(store.repo, "rev-parse", "HEAD"),
                  "result": "next" if published else "previous", "index_readable": True, "git_status": "clean"})


@pytest.mark.parametrize("command", ["commit-tree", "update-ref"])
def test_t01_git_commit_failure_preserves_previous(tmp_path, command):
    store = make_store(tmp_path, "git")
    idx = bootstrap(store)
    auth = store.create("authorization", {"phases": [], "withdrawn": True, "remote": []}, {}, author="user")
    before = store.index()
    head = git(store.repo, "rev-parse", "HEAD")
    idx["bindings"]["authorization"] = auth
    original = store.git
    def failure(*args):
        if args[0] == command:
            raise Blocked("LIFECYCLE_STATE_INVALID", "injected commit/publication failure")
        return original(*args)
    store.git = failure
    with pytest.raises(Blocked):
        store.update_index(idx, before[1], operator="root")
    rebuilt = GitStateStore(store.repo, "W")
    assert rebuilt.index() == before
    assert git(store.repo, "rev-parse", "HEAD") == head
    assert git(store.repo, "status", "--porcelain") == ""


def test_t01_git_surviving_ref_child_restart(tmp_path):
    store = make_store(tmp_path, "git")
    idx = bootstrap(store)
    auth = store.create("authorization", {"phases": [], "withdrawn": True, "remote": []}, {}, author="user")
    before = store.index()
    idx["bindings"]["authorization"] = auth
    ready, release, started = [tmp_path / name for name in ("child-ready", "child-release", "restart-started")]
    child_code = f"""
from pathlib import Path
import json, subprocess, sys, time
Path({str(ready)!r}).write_text('ready')
while not Path({str(release)!r}).exists(): time.sleep(.01)
result=subprocess.run(json.loads(sys.argv[1]), pass_fds=tuple(json.loads(sys.argv[2])))
raise SystemExit(result.returncode)
"""
    writer_code = f"""
import json, sys
from framework import state
from framework.state import GitStateStore
s=GitStateStore({str(store.repo)!r},'W')
run=state.subprocess.run
def delayed(args, **kwargs):
 if 'update-ref' in args:
  return run([sys.executable,'-B','-c',{child_code!r},json.dumps(args),json.dumps(kwargs.get('pass_fds',()))], **kwargs)
 return run(args, **kwargs)
state.subprocess.run=delayed
s.update_index({idx!r}, {before[1]!r}, operator='root')
"""
    writer = subprocess.Popen([sys.executable, "-B", "-c", writer_code], cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def wait_for(path):
        deadline = time.monotonic() + 30
        while not path.exists():
            assert time.monotonic() < deadline, f"timed out awaiting {path.name}"
            time.sleep(.01)
    restart = None
    try:
        wait_for(ready)
        os.kill(writer.pid, signal.SIGKILL)
        restart_code = f"""
import json
from pathlib import Path
from framework import state
from framework.state import GitStateStore
s=GitStateStore({str(store.repo)!r},'W')
flock=state.fcntl.flock
def observed(*args):
 Path({str(started)!r}).write_text('entering lock')
 return flock(*args)
state.fcntl.flock=observed
print(json.dumps(s.index()))
"""
        restart = subprocess.Popen([sys.executable, "-B", "-c", restart_code], cwd=ROOT,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        wait_for(started)
        blocked = False
        try:
            restart.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            blocked = True
    finally:
        release.write_text("release")
        writer_out, writer_err = writer.communicate(timeout=30)
    assert writer.returncode == -9, writer_err
    assert restart is not None
    stdout, stderr = restart.communicate(timeout=30)
    assert restart.returncode == 0, stderr
    assert blocked, "restart passed the lock while the ref writer still survived"
    assert json.loads(stdout)[0] == idx
    assert GitStateStore(store.repo, "W").index()[0] == idx
    assert git(store.repo, "status", "--porcelain") == ""
    observations({"test": "F01-surviving-ref-child", "writer_returncode": -9,
                  "restart_waited_for_child": blocked, "result": "committed next", "git_status": "clean"})


def test_t01_git_unrelated_state_and_competing_ref(tmp_path):
    store = make_store(tmp_path, "git")
    idx = bootstrap(store)
    auth = store.create("authorization", {"phases": [], "withdrawn": True, "remote": []}, {}, author="user")
    before = store.index()
    (store.repo / "base").write_text("staged unrelated\n")
    git(store.repo, "add", "base")
    staged = git(store.repo, "show", ":base")
    (store.repo / "base").write_text("unstaged unrelated\n")
    (store.repo / "untracked").write_text("untracked unrelated\n")
    idx["bindings"]["authorization"] = auth
    store.update_index(idx, before[1], operator="root")
    assert git(store.repo, "show", ":base") == staged
    assert (store.repo / "base").read_text() == "unstaged unrelated\n"
    assert (store.repo / "untracked").read_text() == "untracked unrelated\n"
    assert git(store.repo, "show", "HEAD:base") == "baseline"
    # An external ref writer winning between preparation and CAS is retained.
    before = store.index()
    idx["bindings"]["authorization"] = before[0]["bindings"]["authorization"]
    idx["bindings"]["spec"] = store.create("spec", {"acceptance": "FROZEN", "authority": "Chat/to-spec", "semantics": "fixed"}, {}, author="to-spec")
    original = store.git
    winner = []
    def compete(*args):
        if args[0] == "update-ref":
            old = original("rev-parse", "HEAD")
            other = original("commit-tree", original("rev-parse", "HEAD^{tree}"), "-p", old, "-m", "external writer")
            original("update-ref", "refs/heads/work/W", other, old)
            winner.append(other)
        return original(*args)
    store.git = compete
    with pytest.raises(Blocked):
        store.update_index(idx, before[1], operator="root")
    assert GitStateStore(store.repo, "W").index() == before
    assert git(store.repo, "rev-parse", "HEAD") == winner[0]
    assert git(store.repo, "show", ":base") == staged


@pytest.mark.parametrize("operation", ["index", "immutable"])
def test_t01_concurrent_writers_and_cas(remediation_store, operation):
    store = remediation_store
    idx = bootstrap(store)
    auth = store.create("authorization", {"phases": [], "withdrawn": True, "remote": []}, {}, author="user")
    before = store.index()
    idx["bindings"]["authorization"] = auth
    constructor = f"GitStateStore({str(store.repo)!r},'W')" if isinstance(store, GitStateStore) else f"ProjectStateStore({str(store.root.parents[1])!r},'project','W')"
    code = f"""
from framework.state import GitStateStore, ProjectStateStore
from framework.common import Blocked
s={constructor}
try:
 if {operation!r} == 'index': s.update_index({idx!r}, {before[1]!r}, operator='root')
 else: s.create('spec',{{'acceptance':'FROZEN','authority':'Chat/to-spec','semantics':'fixed'}},{{}},author='to-spec',version=1)
 print('created')
except Blocked: print('rejected')
"""
    children = [subprocess.Popen([sys.executable, "-B", "-c", code], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    outputs = []
    for child in children:
        stdout, stderr = child.communicate(timeout=30)
        assert child.returncode == 0, stderr
        outputs.append(stdout.strip())
    assert sorted(outputs) == ["created", "rejected"]
    assert store.index()[0] == (idx if operation == "index" else before[0])
    assert store.versions("spec") == ([1] if operation == "immutable" else [])
    observations({"test": "CAS", "backend": type(store).__name__, "operation": operation, "outputs": sorted(outputs)})


def test_t01_integrity_never_repaired(remediation_store):
    store = remediation_store
    bootstrap(store)
    path = store.root / "state.yaml"
    path.write_bytes(path.read_bytes() + b"unauthorized: corruption\n")
    corrupt = path.read_bytes()
    with pytest.raises(Blocked) as error:
        store.index()
    assert error.value.code == "LIFECYCLE_STATE_INVALID"
    assert path.read_bytes() == corrupt


@pytest.mark.parametrize("tamper", ["journal", "working", "index"])
def test_t01_interrupted_transaction_corruption_rejected(tmp_path, tamper):
    store = make_store(tmp_path, "git")
    idx = bootstrap(store)
    auth = store.create("authorization", {"phases": [], "withdrawn": True, "remote": []}, {}, author="user")
    before = store.index()
    idx["bindings"]["authorization"] = auth
    original = store.git
    def interrupt(*args):
        result = original(*args)
        if args[0] == "update-ref":
            raise Blocked("LIFECYCLE_STATE_INVALID", "interrupt after ref")
        return result
    store.git = interrupt
    with pytest.raises(Blocked):
        store.update_index(idx, before[1], operator="root")
    journal = store._journal_path()
    path = store.root / "state.yaml"
    if tamper == "journal":
        journal.write_bytes(journal.read_bytes() + b"corrupt")
    else:
        path.write_bytes(b"corrupt\n")
        if tamper == "index":
            git(store.repo, "add", ".engineering/W/state.yaml")
            path.write_bytes(before[0] and git(store.repo, "show", "HEAD~1:.engineering/W/state.yaml").encode() + b"\n")
    bytes_before = path.read_bytes(), journal.read_bytes()
    head = git(store.repo, "rev-parse", "HEAD")
    with pytest.raises(Blocked) as error:
        GitStateStore(store.repo, "W").index()
    assert error.value.code == "LIFECYCLE_STATE_INVALID"
    assert (path.read_bytes(), journal.read_bytes()) == bytes_before
    assert git(store.repo, "rev-parse", "HEAD") == head


@pytest.mark.parametrize("disposition", ["FAIL", "BLOCKED", "INSUFFICIENT_EVIDENCE", "CONTRACT_AMBIGUITY", "PASS", "MISSING_REVIEW", "TRANSITIVE"])
def test_t01_dependency_and_parallel_progression(remediation_store, disposition):
    store = remediation_store
    idx = bootstrap(store)
    def bind(name, ref):
        idx["bindings"][name] = ref
    bind("decisions", store.create("decisions", {"resolved": True, "material_unknowns": 0, "decisions": ["resolved"]}, {}, author="project-grill"))
    spec = store.create("spec", {"acceptance": "FROZEN", "authority": "Chat/to-spec", "semantics": "fixed"}, {}, author="to-spec")
    bind("spec", spec)
    deps = {"T1": [], "T2": ["T1"], "T3": ["T2"] if disposition == "TRANSITIVE" else []}
    graph = store.create("graph", {"responsibilities": [{"id": owner, "meaning": owner, "owner": owner, "boundary": owner, "kind": "local"} for owner in deps],
                                   "tickets": list(deps), "dependencies": deps}, {"spec": spec}, author="to-tickets")
    bind("graph", graph)
    for owner in deps:
        ticket, contract = definition(store, owner, deps[owner])
        bind("ticket:" + owner, ticket)
        bind("contract:" + owner, contract)
        if owner == "T1":
            t1, c1 = ticket, contract
    bind("structure-review", store.create("structure-review", {"status": "APPROVED", "graph_ref": graph}, {"graph": graph}, author="review-contract"))
    args, execution, evidence, payload, context = review_setup(store, t1, c1)
    bind("implementation-evidence:T1", evidence)
    outcome = "FAIL" if disposition == "TRANSITIVE" else disposition
    if disposition != "MISSING_REVIEW":
        bind("review-result:T1", store.create("review-result", {"owner": "T1", "dispositions": {"T1.C1": outcome}, "evidence": [evidence],
             "candidate": "revision-1", "context": context, "reuse": {}}, {"contract": c1, "execution": execution}, author="review"))
    # Remove unrelated parallel branch to exercise the exact prior counterexample.
    restricted = deepcopy(store.read(graph)["payload"])
    restricted["tickets"] = ["T2", "T1"]  # dependency logic must not depend on list order
    restricted["dependencies"].pop("T3")
    restricted["responsibilities"] = restricted["responsibilities"][:2]
    short_graph = store.create("graph", restricted, {"spec": spec}, author="to-tickets")
    bind("graph", short_graph)
    bind("structure-review", store.create("structure-review", {"status": "APPROVED", "graph_ref": short_graph}, {"graph": short_graph}, author="review-contract"))
    store.update_index(idx, store.index()[1], operator="root")
    before = store.index()
    eligibility = g.derive_current(store)
    calls = []
    g.sequence_current(store, "Codex", lambda phase, receipt: calls.append(phase))
    expected = ["safe-implement"] if disposition == "PASS" else ["review"] if disposition == "MISSING_REVIEW" else []
    assert calls == expected
    if not expected:
        assert eligibility == {"next": None, "stop": outcome}
    assert store.index() == before
    # With an unrelated authorized branch present, FAIL/BLOCKED/insufficiency
    # stops the dependent branch while T3 can still run.
    bind("graph", graph)
    bind("structure-review", store.create("structure-review", {"status": "APPROVED", "graph_ref": graph}, {"graph": graph}, author="review-contract"))
    if disposition == "TRANSITIVE":
        t2, c2 = idx["bindings"]["ticket:T2"], idx["bindings"]["contract:T2"]
        _, execution2, evidence2, _, context2 = review_setup(store, t2, c2)
        bind("implementation-evidence:T2", evidence2)
        bind("review-result:T2", store.create("review-result", {"owner": "T2", "dispositions": {"T2.C1": "PASS"}, "evidence": [evidence2],
             "candidate": "revision-1", "context": context2, "reuse": {}}, {"contract": c2, "execution": execution2}, author="review"))
    store.update_index(idx, store.index()[1], operator="root")
    if disposition == "TRANSITIVE":
        calls = []
        g.sequence_current(store, "Codex", lambda phase, receipt: calls.append(phase))
        assert calls == []
        assert g.derive_current(store) == {"next": None, "stop": "FAIL"}
    elif disposition not in {"PASS", "MISSING_REVIEW"}:
        assert g.derive_current(store)["next"] == "safe-implement"
        calls = []
        g.sequence_current(store, "Codex", lambda phase, receipt: calls.append(phase))
        assert calls == ["safe-implement"]
        reduced = store.create("authorization", {"phases": ["review"], "withdrawn": False, "remote": []}, {}, author="user")
        bind("authorization", reduced)
        store.update_index(idx, store.index()[1], operator="root")
        assert g.derive_current(store) == {"next": None, "stop": "NOT_AUTHORIZED"}
    observations({"test": "F02", "backend": type(store).__name__, "prerequisite": disposition, "dependent_invocations": expected,
                  "read_only": True, "unrelated_parallel_eligible": disposition not in {"PASS", "MISSING_REVIEW", "TRANSITIVE"}})


@pytest.mark.parametrize("invalid", ["nonmember", "empty-claims", "mixed-claims", "scope", "strength", "binding", "hash", "work", "version", "type", "reference-schema", "artifact-schema", "reuse"])
def test_t01_exact_loaded_evidence_rejections(remediation_store, invalid):
    store = remediation_store
    bootstrap(store)
    ticket, contract = definition(store, "T1", [])
    args, execution, evidence, payload, context = review_setup(store, ticket, contract)
    if invalid in {"nonmember", "empty-claims", "mixed-claims", "scope", "strength", "binding", "reuse"}:
        fields = {"nonmember": {"claims": ["NOT_IN_CONTRACT"]}, "empty-claims": {"claims": []},
                  "mixed-claims": {"claims": ["T1.C1", "NOT_IN_CONTRACT"]}, "scope": {"scope": ["OUTSIDE_T1"]},
                  "strength": {"strength": "documentation"}, "binding": {}, "reuse": {"candidate": "old-revision"}}
        ref = store.create("implementation-evidence", payload | fields[invalid], {} if invalid == "binding" else {"contract": contract}, author="safe-implement")
    elif invalid == "type":
        ref = store.create("spec", {"acceptance": "FROZEN", "authority": "Chat/to-spec", "semantics": "fixed"},
                           {"contract": contract}, author="to-spec")
    elif invalid == "artifact-schema":
        ref = store.create("implementation-evidence", payload, {"contract": contract}, author="safe-implement")
        path = store.root / "implementation-evidence" / f"{ref['artifact_version']}.yaml"
        obj = yaml.safe_load(path.read_bytes())
        obj["schema_version"] = 999
        raw = yaml.safe_dump(obj, sort_keys=True).encode()
        path.write_bytes(raw)
        if isinstance(store, GitStateStore):
            git(store.repo, "add", "--", path.relative_to(store.repo).as_posix())
            git(store.repo, "commit", "-m", "fixture malformed evidence schema")
        ref = ref | {"sha256": sha(raw)}
    else:
        changes = {"hash": {"sha256": "0" * 64}, "work": {"work_id": "OTHER"}, "version": {"artifact_version": 999},
                   "reference-schema": {"unexpected": True}}
        ref = evidence | changes[invalid]
    before = store.index()
    with pytest.raises(Blocked) as error:
        v.prepare_review(store, **(args | {"evidence_refs": [ref]}))
    assert error.value.code == "EVIDENCE_REFERENCE_INVALID"
    assert store.index() == before
    assert v.prepare_review(store, **args)["evidence"] == [evidence]
    observations({"test": "F03", "backend": type(store).__name__, "invalid": invalid, "error_code": error.value.code, "positive_control": "accepted"})


def test_t01_loaded_evidence_reuse_positive(remediation_store):
    store = remediation_store
    bootstrap(store)
    ticket, contract = definition(store, "T1", [])
    args, execution, evidence, payload, context = review_setup(store, ticket, contract)
    old = store.create("implementation-evidence", payload | {"candidate": "old-revision"}, {"contract": contract}, author="safe-implement")
    proof = store.create("runtime-validation", {"kind": "evidence-reuse", "status": "PASS", "subject": old["sha256"],
        "conditions": {"old_candidate": "old-revision", "new_candidate": "revision-1", "changed": ["OTHER"],
                       "proven_unaffected": ["T1"], "known_impact": True}, "observed_at": 1}, {"evidence": old}, author="root")
    before = store.read(old)
    packet = v.prepare_review(store, **(args | {"evidence_refs": [old], "reuse": {old["sha256"]: proof}}))
    assert packet["evidence"] == [old]
    assert packet["reuse_proofs"] == {old["sha256"]: proof}
    assert store.read(old) == before
    assert store.read(old)["payload"]["candidate"] == "old-revision"
