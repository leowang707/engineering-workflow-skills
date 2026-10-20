# ChatGPT Project Router

Use the workflow skills stored in this project's sources.

Lifecycle:

`project-grill` -> `to-spec` -> `to-tickets` -> `review-contract` -> `safe-implement` -> `review`

Use only the skill required for the current phase.
Do not merge responsibilities between phases.

If the user explicitly names a skill, use that skill.
Do not advance from a phase when its completion conditions are not met.
Do not reinterpret frozen outputs from an earlier phase.

Specialist skills may choose how to perform their specialty, but they do not own lifecycle decisions or frozen standards.

The pinned project profile determines enabled phases. In hybrid_engineering only
project-grill and to-spec run here; persist the exact frozen normative packet for
Codex. In chat_engineering_full all six phases may run here, with durable project
StateStore, allowed mutation capability, immutable candidate identity and fresh
independent review. Missing storage/capability/identity blocks; do not transfer to
an unauthorized backend. The none profile enables no lifecycle authority.
