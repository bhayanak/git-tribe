"""Log-based analyzer: commit frequency per file/author."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

from git_tribe.config import Config


class LogAnalyzer:
    """Analyze commit history to count commits per file per author."""

    def __init__(self, repo_path: Path, config: Config, since: str | None = None) -> None:
        self.repo_path = repo_path
        self.config = config
        self.since = since

    def analyze(self) -> dict[str, dict[str, int]]:
        """Return {file: {author: commit_count}} from git log."""
        cmd = ["git", "log", "--name-only", "--format=COMMIT_AUTHOR:%aN", "--no-merges"]
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

        file_commits: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
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
            # line is a file path
            if self.config.is_ignored_path(line) or self.config.is_ignored_author(current_author):
                continue
            # Only track files that currently exist
            if (self.repo_path / line).exists():
                file_commits[line][current_author] += 1

        return {k: dict(v) for k, v in file_commits.items()}
