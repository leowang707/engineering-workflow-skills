"""Read-only inspection CLI and explicit destination distribution builder."""
import argparse
import json
from pathlib import Path
import shutil
import sys

from .common import Blocked, require, sha
from .delivery import distribution
from .progression import derive_current
from .state import GitStateStore, ProjectStateStore


def build(source, destination, profile, surface):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    require(not destination.exists(), "BLOCKED", "distribution destination must be new")
    manifest = distribution(source, profile, surface)
    destination.mkdir(parents=True)
    # Explicit allowlist; no runtime data, .engineering or .serena discovery.
    for directory in ("framework", "schemas", "policies", "references", "adapters", "migration"):
        for path in sorted((source / directory).rglob("*")):
            if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts:
                out = destination / path.relative_to(source)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, out)
    for phase in manifest["skills"]:
        out = destination / "skills" / phase / "SKILL.md"
        out.parent.mkdir(parents=True)
        shutil.copyfile(source / manifest["skills"][phase]["source"], out)
    for name in ("VERSION", "plugin.json", "skill-registry.yaml"):
        shutil.copyfile(source / name, destination / name)
    manifest["payload_sha256"] = {str(p.relative_to(destination)): sha(p.read_bytes()) for p in sorted(destination.rglob("*")) if p.is_file()}
    (destination / "distribution.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    package = commands.add_parser("build-distribution")
    package.add_argument("--source", required=True)
    package.add_argument("--destination", required=True)
    package.add_argument("--profile", choices=("hybrid_engineering", "chat_engineering_full", "none"), required=True)
    package.add_argument("--surface", choices=("Chat", "Codex"), required=True)
    check = commands.add_parser("validate-state")
    check.add_argument("--backend", choices=("git", "chat-project"), required=True)
    check.add_argument("--root", required=True)
    check.add_argument("--project")
    check.add_argument("--work", required=True)
    args = parser.parse_args()
    try:
        if args.command == "build-distribution":
            result = build(args.source, args.destination, args.profile, args.surface)
        else:
            if args.backend == "git":
                store = GitStateStore(args.root, args.work)
            else:
                require(args.project, "DURABLE_STATE_STORE_UNAVAILABLE", "project ID required")
                store = ProjectStateStore(args.root, args.project, args.work)
            result = derive_current(store)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except Blocked as error:
        print(json.dumps({"status": "BLOCKED", "code": error.code, "detail": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
