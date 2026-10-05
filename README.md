# Engineering Workflow Skills

A compact six-skill workflow kernel for ChatGPT and Codex. The skills separate decision making, specification, parallel work decomposition, pre-implementation acceptance review, bounded implementation, and post-implementation review so that implementation cannot silently rewrite its own requirements or grading standard.

## Workflow

```text
project-grill
    ↓
to-spec
    ↓
to-tickets
    ↓
review-contract
    ↓
safe-implement
    ↓
review
```

| Skill | Authority |
|---|---|
| `project-grill` | Resolve material user decisions; retrieve facts from evidence. |
| `to-spec` | Freeze implementation-neutral requirement semantics. |
| `to-tickets` | Expose separate Tickets only where decomposition creates safe, useful parallel work. |
| `review-contract` | Independently validate decomposition and freeze the acceptance contract before implementation. |
| `safe-implement` | Choose implementation mechanisms only inside the frozen Ticket boundary. |
| `review` | Independently grade against standards frozen before implementation. |

The six lifecycle skills own workflow authority. Existing debugging, research, delegation, navigation, and tool skills remain specialist capabilities beneath the appropriate lifecycle phase; they must not redefine frozen decisions, requirements, Ticket boundaries, review contracts, or PASS criteria.

## Repository layout

```text
engineering-workflow-skills/
├── README.md
├── VERSION
├── CHANGELOG.md
├── plugin.json
├── skill-registry.yaml
├── skills/
│   ├── project-grill/SKILL.md
│   ├── to-spec/SKILL.md
│   ├── to-tickets/SKILL.md
│   ├── review-contract/SKILL.md
│   ├── safe-implement/SKILL.md
│   └── review/SKILL.md
├── adapters/
│   ├── chatgpt-project-instructions.md
│   └── codex-agents-snippet.md
├── references/
│   └── specialist-boundary.md
├── scripts/
│   ├── validate.sh
│   ├── install-codex-user.sh
│   ├── update-codex-user.sh
│   ├── verify-codex-user.sh
│   ├── uninstall-codex-user.sh
│   └── audit_existing_skills.py
├── migration/
│   ├── MIGRATION_PLAN.md
│   └── known-skill-classification.md
└── tests/
    ├── activation_cases.yaml
    └── boundary_cases.yaml
```

## Recommended GitHub setup

Recommended repository name:

```text
engineering-workflow-skills
```

A private repository is a sensible default while the workflow and existing-skill migration are still being validated. This repository should be the authoritative source. Do not edit installed copies under `~/.agents/skills` as the primary development workflow.

After manually creating the empty GitHub repository:

```bash
git clone git@github.com:<YOUR_GITHUB_USER>/engineering-workflow-skills.git
cd engineering-workflow-skills
```

Copy this repository's files into the clone, then:

```bash
git add .
git commit -m "feat: add six-skill engineering workflow kernel"
git branch -M main
git push -u origin main
git tag -a v0.2.1 -m "Engineering workflow skills v0.2.1"
git push origin v0.2.1
```

If you created the GitHub repository with a generated README, `.gitignore`, or license, pull/reconcile that initial commit before pushing instead of force-pushing over it.

## Validate the repository

Before installation:

```bash
./scripts/validate.sh
```

Expected result:

```text
VALIDATION=PASS version=0.2.1 skills=6/6
```

## Install into Codex user scope

Codex supports user-scoped skills under `~/.agents/skills/<skill>/SKILL.md`. The installer copies only the six workflow skills and does not delete unrelated existing skills.

```bash
./scripts/install-codex-user.sh
```

The default user-scope target is `~/.agents/skills`.

For staging or testing without touching the live user-scope directory, override the target explicitly:

```bash
TARGET_SKILLS_HOME=/tmp/engineering-workflow-skills ./scripts/install-codex-user.sh
```

Installation model:

```text
Git repository (authoritative)
        ↓ explicit install
~/.agents/skills/ (installed runtime view)
        ↓
Codex CLI
```

The installer:

1. validates the repository;
2. creates the Codex skills directory if necessary;
3. backs up an existing skill with the same name;
4. installs only the six managed skills;
5. verifies `SKILL.md` hashes;
6. records an install manifest under `~/.local/state/engineering-workflow-skills/`.

It does **not** use a destructive `rsync --delete` against the whole skills directory.

## Verify an installation

```bash
./scripts/verify-codex-user.sh
```

Expected result:

```text
VERIFY=PASS skills=6/6
```

This checks that the installed `SKILL.md` files match the current Git checkout.

## Update

Update the authoritative checkout first, inspect the change, then explicitly deploy it:

```bash
git pull --ff-only
./scripts/validate.sh
./scripts/update-codex-user.sh
./scripts/verify-codex-user.sh
```

This intentionally separates source updates from active Codex installation.

## Uninstall

```bash
./scripts/uninstall-codex-user.sh
```

The uninstaller removes only managed skills whose installed `SKILL.md` still matches the recorded installation hash. A locally modified installed skill is skipped rather than deleted. Backups are retained under `~/.local/state/engineering-workflow-skills/backups/`.

## Existing Codex skills

Do not bulk-disable or delete existing skills when installing this workflow. First inventory them:

```bash
python3 scripts/audit_existing_skills.py \
  --repo /path/to/current/repository \
  --out ./skill-inventory-output
```

Then classify each existing skill as one of:

- lifecycle duplicate/conflict;
- specialist method;
- execution/backend skill;
- meta/skill-authoring skill;
- obsolete.

See:

- `migration/known-skill-classification.md`
- `migration/MIGRATION_PLAN.md`
- `references/specialist-boundary.md`

The core rule is:

> The six workflow skills own lifecycle decisions. Specialist skills may decide how to perform their specialty, but may not reopen resolved decisions, alter `SPEC_ACCEPTANCE`, change Ticket boundaries, change a Frozen Review Contract, create a new blocking criterion, or declare overall PASS.

## Codex `AGENTS.md`

Do not duplicate the six `SKILL.md` files inside `AGENTS.md`. Use `adapters/codex-agents-snippet.md` as a thin routing/policy layer and keep repository-specific facts, commands, hardware constraints, branch policy, and authoritative-document pointers in the repository's own `AGENTS.md`.

## ChatGPT

The `skills/` directory is also packaged as an instruction-only plugin via the root `plugin.json`. For early manual validation in a ChatGPT Project, the six `SKILL.md` files can be added as Project sources and `adapters/chatgpt-project-instructions.md` used as the thin router.

Do not maintain a separate ChatGPT copy of the skill semantics. The files under `skills/` are the source of truth.

## Versioning

Current version:

```text
0.2.1
```

Suggested convention:

- patch: wording, documentation, or non-semantic corrections;
- minor: behavior/authority semantics change while preserving the six-phase model;
- major: breaking workflow or artifact-contract changes.

Keep version metadata at repository/package level rather than bloating each `SKILL.md`.

## Security and repository hygiene

Do not commit credentials, Codex authentication files, SSH keys, `.env` files, machine-specific secrets, or generated skill inventories containing sensitive local paths unless intentionally reviewed.

The repository contains instruction-only workflow skills and maintenance helpers. Installation does not require modifying Codex source code.

## License

No license is included yet. If this repository is public, choose and add a license deliberately before treating the contents as reusable by others.
