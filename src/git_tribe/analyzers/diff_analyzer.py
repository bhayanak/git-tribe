"""Diff-based analyzer: lines added/removed per author."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

from git_tribe.config import Config


class DiffAnalyzer:
    """Analyze lines added/removed per author using git log --numstat."""

    def __init__(self, repo_path: Path, config: Config, since: str | None = None) -> None:
        self.repo_path = repo_path
        self.config = config
        self.since = since

    def analyze(self) -> dict[str, dict[str, dict[str, int]]]:
        """Return {file: {author: {added: N, removed: N}}}."""
        cmd = ["git", "log", "--numstat", "--format=COMMIT_AUTHOR:%aN", "--no-merges"]
        if self.since:
            cmd.append(f"--since={self.since}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (subprocess.TimeoutExpired, OSError):
            return {}

        if result.returncode != 0:
            return {}

        stats: dict[str, dict[str, dict[str, int]]] = defaultdict(
            lambda: defaultdict(lambda: {"added": 0, "removed": 0})
        )
        current_author: str | None = None

        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("COMMIT_AUTHOR:"):
                current_author = line[14:]
                continue
            if current_author is None:
                continue

            parts = line.split("\t")
            if len(parts) != 3:
                continue

            added_str, removed_str, file_path = parts
            if added_str == "-" or removed_str == "-":
                continue  # Binary file
            if self.config.is_ignored_path(file_path) or self.config.is_ignored_author(
                current_author
            ):
                continue

            stats[file_path][current_author]["added"] += int(added_str)
            stats[file_path][current_author]["removed"] += int(removed_str)

        return {k: {a: dict(v) for a, v in authors.items()} for k, authors in stats.items()}
