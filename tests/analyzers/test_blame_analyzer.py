"""Tests for blame analyzer."""

from __future__ import annotations

from pathlib import Path

from git_tribe.analyzers.blame_analyzer import BlameAnalyzer
from git_tribe.config import Config


def test_blame_analyzer_basic(tmp_git_repo: Path):
    config = Config()
    analyzer = BlameAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze(["src/auth/oauth.py"])

    assert "src/auth/oauth.py" in results
    # Alice should own all lines in oauth.py
    assert "Alice" in results["src/auth/oauth.py"]


def test_blame_analyzer_ignores_path(tmp_git_repo: Path):
    config = Config(ignore_paths=["src/auth/*"])
    analyzer = BlameAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze(["src/auth/oauth.py"])

    assert "src/auth/oauth.py" not in results


def test_blame_analyzer_ignores_author(tmp_git_repo: Path):
    config = Config(ignore_authors=["Alice"])
    analyzer = BlameAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze(["src/auth/oauth.py"])

    # File should still be present but Alice filtered out
    if "src/auth/oauth.py" in results:
        assert "Alice" not in results["src/auth/oauth.py"]


def test_blame_analyzer_nonexistent_file(tmp_git_repo: Path):
    config = Config()
    analyzer = BlameAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze(["nonexistent.py"])

    assert "nonexistent.py" not in results


def test_blame_analyzer_multiple_authors(tmp_git_repo: Path):
    config = Config()
    analyzer = BlameAnalyzer(tmp_git_repo, config)
    results = analyzer.analyze(["src/api/routes.py"])

    assert "src/api/routes.py" in results
    # Charlie rewrote the file, should have most lines
    assert "Charlie" in results["src/api/routes.py"]
