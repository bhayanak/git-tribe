"""Bus factor computation."""

from __future__ import annotations

from git_tribe.metrics.ownership import OwnershipEntry


def compute_bus_factor(ownership: dict[str, list[OwnershipEntry]]) -> dict[str, int]:
    """
    Compute bus factor per file.

    Bus factor = minimum number of contributors whose departure would result
    in >50% of the code having no active author.

    Algorithm: Sort authors by contribution %, accumulate until >50%.
    That count = bus factor.
    """
    results: dict[str, int] = {}

    for file_path, entries in ownership.items():
        if not entries:
            results[file_path] = 0
            continue

        cumulative = 0.0
        count = 0
        for entry in entries:
            cumulative += entry.percentage
            count += 1
            if cumulative > 50.0:
                break

        results[file_path] = count

    return results


def compute_directory_bus_factor(
    ownership: dict[str, list[OwnershipEntry]],
) -> dict[str, int]:
    """Compute bus factor at directory level by aggregating file ownership."""
    from collections import defaultdict
    from pathlib import PurePosixPath

    dir_authors: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for file_path, entries in ownership.items():
        parts = PurePosixPath(file_path).parts
        # Aggregate at each directory level
        for i in range(1, len(parts)):
            dir_path = str(PurePosixPath(*parts[:i])) + "/"
            for entry in entries:
                dir_authors[dir_path][entry.author] += entry.percentage

    results: dict[str, int] = {}
    for dir_path, authors in dir_authors.items():
        total = sum(authors.values()) or 1
        sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
        cumulative = 0.0
        count = 0
        for _, share in sorted_authors:
            cumulative += (share / total) * 100
            count += 1
            if cumulative > 50.0:
                break
        results[dir_path] = count

    return results
