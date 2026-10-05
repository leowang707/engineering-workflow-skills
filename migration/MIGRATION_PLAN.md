# Migration Plan

1. Install the six core lifecycle skills without removing existing skills.
2. Add the small ChatGPT/Codex router adapter; do not copy full Skill procedures into Project Instructions or `AGENTS.md`.
3. Run the read-only inventory scanner on the actual Codex host.
4. Classify every discovered skill as lifecycle, specialist, backend/operator, meta, obsolete, or needs-audit.
5. Resolve lifecycle conflicts first.
6. Add `allowed_under` mappings only where they materially constrain authority.
7. Run activation and boundary cases.
8. Only after acceptance, alias/disable/retire conflicting or obsolete skills.

Never bulk-delete existing skills from the known-but-incomplete inventory.
