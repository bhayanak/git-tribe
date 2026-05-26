"""Ownership computation with weighted formula."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OwnershipEntry:
    author: str
    percentage: float


def compute_ownership(
    log_data: dict[str, dict[str, int]],
    blame_data: dict[str, dict[str, int]],
) -> dict[str, list[OwnershipEntry]]:
    """
    Compute ownership per file by combining:
    - 60% weight: blame-based (current lines attributed to author)
    - 40% weight: commit-frequency based (number of commits touching file)

    Returns {file_path: [OwnershipEntry(author, percentage)]} sorted by share descending.
    """
    all_files = set(log_data.keys()) | set(blame_data.keys())
    results: dict[str, list[OwnershipEntry]] = {}

    for file_path in all_files:
        authors: set[str] = set()
        blame_counts = blame_data.get(file_path, {})
        log_counts = log_data.get(file_path, {})
        authors.update(blame_counts.keys())
        authors.update(log_counts.keys())

        if not authors:
            continue

        # Normalize blame scores
        blame_total = sum(blame_counts.values()) or 1
        blame_norm = {a: blame_counts.get(a, 0) / blame_total for a in authors}

        # Normalize log scores
        log_total = sum(log_counts.values()) or 1
        log_norm = {a: log_counts.get(a, 0) / log_total for a in authors}

        # Weighted combination
        scores: dict[str, float] = {}
        for author in authors:
            scores[author] = 0.6 * blame_norm.get(author, 0) + 0.4 * log_norm.get(author, 0)

        # Normalize to percentages
        total_score = sum(scores.values()) or 1
        entries = [
            OwnershipEntry(author=a, percentage=round((s / total_score) * 100, 1))
            for a, s in scores.items()
        ]
        entries.sort(key=lambda e: e.percentage, reverse=True)
        results[file_path] = entries

    return results
