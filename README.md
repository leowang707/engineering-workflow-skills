# Engineering Workflow Skills

Leo's personal engineering workflow as agent skills. They work in **Claude Code** and **Codex**, and new skills can be added with one command.

It combines two sources:

- the small, composable skills from [mattpocock/skills](https://github.com/mattpocock/skills) (grilling, spec, tracer-bullet tickets, TDD, bug diagnosis, two-axis review, handoff);
- the strict parts of this repo's earlier v0.4 lifecycle: acceptance criteria frozen **before** coding, a review that can't add criteria after seeing the code, and a fixed verdict order.

Every loop has a stop: acceptance freezing and review each run **at most 2 rounds**. When a review does not pass, `resolve-review` gives each finding one cause and fixes them in one batch; whatever still fails after round 2 comes to you with four options (reopen the criterion, split a ticket, accept with a follow-up, drop).

## Install

Pick one method per tool. Installing both gives you every skill twice.

### Claude Code

```sh
claude plugin marketplace add leowang707/engineering-workflow-skills
claude plugin install engineering-workflow-skills@leowang707
```

Skills appear as `/engineering-workflow-skills:<skill>`.

### Codex

```sh
codex plugin marketplace add leowang707/engineering-workflow-skills
codex plugin add engineering-workflow-skills@leowang707
```

### Either tool, from a local checkout

```sh
git clone https://github.com/leowang707/engineering-workflow-skills
cd engineering-workflow-skills
scripts/link-skills.sh
```

This symlinks every skill into `~/.claude/skills` (Claude Code) and `~/.agents/skills` (Codex). `git pull` updates them; re-run the script after adding a skill.

If you install the skills in Claude another way (for example by uploading them to your Claude account), run `scripts/link-skills.sh --codex-only` so only `~/.agents/skills` is linked and Claude doesn't see every skill twice.

## The flow

```
grilling ──▶ /to-spec ──▶ /to-tickets ──▶ /implement (per ticket) or /implement-spec (parallel)
                              │                 │
                              ▼                 ├─▶ tdd
                       freeze-acceptance        └─▶ frozen-review ──not passed──▶ resolve-review
                        (≤ 2 rounds)              (≤ 2 rounds)                    (fix by cause, or you decide)
                                                        │
                                                        ▼
                                                   pr ──▶ /retro
```

Each step ends with a `Next:` line telling you what to run after it, and `/next` works it out from `.workflow/` when you come back later. Run `/workflow` for the full map. Work artifacts go in `.workflow/<feature>/` in your project (decisions, spec, tickets, acceptance rounds, reviews), so a Claude session can pick up what a Codex session started and the other way around.

## Skills

**User-invoked** (you type them):

- [`workflow`](skills/workflow/SKILL.md): map of the skills and which one fits now.
- [`next`](skills/next/SKILL.md): read `.workflow/` and say where the work stands and which command to run next.
- [`to-spec`](skills/to-spec/SKILL.md): turn settled decisions into a spec with numbered, falsifiable requirements.
- [`to-tickets`](skills/to-tickets/SKILL.md): split a spec into tracer-bullet tickets and freeze their acceptance criteria.
- [`implement`](skills/implement/SKILL.md): build one frozen ticket test-first, inside its boundary, then review it.
- [`implement-spec`](skills/implement-spec/SKILL.md): build every ticket of a spec in parallel with sub-agents on one integration branch.
- [`retro`](skills/retro/SKILL.md): after a build, suggest changes to checks, standards and these skills.
- [`handoff`](skills/handoff/SKILL.md): write a handoff file for the next session or tool.
- [`new-skill`](skills/new-skill/SKILL.md): add a new skill to this repo.

**Model-invoked** (the agent can also reach for them):

- [`grilling`](skills/grilling/SKILL.md): settle decisions round by round; facts are looked up, decisions are asked.
- [`freeze-acceptance`](skills/freeze-acceptance/SKILL.md): independently check tickets and lock their acceptance criteria.
- [`tdd`](skills/tdd/SKILL.md): red-green loop at agreed seams.
- [`frozen-review`](skills/frozen-review/SKILL.md): review on two axes (frozen criteria and coding standards) with a fixed verdict.
- [`resolve-review`](skills/resolve-review/SKILL.md): when a review does not pass, classify each finding by cause, fix in one batch, and hand the rest to you.
- [`pr`](skills/pr/SKILL.md): PR body with the smallest useful visual, before/after evidence and merge danger.
- [`prototype`](skills/prototype/SKILL.md): throwaway code that answers a design question.
- [`research`](skills/research/SKILL.md): background research against primary sources, written to a cited notes file.
- [`writing-for-agents`](skills/writing-for-agents/SKILL.md): how to write skills, `AGENTS.md` and `CLAUDE.md`.
- [`diagnosing-bugs`](skills/diagnosing-bugs/SKILL.md): build a feedback loop that goes red on the bug before theorizing.

## Adding a skill

Run `/new-skill` in Claude Code or Codex from this repo, or by hand:

```sh
scripts/new-skill.sh <name> <model|user> "<Display Name>" "<short description>"
# write skills/<name>/SKILL.md, add it to skills/workflow/SKILL.md and this README
python3 scripts/validate.py
```

`scripts/new-skill.sh` creates both the `SKILL.md` (Claude Code and Codex) and `agents/openai.yaml` (Codex picker metadata and invocation policy). `scripts/validate.py` checks, with no dependencies:

- the frontmatter is valid and the name matches the folder;
- a model-invoked description has a "Use when" trigger;
- Claude and Codex agree on whether the skill is user-invoked;
- skill-to-skill calls point at a real, model-invoked skill;
- every skill is on the workflow map and in this README;
- the manifest versions match `VERSION`.

CI runs it on every push and pull request.

## Earlier version

The v0.4 lifecycle (six kernels, Python framework, Device A records) is kept unchanged under [`legacy/v0.4/`](legacy/v0.4/README.md) for reference. It is not installed by the plugin.

## Credits

Several skills are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) under the MIT License. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
