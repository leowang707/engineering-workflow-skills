"""Local isolated Git operations; semantic conflicts always return to engineering."""
from pathlib import Path
import subprocess

from .common import Blocked, identifier, require
from .policy import permission


class GitLifecycle:
    def __init__(self, repository):
        self.repo = Path(repository).resolve()

    def git(self, *args, check=True):
        result = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True)
        if check:
            require(result.returncode == 0, "BLOCKED", result.stderr.strip())
        return result

    def exact_commit(self, commit):
        require(len(commit) in {40, 64} and all(c in "0123456789abcdef" for c in commit), "IMPLEMENTATION_IDENTITY_INVALID", "exact SHA required")
        require(self.git("rev-parse", f"{commit}^{{commit}}").stdout.strip() == commit, "IMPLEMENTATION_IDENTITY_INVALID", "not a commit")

    def control(self, work_id, target_base, *, operator):
        permission(operator, "persist")
        self.exact_commit(target_base)
        name = f"work/{identifier(work_id)}"
        self.git("branch", name, target_base)
        return {"branch": name, "target_base": target_base}

    def isolate(self, work_id, ticket, control_base, directory, *, operator):
        permission(operator, "route")
        self.exact_commit(control_base)
        control = self.git("rev-parse", f"work/{identifier(work_id)}").stdout.strip()
        require(control == control_base, "BLOCKED", "invalid control base")
        branch = f"ticket/{work_id}/{identifier(ticket)}"
        self.git("worktree", "add", "-b", branch, str(directory), control_base)
        return {"control_base": control_base, "branch": branch, "worktree": str(Path(directory).resolve())}

    def candidate(self, instance, paths, allowed_roots, *, operator):
        permission(operator, "candidate", paths, allowed_roots)
        require(self.repo == Path(instance["worktree"]).resolve(), "BLOCKED", "wrong worktree")
        require(self.git("branch", "--show-current").stdout.strip() == instance["branch"]
                and self.git("rev-parse", "HEAD").stdout.strip() == instance["control_base"], "BLOCKED", "execution instance drift")
        require(bool(paths) and not self.git("diff", "--cached", "--name-only").stdout.strip(), "BLOCKED", "empty candidate or pre-staged content")
        self.git("add", "--", *paths)
        staged = self.git("diff", "--cached", "--name-only").stdout.splitlines()
        permission(operator, "candidate", staged, allowed_roots)
        self.git("commit", "-m", "Bounded implementation candidate")
        commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.exact_commit(commit)
        return commit

    def integrate(self, candidate, target_base, expected_tree, *, operator, reviewed,
                  provenance_path, frozen_checks=(), nonmaterial_drift=False):
        permission(operator, "integrate")
        self.exact_commit(candidate)
        self.exact_commit(target_base)
        require(reviewed == candidate, "BLOCKED", "exact reviewed identity required")
        require(not self.git("status", "--porcelain").stdout.strip(), "BLOCKED", "integration tree is dirty")
        current = self.git("rev-parse", "HEAD").stdout.strip()
        require(current == target_base or nonmaterial_drift is True, "BLOCKED", "target drift requires deterministic impact resolution")
        # merge-tree computes a tree without editing a worktree or rewriting history.
        merged = self.git("merge-tree", "--write-tree", current, candidate, check=False)
        require(merged.returncode == 0, "INTEGRATION_REQUIRED", "conflict requires JOIN engineering")
        tree = merged.stdout.splitlines()[0]
        require(tree == expected_tree, "INTEGRATION_REQUIRED", "unexpected integrated content")
        require(provenance_path.startswith(".engineering/") and ".." not in Path(provenance_path).parts,
                "BLOCKED", "lifecycle provenance path required")
        require(self.git("ls-tree", "-r", "--name-only", tree, "--", provenance_path).stdout.strip(), "BLOCKED", "provenance must travel with implementation")
        for check in frozen_checks:
            require(check(self, tree) is True, "BLOCKED", "pre-frozen integration check failed")
        # This is only reachable for a conflict-free, preverified tree.
        self.git("merge", "--no-ff", "--no-edit", candidate)
        require(self.git("rev-parse", "HEAD^{tree}").stdout.strip() == tree, "BLOCKED", "post-merge identity mismatch")
        return {"target": self.git("rev-parse", "HEAD").stdout.strip(), "candidate": candidate,
                "provenance": provenance_path, "verified": True}


def terminalize(store, *, derived_complete, integration_ref, operator):
    permission(operator, "persist")
    receipt = store.read(integration_ref)
    require(derived_complete is True and receipt["artifact_type"] == "integration-receipt"
            and receipt["payload"]["verified"] is True, "BLOCKED", "successful completion and integration required")
    return store.create("terminal-history", {"integration": integration_ref},
                        {"integration": integration_ref}, author="root", version=1)
