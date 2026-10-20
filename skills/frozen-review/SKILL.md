---
name: frozen-review
description: Review a diff on two separate axes, the ticket's frozen acceptance criteria and the repo's coding standards, with a fixed verdict and at most 2 review rounds. Use when a ticket has just been implemented, or when the user asks to review a branch, PR, or work-in-progress against its spec or ticket.
---

Two separate checks of the diff between `HEAD` and a fixed point:

- **Acceptance**: does the code meet the ticket's frozen acceptance criteria? This decides the verdict.
- **Standards**: does the code follow this repo's documented coding standards? These findings never block on their own.

## 1. Round limit

Find the review history in `.workflow/<feature>/reviews/<NN>-r<K>.md`. **At most 2 rounds per ticket.** If round 2 is not `PASS` or `PASS_WITH_FINDINGS`, stop and hand the remaining findings to the user to decide. Do not start a round 3 on your own, and do not hand the work back to implementation automatically.

## 2. Pin the inputs

- **Fixed point**: what the user named, otherwise the merge-base with the default branch. Confirm it resolves (`git rev-parse`) and the diff (`git diff <fixed-point>...HEAD`) is not empty before going on.
- **Criteria**: the ticket's "Frozen acceptance criteria". If the ticket is not frozen (no `.workflow` files, a plain PR), use the spec or issue the user points to, and say in the report that the criteria were not frozen in advance.
- **Standards**: every file that documents how code should be written here (`CONTRIBUTING.md`, `CODING_STANDARDS.md`, `CLAUDE.md`, `AGENTS.md`, linters' configs).

Read the criteria **before** reading the diff.

## 3. Review both axes

Run each axis in its own sub-agent if your harness has them, in parallel, each given the diff command and only its own inputs. Without sub-agents, do them one after the other and keep the reports separate.

**Acceptance axis.** For every frozen criterion, return exactly one disposition with evidence (a test name and its output, a command you ran, a quoted line of the diff):

- `PASS`: the evidence shows the criterion holds.
- `FAIL`: the evidence shows it does not. Name the violated criterion; do not prescribe the fix.
- `INSUFFICIENT_EVIDENCE`: the criterion may hold, but the evidence it names is missing. Say exactly what evidence is missing.
- `BLOCKED`: the criterion can't be checked here (missing environment, credentials). Say what is missing.

You may gather evidence yourself (run the tests, run the command the criterion names), as long as it proves the same property. Do not add, weaken, or reinterpret criteria after seeing the code. If a criterion has two reasonable meanings, return `CONTRACT_AMBIGUITY` for it and stop for the user. Anything useful you notice outside the criteria is a **non-blocking finding**.

**Standards axis.** Report each place the diff breaks a documented standard, citing the file and rule. Skip anything tooling already enforces. Every finding here is non-blocking.

## 4. Verdict

Derive it mechanically; do not override it:

1. any `FAIL` → `FAIL`
2. else any `BLOCKED` → `BLOCKED`
3. else any `INSUFFICIENT_EVIDENCE` → `INSUFFICIENT_EVIDENCE`
4. else any non-blocking finding → `PASS_WITH_FINDINGS`
5. else → `PASS`

What happens next:

- `PASS` / `PASS_WITH_FINDINGS`: done. Non-blocking findings go to the user as candidates for future work.
- `FAIL`: implementation fixes the named failures; this is the one case that loops, and only within the round limit.
- `INSUFFICIENT_EVIDENCE` / `BLOCKED` / `CONTRACT_AMBIGUITY`: stop and show the user what is missing. Do not re-review automatically.

On a second round, re-check the previous failures and any criteria the fix may have touched; keep the earlier results that the fix could not have affected.

## 5. Report

Write the report to `.workflow/<feature>/reviews/<NN>-r<K>.md` (when there is a `.workflow` folder) and show it to the user:

```
# Review: <ticket> round <K>

Verdict: <VERDICT>

## Acceptance
- <criterion>: <DISPOSITION> | evidence: <...>

## Standards (non-blocking)
- <file:line>: <rule broken> (<standards file>)

## Other non-blocking findings
- ...
```
