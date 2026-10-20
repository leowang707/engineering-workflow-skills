# Changelog

## 1.2.0 - 2026-10-20

- `grilling`, `to-spec`, `to-tickets`, `implement`, `implement-spec` and `resolve-review` end with a `Next:` line naming the command to run after them. They still never run that command themselves.
- Add `next`: reads `.workflow/<feature>/` and says where the work stands and the one command to run next, without running it.
- `scripts/link-skills.sh --codex-only` links only `~/.agents/skills`, for when Claude gets the skills another way.

## 1.1.0 - 2026-10-20

- Add `resolve-review`: when a review does not pass, each finding gets one cause (defect, evidence gap, environment, criterion problem, boundary, reviewer error) and a matching action; fixes go in one batch; after round 2 the user picks reopen, split, accept or drop.
- `frozen-review` and `implement` hand every non-passing result to `resolve-review` instead of looping on their own.
- Add from mattpocock/skills: `implement-spec` (adapted to frozen tickets), `pr`, `retro` (also reviews these skills), `prototype`, `research`, `writing-for-agents`.

## 1.0.0 - 2026-10-20

Rebuilt as a personal workflow that runs in both Claude Code and Codex.

- Add 11 skills: `workflow`, `grilling`, `to-spec`, `to-tickets`, `freeze-acceptance`, `implement`, `tdd`, `frozen-review`, `diagnosing-bugs`, `handoff`, `new-skill`. Several are adapted from mattpocock/skills (MIT).
- Keep v0.4's strict ideas: acceptance criteria frozen before coding, no criteria added after seeing the code, fixed verdict order, `PARTIAL` specs.
- Fix repeated reviews: `freeze-acceptance` and `frozen-review` run at most 2 rounds, then hand the decision to the user; missing evidence or blocked checks stop instead of looping.
- Rename `review` to `frozen-review` to avoid clashing with built-in review commands.
- Add Claude Code plugin and marketplace manifests, `agents/openai.yaml` for Codex, `scripts/link-skills.sh`, `scripts/new-skill.sh`, `scripts/validate.py` and a CI workflow.
- Move the v0.4 kernels, framework and records unchanged to `legacy/v0.4/`.

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
