---
name: to-tickets
description: Split a spec or plan into tracer-bullet tickets with blocking edges, then freeze their acceptance criteria.
disable-model-invocation: true
---

Break a spec, plan, or the current conversation into **tickets**: thin vertical slices, each declaring the tickets that **block** it.

## 1. Gather context

Read `.workflow/<feature>/spec.md` (or the reference the user passed). If the spec says `Status: PARTIAL`, stop and tell the user which decisions are still open.

Explore the codebase if you have not already. Look for prefactoring that makes the change easy: "Make the change easy, then make the easy change."

## 2. Draft vertical slices

- Each ticket cuts a narrow but complete path through every layer it touches (schema, API, UI, tests), not a horizontal slice of one layer.
- Each ticket is demoable or verifiable on its own.
- Each ticket fits in one fresh context window.
- Prefactoring comes first.
- Do not split purely sequential steps into separate tickets just to list them; keep them as a checklist inside one ticket.

Give each ticket its **blocking edges**: the tickets that must finish before it can start.

**Wide refactors** (one mechanical change that breaks many call sites at once) don't fit a vertical slice. Sequence them as expand, migrate in batches, contract: add the new form beside the old, migrate callers in batches that each stay green, then delete the old form once nothing uses it.

## 3. Check with the user

Show the breakdown as a numbered list with title, blocked by, and what it delivers. Ask whether the granularity and the blocking edges are right, and iterate until the user approves.

## 4. Write the tickets

Write one file per ticket to `.workflow/<feature>/tickets/<NN>-<slug>.md`, numbered in dependency order (blockers first). If the user asks for GitHub Issues, also publish one issue per ticket with `gh`, blockers first, and record the issue URL in each file.

<ticket-template>

# <NN>: <Ticket title>

**Spec requirements covered:** R1, R4

**What to build:** the end-to-end behavior this ticket makes work, from the user's perspective.

**Blocked by:** ticket numbers, or "None".

**Draft acceptance criteria:**

- [ ] <observable, falsifiable criterion>
- [ ] <observable, falsifiable criterion>

**Status:** draft

</ticket-template>

Avoid file paths and code snippets in tickets; they go stale fast.

## 5. Freeze acceptance

Every spec requirement must be covered by at least one ticket. Then call the Skill tool with "freeze-acceptance" for the ticket set. Tickets are ready to implement only after it returns `APPROVED`.
