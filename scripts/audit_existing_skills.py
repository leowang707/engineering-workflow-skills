#!/usr/bin/env python3
"""Read-only inventory scanner for Agent/Codex skills.

Finds SKILL.md files, extracts front matter name/description, records SHA-256,
and writes JSON/TSV/Markdown. It does not modify skill directories or configs.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from pathlib import Path

DEFAULT_ROOTS = [
    Path.home() / ".codex" / "skills",
    Path.home() / ".agents" / "skills",
    Path("/etc/codex/skills"),
]

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)

def parse_frontmatter(text: str):
    m = FM_RE.match(text)
    if not m:
        return None, None
    name = description = None
    for raw in m.group(1).splitlines():
        if ":" not in raw:
            continue
        k, v = raw.split(":", 1)
        k, v = k.strip(), v.strip().strip('"\'')
        if k == "name": name = v
        elif k == "description": description = v
    return name, description

def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def discover(roots):
    rows = []
    seen = set()
    for root in roots:
        root = root.expanduser().resolve()
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.name.lower() != "skill.md":
                continue
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            try:
                text = p.read_text(encoding="utf-8")
                name, description = parse_frontmatter(text)
                rows.append({
                    "name": name or p.parent.name,
                    "description": description or "",
                    "skill_md": rp,
                    "root": str(root),
                    "sha256": sha256(p),
                    "path_contains_disabled": any(part.lower() in {".disabled", "disabled"} for part in p.parts),
                })
            except Exception as e:
                rows.append({"name": p.parent.name, "description": "", "skill_md": rp, "root": str(root), "sha256": "", "error": str(e)})
    return sorted(rows, key=lambda r: (r.get("name", ""), r.get("skill_md", "")))

def write_outputs(rows, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "skills-inventory.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cols = ["name", "description", "skill_md", "root", "sha256", "path_contains_disabled"]
    with (outdir / "skills-inventory.tsv").open("w", encoding="utf-8", newline="") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
    lines = ["# Discovered Skills Inventory", "", f"Total discovered SKILL.md files: **{len(rows)}**", "", "| Name | Path | SHA-256 | Description |", "|---|---|---|---|"]
    for r in rows:
        desc = str(r.get("description", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {r.get('name','')} | `{r.get('skill_md','')}` | `{r.get('sha256','')[:16]}` | {desc} |")
    (outdir / "skills-inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", default=[], help="Additional skill root; may be repeated")
    ap.add_argument("--repo", help="Repo root; scans .codex/skills and .agents/skills under it")
    ap.add_argument("--out", default="./skill-inventory-output")
    args = ap.parse_args()
    roots = list(DEFAULT_ROOTS)
    if args.repo:
        repo = Path(args.repo).expanduser()
        roots += [repo / ".codex" / "skills", repo / ".agents" / "skills"]
    roots += [Path(x) for x in args.root]
    rows = discover(roots)
    write_outputs(rows, Path(args.out))
    print(f"Discovered {len(rows)} SKILL.md files. Wrote inventory to {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
