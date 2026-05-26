"""Configuration loading and team mapping."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class Thresholds:
    bus_factor_warning: int = 2
    silo_max_authors: int = 2
    stale_months: int = 6


@dataclass
class Config:
    teams: dict[str, list[str]] = field(default_factory=dict)
    ignore_paths: list[str] = field(default_factory=list)
    ignore_authors: list[str] = field(default_factory=list)
    thresholds: Thresholds = field(default_factory=Thresholds)

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        """Load config from .git-tribe.toml or return defaults."""
        if path is None:
            path = Path.cwd() / ".git-tribe.toml"
        if not path.exists():
            return cls()
        return cls.from_toml(path)

    @classmethod
    def from_toml(cls, path: Path) -> Config:
        with open(path, "rb") as f:
            data: dict[str, Any] = tomllib.load(f)

        teams = data.get("teams", {})
        ignore = data.get("ignore", {})
        thresholds_data = data.get("thresholds", {})

        return cls(
            teams=teams,
            ignore_paths=ignore.get("paths", []),
            ignore_authors=ignore.get("authors", []),
            thresholds=Thresholds(
                bus_factor_warning=thresholds_data.get("bus_factor_warning", 2),
                silo_max_authors=thresholds_data.get("silo_max_authors", 2),
                stale_months=thresholds_data.get("stale_months", 6),
            ),
        )

    def is_ignored_path(self, path: str) -> bool:
        """Check if a path should be ignored."""
        from fnmatch import fnmatch

        return any(fnmatch(path, pattern) for pattern in self.ignore_paths)

    def is_ignored_author(self, author: str) -> bool:
        """Check if an author should be ignored."""
        return author in self.ignore_authors

    def get_team_for_author(self, author: str) -> str | None:
        """Return team name for an author, or None."""
        for team, members in self.teams.items():
            if author in members:
                return team
        return None
