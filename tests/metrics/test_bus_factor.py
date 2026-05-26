"""Tests for bus factor computation."""

from __future__ import annotations

from git_tribe.metrics.bus_factor import compute_bus_factor, compute_directory_bus_factor
from git_tribe.metrics.ownership import OwnershipEntry


def test_bus_factor_single_author():
    ownership = {
        "file.py": [OwnershipEntry("Alice", 100.0)],
    }
    result = compute_bus_factor(ownership)
    assert result["file.py"] == 1


def test_bus_factor_two_equal_authors():
    ownership = {
        "file.py": [OwnershipEntry("Alice", 50.0), OwnershipEntry("Bob", 50.0)],
    }
    result = compute_bus_factor(ownership)
    # First author gets us to 50%, need to exceed 50%, so 2
    assert result["file.py"] == 2


def test_bus_factor_dominant_author():
    ownership = {
        "file.py": [
            OwnershipEntry("Alice", 70.0),
            OwnershipEntry("Bob", 20.0),
            OwnershipEntry("Charlie", 10.0),
        ],
    }
    result = compute_bus_factor(ownership)
    assert result["file.py"] == 1


def test_bus_factor_well_distributed():
    ownership = {
        "file.py": [
            OwnershipEntry("Alice", 30.0),
            OwnershipEntry("Bob", 25.0),
            OwnershipEntry("Charlie", 25.0),
            OwnershipEntry("Diana", 20.0),
        ],
    }
    result = compute_bus_factor(ownership)
    # 30 + 25 = 55 > 50, so bus factor is 2
    assert result["file.py"] == 2


def test_bus_factor_empty():
    ownership = {"file.py": []}
    result = compute_bus_factor(ownership)
    assert result["file.py"] == 0


def test_directory_bus_factor():
    ownership = {
        "src/auth/oauth.py": [OwnershipEntry("Alice", 100.0)],
        "src/auth/jwt.py": [OwnershipEntry("Alice", 90.0), OwnershipEntry("Bob", 10.0)],
        "src/api/routes.py": [OwnershipEntry("Bob", 50.0), OwnershipEntry("Charlie", 50.0)],
    }
    result = compute_directory_bus_factor(ownership)
    # src/auth/ is dominated by Alice -> bus factor 1
    assert result.get("src/auth/", 0) == 1
