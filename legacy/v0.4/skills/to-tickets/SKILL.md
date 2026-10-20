---
name: to-tickets
description: Decompose a frozen specification only where separate engineering Tickets create safe, useful parallel work.
---

Start from frozen specification semantics.

Recursively decompose work.

Create separate Tickets only when each resulting unit is:
- parallel-safe;
- independently assignable;
- independently completable;
- independently reviewable;
- meaningfully scoped;
- materially more useful in parallel than the coordination, context, setup, validation, integration, and review overhead it introduces.

Otherwise keep the finer work inside one Ticket as an advisory Work Outline.

When choosing between valid decompositions, prefer:
1. safety;
2. independence;
3. material parallelism;
4. lower overhead;
5. simpler integration and review;
6. fewer Tickets and simpler topology.

For each Ticket define:
- `topology_role`: `NORMAL`, `FORK`, or `JOIN`;
- normative scope;
- semantic reads;
- semantic writes;
- dependencies;
- parallel-safety status;
- minimal complete `TICKET_LOCAL` Claims;
- Review Contract Candidate;
- Execution Preconditions Candidate.

Outcome and Work Outline are non-normative.

Sequential engineering work remains inside one Ticket.

A `NORMAL` Ticket in a multi-ticket graph must belong to at least one material safe parallel region.

Use `FORK` only for engineering work that establishes a frozen boundary enabling multiple parallel branches.

Use `JOIN` only for engineering work that genuinely consumes multiple parallel branches.

Cross-ticket behavior uses explicit `INTEGRATION` or aggregate Claims.
Each local Claim has exactly one accountable Ticket owner.

Mechanical, decision-free shared setup may be `SHARED_PREPARATION`; engineering responsibility must be a Ticket.

Parallel safety is `VERIFIED`, `PROVISIONAL`, `NOT_SAFE`, or `UNKNOWN`.
`UNKNOWN` cannot justify a split.

Output only:
- the selected graph;
- material maximal parallel regions;
- material decomposition decisions;
- material rejected boundaries or alternatives.

If a required shared contract is not frozen, return `PARALLEL_BOUNDARY_BLOCKED`.
