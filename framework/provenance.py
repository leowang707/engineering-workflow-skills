"""Responsibility dependencies, immutable identities and frozen review inputs."""
from copy import deepcopy
from pathlib import Path
import subprocess

from .common import Blocked, digest, require, sha

INVARIANTS = {
    "RI-1": "exact artifact/hash/schema/binding integrity",
    "RI-2": "immutable unique verifiable retrievable attributable candidate",
    "RI-3": "current binding-valid schema-valid PASS runtime validations before grading",
    "RI-4": "frozen authority and mutation scope; remote authorization separate",
    "RI-5": "fresh independent review against frozen standards",
    "RI-6": "durable resolution before first mutation; renewed after drift",
    "RI-7": "frozen evidence strength/invalidation; blocking acquired evidence durable before use",
}


def responsibility_graph(graph):
    nodes = graph["responsibilities"]
    require(bool(nodes) and len({n["id"] for n in nodes}) == len(nodes), "STRUCTURAL_CHANGE", "responsibility identity/ownership")
    tickets = set(graph["tickets"])
    for node in nodes:
        require(set(node) == {"id", "meaning", "owner", "boundary", "kind"}
                and node["owner"] in tickets and node["meaning"] and node["boundary"]
                and node["kind"] in {"local", "integration", "aggregate"}, "STRUCTURAL_CHANGE", "incomplete responsibility")
    dependencies = graph["dependencies"]
    require(set(dependencies) == tickets and all(set(v) <= tickets for v in dependencies.values()), "STRUCTURAL_CHANGE", "dependency closure")
    visited, visiting = set(), set()
    def visit(ticket):
        require(ticket not in visiting, "STRUCTURAL_CHANGE", "cyclic Ticket dependency")
        if ticket in visited:
            return
        visiting.add(ticket)
        for parent in dependencies[ticket]:
            visit(parent)
        visiting.remove(ticket)
        visited.add(ticket)
    for ticket in sorted(tickets):
        visit(ticket)
    return deepcopy(graph)


def refine_mapping(old, proposed, operator):
    require(operator == "root", "BLOCKED", "worker can only propose mappings")
    require(old["responsibilities"] == proposed["responsibilities"], "STRUCTURAL_CHANGE", "mapping changed semantic boundary")
    require(set(proposed["locators"]) == {n["id"] for n in old["responsibilities"]}, "STRUCTURAL_CHANGE", "mapping closure")
    return deepcopy(proposed)


def affected(dependencies, changed, proven_unaffected, known_impact):
    """Do not rebind old evidence; derive staleness from exact dependency facts."""
    deps = set(dependencies)
    if deps & set(changed) or known_impact is not True:
        return "STALE"
    return "REUSABLE" if deps <= set(proven_unaffected) else "STALE"


def remediation(before, after):
    fields = ("scope", "claims", "dependencies", "contract", "shared_contracts")
    require(all(before[k] == after[k] for k in fields), "STRUCTURAL_CHANGE", "return to semantic owner")
    return "SAME_TICKET_AND_CONTRACT"


def freeze_invariants(frozen_state, triggers):
    require(set(frozen_state) == {"preimplementation", "facts"} and frozen_state["preimplementation"] is True,
            "BLOCKED", "only preimplementation frozen facts may trigger invariants")
    require(set(triggers) == set(INVARIANTS), "BLOCKED", "complete pinned invariant set required")
    result = {}
    for name, trigger in sorted(triggers.items()):
        require(set(trigger) == {"fact", "runtime_resolvable", "semantic"}, "BLOCKED", "trigger fields")
        require(trigger["fact"] in frozen_state["facts"], "BLOCKED", "trigger reads unavailable/postimplementation fact")
        value = frozen_state["facts"][trigger["fact"]]
        require(value is True or value is False or value is None, "BLOCKED", "trigger not deterministic boolean")
        result[name] = ("APPLICABLE" if value is True else "NOT_APPLICABLE" if value is False
                        else "CONDITIONALLY_APPROVED" if trigger["runtime_resolvable"] and not trigger["semantic"] else "NOT_APPROVED")
    return {"semantics_hash": digest(INVARIANTS), "state_hash": digest(frozen_state), "applicability": result}


def resolve_preconditions(store, refs, current_conditions, mutation_time):
    require(bool(refs), "BLOCKED", "required precondition resolutions absent")
    for ref in refs:
        obj = store.read(ref)
        p = obj["payload"]
        require(obj["artifact_type"] == "runtime-validation" and p["kind"] == "precondition"
                and p["status"] == "PASS" and p["conditions"] == current_conditions.get(p["subject"])
                and p["observed_at"] < mutation_time,
                "BLOCKED", "unresolved, stale or late mutation prerequisite")


def pre_mutation_gate(store, contract_ref, ticket_ref, resolution_refs, current_conditions, mutation_time):
    contract = store.read(contract_ref)["payload"]
    ticket = store.read(ticket_ref)["payload"]
    require(store.read(contract_ref)["bindings"].get("ticket") == ticket_ref
            and contract["status"] in {"APPROVED", "CONDITIONALLY_APPROVED"}
            and contract["frozen_before_implementation"] is True and ticket["frozen"] is True,
            "BLOCKED", "frozen boundary/contract required before mutation")
    require("NOT_APPROVED" not in contract["invariants"]["applicability"].values(), "BLOCKED", "semantic invariant UNKNOWN")
    observations = []
    for ref in resolution_refs:
        obj = store.read(ref)
        require(obj["artifact_type"] == "runtime-validation", "BLOCKED", "durable resolution required")
        o = obj["payload"]
        require(o["status"] == "PASS" and o["conditions"] == current_conditions.get(o["subject"])
                and o["observed_at"] < mutation_time, "BLOCKED", "resolution stale, ineligible or too late")
        observations.append(o)
    for condition in contract["preconditions"]:
        if condition["before_mutation"]:
            require(any(o["subject"] == condition["subject"] and o["kind"] == condition["kind"]
                        and set(condition["properties"]) <= set(o["conditions"].get("properties", []))
                        for o in observations), "BLOCKED", "required precondition unresolved")
    if "CONDITIONALLY_APPROVED" in contract["invariants"]["applicability"].values():
        for invariant, applicability in contract["invariants"]["applicability"].items():
            if applicability == "CONDITIONALLY_APPROVED":
                require(any(o["kind"] == "precondition" and o["subject"] == invariant for o in observations), "BLOCKED", "conditional invariant unresolved")
    return {"contract": contract_ref, "ticket": ticket_ref, "resolutions": deepcopy(resolution_refs), "before": mutation_time}


class IdentityRegistry:
    """Only registered adapters may attest the five frozen identity properties."""
    def __init__(self, providers):
        self.providers = dict(providers)

    def validate(self, candidate):
        try:
            require(set(candidate) == {"provider", "id", "sha256", "execution"}
                    and candidate["execution"], "IMPLEMENTATION_IDENTITY_INVALID", "candidate attribution")
            provider = self.providers[candidate["provider"]]
            first = provider(candidate["id"])
            second = provider(candidate["id"])
            require(first == second and first["immutable"] is True
                    and first["id"] == candidate["id"] and sha(first["bytes"]) == candidate["sha256"],
                    "IMPLEMENTATION_IDENTITY_INVALID", "identity properties not established")
            return {"candidate": deepcopy(candidate), "status": "PASS", "provider": candidate["provider"]}
        except (KeyError, TypeError, OSError, ValueError) as error:
            raise Blocked("IMPLEMENTATION_IDENTITY_INVALID", str(error)) from error


def git_identity_provider(repo):
    def retrieve(commit):
        require(len(commit) in {40, 64} and all(c in "0123456789abcdef" for c in commit), "IMPLEMENTATION_IDENTITY_INVALID", "exact commit required")
        result = subprocess.run(["git", "-C", str(repo), "cat-file", "commit", commit], capture_output=True)
        require(result.returncode == 0, "IMPLEMENTATION_IDENTITY_INVALID", "commit unavailable")
        # Git object integrity is verified independently of its name.
        hashed = subprocess.run(["git", "-C", str(repo), "hash-object", "-t", "commit", "--stdin"], input=result.stdout, capture_output=True)
        require(hashed.returncode == 0 and hashed.stdout.decode().strip() == commit,
                "IMPLEMENTATION_IDENTITY_INVALID", "Git object integrity")
        integrity = subprocess.run(["git", "-C", str(repo), "fsck", "--strict", "--no-reflogs", commit], capture_output=True)
        require(integrity.returncode == 0, "IMPLEMENTATION_IDENTITY_INVALID", "Git candidate object closure invalid")
        return {"id": commit, "immutable": True, "bytes": result.stdout}
    return retrieve


def artifact_identity_provider(store, revisions):
    def retrieve(revision):
        ref = revisions[revision]
        obj = store.read(ref)
        from .common import canonical
        return {"id": revision, "immutable": True, "bytes": canonical(obj)}
    return retrieve


def provenance_gate(store, execution_ref, expected_bindings, conditions, required_kinds):
    execution = store.read(execution_ref, expected_bindings)
    require(execution["artifact_type"] == "execution", "REVIEW_PRECONDITION_UNSATISFIED", "execution identity")
    found = set()
    for ref in execution["payload"]["validations"]:
        obj = store.read(ref)
        p = obj["payload"]
        require(obj["artifact_type"] == "runtime-validation" and p["status"] == "PASS"
                and p["conditions"] == conditions.get(p["subject"]),
                "REVIEW_PRECONDITION_UNSATISFIED", "stale/ineligible runtime validation")
        found.add(p["kind"])
    require(set(required_kinds) <= found, "REVIEW_PRECONDITION_UNSATISFIED", "missing applicable validation")
    return execution


def evidence_resolve(store, ref, *, bindings, allowed_scope, requirement):
    try:
        obj = store.read(ref, bindings)
        require(obj["artifact_type"] in {"implementation-evidence", "review-evidence"}, detail="not evidence")
        p = obj["payload"]
        require(set(p["scope"]) <= set(allowed_scope) and requirement["claim"] in p["claims"]
                and p["strength"] in requirement["strengths"] and p["conditions"] and p["observations"], detail="scope/evidence strength")
        return obj
    except (Blocked, KeyError, TypeError) as error:
        raise Blocked("EVIDENCE_REFERENCE_INVALID", str(error)) from error


def review_packet(store, contract_ref, ticket_ref, candidate, evidence_refs):
    """Projection only: no persistence, source ingestion, criteria synthesis or grading."""
    contract = store.read(contract_ref)
    ticket = store.read(ticket_ref)
    require(contract["artifact_type"] in {"contract", "integration-contract"}
            and contract["payload"]["status"] in {"APPROVED", "CONDITIONALLY_APPROVED"}
            and contract["payload"]["frozen_before_implementation"] is True,
            "REVIEW_PRECONDITION_UNSATISFIED", "frozen approved contract required")
    subject_binding = "integration" if contract["artifact_type"] == "integration-contract" else "ticket"
    require(contract["bindings"].get(subject_binding) == ticket_ref
            and contract["payload"]["claims"] == ticket["payload"]["claims"],
            "REVIEW_PRECONDITION_UNSATISFIED", "contract/Ticket binding")
    return {"kind": "REVIEW_INPUT_PACKET", "authoritative": False, "durable": False,
            "contract": deepcopy(contract_ref), "ticket": deepcopy(ticket_ref),
            "standards": deepcopy(contract["payload"]), "candidate": deepcopy(candidate),
            "evidence": sorted(deepcopy(evidence_refs), key=digest)}


def blocking_review_evidence(store, result):
    """All cited blocking evidence must already exist durably before result creation."""
    for ref in result["evidence"]:
        obj = store.read(ref)
        require(obj["artifact_type"] in {"review-evidence", "implementation-evidence"},
                "EVIDENCE_REFERENCE_INVALID", "durable evidence required")
        if obj["payload"]["candidate"] != result["candidate"]:
            proof = result.get("reuse", {}).get(ref["sha256"])
            require(proof is not None, "EVIDENCE_REFERENCE_INVALID", "candidate reuse proof missing")
            reuse_evidence(store, ref, result["candidate"], proof)


def reuse_evidence(store, evidence_ref, new_candidate, proof_ref):
    evidence = store.read(evidence_ref)
    proof = store.read(proof_ref)
    p = proof["payload"]
    conditions = p["conditions"]
    require(proof["artifact_type"] == "runtime-validation" and p["kind"] == "evidence-reuse"
            and p["status"] == "PASS" and p["subject"] == evidence_ref["sha256"]
            and proof["bindings"].get("evidence") == evidence_ref
            and conditions["old_candidate"] == evidence["payload"]["candidate"]
            and conditions["new_candidate"] == new_candidate
            and affected(evidence["payload"]["dependencies"], conditions["changed"], conditions["proven_unaffected"], conditions["known_impact"]) == "REUSABLE",
            "EVIDENCE_REFERENCE_INVALID", "affected or unproven candidate evidence reuse")
    return evidence  # original bytes/identity preserved, never rebound


def candidate_attribution(store, registry, candidate, execution_ref):
    execution = store.read(execution_ref)
    require(execution["artifact_type"] == "execution" and candidate["execution"] == execution_ref
            and execution["payload"]["candidate"] == candidate["id"],
            "IMPLEMENTATION_IDENTITY_INVALID", "candidate must bind exactly one durable execution result")
    return registry.validate(candidate)


def prepare_review(store, *, contract_ref, ticket_ref, candidate, identity_registry,
                   execution_ref, expected_execution_bindings, current_conditions,
                   required_validation_kinds, review_context, evidence_refs, reuse=None):
    """One pre-grading entry point for exact identity, runtime and independence gates."""
    try:
        contract = store.read(contract_ref)["payload"]
        required = {"role", "identity"} | {c["kind"] for c in contract["preconditions"]}
        require(required <= set(required_validation_kinds), "REVIEW_PRECONDITION_UNSATISFIED", "caller omitted frozen provenance requirement")
        execution = provenance_gate(store, execution_ref, expected_execution_bindings,
                                    current_conditions, required_validation_kinds)
        observations = [store.read(ref)["payload"] for ref in execution["payload"]["validations"]]
        for invariant, applicability in contract["invariants"]["applicability"].items():
            require(applicability != "NOT_APPROVED", "REVIEW_PRECONDITION_UNSATISFIED", "semantic invariant unresolved")
            if applicability == "CONDITIONALLY_APPROVED":
                require(any(o["kind"] == "precondition" and o["subject"] == invariant for o in observations),
                        "REVIEW_PRECONDITION_UNSATISFIED", "conditional invariant unresolved")
        for condition in contract["preconditions"]:
            require(any(o["subject"] == condition["subject"] and o["kind"] == condition["kind"]
                        and set(condition["properties"]) <= set(o["conditions"].get("properties", []))
                        for o in observations), "REVIEW_PRECONDITION_UNSATISFIED", "frozen property resolution absent")
        candidate_attribution(store, identity_registry, candidate, execution_ref)
        from .policy import independent_review
        independent_review(review_context, execution["payload"]["context"])
        packet = review_packet(store, contract_ref, ticket_ref, candidate, evidence_refs)
        ticket = store.read(ticket_ref)["payload"]
        for ref in evidence_refs:
            try:
                evidence = store.read(ref, {"contract": contract_ref})
                require(evidence["artifact_type"] in {"implementation-evidence", "review-evidence"},
                        "EVIDENCE_REFERENCE_INVALID", "not evidence")
                claims = {claim["id"]: claim for claim in contract["claims"]}
                cited = evidence["payload"]["claims"]
                require(bool(cited) and set(cited) <= set(claims),
                        "EVIDENCE_REFERENCE_INVALID", "evidence claims outside frozen contract")
                if evidence["payload"]["candidate"] != candidate["id"]:
                    proof = (reuse or {}).get(ref["sha256"])
                    require(proof is not None, "EVIDENCE_REFERENCE_INVALID", "candidate mismatch without reuse proof")
                    reuse_evidence(store, ref, candidate["id"], proof)
                for claim_id in cited:
                    claim = claims[claim_id]
                    evidence_resolve(store, ref, bindings={"contract": contract_ref},
                                     allowed_scope=ticket["scope"], requirement={"claim": claim["id"], "strengths": claim["strengths"]})
            except (Blocked, KeyError, TypeError) as error:
                raise Blocked("EVIDENCE_REFERENCE_INVALID", str(error)) from error
        packet["reuse_proofs"] = deepcopy(reuse or {})
        return packet
    except Blocked as error:
        if error.code == "LIFECYCLE_STATE_INVALID":
            raise Blocked("REVIEW_PRECONDITION_UNSATISFIED", str(error)) from error
        raise
