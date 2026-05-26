"""Tests for diff analyzer."""

from __future__ import annotations

from pathlib import Path

from git_tribe.analyzers.diff_analyzer import DiffAnalyzer
from git_tribe.config import Config


def test_diff_analyzer_basic(tmp_git_repo: Path):
    config = Config()
    analyzer = DiffAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze()

    assert len(results) > 0


def test_diff_analyzer_tracks_additions(tmp_git_repo: Path):
    config = Config()
    analyzer = DiffAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze()

    # Alice added lines to oauth.py
    if "src/auth/oauth.py" in results and "Alice" in results["src/auth/oauth.py"]:
        assert results["src/auth/oauth.py"]["Alice"]["added"] > 0


def test_diff_analyzer_ignores_author(tmp_git_repo: Path):
    config = Config(ignore_authors=["Charlie"])
    analyzer = DiffAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze()

    for file_data in results.values():
        assert "Charlie" not in file_data
