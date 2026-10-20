---
name: new-skill
description: Add a new skill to this workflow repo so it works in both Claude Code and Codex and shows up on the workflow map.
disable-model-invocation: true
---

Add a new skill to this repository. Run this from the root of the `engineering-workflow-skills` checkout.

## 1. Pin down the skill

Ask the user, in one round with your recommendations:

- **Name**: lowercase kebab-case, not already used under `skills/`, and not a name a harness already uses for a built-in command (`review`, `init`, `help`, `compact`, `clear`).
- **Invocation**:
  - **model-invoked** (default) when the agent could usefully reach for it on its own;
  - **user-invoked** when it should run only when the user types it, for example a step that publishes something or starts a long flow.
- **Where it fits**: a step in the main flow, an on-ramp, or standalone.

## 2. Scaffold

Run:

```sh
scripts/new-skill.sh <name> <model|user> "<Display Name>" "<short description>"
```

It creates `skills/<name>/SKILL.md` from `templates/SKILL.md` and `skills/<name>/agents/openai.yaml` for Codex, with the invocation setting matched in both files.

## 3. Write the skill

Call the Skill tool with "writing-for-agents" for the writing guide, then fill in `SKILL.md`:

- **description**: for a model-invoked skill, say what it does and then "Use when ..." with the phrases a user would actually say; this is what makes the agent pick it. For a user-invoked skill, a one-line human summary is enough. Keep it under 1024 characters.
- **body**: short and imperative. Give the agent concrete output formats (templates, file locations under `.workflow/<feature>/`) rather than abstract rules. Define any term the skill relies on inside the skill itself.
- Every loop needs an explicit stop condition: a round limit, and what to hand back to the user when it is reached.
- To use another skill, write `Call the Skill tool with "<name>"`. That only works for model-invoked skills; for a user-invoked one, tell the user to run `/<name>`.
- Longer reference material goes in extra files next to `SKILL.md`, linked from it, so it loads only when needed.

## 4. Register

- Add the skill to the map and the table in `skills/workflow/SKILL.md`.
- Add it to the skill list in `README.md`.
- Add a line to `CHANGELOG.md`.

## 5. Validate and install

Run `python3 scripts/validate.py`; fix anything it reports. Then:

- If the user installed through a plugin, they get the new skill after they push and the plugin updates.
- If the user installed with `scripts/link-skills.sh`, run it again so the new folder is linked into `~/.claude/skills` and `~/.agents/skills`.
