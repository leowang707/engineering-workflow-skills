# Changelog

## 0.4.0 - 2026-10-08

- Add multi-surface framework infrastructure, durable YAML StateStores, exact provenance and review projections.
- Add role/capability boundaries, selective invalidation, Git isolation and authorized progression.
- Add explicit distribution payloads and staged migration support; preserve all six kernel bytes.
- Device runtime migration and release publication remain separately authorized operations.

## 0.3.0 - 2026-10-05

Test-derived workflow semantics fixes:

- `to-spec`: define fail-closed `PARTIAL_SPEC` behavior when material decisions remain unresolved;
- `review-contract`: make structural review a hard gate before Contract Review;
- `review`: restore deterministic overall-result aggregation, including `PASS_WITH_FINDINGS`;
- add regression boundary cases for all three behaviors.

## 0.2.2 - 2026-10-05

ChatGPT distribution support:

- add a GitHub-backed plugin marketplace manifest;
- allow the six core lifecycle Skills to be imported into ChatGPT from the authoritative repository;
- no lifecycle Skill semantics changed.

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
