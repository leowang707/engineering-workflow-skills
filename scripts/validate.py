#!/usr/bin/env python3
"""Check that every skill works in both Claude Code and Codex and is registered.

Standard library only. Run from anywhere: python3 scripts/validate.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
RESERVED = {"review", "init", "help", "compact", "clear", "config", "code-review"}
errors = []


def err(msg):
    errors.append(msg)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    fields = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields, text[end + 4:]


def openai_yaml(path):
    text = path.read_text(encoding="utf-8")
    get = lambda key: (re.search(rf"^\s*{key}:\s*(.+)$", text, re.M) or [None, None])[1]
    implicit = get("allow_implicit_invocation")
    return {
        "display_name": get("display_name"),
        "short_description": get("short_description"),
        "implicit": None if implicit is None else implicit.strip().lower() == "true",
    }


skills = {}
for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
    name = d.name
    skill_md = d / "SKILL.md"
    if not skill_md.is_file():
        err(f"{name}: missing SKILL.md")
        continue
    fm, body = frontmatter(skill_md)
    if fm is None:
        err(f"{name}: SKILL.md has no YAML frontmatter")
        continue
    if fm.get("name") != name:
        err(f"{name}: frontmatter name '{fm.get('name')}' must match the folder name")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        err(f"{name}: name must be lowercase kebab-case, at most 64 characters")
    if name in RESERVED:
        err(f"{name}: collides with a built-in harness command")
    desc = fm.get("description", "")
    user_invoked = fm.get("disable-model-invocation", "").lower() == "true"
    if not desc:
        err(f"{name}: missing description")
    elif len(desc) > 1024:
        err(f"{name}: description longer than 1024 characters")
    elif "<" in desc or ">" in desc:
        err(f"{name}: description must not contain angle brackets")
    elif not user_invoked and "Use when" not in desc:
        err(f"{name}: model-invoked description needs a 'Use when ...' trigger")
    if not body.strip() or "Replace this comment with the skill body" in body:
        err(f"{name}: SKILL.md body is empty or still the template")

    oy = d / "agents" / "openai.yaml"
    if not oy.is_file():
        err(f"{name}: missing agents/openai.yaml (Codex metadata)")
    else:
        meta = openai_yaml(oy)
        if not meta["display_name"] or not meta["short_description"]:
            err(f"{name}: agents/openai.yaml needs interface.display_name and short_description")
        codex_user_only = meta["implicit"] is False
        if codex_user_only != user_invoked:
            err(f"{name}: invocation differs between Claude (disable-model-invocation) "
                f"and Codex (policy.allow_implicit_invocation)")
    skills[name] = {"user_invoked": user_invoked, "text": skill_md.read_text(encoding="utf-8")}

# Skill-to-skill calls must target an existing, model-invoked skill.
for name, info in skills.items():
    for target in re.findall(r'Call the Skill tool with "([a-z0-9-]+)"', info["text"]):
        if target not in skills:
            err(f"{name}: calls unknown skill '{target}'")
        elif skills[target]["user_invoked"]:
            err(f"{name}: calls user-invoked skill '{target}'; tell the user to run /{target} instead")

# Every skill must be on the workflow map and in the README.
workflow = skills.get("workflow", {}).get("text", "")
readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
for name in skills:
    if f"| `{name}` |" not in workflow:
        err(f"{name}: not listed in the table in skills/workflow/SKILL.md")
    if f"skills/{name}/SKILL.md" not in readme:
        err(f"{name}: not linked from README.md")

# Manifests agree on the version.
version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
for rel in (".claude-plugin/plugin.json", "plugin.json"):
    try:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"{rel}: invalid JSON ({e})")
        continue
    if data.get("version") != version:
        err(f"{rel}: version {data.get('version')} does not match VERSION {version}")
for rel in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
    try:
        json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"{rel}: invalid JSON ({e})")

if errors:
    print("VALIDATION=FAIL")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)
print(f"VALIDATION=PASS version={version} skills={len(skills)}")
