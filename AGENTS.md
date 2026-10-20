# Working in this repo

This repo is a set of agent skills for both Claude Code and Codex.

- Each skill is a folder `skills/<name>/` holding `SKILL.md` (used by both tools) and `agents/openai.yaml` (Codex picker metadata).
- A skill is either **user-invoked** (`disable-model-invocation: true` in `SKILL.md` and `policy.allow_implicit_invocation: false` in `agents/openai.yaml`) or **model-invoked** (neither). Keep the two files in agreement.
- A model-invoked description says what the skill does, then "Use when ..." with phrases a user would say. A user-invoked description is a one-line human summary.
- One skill uses another by saying `Call the Skill tool with "<name>"`, and only for model-invoked skills. For a user-invoked one, tell the user to run `/<name>`.
- Every loop in a skill needs a stop condition and says what goes back to the user when it is reached.
- Work artifacts in user projects go under `.workflow/<feature>/`.
- To add a skill, follow `skills/new-skill/SKILL.md`: scaffold with `scripts/new-skill.sh`, register it in `skills/workflow/SKILL.md` and `README.md`, add a `CHANGELOG.md` line, and run `python3 scripts/validate.py`.
- `legacy/v0.4/` is a frozen archive. Do not edit it.
