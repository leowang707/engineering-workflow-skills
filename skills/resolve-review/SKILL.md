---
name: resolve-review
description: Decide what to do with a review that did not pass, classifying each finding by cause and fixing all of them in one batch before the next round. Use when a review returns FAIL, INSUFFICIENT_EVIDENCE, BLOCKED or CONTRACT_AMBIGUITY, when a review hits its round limit, or when the user asks how to handle review findings.
---

A failed review is a list of findings, and each finding has one **cause**. Fixing the cause, not the symptom, is what stops review ping-pong. Work from the latest report in `.workflow/<feature>/reviews/<NN>-r<K>.md` (or the review in this conversation).

## 1. Classify every finding

Give each non-passing item exactly one cause:

| Cause | Looks like | What to do |
|---|---|---|
| **defect** | `FAIL`: the code does the wrong thing | Fix the code inside the ticket boundary. If the root cause is not obvious within one look, call the Skill tool with "diagnosing-bugs" and get a red loop first. |
| **evidence gap** | `INSUFFICIENT_EVIDENCE`: behavior may be right, proof is missing | Add the evidence the criterion names (a test at the agreed seam, a recorded command output). Change code only if the new test goes red, and then it is a defect. |
| **environment** | `BLOCKED`: missing credentials, service, data, or a flaky run | Do not touch the code. Tell the user exactly what is missing. A flaky test is not a cause: re-run it once; a second failure is a defect or an environment problem to diagnose. |
| **criterion problem** | `CONTRACT_AMBIGUITY`, or a criterion that contradicts the spec or cannot be met | Never edit a frozen criterion yourself. Put it to the user (step 3). |
| **boundary** | The fix needs a new dependency, a public API change, or another ticket's area | Stop. Propose a new ticket or a change to the ticket split (step 3). |
| **reviewer error** | The evidence already shows the criterion holds | Do not change code to appease the review. Write the rebuttal with the evidence into the report; the next round decides. |

Non-blocking findings (`PASS_WITH_FINDINGS`, Standards axis) are not fixed now. Append them to `.workflow/<feature>/followups.md` as candidates for later tickets.

## 2. Plan one batch

All fixes for this round go into **one batch**, so the next review sees everything at once. Order:

1. user questions (criterion problems, boundary): their answers can make other fixes unnecessary;
2. defects;
3. evidence gaps.

Hard rules while fixing: never change an expected value to make a test pass, never weaken, skip, or delete a test, never widen the ticket.

## 3. Ask the user, once

If any finding is a criterion problem or a boundary issue, ask in one message, one numbered question per finding, each with options and your recommendation:

- **reopen**: the user rewrites or clarifies the criterion; record it in the ticket as `Reopened by user on <date>: <old> → <new>`;
- **split**: move the work into a new ticket (draft it with the `to-tickets` template, then freeze it);
- **accept**: ship this ticket with the finding recorded in `followups.md`;
- **drop**: remove the criterion or the ticket from this spec.

Continue with the defects and evidence gaps that the questions do not affect while waiting.

## 4. Verify before asking for the next round

Re-run the evidence for every item you fixed and for every passing criterion the fix could have touched, then the full test suite. Only when that is clean, call the Skill tool with "frozen-review" for the next round.

## 5. When the round limit is reached

If the latest round was the last one allowed (round 2) and it still did not pass, do not fix anything more. Write `.workflow/<feature>/reviews/<NN>-decision.md` with each remaining finding, its cause, and the same four options (reopen, split, accept, drop) with your recommendation, and ask the user to pick. Their choice is the outcome; record it in that file. Then end with the next step on its own line, worked out the same way `/implement` does (the next unblocked ticket, or the PR when every ticket is done).

If the same cause showed up in both rounds, suggest the user run `/retro` so the next ticket does not repeat it (a missing check, a vague criterion, an unclear standard).
