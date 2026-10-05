# Changelog

## 0.2.1 — 2026-10-05

Distribution-only correction:

- use `~/.agents/skills` as the default Codex user-scope Skills location;
- move installer state outside the Skills directory to `~/.local/state/engineering-workflow-skills`;
- add explicit staging overrides instead of treating `CODEX_HOME` as the Skills root;
- enforce LF line endings for portable scripts;
- mark shell helpers executable in Git;
- no lifecycle Skill semantics changed.
## 0.2.0 — 2026-10-05

Initial repository release of the six-skill engineering workflow kernel:

- `project-grill`
- `to-spec`
- `to-tickets`
- `review-contract`
- `safe-implement`
- `review`

Includes Codex user-scope install/update/verify/uninstall helpers, ChatGPT/Codex routing adapters, existing-skill migration guidance, and activation/boundary test fixtures.
