"""Knowledge silo detection."""

from __future__ import annotations

from dataclasses import dataclass

from git_tribe.metrics.ownership import OwnershipEntry


@dataclass
class SiloEntry:
    file_path: str
    authors: list[OwnershipEntry]
    num_contributors: int


def detect_silos(
    ownership: dict[str, list[OwnershipEntry]],
    max_authors: int = 2,
) -> list[SiloEntry]:
    """
    Detect knowledge silos — files with too few contributors.

    A silo is any file where the number of meaningful contributors
    (those with >5% ownership) is <= max_authors.
    """
    silos: list[SiloEntry] = []

    for file_path, entries in ownership.items():
        meaningful = [e for e in entries if e.percentage > 5.0]
        if len(meaningful) <= max_authors:
            silos.append(
                SiloEntry(
                    file_path=file_path,
                    authors=meaningful,
                    num_contributors=len(meaningful),
                )
            )

    silos.sort(key=lambda s: s.num_contributors)
    return silos
