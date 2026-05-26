"""Blame-based analyzer: per-line authorship from git blame."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

from git_tribe.config import Config


class BlameAnalyzer:
    """Analyze per-line authorship using git blame."""

    def __init__(self, repo_path: Path, config: Config) -> None:
        self.repo_path = repo_path
        self.config = config

    def analyze(self, files: list[str]) -> dict[str, dict[str, int]]:
        """Return {file: {author: line_count}} from git blame."""
        results: dict[str, dict[str, int]] = {}
        for file_path in files:
            if self.config.is_ignored_path(file_path):
                continue
            blame_data = self._blame_file(file_path)
            if blame_data:
                results[file_path] = blame_data
        return results

    def _blame_file(self, file_path: str) -> dict[str, int]:
        """Run git blame on a single file and count lines per author."""
        full_path = self.repo_path / file_path
        if not full_path.exists() or full_path.is_dir():
            return {}

        try:
            result = subprocess.run(
                ["git", "blame", "--line-porcelain", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (subprocess.TimeoutExpired, OSError):
            return {}

        if result.returncode != 0:
            return {}

        counts: dict[str, int] = defaultdict(int)
        for line in result.stdout.splitlines():
            if line.startswith("author "):
                author = line[7:].strip()
                if not self.config.is_ignored_author(author):
                    counts[author] += 1

        return dict(counts)
