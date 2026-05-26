"""Turnover risk detection — files where top contributors are inactive."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class TurnoverEntry:
    file_path: str
    author: str
    ownership_pct: float
    last_commit_date: str
    months_inactive: int


def detect_turnover_risk(
    log_data: dict[str, dict[str, int]],
    repo_path: Path,
    stale_months: int = 6,
) -> list[TurnoverEntry]:
    """
    Identify files where top contributors haven't committed recently.

    A contributor is "at risk" if they haven't committed to the repo
    in the past `stale_months` months.
    """
    # Get last commit date per author
    author_last_active = _get_author_last_active(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=stale_months * 30)

    risks: list[TurnoverEntry] = []

    for file_path, authors in log_data.items():
        total = sum(authors.values()) or 1
        for author, commits in authors.items():
            pct = (commits / total) * 100
            if pct < 20:
                continue  # Only care about significant contributors

            last_active = author_last_active.get(author)
            if last_active and last_active < cutoff:
                months = (datetime.now(tz=timezone.utc) - last_active).days // 30
                risks.append(
                    TurnoverEntry(
                        file_path=file_path,
                        author=author,
                        ownership_pct=round(pct, 1),
                        last_commit_date=last_active.strftime("%Y-%m-%d"),
                        months_inactive=months,
                    )
                )

    risks.sort(key=lambda r: r.months_inactive, reverse=True)
    return risks


def _get_author_last_active(repo_path: Path) -> dict[str, datetime]:
    """Get the last commit date for each author in the repo."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%aN|%aI", "--no-merges"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {}

    if result.returncode != 0:
        return {}

    last_active: dict[str, datetime] = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if "|" not in line:
            continue
        author, date_str = line.rsplit("|", 1)
        try:
            dt = datetime.fromisoformat(date_str)
        except ValueError:
            continue
        if author not in last_active or dt > last_active[author]:
            last_active[author] = dt

    return last_active
