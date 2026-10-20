# Engineering Workflow Skills 0.4.0

Version 0.4.0 combines six unchanged lifecycle skills with a multi-surface execution framework, durable lifecycle state and deterministic execution and review support. The six skills are the sole lifecycle semantic source; adapters and framework code provide storage, validation, routing and surface projections around them.

| Profile | Chat | Codex |
|---|---|---|
| `hybrid_engineering` | `project-grill`, `to-spec` | `to-tickets`, `review-contract`, `safe-implement`, `review` |
| `chat_engineering_full` | all six | none |
| `none` | none | none |

Runtime behavior does not transfer a phase to another surface as a fallback. In the hybrid profile, Chat authors the decisions and Frozen Spec; Codex consumes the exact durable Frozen Spec bytes and may persist them mechanically. Conversation history, paths and summaries are not substitutes for the artifact.

## Authority and execution

The six lifecycle skills own decisions, specification, decomposition, acceptance contracts, bounded implementation and formal grading. Project policy selects the profile and eligible capabilities without changing those semantics. The root coordinates work, persists control data, routes and integrates bounded candidates. `codex_explorer` supplies read-only evidence; `codex_fast_worker` and `codex_complex_worker` implement only their assigned frozen Ticket. A fresh independent context performs formal review; a bounded evidence specialist does not create another review authority.

Codex's native execution router selects models and effort from local role configuration. Model choice remains outside lifecycle semantics and cannot change a Ticket or acceptance contract. Prefer a lower-cost model when it is adequate; use a stronger model for work that needs it, and record the actual model and context as provenance. There is no separate model-router skill.

## Durable work state

Git-backed work stores versioned lifecycle records under `.engineering/<work-id>` on the work branch. Chat-only work requires a durable project `ProjectStateStore`; conversation text is not a state backend. In a hybrid handoff, Chat authors the exact Frozen Spec and the Codex side persists those same bytes through the approved durable mechanism. Artifacts and references bind exact identities and hashes. Changed inputs invalidate affected downstream work; missing or stale evidence cannot advance the lifecycle.

The [framework contract](references/framework.md) describes the StateStore APIs, capability checks, role validation, provenance and failure boundaries.

## Project workflow

1. Resolve material decisions with `project-grill`, then freeze the specification with `to-spec` on the profile's authorized surface.
2. Persist or transport the exact Frozen Spec into the durable store used by the project.
3. Use `to-tickets` to define useful implementation boundaries, then independently freeze their acceptance contracts with `review-contract` before implementation.
4. Implement each Ticket with `safe-implement`, within its frozen boundary.
5. Review the exact candidate with `review` in a fresh independent context. Integrate accepted candidates and preserve their provenance before delivery.

Parallel work needs independent Ticket boundaries and isolated worktrees. It is not a default reason to split work.

## Validate and build a distribution

Use Python 3.12 with PyYAML, jsonschema and pytest installed. The [validation script](scripts/validate.sh) runs against temporary fixtures; it does not install a distribution or certify Device A.

```sh
scripts/validate.sh
python3 -B -m framework build-distribution --source . --destination /tmp/ews-chat-0.4.0 --profile hybrid_engineering --surface Chat
TARGET_FRAMEWORK_HOME=/tmp/ews-codex-0.4.0 LIFECYCLE_PROFILE=hybrid_engineering scripts/install-codex-user.sh
TARGET_FRAMEWORK_HOME=/tmp/ews-codex-0.4.0 scripts/verify-codex-user.sh
```

Each destination must be new and explicit. The [Codex build helper](scripts/install-codex-user.sh) builds the Codex-surface payload at that destination; it does not register plugins, change routing or activate runtime configuration. The [update helper](scripts/update-codex-user.sh) uses the same explicit-destination build path. The [verification helper](scripts/verify-codex-user.sh) checks the distribution manifest and payload hashes. The [uninstall helper](scripts/uninstall-codex-user.sh) verifies and removes only the managed files listed for the selected distribution, leaving unrelated files in place.

The source repository retains all six kernels. Each distribution references the same semantic source and includes only the selected profile's enabled surface subset. The build command also supports `--surface Codex` and profiles `hybrid_engineering`, `chat_engineering_full` and `none`; there is no Codex-full fallback.

## Runtime capabilities

Native capabilities are baseline-allowed. A custom capability requires project opt-in and actual runtime eligibility checks; configuration declaration alone is insufficient. Opt-in does not create a hard dependency or grant lifecycle authority.

Serena is available only to an explicitly opted-in project. Its connection must be project-scoped and read-only, with no global activation or write exposure. The eligible tool set is `find_symbol`, `find_referencing_symbols`, `get_symbols_overview`, `search_for_pattern` and `get_current_config`. Verify the actual connected catalog; a configuration declaration alone does not qualify it. Projects without Serena opt-in use native read tools. Hermes and RTK are outside Codex routing; this does not require removing installations used independently of Codex.

## Migration and status

Device A migration is staged, gated and reversible: back up known-good state; validate the framework; normalize distributions and surfaces; migrate execution roles; remove duplicate routing and review control; establish the Serena boundary; validate coexistence and end-to-end behavior; then seal only after all acceptance conditions pass. The [migration plan](migration/MIGRATION_PLAN.md) describes the deployment and recovery support.

The Device A reference integration has completed all migration phases and the actual hybrid lifecycle, parallel execution, independent review, persistence and recovery checks. Fresh formal T03 review returned `PASS_WITH_FINDINGS`: all four Claims, seven Review Invariants and 17 R74 seal conditions passed, with no blocking finding. Device A is sealed under the recorded environment and recovery assumptions; see the [acceptance record](docs/DEVICE_A_ACCEPTANCE.md). Source or configuration conformance alone is not a seal.

GitHub repository delivery is separate from building or activating a runtime distribution. A commit or push does not itself establish the Device A integration seal.
