---
name: safe-implement
description: Implement inside one frozen Ticket boundary without changing requirements, architecture, or review standards.
---

Work only inside the frozen Ticket boundary.

Resolve Execution Preconditions before mutation.
If unresolved, return `BLOCKED`.
If they invalidate the reviewed boundary, return `STRUCTURAL_CHANGE`.

Own implementation mechanism, not architecture, requirements, or shared contracts.

Choose local algorithms, helpers, data structures, refactoring, and coding order freely only while remaining inside the frozen semantic boundary.

Do not introduce a new dependency, shared abstraction, public contract, observable behavior, cross-module responsibility, or material risk.

Treat the Work Outline as advisory.

Tests and validation code may change only to prove the Frozen Review Contract.
Never change expected semantics to fit the implementation.

Honor any blocking invariant whose frozen trigger activates.

Fix only defects required by the Ticket.
Record unrelated defects without expanding scope.

If relevant repository drift invalidates a frozen assumption, stop until that assumption is revalidated.

Before handoff, confirm:
- frozen local responsibility is addressed;
- required local Claims have candidate evidence;
- active invariants were handled;
- Execution Preconditions remain valid;
- no known blocking contract violation remains.

Return only:
- `READY_FOR_REVIEW`;
- `BLOCKED`;
- `STRUCTURAL_CHANGE`.

Never declare `PASS`.
