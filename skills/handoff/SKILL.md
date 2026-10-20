---
name: handoff
description: Compact the current conversation into a handoff document for another agent or session to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarizing the current conversation so a fresh agent (Claude or Codex) can continue the work.

Save it to `.workflow/<feature>/handoff.md` when a `.workflow` folder exists for this work; otherwise to the OS temporary directory (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows), not the workspace.

Include:

- what the goal is and where the work stands;
- which tickets are done, in progress, or blocked, and why;
- a "suggested skills" section naming which skills the next agent should call the Skill tool for.

Do not duplicate what other artifacts already hold (spec, tickets, reviews, decisions, commits, diffs). Reference them by path or URL.

Redact secrets and personal data: API keys, passwords, tokens.

If the user passed arguments, treat them as what the next session will focus on and tailor the document to it.
