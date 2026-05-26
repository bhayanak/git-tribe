"""Tests for knowledge silo detection."""

from __future__ import annotations

from git_tribe.metrics.ownership import OwnershipEntry
from git_tribe.metrics.silos import detect_silos


def test_detect_single_author_silo():
    ownership = {
        "file.py": [OwnershipEntry("Alice", 100.0)],
    }
    silos = detect_silos(ownership, max_authors=2)
    assert len(silos) == 1
    assert silos[0].file_path == "file.py"
    assert silos[0].num_contributors == 1


def test_detect_two_author_silo():
    ownership = {
        "file.py": [OwnershipEntry("Alice", 60.0), OwnershipEntry("Bob", 40.0)],
    }
    silos = detect_silos(ownership, max_authors=2)
    assert len(silos) == 1


def test_no_silo_when_well_distributed():
    ownership = {
        "file.py": [
            OwnershipEntry("Alice", 35.0),
            OwnershipEntry("Bob", 35.0),
            OwnershipEntry("Charlie", 30.0),
        ],
    }
    silos = detect_silos(ownership, max_authors=2)
    assert len(silos) == 0


def test_silo_ignores_minor_contributors():
    ownership = {
        "file.py": [
            OwnershipEntry("Alice", 90.0),
            OwnershipEntry("Bob", 3.0),  # Below 5% threshold
            OwnershipEntry("Charlie", 4.0),  # Below 5% threshold
            OwnershipEntry("Diana", 3.0),  # Below 5% threshold
        ],
    }
    silos = detect_silos(ownership, max_authors=2)
    assert len(silos) == 1
    assert silos[0].num_contributors == 1


def test_silo_threshold_configurable():
    ownership = {
        "file.py": [OwnershipEntry("Alice", 50.0), OwnershipEntry("Bob", 50.0)],
    }
    # With threshold 1, two authors is not a silo
    silos = detect_silos(ownership, max_authors=1)
    assert len(silos) == 0


def test_silos_sorted_by_contributor_count():
    ownership = {
        "a.py": [OwnershipEntry("Alice", 60.0), OwnershipEntry("Bob", 40.0)],
        "b.py": [OwnershipEntry("Alice", 100.0)],
    }
    silos = detect_silos(ownership, max_authors=2)
    # Single author first
    assert silos[0].file_path == "b.py"
    assert silos[1].file_path == "a.py"
