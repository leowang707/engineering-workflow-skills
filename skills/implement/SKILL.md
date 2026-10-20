---
name: implement
description: Implement one ticket test-first inside its frozen boundary, then review it against its frozen acceptance criteria.
disable-model-invocation: true
---

Implement the ticket the user names (a path under `.workflow/<feature>/tickets/`, a number, or an issue URL). State its title before starting. If the reference is ambiguous, ask.

## Before you start

- The ticket must say `**Status:** frozen`. If it is still a draft, tell the user to run `/to-tickets` (which freezes acceptance) first.
- Every ticket it is blocked by must be done.
- Re-read the spec and the frozen criteria. If the code has drifted so that a frozen assumption no longer holds, stop and report it.

## Boundary

You own the **mechanism**: local algorithms, helpers, data structures, refactors inside the ticket's area, and the order of work.

You do not own requirements, architecture, or shared contracts. Without the user's approval do not add a new dependency, a new shared abstraction, a new public API, or behavior the ticket did not ask for. If the ticket can't be done without one, stop and return `STRUCTURAL_CHANGE` with the reason.

Tests may change only to prove the frozen criteria. Never change an expected value to make the code pass.

Fix only the defects this ticket needs. Note unrelated defects at the end instead of fixing them.

## Build

Call the Skill tool with "tdd" and work one red-green slice at a time at the seams the spec agreed. Run the type checker and single test files often, and the full test suite once at the end.

## Hand off

Before review, confirm each frozen criterion has candidate evidence (a passing test, a command output) and no known violation remains. Then return one of:

- `READY_FOR_REVIEW`
- `BLOCKED` (a precondition is missing; say which)
- `STRUCTURAL_CHANGE` (the frozen boundary does not fit; say why)

On `READY_FOR_REVIEW`, call the Skill tool with "frozen-review" for this ticket. Never declare the ticket passed yourself.

If the review returns `FAIL`, fix the named failures and call "frozen-review" again. Its round limit decides when to stop and ask the user.

When the review passes, commit to the current branch with the ticket number in the message, and set the ticket file to `**Status:** done`.
