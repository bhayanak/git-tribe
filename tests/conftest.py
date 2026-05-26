"""Shared pytest fixtures."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def tmp_git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repo with known history for testing."""
    repo = tmp_path / "test-repo"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "alice@test.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Alice"], cwd=repo, capture_output=True)

    # Create initial structure
    (repo / "src").mkdir()
    (repo / "src" / "auth").mkdir(parents=True)
    (repo / "src" / "api").mkdir(parents=True)

    # Alice creates auth module
    (repo / "src" / "auth" / "oauth.py").write_text("# OAuth module\nclass OAuth:\n    pass\n")
    (repo / "src" / "auth" / "jwt_handler.py").write_text(
        "# JWT handler\ndef verify_token(t):\n    return True\n"
    )
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Alice: initial auth"], cwd=repo, capture_output=True)

    # Bob adds API module
    subprocess.run(["git", "config", "user.name", "Bob"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "bob@test.com"], cwd=repo, capture_output=True)
    (repo / "src" / "api" / "routes.py").write_text(
        "# API routes\ndef get_users():\n    pass\n\ndef get_items():\n    pass\n"
    )
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Bob: add API routes"], cwd=repo, capture_output=True)

    # Charlie contributes to API
    subprocess.run(["git", "config", "user.name", "Charlie"], cwd=repo, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "charlie@test.com"], cwd=repo, capture_output=True
    )
    (repo / "src" / "api" / "routes.py").write_text(
        "# API routes\n"
        "def get_users():\n    return []\n\n"
        "def get_items():\n    return []\n\n"
        "def create_item():\n    pass\n"
    )
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Charlie: extend API"], cwd=repo, capture_output=True)

    # Alice adds more to auth
    subprocess.run(["git", "config", "user.name", "Alice"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "alice@test.com"], cwd=repo, capture_output=True)
    (repo / "src" / "auth" / "oauth.py").write_text(
        "# OAuth module\n"
        "class OAuth:\n"
        "    def authenticate(self):\n        return True\n\n"
        "    def refresh(self):\n        return True\n"
    )
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Alice: enhance oauth"], cwd=repo, capture_output=True)

    return repo
