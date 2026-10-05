---
name: review-contract
description: Independently validate Ticket decomposition and freeze acceptance contracts before implementation is seen.
---

Use an independent context.

Read frozen requirements and authoritative repository evidence.
Do not inspect implementation results or author reasoning.

Review structure before contract details.

First validate:
- over/under splitting;
- dependencies and semantic boundaries;
- parallel and set-level composition safety;
- `FORK` / `JOIN` validity;
- responsibility and Claim closure;
- shared preparation classification;
- whether parallel value materially exceeds introduced overhead.

Only then validate:
- minimal complete local Claims;
- Claim ownership and relationships;
- implementation-neutral, falsifiable PASS/FAIL semantics;
- evidence properties, required strength, and composition;
- applicable blocking Review Invariants and frozen conditional triggers;
- Execution Preconditions.

Do not edit the candidate.

Return `APPROVED`, `CONDITIONALLY_APPROVED`, or `REJECTED`.

A rejection finding states:
- the defect;
- supporting evidence;
- the required property.

Do not prescribe the redesign.

Reject material defects, not stylistic preferences.

Approved work boundaries, contracts, preconditions, invariants, and reviewed graph relations are frozen.

If contract review reveals a structural defect, reopen only the affected subgraph.
