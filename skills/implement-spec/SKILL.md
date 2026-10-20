---
name: implement-spec
description: Build a whole spec in one run by working its frozen tickets in parallel with sub-agents on one integration branch.
disable-model-invocation: true
---

Implement every ticket of a spec in one run. Use this instead of `/implement` per ticket when you would rather orchestrate the build than drive each ticket yourself. It needs a harness with sub-agents; without them, tell the user to run `/implement` ticket by ticket instead.

The goal is the whole spec built on one **integration branch**, with every ticket reviewed against its frozen criteria.

## Before you start

- Read `.workflow/<feature>/spec.md` and every file in `.workflow/<feature>/tickets/`.
- Every ticket must say `**Status:** frozen` (or `done`). If any is still a draft, stop and tell the user to finish `/to-tickets`, which freezes acceptance.

The tickets are not a list of steps but a **task graph**: their "Blocked by" edges decide the **frontier**, the tickets whose blockers are all done.

Keep messages to and from sub-agents short. Pass **context pointers** (paths to the spec, ticket, notes, commits), not copies of their contents.

## Steps

1. (optional) Run an **exploration sub-agent** for exploration the tickets need (relevant code, external docs). It saves its notes outside the repo where later sub-agents can read them.
2. Create the integration branch from the current branch.
3. For each ticket on the frontier, start an **implementer sub-agent**, in the background where possible, each in its own worktree on its own branch based on the integration branch. Its brief: the ticket path, the spec path, and these rules:
   - stay inside the ticket's boundary: no new dependency, shared abstraction, public API, or unrequested behavior; if one is needed, stop and report `STRUCTURAL_CHANGE`;
   - call the Skill tool with "tdd" to build it;
   - call the Skill tool with "frozen-review" for the ticket, and on a non-passing result call the Skill tool with "resolve-review"; both stop after 2 rounds;
   - merge the integration branch tip into its own branch before reporting;
   - report one of `PASSED`, `NEEDS_USER` (with the decision file path), `BLOCKED`, or `STRUCTURAL_CHANGE`.
4. When an implementer reports `PASSED`, merge its branch into the integration branch with a **merger sub-agent**, and set the ticket to `**Status:** done`.
5. If the merge changes the frontier, start implementers for the newly unblocked tickets.
6. Tickets that report anything other than `PASSED` stay out of the integration branch. Collect them; tickets blocked by them stay unstarted.
7. When no ticket can move, review the whole integration branch: call the Skill tool with "frozen-review" against all frozen criteria, so cross-ticket problems show up. On a non-passing result call the Skill tool with "resolve-review"; its fixes go into one implementer sub-agent.
8. Clean up all implementer worktrees.

## Report

Tell the user: the integration branch name, which tickets passed, and for each one that did not, why and what decision it needs (link its `<NN>-decision.md`). If the user wants a PR, call the Skill tool with "pr" to write its body.

End with the next step on its own line: the open decisions to answer if any ticket did not pass, otherwise `Next: open the PR, then run /retro`.
