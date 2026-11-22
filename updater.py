#!/usr/bin/env python3

"""GitPython equivalent of:

    git submodule foreach --recursive "(git checkout master || git checkout main)"

followed by: listing the repos that report "...and can be fast-forwarded"
and running `git pull` on those.

Usage:
    python updater.py [main_repo_folder] [--dry-run]
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from git import InvalidGitRepositoryError, Repo

FF_MARKER = "and can be fast-forwarded"


@dataclass
class CheckoutResult:
    repo: Repo
    path: Path          # path relative to the root (for display)
    branch: str | None  # branch it ended up on (None if none worked)
    output: str         # stdout + stderr of the checkout that worked

    @property
    def can_fast_forward(self) -> bool:
        return FF_MARKER in self.output


class SubmoduleUpdater:
    def __init__(self, root: str | Path = ".", branches: tuple[str, ...] = ("master", "main")):
        self.root = Path(root).resolve()
        self.branches = branches
        self.main_repo = Repo(self.root)
        self.results: list[CheckoutResult] = []

    # ---- submodule foreach --recursive -------------------------------------
    def _iter_repos(self, repo: Repo) -> Iterator[Repo]:
        """Walk the submodules recursively (parent first, then children)."""
        for sm in repo.submodules:
            if not sm.module_exists():  # submodule not initialized
                continue
            try:
                sub = sm.module()
            except InvalidGitRepositoryError:
                continue
            yield sub
            yield from self._iter_repos(sub)

    # ---- (git checkout master || git checkout main) -------------------------
    def _checkout(self, repo: Repo) -> tuple[str | None, str]:
        for branch in self.branches:
            status, out, err = repo.git.checkout(
                branch, with_extended_output=True, with_exceptions=False
            )
            text = "\n".join(t for t in (out, err) if t)
            if status == 0:
                return branch, text
            print(text)  # like the shell: show the error and try the next branch
        return None, ""

    def _display_path(self, repo: Repo) -> Path:
        full = Path(repo.working_tree_dir).resolve()
        return full.relative_to(self.root) if self.root in full.parents else full

    def checkout_all(self) -> list[CheckoutResult]:
        self.results = []
        for repo in self._iter_repos(self.main_repo):
            rel = self._display_path(repo)
            print(f"Entering '{rel}'")
            branch, output = self._checkout(repo)
            if output:
                print(output)
            self.results.append(CheckoutResult(repo, rel, branch, output))
        return self.results

    # ---- repos that can be fast-forwarded -----------------------------------
    def fast_forwardable(self) -> list[CheckoutResult]:
        return [r for r in self.results if r.can_fast_forward]

    # ---- git pull -----------------------------------------------------------
    def pull(self, results: list[CheckoutResult]) -> None:
        for r in results:
            print(f"\n>>> git pull in '{r.path}'")
            print(r.repo.git.pull())

    # ---- everything together ------------------------------------------------
    def run(self, dry_run: bool = False) -> None:
        self.checkout_all()
        ff = self.fast_forwardable()

        print("\n=== Repos that can be fast-forwarded ===")
        if not ff:
            print("(none)")
            return
        for r in ff:
            print(f"  {r.path}  [{r.branch}]")

        if not dry_run:
            self.pull(ff)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", help="main repo (default: current folder)")
    ap.add_argument("--dry-run", action="store_true", help="only list, do not pull")
    args = ap.parse_args()
    SubmoduleUpdater(args.root).run(dry_run=args.dry_run)
