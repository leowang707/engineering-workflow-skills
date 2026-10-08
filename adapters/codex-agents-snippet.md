# Reusable Engineering Workflow

Reusable workflow procedures live in Skills, not in `AGENTS.md`.

Lifecycle skills:
- `project-grill`: resolve material user decisions.
- `to-spec`: freeze requirement semantics.
- `to-tickets`: expose safe, useful parallel work.
- `review-contract`: independently freeze work boundaries and acceptance contracts before implementation.
- `safe-implement`: implement only inside a frozen Ticket boundary.
- `review`: independently grade only against frozen blocking standards.

When a lifecycle skill is explicitly requested, follow it.
Do not duplicate or override its procedure here.
Repository-specific facts, commands, constraints, and authorization rules belong in this `AGENTS.md`.

Use the project's pinned lifecycle profile and capability policy. In the default
hybrid profile, Codex owns only to-tickets, review-contract, safe-implement and
review. Require the exact durable Chat Frozen Spec before downstream work.
Use framework eligibility and role validation; root coordinates and persists
control data, workers implement bounded production changes, and formal review
uses a fresh independent root context. Only native execution routing participates.
Custom capabilities require explicit project opt-in; Serena must remain read-only.
Read durable state through the StateStore and derive eligibility; never treat
conversation history or a stored current-phase label as authority.
