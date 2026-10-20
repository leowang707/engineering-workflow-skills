---
name: to-spec
description: Turn the settled decisions in this conversation into a written spec, with no new interview.
disable-model-invocation: true
---

Turn the current conversation, and `.workflow/<feature>/decisions.md` if it exists, into a spec. Do NOT interview the user; synthesize what is already settled.

## Process

1. Explore the repo to understand the current code, if you haven't already. Use the project's own vocabulary (`GLOSSARY.md`, ADRs, README) throughout.
2. Sketch the **seams** where the feature will be tested: the public interfaces where behavior can be observed without reaching inside. Prefer existing seams and the highest seam possible; the ideal number is one. Check the seams with the user.
3. Check completeness. If a material decision is still missing or contradicted, write the spec anyway but mark it `Status: PARTIAL`, list the open decisions at the top, and tell the user to resolve them (the `grilling` skill) before `/to-tickets`. Never present a partial spec as complete, and keep unverified facts as `UNKNOWN`.
4. Write the spec with the template below to `.workflow/<feature>/spec.md`. If the user asks for it on GitHub Issues instead, publish it there with `gh` and also keep the local file.

<spec-template>

# <Feature name>

Status: COMPLETE | PARTIAL

## Problem Statement

The problem from the user's perspective.

## Solution

The solution from the user's perspective.

## User Stories

A long, numbered list covering every aspect of the feature:

1. As an <actor>, I want a <feature>, so that <benefit>

## Requirements

Numbered, observable, falsifiable statements of required behavior (R1, R2, ...). Each one must be judgeable as PASS or FAIL without seeing the implementation. Include failure behavior and any public contract (API, schema, CLI) the feature must honor.

## Implementation Decisions

Decisions already made: modules to build or change, their interfaces, schema changes, API contracts, architectural choices. No file paths or code snippets, which go stale fast. Exception: a snippet from a prototype that encodes a decision more precisely than prose (a state machine, a type shape), trimmed to the decision.

## Testing Decisions

The agreed seams, what makes a good test here (external behavior only), and prior art for tests in the codebase.

## Out of Scope

What this spec deliberately does not cover.

## Open Decisions and Unknowns

Only for a PARTIAL spec, or facts still `UNKNOWN`.

</spec-template>

Do not split the work into tickets here; that is `/to-tickets`.

## Next step

End with the next step on its own line:

- `COMPLETE`: `Next: /to-tickets` in this same conversation, so the tickets build on the same thinking.
- `PARTIAL`: `Next: settle the open decisions with grilling, then run /to-spec again`.
