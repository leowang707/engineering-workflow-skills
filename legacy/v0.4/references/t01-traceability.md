# T01 source traceability

This is an implementation evidence locator, not a review disposition. The exact
bootstrap specification and Frozen Review Contract remain normative. R71–R73
rows cover framework source only; runtime migration and R74 seal belong to T03.

All tests below are in `tests/test_framework.py`. Both StateStore fixtures execute
each parametrized case with a separate durable Chat project root and a local Git
control repository. No fixture uses Device A runtime or preserved Serena residue.

| Requirement | Local Claim | Implementation locator | Behavioral evidence locator |
|---|---|---|---|
| R1 | T01.C01 | policy.authority / surface / handoff; delivery.distribution | test_c01_authority_surface_and_handoff; test_c10_distribution_and_migration |
| R2 | T01.C01 | policy.authority / surface / handoff; delivery.distribution | test_c01_authority_surface_and_handoff; test_c10_distribution_and_migration |
| R3 | T01.C01 | policy.authority / surface / handoff; delivery.distribution | test_c01_authority_surface_and_handoff; test_c10_distribution_and_migration |
| R4 | T01.C01 | policy.authority / surface / handoff; delivery.distribution | test_c01_authority_surface_and_handoff; test_c10_distribution_and_migration |
| R5 | T01.C01 | policy.authority / surface / handoff; delivery.distribution | test_c01_authority_surface_and_handoff; test_c10_distribution_and_migration |
| R6 | T01.C02 | policy.project_policy / CapabilityRegistry.resolve; state index pins | test_c02_capability_runtime_eligibility_optin_and_order; test_c04_authorization_migration_and_spec_bytes |
| R7 | T01.C02 | policy.project_policy / CapabilityRegistry.resolve; state index pins | test_c02_capability_runtime_eligibility_optin_and_order; test_c04_authorization_migration_and_spec_bytes |
| R8 | T01.C02 | policy.project_policy / CapabilityRegistry.resolve; state index pins | test_c02_capability_runtime_eligibility_optin_and_order; test_c04_authorization_migration_and_spec_bytes |
| R9 | T01.C02 | policy.project_policy / CapabilityRegistry.resolve; state index pins | test_c02_capability_runtime_eligibility_optin_and_order; test_c04_authorization_migration_and_spec_bytes |
| R10 | T01.C02 | policy.project_policy / CapabilityRegistry.resolve; state index pins | test_c02_capability_runtime_eligibility_optin_and_order; test_c04_authorization_migration_and_spec_bytes |
| R11 | T01.C02 | policy.project_policy / CapabilityRegistry.resolve; state index pins | test_c02_capability_runtime_eligibility_optin_and_order; test_c04_authorization_migration_and_spec_bytes |
| R12 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R13 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R14 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R15 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R16 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R17 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R18 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R19 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R20 | T01.C03 | policy.route / permission / escalate / independent_review; policies/execution.yaml | test_c03_roles_drift_escalation_independence; test_c03_resource_routing_does_not_change_boundary |
| R21 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R22 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R23 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R24 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R25 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R26 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R27 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R28 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R29 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R30 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R31 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R32 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R33 | T01.C04 | state.ProjectStateStore / GitStateStore / schemas; versioned authorization and migration | test_c04_both_stores_reconstruct_exact_versions_and_atomic_index; test_c04_authorization_migration_and_spec_bytes; test_c04_integrity_corruption_does_not_repair; test_c04_atomic_failure_and_competing_writers |
| R34 | T01.C05 | state independent artifact families; provenance responsibility and review binding | test_c05_local_artifacts_do_not_invalidate_unrelated_contracts; test_c07_integration_packet_has_own_contract |
| R35 | T01.C05 | state independent artifact families; provenance responsibility and review binding | test_c05_local_artifacts_do_not_invalidate_unrelated_contracts; test_c07_integration_packet_has_own_contract |
| R36 | T01.C05 | state independent artifact families; provenance responsibility and review binding | test_c05_local_artifacts_do_not_invalidate_unrelated_contracts; test_c07_integration_packet_has_own_contract |
| R37 | T01.C08 | progression.complete / derive_current; gitops.terminalize | test_c08_completion_remote_cleanup_terminal; test_c09_durable_end_to_end_and_c07_review_gates |
| R38 | T01.C08 | progression.complete / derive_current; gitops.terminalize | test_c08_completion_remote_cleanup_terminal; test_c09_durable_end_to_end_and_c07_review_gates |
| R39 | T01.C05 | provenance.responsibility_graph / refine_mapping / affected / reuse_evidence | test_c05_ownership_mapping_selective_reuse; test_c05_durable_reuse_preserves_identity_and_rejects_unknown |
| R40 | T01.C05 | provenance.responsibility_graph / refine_mapping / affected / reuse_evidence | test_c05_ownership_mapping_selective_reuse; test_c05_durable_reuse_preserves_identity_and_rejects_unknown |
| R41 | T01.C05 | provenance.responsibility_graph / refine_mapping / affected / reuse_evidence | test_c05_ownership_mapping_selective_reuse; test_c05_durable_reuse_preserves_identity_and_rejects_unknown |
| R42 | T01.C05 | provenance.responsibility_graph / refine_mapping / affected / reuse_evidence | test_c05_ownership_mapping_selective_reuse; test_c05_durable_reuse_preserves_identity_and_rejects_unknown |
| R43 | T01.C06 | provenance.IdentityRegistry / candidate_attribution / provider adapters / provenance_gate | test_c06_identity_and_prefrozen_triggers; test_c06_runtime_gates_and_timing; test_c09_durable_end_to_end_and_c07_review_gates |
| R44 | T01.C06 | provenance.IdentityRegistry / candidate_attribution / provider adapters / provenance_gate | test_c06_identity_and_prefrozen_triggers; test_c06_runtime_gates_and_timing; test_c09_durable_end_to_end_and_c07_review_gates |
| R45 | T01.C06 | provenance.IdentityRegistry / candidate_attribution / provider adapters / provenance_gate | test_c06_identity_and_prefrozen_triggers; test_c06_runtime_gates_and_timing; test_c09_durable_end_to_end_and_c07_review_gates |
| R46 | T01.C06 | provenance.IdentityRegistry / candidate_attribution / provider adapters / provenance_gate | test_c06_identity_and_prefrozen_triggers; test_c06_runtime_gates_and_timing; test_c09_durable_end_to_end_and_c07_review_gates |
| R47 | T01.C03 | policy.validate_role / use_role; state execution artifacts | test_c03_roles_drift_escalation_independence; test_c06_runtime_gates_and_timing |
| R48 | T01.C03 | policy.validate_role / use_role; state execution artifacts | test_c03_roles_drift_escalation_independence; test_c06_runtime_gates_and_timing |
| R49 | T01.C06 | provenance.prepare_review / freeze_invariants / pre_mutation_gate | test_c06_identity_and_prefrozen_triggers; test_c06_frozen_mutation_preconditions_fail_closed; test_c09_durable_end_to_end_and_c07_review_gates |
| R50 | T01.C06 | provenance.prepare_review / freeze_invariants / pre_mutation_gate | test_c06_identity_and_prefrozen_triggers; test_c06_frozen_mutation_preconditions_fail_closed; test_c09_durable_end_to_end_and_c07_review_gates |
| R51 | T01.C06 | provenance.prepare_review / freeze_invariants / pre_mutation_gate | test_c06_identity_and_prefrozen_triggers; test_c06_frozen_mutation_preconditions_fail_closed; test_c09_durable_end_to_end_and_c07_review_gates |
| R52 | T01.C06 | provenance.prepare_review / freeze_invariants / pre_mutation_gate | test_c06_identity_and_prefrozen_triggers; test_c06_frozen_mutation_preconditions_fail_closed; test_c09_durable_end_to_end_and_c07_review_gates |
| R53 | T01.C07 | provenance.review_packet / evidence_resolve / blocking_review_evidence; state review-result persistence | test_c07_exact_packet_evidence_and_durable_review; test_c09_durable_end_to_end_and_c07_review_gates |
| R54 | T01.C07 | provenance.review_packet / evidence_resolve / blocking_review_evidence; state review-result persistence | test_c07_exact_packet_evidence_and_durable_review; test_c09_durable_end_to_end_and_c07_review_gates |
| R55 | T01.C07 | provenance.review_packet / evidence_resolve / blocking_review_evidence; state review-result persistence | test_c07_exact_packet_evidence_and_durable_review; test_c09_durable_end_to_end_and_c07_review_gates |
| R56 | T01.C05 | provenance.remediation / affected / reuse_evidence | test_c05_ownership_mapping_selective_reuse; test_c05_durable_reuse_preserves_identity_and_rejects_unknown |
| R57 | T01.C05 | provenance.remediation / affected / reuse_evidence | test_c05_ownership_mapping_selective_reuse; test_c05_durable_reuse_preserves_identity_and_rejects_unknown |
| R58 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R59 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R60 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R61 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R62 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R63 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R64 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R65 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R66 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R67 | T01.C08 | gitops.GitLifecycle; progression remote/cleanup gates; terminal persistence | test_c08_git_isolation_mechanical_integration_and_conflict; test_c08_completion_remote_cleanup_terminal |
| R68 | T01.C09 | progression.derive_current / sequence_current / chat_implementation | test_c09_authorized_progression_and_all_stops; test_c09_durable_end_to_end_and_c07_review_gates; test_c09_authorization_reduction_is_immediate |
| R69 | T01.C09 | progression.derive_current / sequence_current / chat_implementation | test_c09_authorized_progression_and_all_stops; test_c09_durable_end_to_end_and_c07_review_gates; test_c09_authorization_reduction_is_immediate |
| R70 | T01.C09 | progression.derive_current / sequence_current / chat_implementation | test_c09_authorized_progression_and_all_stops; test_c09_durable_end_to_end_and_c07_review_gates; test_c09_authorization_reduction_is_immediate |
| R71 | T01.C10 | delivery / explicit payload builder / migration guidance / release metadata | test_c10_distribution_and_migration; test_c10_payload_and_helpers_only_explicit_destinations |
| R72 | T01.C10 | delivery / explicit payload builder / migration guidance / release metadata | test_c10_distribution_and_migration; test_c10_payload_and_helpers_only_explicit_destinations |
| R73 | T01.C10 | delivery / explicit payload builder / migration guidance / release metadata | test_c10_distribution_and_migration; test_c10_payload_and_helpers_only_explicit_destinations |

## Invariant implementation evidence

| Invariant | Evidence |
|---|---|
| RI-1 | Both-store integrity/schema/binding rejection and exact source manifest checks. |
| RI-2 | Exact Git object verification, durable artifact revision retrieval and execution attribution tests. |
| RI-3 | Current exact validation references; config drift, missing/failed provenance and review preparation rejection tests. |
| RI-4 | Role/surface/mutation scope and remote authorization tests; implementation worker admission/exit observations are separate external evidence. |
| RI-5 | Fresh independent context acceptance and same-context/history/specialist rejection; no formal review occurs in this test suite. |
| RI-6 | Frozen mutation preconditions resolved durably before mutation; missing, late and drifted resolution rejection. |
| RI-7 | Exact evidence strength/scope checks, durable acquired evidence, affected/unknown rejection and unaffected reuse without rebinding. |

Kernel identities are pinned in `policies/kernel-hashes.json`; `scripts/validate.sh`
checks them and the artifact/reference schema exports. The release manifest excludes
`.serena/**` and `.engineering/**`. Tests produce observations; they cannot grade
this bootstrap Ticket or retroactively change its acceptance standards.
