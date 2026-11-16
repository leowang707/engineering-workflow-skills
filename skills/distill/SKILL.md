---
name: distill
description: Decide which specs and lessons from recent work are worth keeping, and file them as structured entries in the project's `.knowledge/` folder; also read that folder before planning or building. Use when a feature or bug fix is finished, after a review hit its round limit, when the user corrected the agent, when starting work in a project that has `.knowledge/INDEX.md`, or when the user says "remember this", "記下來", "save the lesson", "what did we learn".
---

Keep a small, curated store of what this project must not forget. You decide what goes in; the test below is how. Nothing needs setting up: the first write creates the store.

The workflow skills call this skill on their own at checkpoints (spec written, ticket done, review decided, bug fixed), so in daily use the user never has to ask. It runs in one of three modes:

- **checkpoint**: another skill called you and named its sources. Do not ask the user anything except to settle a contradiction. Report in one line.
- **manual**: the user asked ("remember this", "記下來", "what did we learn"). Full report, and you may offer the pointer line below.
- **reading**: you are about to plan or build. Read only.

Terms:

- **spec**: a rule the project must keep that the code alone does not make obvious: an invariant, a contract with another system, a constraint, or a decision together with the alternatives it beat.
- **lesson**: something learned the hard way: a pitfall, an approach that failed and why, a gotcha in the environment or a dependency.

## The store

```
.knowledge/
  INDEX.md            one line per active entry; the only file read every time
  specs/<slug>.md
  lessons/<slug>.md
```

It lives at the project root, outside `.workflow/` (which holds one feature's working files and is read by `/next`). Commit it like code, so Claude and Codex sessions share it.

`INDEX.md`:

```
# Project knowledge

- [spec] <title>: <the rule in one line> (specs/<slug>.md)
- [lesson] <title>: <the rule in one line> (lessons/<slug>.md)
```

Entry file:

```
---
type: spec | lesson
title: <short title>
status: active | superseded
updated: <YYYY-MM-DD>
applies-to: <paths or globs, or "whole project">
source: <where it came from: .workflow/<feature>/..., commit, PR, or "conversation YYYY-MM-DD">
---

**Rule:** <one sentence an agent can follow>

**Why:** <the reason or the incident; for a lesson, what happened>

**How to apply:** <when it matters and what to do; for a spec, the rejected alternatives>
```

## Reading (before planning or building)

When `.knowledge/INDEX.md` exists and you are about to plan, grill, write a spec, or implement: read `INDEX.md`, then open only the entries whose `applies-to` or title touches the work. Follow them. If the work would break an active spec, say so to the user before going on. Do not write anything in this mode.

## Writing

### 1. Gather

Read the sources for the work the user names, or the current session if they name none: the conversation, `.workflow/<feature>/` (`decisions.md`, `spec.md`, `reviews/`, `<NN>-decision.md`, `followups.md`, `handoff.md`), the diff and commit messages. Read `.knowledge/INDEX.md` too, so you update instead of duplicating.

### 2. Judge

List candidates, then keep one only if it passes all three:

1. **Durable**: still true after this feature ships. Status, progress and next steps fail; they belong in `handoff`.
2. **Not derivable**: an agent could not learn it in a minute from the code, tests, or `git log`. "The parser lives in `src/parse.ts`" fails.
3. **Costly to forget**: ignoring it would cause a bug, rework, a wrong decision, or a repeat of a long debug.

Strong signals that a candidate passes: the user corrected the agent; the same cause came up twice; a review hit its round limit; a bug's root cause was not where anyone first looked; a decision had real alternatives; a limit came from outside (an API, production, money, law).

Send elsewhere instead of keeping:

- a change to checks, lint, coding standards or these skills → suggest `/retro`;
- generic advice that holds for any project → drop;
- secrets, tokens, personal data → never store; keep only the rule ("keys come from the env var, never the repo").

### 3. File

For each kept candidate:

- If an active entry already covers it, update that entry (and its `updated` date) instead of adding one.
- If it contradicts an active entry, ask the user which holds. Mark the loser `status: superseded` and add a line to it saying what replaced it; remove it from `INDEX.md`.
- Otherwise write a new entry file and add its line to `INDEX.md`.

Write at most 5 entries in one run. If more candidates passed, keep the 5 costliest to forget and list the rest in your reply for the user to pick.

Keep `INDEX.md` under 100 lines. When it would go over, merge overlapping entries before adding new ones.

### 4. Report

In checkpoint mode, reply with one line: `Distilled: <k> kept (<titles>)` or `Distilled: nothing new`. In manual mode, reply with:

```
Kept:
- [spec|lesson] <title>: <rule> (new | updated | superseded <old>)
Not kept:
- <candidate>: <which test it failed, or where it went instead>
```

Stop there. The user can veto or edit any entry; the files are plain Markdown.

## First run in a project

If `.knowledge/` does not exist, create it with the layout above without asking. In manual mode only, offer once to add this one line to the project's `AGENTS.md` (Codex) or `CLAUDE.md` (Claude), so sessions that never load this skill still see the store:

```
Project knowledge: read `.knowledge/INDEX.md` before planning or changing code.
```

Add it only if the user agrees, and never add anything else to those files.
