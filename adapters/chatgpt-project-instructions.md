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
