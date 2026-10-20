---
name: freeze-acceptance
description: Independently check a ticket set against its spec and freeze each ticket's acceptance criteria before any code is written. Use when tickets are drafted and not yet implemented, or when the user asks to lock down what "done" means for a ticket.
---

Acceptance criteria are written **before** implementation so the review can't be bent to fit the code. This skill checks the tickets and freezes those criteria.

## Independence

Run the check in a sub-agent if your harness has one, giving it only the spec, the ticket files, and read access to the repository: not this conversation and not anyone's reasoning about how to build it. Without sub-agents, do it yourself and judge only from those files.

## Round limit

Read `.workflow/<feature>/acceptance.md` if it exists and find the round number. **At most 2 rounds.** If round 2 still ends in `REJECTED`, stop: show the user the remaining findings and let them decide (accept as is, edit the tickets themselves, or drop the ticket). Do not start a round 3 on your own.

## Phase 1: Structure (a hard gate)

For the ticket set as a whole, check:

- every spec requirement (R1, R2, ...) is covered by some ticket;
- each ticket is a real vertical slice, not over-split sequential steps and not an oversized bundle;
- blocking edges are correct and there are no cycles;
- no two tickets that can run at the same time write the same behavior.

A ticket that fails structure gets no contract check in this round.

## Phase 2: Contract

For each ticket that passed structure, check every acceptance criterion:

- it is observable and falsifiable: PASS or FAIL can be judged without seeing the implementation;
- it is implementation-neutral: it states behavior, not mechanism, unless the spec already fixed the mechanism;
- it names the **evidence** that proves it (a test at an agreed seam, a command and its expected output, a screenshot);
- together the criteria cover everything the ticket claims to deliver, and nothing outside it.

## Findings

Reject material defects only, not style. Each finding states the defect, the evidence for it, and the property that is missing. Do not prescribe the redesign; the ticket author fixes it.

## Result

Return `APPROVED` or `REJECTED` for each ticket. Append the round to `.workflow/<feature>/acceptance.md`:

```
## Round <N>

- 01-<slug>: APPROVED
- 02-<slug>: REJECTED
  - <defect> | evidence: <...> | missing: <property>
```

For each `APPROVED` ticket, set its file to `**Status:** frozen` and rename its "Draft acceptance criteria" heading to "Frozen acceptance criteria". From then on the criteria change only if the user explicitly reopens them.

After a rejection, the author revises the rejected tickets and calls this skill again for round 2. Approved tickets stay frozen.
