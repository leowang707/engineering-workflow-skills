---
name: grilling
description: Interview the user round by round until every material decision about a plan or design is settled. Use when the user wants to plan a feature, stress-test a design, decide requirements before building, or says "grill me".
---

Interview the user until you reach a shared understanding. Map the problem as a **design tree**: every decision branches into the decisions that hang off it.

## Facts are yours, decisions are the user's

Finding **facts** is your job, never the user's. When a question needs a fact from the environment (code, config, docs, tools), look it up yourself, or in a sub-agent if your harness has one. Never ask the user to guess a fact. A fact you cannot verify stays marked `UNKNOWN`.

**Decisions** belong to the user. Ask only decisions that can materially change scope, architecture, observable behavior, risk, acceptance, or how the work splits. Settle trivia yourself and say what you chose.

## Rounds

The **frontier** is every open decision whose prerequisites are already settled. Ask the whole frontier in one round, numbered, each with your recommended answer. Then wait.

```
❓ **Q1** - **<question title>**: <question body, including the options and the key trade-off>

➡️ <your recommended answer>

---

❓ **Q2** - ...
```

Word each question so "yes" accepts your recommendation. A question that depends on another question still open in this round belongs to a later round.

After each round, record the answers, recompute the frontier, and ask the next round. Reuse earlier decisions unless new evidence contradicts one; then reopen only that branch.

## Record

When working in a repository, keep the settled decisions in `.workflow/<feature>/decisions.md` as you go: one line per decision with its reason, plus a list of remaining `UNKNOWN` facts. Later skills (`to-spec`) read this file, so it survives a cleared context.

## Done

The session is done when the frontier is empty: every branch visited, every remaining unknown written down, nothing silently assumed. Confirm the shared understanding with the user before anything is built. Do not implement.

If this grilling is the start of a build, end with the next step on its own line, in the same conversation:

- `Next: /to-spec`, for work that needs a spec and tickets;
- `Next: build it with tdd, then review with frozen-review`, for a small change that fits in this session.
