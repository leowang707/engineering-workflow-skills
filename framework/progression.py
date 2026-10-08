"""Read-only derived eligibility and authorized sequencing; never formal grading."""
from .common import require
from .policy import PHASES, PROFILES, surface

STOPS = frozenset({"USER_DECISION_REQUIRED", "MATERIAL_UNKNOWN", "SPEC_NOT_FROZEN",
                   "PARALLEL_BOUNDARY_BLOCKED", "REVIEW_CONTRACT_REJECTED", "SAFE_IMPLEMENT_BLOCKED",
                   "STRUCTURAL_CHANGE", "CONTRACT_AMBIGUITY", "LIFECYCLE_STATE_INVALID", "AUTHORIZATION_WITHDRAWN"})


def derive_current(store):
    """Production entry point: derive solely from verified current durable bindings.

    No caller-supplied current phase or grading booleans are authoritative.
    Missing evidence returns the phase that owns producing it. Failed frozen
    outcomes stop; this function never decides how a lifecycle authority resolves them.
    """
    index, _ = store.index()
    bindings = index["bindings"]
    artifacts = {name: store.read(ref) for name, ref in bindings.items()}
    require("authorization" in artifacts, "BLOCKED", "durable authorization missing")
    authorization = artifacts["authorization"]["payload"]
    if authorization["withdrawn"]:
        return {"next": None, "stop": "AUTHORIZATION_WITHDRAWN"}
    if store._terminal():
        return {"next": None, "stop": "TERMINAL"}
    for name, artifact in sorted(artifacts.items()):
        if artifact["artifact_type"] == "phase-result":
            require(name == "phase-result:" + artifact["payload"]["phase"], detail="phase result identity")
            for key, ref in artifact["bindings"].items():
                require(bindings.get(key) == ref, detail="stale phase result binding")
            if artifact["payload"]["status"] != "COMPLETE":
                return {"next": None, "stop": artifact["payload"]["status"]}
    profile = index["pins"]["profile"]
    def ready(phase):
        if phase not in PROFILES[profile]:
            return {"next": None, "stop": "PROFILE_DISABLED"}
        if phase not in authorization["phases"]:
            return {"next": None, "stop": "NOT_AUTHORIZED"}
        return {"next": phase, "surface": PROFILES[profile][phase], "authorization": bindings["authorization"]}
    def stop(reason):
        return {"next": None, "stop": reason}
    if "decisions" not in artifacts:
        return ready("project-grill")
    decisions = artifacts["decisions"]["payload"]
    if decisions["material_unknowns"]:
        return stop("MATERIAL_UNKNOWN")
    if not decisions["resolved"]:
        return stop("USER_DECISION_REQUIRED")
    if "spec" not in artifacts:
        return ready("to-spec")
    specification = artifacts["spec"]
    if specification["payload"]["acceptance"] != "FROZEN":
        return stop("SPEC_NOT_FROZEN")
    if "graph" not in artifacts:
        return ready("to-tickets")
    graph = artifacts["graph"]
    require(graph["bindings"].get("spec") == bindings["spec"], detail="stale graph/spec binding")
    tickets = graph["payload"]["tickets"]
    for ticket_id in tickets:
        key = f"ticket:{ticket_id}"
        if key not in artifacts:
            return ready("to-tickets")
        require(artifacts[key]["payload"]["ticket_id"] == ticket_id, detail="Ticket identity")
        if not artifacts[key]["payload"]["frozen"]:
            return stop("PARALLEL_BOUNDARY_BLOCKED")
    structure = artifacts.get("structure-review")
    if structure is None:
        return ready("review-contract")
    require(structure["payload"]["graph_ref"] == bindings["graph"], detail="stale structure review")
    if structure["payload"]["status"] != "APPROVED":
        return stop("REVIEW_CONTRACT_REJECTED")
    all_claims, dispositions, local = [], {}, {}
    for ticket_id in tickets:
        ticket_key = f"ticket:{ticket_id}"
        contract_key = f"contract:{ticket_id}"
        require(set(artifacts[ticket_key]["payload"]["dependencies"]) == set(graph["payload"]["dependencies"][ticket_id]),
                detail="Ticket/graph dependency mismatch")
        if contract_key not in artifacts:
            local[ticket_id] = {"phase": "review-contract", "accepted": False}
            continue
        contract = artifacts[contract_key]
        require(contract["bindings"].get("ticket") == bindings[ticket_key], detail="stale local contract")
        cp = contract["payload"]
        if cp["status"] not in {"APPROVED", "CONDITIONALLY_APPROVED"} or not cp["frozen_before_implementation"]:
            local[ticket_id] = {"stop": "REVIEW_CONTRACT_REJECTED", "accepted": False}
            continue
        evidence_key = f"implementation-evidence:{ticket_id}"
        if evidence_key not in artifacts:
            local[ticket_id] = {"phase": "safe-implement", "accepted": False}
            continue
        evidence = artifacts[evidence_key]
        require(evidence["bindings"].get("contract") == bindings[contract_key], detail="stale implementation evidence")
        result_key = f"review-result:{ticket_id}"
        if result_key not in artifacts:
            local[ticket_id] = {"phase": "review", "accepted": False}
            continue
        result = artifacts[result_key]
        require(result["bindings"].get("contract") == bindings[contract_key]
                and result["payload"]["candidate"] == evidence["payload"]["candidate"], detail="stale reviewed candidate/contract")
        claims = [claim["id"] for claim in cp["claims"]]
        require(set(result["payload"]["dispositions"]) == set(claims), detail="incomplete local review")
        all_claims.extend(claims)
        dispositions.update(result["payload"]["dispositions"])
        local[ticket_id] = {"accepted": all(s == "PASS" for s in result["payload"]["dispositions"].values())}
    # Gather every prerequisite's current outcome before selecting work. An
    # unrelated parallel branch remains eligible even when another branch fails.
    def accepted(ticket_id):
        return local[ticket_id]["accepted"] and all(accepted(parent) for parent in graph["payload"]["dependencies"][ticket_id])
    for ticket_id in tickets:
        pending = local[ticket_id].get("phase")
        if pending and (pending == "review-contract" or
                        all(accepted(parent) for parent in graph["payload"]["dependencies"][ticket_id])):
            return ready(pending)
    if not all(state["accepted"] for state in local.values()):
        reasons = set(dispositions.values()) | {state["stop"] for state in local.values() if "stop" in state}
        return stop(next((s for s in ("REVIEW_CONTRACT_REJECTED", "CONTRACT_AMBIGUITY", "BLOCKED", "INSUFFICIENT_EVIDENCE", "FAIL")
                          if s in reasons), "PARALLEL_BOUNDARY_BLOCKED"))
    # Explicit integration/aggregate owners are independent from Ticket-local artifacts.
    integration_owners = {n["owner"] for n in graph["payload"]["responsibilities"] if n["kind"] in {"integration", "aggregate"}}
    require(integration_owners <= {a["payload"]["owner"] for a in artifacts.values() if a["artifact_type"] == "integration"},
            detail="required integration/aggregate definitions missing")
    for key, integration in artifacts.items():
        if integration["artifact_type"] != "integration":
            continue
        owner = integration["payload"]["owner"]
        contract_key = f"integration-contract:{owner}"
        if contract_key not in artifacts:
            return ready("review-contract")
        contract = artifacts[contract_key]
        require(contract["bindings"].get("integration") == bindings[key], detail="stale integration contract")
        if contract["payload"]["status"] not in {"APPROVED", "CONDITIONALLY_APPROVED"}:
            return stop("REVIEW_CONTRACT_REJECTED")
        review_key = f"review-result:integration-{owner}"
        if review_key not in artifacts:
            return ready("review")
        review = artifacts[review_key]
        require(review["bindings"].get("contract") == bindings[contract_key], detail="stale integration review")
        claims = [claim["id"] for claim in contract["payload"]["claims"]]
        require(set(review["payload"]["dispositions"]) == set(claims), detail="integration review coverage")
        all_claims.extend(claims)
        dispositions.update(review["payload"]["dispositions"])
    if complete(all_claims, dispositions, valid_state=True, stale=False):
        return {"next": None, "derived_complete": True, "authoritative": False}
    return stop(next((s for s in ("CONTRACT_AMBIGUITY", "BLOCKED", "INSUFFICIENT_EVIDENCE", "FAIL") if s in dispositions.values()), "BLOCKED"))


def sequence_current(store, actual_surface, invoke):
    eligibility = derive_current(store)
    if eligibility["next"] is None:
        return eligibility
    require(eligibility["surface"] == actual_surface, "HANDOFF_NOT_READY", "no implicit backend transfer")
    require(derive_current(store) == eligibility, "BLOCKED", "state/authorization changed")
    return invoke(eligibility["next"], eligibility)


def complete(claims, results, *, valid_state, stale):
    require(len(set(claims)) == len(claims), detail="duplicate Claim ownership")
    return bool(claims) and valid_state and not stale and all(results.get(c) == "PASS" for c in claims) and set(results) == set(claims)


def derive(store, gates):
    index, _ = store.index()
    ref = index["bindings"].get("authorization")
    require(ref is not None, "BLOCKED", "durable authorization required")
    authorization = store.read(ref)["payload"]
    if authorization["withdrawn"]:
        return {"next": None, "stop": "AUTHORIZATION_WITHDRAWN"}
    require(set(gates) == {"stops", "outcomes", "terminal"}, detail="unknown gate input")
    stops = set(gates["stops"])
    require(stops <= STOPS, detail="unrecognized stop condition")
    if stops:
        return {"next": None, "stop": sorted(stops)[0]}
    if gates["terminal"] or store._terminal():
        return {"next": None, "stop": "TERMINAL"}
    profile = index["pins"]["profile"]
    for phase in PHASES:
        if phase not in PROFILES[profile]:
            return {"next": None, "stop": "PROFILE_DISABLED"}
        if gates["outcomes"].get(phase) == "COMPLETE":
            continue
        if phase in gates["outcomes"]:
            return {"next": None, "stop": gates["outcomes"][phase]}
        if phase not in authorization["phases"]:
            return {"next": None, "stop": "NOT_AUTHORIZED"}
        if phase in PHASES[2:]:
            from .policy import handoff
            require("spec" in index["bindings"], "HANDOFF_NOT_READY", "Frozen Spec missing")
            handoff(store.read(index["bindings"]["spec"]))
        return {"next": phase, "surface": PROFILES[profile][phase], "authorization": ref}
    return {"next": None, "stop": "REVIEW_GRAPH_REQUIRED"}


def sequence(store, gates, actual_surface, invoke):
    eligibility = derive(store, gates)
    if eligibility["next"] is None:
        return eligibility
    require(eligibility["surface"] == actual_surface, "HANDOFF_NOT_READY", "no implicit surface transfer")
    # Re-read current authorization immediately before invocation (withdrawal/reduction).
    require(derive(store, gates) == eligibility, "BLOCKED", "authorization/state drift")
    return invoke(eligibility["next"], eligibility)


def chat_implementation(*, frozen_ticket, allowed_capability, preconditions, identity_available):
    require(all(x is True for x in (frozen_ticket, allowed_capability, preconditions, identity_available)),
            "BLOCKED", "Chat mutation prerequisites/identity unavailable")
    return "Chat"


def remote_gate(role, authorization, *, reviewed_sha, actual_sha, remote, branch,
                reviews_current, bindings_valid, conflict=False, divergence=False, judgment=False):
    require(role == "root" and authorization is not None and set(authorization) == {"remote", "branch", "sha"}
            and authorization == {"remote": remote, "branch": branch, "sha": actual_sha}
            and actual_sha == reviewed_sha and reviews_current and bindings_valid
            and not any((conflict, divergence, judgment)), "REMOTE_OPERATION_BLOCKED", "separate exact remote authorization/gates required")


def cleanup_gate(*, derived_complete, verified_integration, provenance_in_target, remote_required, remote_completed):
    require(derived_complete and verified_integration and provenance_in_target
            and (not remote_required or remote_completed), "BLOCKED", "retain execution history until verified delivery")
