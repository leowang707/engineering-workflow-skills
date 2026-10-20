---
name: next
description: Read the work saved in .workflow/ and say where the build stands and which command to run next, without running it.
disable-model-invocation: true
---

Tell the user where their work stands and the one command to run next. Read files only; do not run the next step, change any file, or start a review.

## 1. Find the feature

List the folders under `.workflow/` in the project. If the user named a feature, use that one. If there is exactly one, use it. If there are several, show each with its stage (step 2) and ask which one; stop there. If `.workflow/` does not exist, say so and suggest starting with the `grilling` skill.

## 2. Work out the stage

Check these in order and stop at the first that matches. Read the files; do not guess from file names alone.

| What you find | Stage | Next |
|---|---|---|
| a `reviews/<NN>-decision.md` with no recorded choice | waiting on the user | answer the decision in that file |
| no `spec.md` | deciding | keep grilling, or `/to-spec` if `decisions.md` has no open decisions |
| `spec.md` says `Status: PARTIAL` | spec has gaps | settle the listed open decisions with grilling, then `/to-spec` again |
| no tickets, or any ticket says `**Status:** draft` | splitting | `/to-tickets` (it also freezes acceptance) |
| some tickets not `done` | building | `/implement <NN>` in a new conversation, for a ticket whose blockers are all `done`; mention `/implement-spec` when two or more are unblocked |
| every ticket `done` | finished | open the PR (the `pr` skill writes the body), then `/retro` |

If tickets remain but none is unblocked, name the ticket that blocks them and why it is stuck (check its latest file in `reviews/`).

## 3. Answer

Reply in at most five lines:

```
Feature: <name>
Stage: <stage> (<k> of <n> tickets done, if building)
Last activity: <the most recent file touched in .workflow/<feature>/ and what it says>
Next: <the exact command>
```

Add one line only if something needs attention first, such as a non-empty `followups.md` or a ticket marked `STRUCTURAL_CHANGE`.
