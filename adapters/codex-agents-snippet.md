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
