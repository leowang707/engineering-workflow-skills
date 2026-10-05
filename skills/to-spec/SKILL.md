---
name: to-spec
description: Freeze resolved requirements into an implementation-neutral specification with requirement-level acceptance semantics.
---

Use resolved decisions, authoritative evidence, and explicit `UNKNOWN`s.

Do not reopen decisions.
If a material decision is missing or contradicted, stop and identify it.

Define the objective, non-goals, constraints, observable required behavior, shared/public contracts, failure behavior, and requirement-level acceptance semantics.

Create a minimal, complete set of `REQUIREMENT` Claims.

Every blocking acceptance criterion must be implementation-neutral, judgeable, and falsifiable before implementation is seen.

Do not prescribe implementation mechanisms unless they are already frozen requirements.

Freeze `SPEC_ACCEPTANCE` only when:
- requirement semantics are unambiguous;
- Claim coverage is complete;
- no unresolved material decision remains.

Do not decompose implementation work.
