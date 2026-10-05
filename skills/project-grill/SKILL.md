---
name: project-grill
description: Resolve material user decisions before specification while retrieving factual answers from authoritative evidence.
---

Map the problem as a decision tree.

Facts are yours to find. Decisions are the user's.
Do not ask for information available from authoritative evidence.

Ask only decisions that can materially change architecture, scope, observable behavior, risk, acceptance, or decomposition.

Maintain a decision frontier.
Ask one material decision at a time.
Batch only trivial, independent decisions that cannot affect one another or the downstream frontier.

For each decision:
- present materially distinct options;
- recommend one when justified;
- state the key trade-off.

After each answer, preserve resolved decisions and recompute the frontier.

Reuse existing decisions unless authoritative evidence materially contradicts them.
Then reopen only the affected branch.

Keep unverifiable facts `UNKNOWN`.
Never ask the user to guess a fact.

Complete only when all material decision branches are resolved, remaining unknowns are explicit, no silent assumptions remain, and shared understanding is confirmed.

Do not implement.
