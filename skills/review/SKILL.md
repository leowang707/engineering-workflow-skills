---
name: review
description: Independently grade an implementation only against blocking standards frozen before implementation.
---

Read the Frozen Review Contract before the implementation.

Establish the frozen blocking Claims, evidence requirements, PASS/FAIL semantics, and applicable Review Invariants.

Then inspect the affected implementation responsibility and its evidence.

Evaluate every frozen blocking Claim and active blocking Invariant.

For each, return a concise disposition with evidence references:
- `PASS`;
- `FAIL`;
- `INSUFFICIENT_EVIDENCE`;
- `BLOCKED`.

Reviewer may independently obtain evidence within the Frozen Evidence Requirements.

Evidence methods may vary only when they prove the same frozen property at equivalent or greater required strength.

Inconsistent evidence cannot support `PASS` unless the Frozen Contract already defines how such variation is evaluated.

Do not add, weaken, reinterpret, or replace blocking standards after seeing the implementation.

If the frozen contract is materially ambiguous, return `CONTRACT_AMBIGUITY`.

New concerns outside frozen standards are non-blocking candidates for future planning.

On `FAIL`, identify the violated frozen property and supporting evidence.
Do not prescribe the repair.

On `INSUFFICIENT_EVIDENCE`, identify the unmet frozen evidence requirement.
Do not prescribe the validation implementation.

After remediation, re-evaluate prior failures and any previously passing criteria that may have been affected.
Preserve proven unaffected results.

Complete only when every frozen blocking criterion has a disposition and no unresolved contract ambiguity remains.

Return per-criterion dispositions and findings.
The overall Ticket result is derived from them; do not override it.
