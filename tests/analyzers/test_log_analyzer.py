"""Tests for log analyzer."""

from __future__ import annotations

from pathlib import Path

from git_tribe.analyzers.log_analyzer import LogAnalyzer
from git_tribe.config import Config


def test_log_analyzer_basic(tmp_git_repo: Path):
    config = Config()
    analyzer = LogAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze()

    # Should detect files
    assert len(results) > 0
    # Alice committed to auth files
    assert "src/auth/oauth.py" in results
    assert "Alice" in results["src/auth/oauth.py"]


def test_log_analyzer_commit_counts(tmp_git_repo: Path):
    config = Config()
    analyzer = LogAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze()

    # Alice has 2 commits to oauth.py (initial + enhance)
    assert results["src/auth/oauth.py"]["Alice"] == 2


def test_log_analyzer_ignores_author(tmp_git_repo: Path):
    config = Config(ignore_authors=["Bob"])
    analyzer = LogAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze()

    # Bob should be filtered
    for authors in results.values():
        assert "Bob" not in authors


def test_log_analyzer_since_filter(tmp_git_repo: Path):
    config = Config()
    analyzer = LogAnalyzer(tmp_git_repo, config, since="1 year ago")
    results = analyzer.analyze()

    # Should still find commits (they're recent)
    assert len(results) > 0


def test_log_analyzer_multiple_contributors(tmp_git_repo: Path):
    config = Config()
    analyzer = LogAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze()

    # routes.py has both Bob and Charlie
    assert "src/api/routes.py" in results
    assert "Bob" in results["src/api/routes.py"]
    assert "Charlie" in results["src/api/routes.py"]
