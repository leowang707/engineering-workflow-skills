---
name: workflow
description: Show which skill or flow fits what you are doing. A map of every skill in this workflow.
disable-model-invocation: true
---

# Workflow map

Help the user pick the right skill. Before describing what a skill does or recommending that a step be skipped, read that skill's `SKILL.md`; the summaries here are for orientation only.

Work artifacts live in `.workflow/<feature>/` in the project, so any session (Claude or Codex) can pick up where the last one stopped:

```
.workflow/<feature>/
  decisions.md      settled decisions and UNKNOWNs (grilling)
  spec.md           the spec (to-spec)
  tickets/NN-*.md   one file per ticket (to-tickets)
  acceptance.md     freeze rounds and results (freeze-acceptance)
  reviews/NN-rK.md  review reports (frozen-review)
  handoff.md        handoff notes (handoff)
```

## Main flow: idea to shipped code

1. **`grilling`**: settle every material decision, one round at a time. Facts are looked up, decisions are asked.
2. **`/to-spec`**: write the settled decisions into a spec with numbered, falsifiable requirements. Marked `PARTIAL` if a decision is still open.
3. **`/to-tickets`**: split the spec into tracer-bullet tickets with blocking edges, then call **`freeze-acceptance`** to check the set and lock each ticket's acceptance criteria (at most 2 rounds).
4. **`/implement`** one ticket at a time, clearing context between tickets. It builds with **`tdd`** inside the ticket's boundary, then calls **`frozen-review`**, which grades only against the frozen criteria (at most 2 rounds, then the user decides).

Small change that fits in one session? Skip steps 2 and 3: grill if needed, then build with `tdd` and review with `frozen-review` against what was agreed in the conversation.

Keep steps 1 to 3 in one unbroken context so the spec and tickets build on the same thinking. Each `/implement` starts fresh from its ticket file.

## On-ramps

- **Something is broken** → **`diagnosing-bugs`**. It builds a tight feedback loop that goes red on this bug before forming any theory, then fixes it with a regression test.

## Moving between sessions

- **`/handoff`**: write a handoff file so another session, another tool (Claude or Codex), or a colleague can continue.

## Extending

- **`/new-skill`**: add a new skill to this workflow so it works in both Claude and Codex and appears on this map.

## Skills

<!-- Every skill folder under skills/ must be listed here; scripts/validate.py checks it. -->

| Skill | Invoked by | Purpose |
|---|---|---|
| `workflow` | user | This map |
| `grilling` | model or user | Settle decisions round by round |
| `to-spec` | user | Write the spec |
| `to-tickets` | user | Split into tickets and freeze acceptance |
| `freeze-acceptance` | model or user | Check tickets and lock acceptance criteria |
| `implement` | user | Build one frozen ticket |
| `tdd` | model or user | Red-green loop at agreed seams |
| `frozen-review` | model or user | Two-axis review with a fixed verdict |
| `diagnosing-bugs` | model or user | Feedback-loop-first debugging |
| `handoff` | user | Handoff document for the next session |
| `new-skill` | user | Add a skill to this workflow |
