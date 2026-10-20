# Framework v0.4.0

The six `skills/*/SKILL.md` files remain the sole semantic authority. This package
implements storage, validation, routing and projections around them. Python API
callers are trusted persistence/execution operators: an `author` argument identifies
the upstream authority whose exact output is being persisted; it does not empower
a caller to make that authority's decisions. Runtime permissions must enforce the
same role boundary. No API grants a specialist formal grading authority.

## Running locally

Python 3.12, PyYAML, jsonschema and pytest are required. No network service is
needed. Run `scripts/validate.sh` for source validation and isolated behavioral
tests. Tests use explicit temporary directories and never install the framework.

`python3 -B -m framework build-distribution --source . --destination /tmp/new-payload
--profile hybrid_engineering --surface Codex` builds a new payload. Use one shell
line. Its manifest binds the selected payload and all six source kernel hashes.
The Chat payload uses the same source with `--surface Chat`. No separate semantic
copies are maintained in this repository. `chat_engineering_full` deploys all six
on Chat; `none` enables none. There is no Codex-full fallback.

Deployment helpers require explicit destination and state directories; deployment
is a separate authorized operation. Framework source validation is not Device A
acceptance or migration. A Chat deployment must expose an eligible durable
project file capability; conversation text is never a StateStore backend.

## StateStore and artifacts

`ProjectStateStore(root, project_id, work_id)` provides durable project-scoped
Chat artifact semantics over a file capability. `GitStateStore(repository, work_id)`
uses `.engineering/<work-id>` on `work/<work-id>` and commits every publication.
Both expose `create`, `read`, `versions`, `index`, `update_index`, and
`persist_spec`. A session can reconstruct all state from the explicit root and
exact references. Chat providers without that durable capability block.

Authoritative data is strict YAML with a JSON-compatible value domain. Duplicate
keys, unsupported types, schema mismatches, incorrect references, hashes or parent
bindings reject. SHA-256 covers the exact serialized bytes. References contain
work ID, type, version and hash. A Git commit supplements this identity.

Chat artifacts publish by fsynced exclusive link; index updates use a lock,
fsynced rename and compare-and-swap. Existing versions are never overwritten.
Git publication prepares durable objects and a single-path control commit using
a private index, then writes a checksummed transaction record in Git metadata.
An atomic ref compare-and-swap publishes the commit before projecting its bytes
to the working file and real index. A repository-wide lock serializes cooperating
writers and graph reads. Unrelated staged, unstaged and untracked content is
preserved and never included in the control commit.
Git subprocesses inherit the writer lock so a surviving ref-update child retains
exclusion after its Python parent is killed; restart waits for that child before
interpreting the transaction record.

After process interruption, a new store instance validates the transaction's
exact commit identities, parent, path, blob content, branch and old/new working
and index values. It abandons an unpublished preparation or finishes a published
projection. Concurrent ref changes are accepted only when commit ancestry and
the exact affected path establish that disposition. Unknown or corrupted journal,
artifact, index or ref state blocks without repair. Recovery never changes a
published semantic artifact or advances the ref. Synchronization and transaction
metadata are operational, not authoritative lifecycle content.

`state.yaml` contains only work ID, framework/schema/policy pins and exact semantic
artifact bindings. Runtime validations belong to individual execution/evidence
references, never a work-wide current pointer. Framework and policy upgrades
require an explicit successful migration record with semantic comparison, affected
state and revalidated gates. Project defaults do not change existing pins.

Authorization is an immutable family with independently versioned phase and
remote grants. The current binding takes effect on the next eligibility check.
Old artifacts remain historical. `persist_spec` preserves exact frozen Chat packet
bytes, including UNKNOWNs, and refuses a semantic-changing serialization.

## Execution, review and progression

`CapabilityRegistry` combines framework eligibility definitions, project opt-in,
runtime probes and deterministic preferences. Probes must observe actual version,
mode and properties; registry declarations alone never qualify a provider.
Serena must additionally report project-read-only mode, no global activation and
no write exposure. Opt-in means allowed; required properties come from the frozen
Execution Preconditions. Missing eligible providers block without weakening them.

Role validation runs fully per session and checks the exact configuration hash
per use. Drift requires renewed validation; replacing a model does not change a
Ticket. `route` chooses resources only, and `escalate` permits one unchanged-boundary
fast-to-complex transition. Production writes belong only to bounded workers;
root persists control data, coordinates and performs mechanical integration.

Review uses `IdentityRegistry`, exact durable execution attribution,
`provenance_gate`, `independent_review`, `review_packet` and `evidence_resolve`.
The packet is an ephemeral deterministic projection, never a new standard.
Reviewers lazy-load exact evidence under frozen strength/scope requirements.
Every loaded reference must bind the exact contract, cite only its member Claims,
and meet each cited Claim's frozen strength and the Ticket's allowed scope.
Invalid identity, hash, schema, binding, scope or strength retains
`EVIDENCE_REFERENCE_INVALID` through the pre-grading entry point. Proven unaffected
evidence reuse preserves the original candidate identity and requires an exact
durable reuse proof.
Blocking reviewer-acquired evidence must already exist durably before a result
can cite it. Invariant applicability reads only preimplementation facts; semantic
UNKNOWNs return upstream, runtime-only conditions resolve durably before mutation.

`derive_current` is the production read-only eligibility entry point; it reloads
durable authorization, pins, bindings and frozen outcomes. `sequence_current`
invokes only an eligible phase on its authorized surface. It neither implements
nor grades. Implementation/review eligibility requires accepted direct and
transitive Ticket prerequisites; current failure, blocked or insufficient outcomes
cannot be bypassed by missing dependent evidence. Unrelated authorized parallel
work remains eligible. The lower-level `derive` accepts an already resolved gate snapshot
for adapters and tests; such a snapshot is not authoritative persistent state.
Completion is derived from the complete local and explicit integration Claim set.
No additional global grading artifact is produced.

Responsibility IDs, owners, meanings and boundaries are stable. Locator refinement
requires root persistence and exact semantic equality. Local artifacts are
independently versioned. `affected` computes affected/unknown as STALE and requires
explicit proof for unaffected reuse. It never edits old evidence to bind a new
candidate. Same-boundary remediation preserves Ticket/Contract identity.

Git operations pin control/target bases, isolate Ticket worktrees, retain reviewed
candidate history and integrate only a conflict-free exact expected tree. Conflicts
return `INTEGRATION_REQUIRED` for explicit engineering. Target drift requires
impact resolution; reviewed history is never rebased. Provenance travels into the
target tree. Cleanup requires derived completion, verified integration, retained
provenance and completion of separately required remote operations. Remote checks
require root and a separate exact remote/branch/SHA grant; workers never push.

Terminalization is a historical persistence operation after completion and
integration, not grading. Terminal work cannot acquire new versions; follow-up
engineering uses a new work ID and may refer to the old record.

## Failure boundary

`Blocked.code` preserves HANDOFF_NOT_READY, DURABLE_STATE_STORE_UNAVAILABLE,
LIFECYCLE_STATE_INVALID, ROLE_CONFIG_INVALID, CONFIG_DRIFT_DETECTED,
REQUIRED_CAPABILITY_UNSATISFIED, IMPLEMENTATION_IDENTITY_INVALID,
REVIEW_PRECONDITION_UNSATISFIED, EVIDENCE_REFERENCE_INVALID, STRUCTURAL_CHANGE,
INTEGRATION_REQUIRED, REMOTE_OPERATION_BLOCKED and BLOCKED. Contract ambiguity
remains a lifecycle stop. These are never automatically product Claim FAILs.

The implementation and its tests cannot create retrospective standards for the
bootstrap T01 execution. Its independently frozen specification and contract
remain the acceptance authority.
