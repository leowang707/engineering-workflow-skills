# Engineering Workflow Skills

Version 0.4.0 combines six unchanged lifecycle kernels with a multi-surface
execution framework, durable lifecycle state and deterministic review infrastructure.

The six phases are project-grill, to-spec, to-tickets, review-contract,
safe-implement and review. They alone own decisions, semantics, decomposition,
contracts, bounded implementation and formal grading respectively.

| Profile | Chat | Codex |
|---|---|---|
| hybrid_engineering | project-grill, to-spec | to-tickets, review-contract, safe-implement, review |
| chat_engineering_full | all six | none |
| none | none | none |

No runtime fallback changes these surfaces. Codex consumes an exact durable Frozen
Spec and may persist its bytes mechanically. Descriptive evidence or conversation
history cannot substitute for that handoff.

## Validate source

Use Python 3.12 with PyYAML, jsonschema and pytest already installed:

```sh
scripts/validate.sh
```

This validates source, schemas, release identities, kernel hashes and isolated
positive/negative behavior. It does not perform formal lifecycle grading or certify
Device A. Tests write only to a temporary fixture root; no installation is needed.

## Build an explicit distribution

```sh
python3 -B -m framework build-distribution --source . --destination /tmp/ews-chat-0.4.0 --profile hybrid_engineering --surface Chat
TARGET_FRAMEWORK_HOME=/tmp/ews-codex-0.4.0 scripts/install-codex-user.sh
TARGET_FRAMEWORK_HOME=/tmp/ews-codex-0.4.0 scripts/verify-codex-user.sh
```

Destinations must be new and explicit. These commands assemble a payload; they do
not register plugins, change routing or activate runtime configuration. The source
repository retains all six kernels; each payload references that same semantic
source and includes only the profile's enabled surface subset.

The update helper builds into another new explicit destination. The uninstall
helper removes only receipt-listed files after verifying their hashes, retaining
unrelated files. Active-runtime migration requires its own accepted transaction.

## Infrastructure

- `framework/`: authority, capability, execution, persistence, review, Git and progression APIs.
- `schemas/`: versioned YAML-artifact/reference JSON schemas.
- `policies/`: project policy, eligibility registry and stable role contracts.
- `references/framework.md`: API contracts, failure semantics and operator boundaries.
- `tests/test_framework.py`: behavioral source evidence.
- `migration/`: staged deployment and recovery support without active-runtime mutation.
- `adapters/`: thin surface instructions; never copied lifecycle semantics.

Read [the framework contract](references/framework.md) for exact identities,
StateStore APIs, authorization, schema pinning, migration, selective invalidation,
review evidence and terminal history. Read [migration support](migration/MIGRATION_PLAN.md)
before any separately authorized deployment.

Native capabilities are baseline-allowed. Custom capabilities require project
opt-in and actual runtime eligibility verification. Opt-in does not create a hard
dependency or grant lifecycle authority. Exact model assignments belong in local
execution policy and are recorded as provenance, outside lifecycle semantics.

Publishing, tagging, pushing and remote merging require separate authorization.
All six kernel bytes retain compatibility with the reviewed pre-v0.4.0 source.
