# Known Existing Skill Classification

This matrix is **provisional**. It contains only skills/components established by prior project evidence. It is not a claim that these are the complete skills currently installed on the Codex host. Run `scripts/audit_existing_skills.py` on the host before migration.

| Name | Known role | Target class | Disposition | Core authority after migration |
|---|---|---|---|---|
| systematic-debugging | Debugging method | SPECIALIST | KEEP | None; operates under `safe-implement` |
| requesting-code-review | Code review workflow | LIFECYCLE_DUPLICATE | ALIAS_OR_RETIRE | Replaced by `review` |
| hermes-local-delegator | Bounded delegated execution | BACKEND | REMOVE_FROM_CODEX_INTEGRATION | Independent installation may remain |
| multi-model-agent-orchestrator | Mixed planning/delegation/review authority | MIXED_AUTHORITY | DISABLE_UNTIL_REWRITTEN | Rewrite only as execution backend if still needed |
| hermes-agent-skill-authoring | Skill authoring | META | KEEP_SEPARATE | None |
| hermes-agent | Broad Hermes agent workflow | NEEDS_AUDIT | INSPECT | Must not duplicate lifecycle authority |
| arxiv | Research | RESEARCH_SPECIALIST | KEEP_SEPARATE | None |
| llm-wiki | Research/reference | RESEARCH_SPECIALIST | KEEP_SEPARATE_PROVISIONAL | None; audit exact behavior |
| grounded-citations | Citation/evidence presentation | METHOD_SPECIALIST | KEEP_SEPARATE_PROVISIONAL | None; audit exact behavior |
| subagent-driven-development | Development orchestration | NEEDS_AUDIT | LIKELY_OVERLAP | Must not own decomposition, acceptance, or PASS |
| hermes-s6-container-supervision | Legacy container supervision | OBSOLETE | RETIRE | None |
| haoye-stock-analysis | Domain analysis | DOMAIN_SPECIALIST | KEEP_SEPARATE | None |
| taiwan-stock-data | Domain data | DOMAIN_SPECIALIST | KEEP_SEPARATE | None |
| taiwan-stock-strategy | Domain analysis | DOMAIN_SPECIALIST | KEEP_SEPARATE | None |
| taiwan-stock-timeframe | Domain analysis | DOMAIN_SPECIALIST | KEEP_SEPARATE | None |
| taiwan-stock-backtest | Domain analysis | DOMAIN_SPECIALIST | KEEP_SEPARATE | None |
| etf-accumulate-analysis | Domain analysis | DOMAIN_SPECIALIST | KEEP_SEPARATE | None |
| architecture-audit | Audit method | NEEDS_AUDIT | KEEP_IF_NONAUTHORITATIVE | May produce evidence/findings; must not replace `review-contract` or `review` |
| github-maintenance | Repository operations | OPERATOR | KEEP_SEPARATE | Requires explicit authorization policy; no lifecycle authority |
| cron-watchdog | Operations monitoring | OPERATOR | KEEP_SEPARATE | None |
| ollama-cloud-provider | Provider/backend integration | BACKEND | KEEP_SEPARATE | None |
| RTK | Command-output/navigation tool, not a workflow skill | TOOL | REMOVE_CODEX_ROUTING_KEEP_BINARY | None |
| Serena | Navigation MCP/tool, not a workflow skill | TOOL | PROJECT_OPT_IN_READ_ONLY | Navigation/evidence only |

## Classification rule

For every discovered existing skill:

1. If it owns a lifecycle decision already owned by one of the six core skills, classify it as `LIFECYCLE_DUPLICATE` or `MIXED_AUTHORITY`; merge, alias, split, or disable it.
2. If it provides a reusable method inside a lifecycle phase, classify it as `SPECIALIST`.
3. If it only executes tools/backends, classify it as `BACKEND` or `OPERATOR`.
4. If its behavior is not known well enough to make that decision, classify it as `NEEDS_AUDIT`; do not infer authority from its name.
