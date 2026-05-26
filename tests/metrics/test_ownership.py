"""Tests for ownership computation."""

from __future__ import annotations

from git_tribe.metrics.ownership import compute_ownership


def test_compute_ownership_basic():
    log_data = {
        "file.py": {"Alice": 5, "Bob": 3},
    }
    blame_data = {
        "file.py": {"Alice": 80, "Bob": 20},
    }

    result = compute_ownership(log_data, blame_data)
    assert "file.py" in result
    entries = result["file.py"]
    assert len(entries) == 2
    # Alice should be primary owner
    assert entries[0].author == "Alice"
    assert entries[0].percentage > entries[1].percentage


def test_compute_ownership_blame_only():
    log_data: dict[str, dict[str, int]] = {}
    blame_data = {"file.py": {"Alice": 100}}

    result = compute_ownership(log_data, blame_data)
    assert "file.py" in result
    assert result["file.py"][0].author == "Alice"
    assert result["file.py"][0].percentage == 100.0


def test_compute_ownership_log_only():
    log_data = {"file.py": {"Bob": 10}}
    blame_data: dict[str, dict[str, int]] = {}

    result = compute_ownership(log_data, blame_data)
    assert "file.py" in result
    assert result["file.py"][0].author == "Bob"


def test_compute_ownership_percentages_sum_to_100():
    log_data = {"file.py": {"Alice": 5, "Bob": 3, "Charlie": 2}}
    blame_data = {"file.py": {"Alice": 50, "Bob": 30, "Charlie": 20}}

    result = compute_ownership(log_data, blame_data)
    total = sum(e.percentage for e in result["file.py"])
    assert abs(total - 100.0) < 1.0  # Allow rounding


def test_compute_ownership_sorted_descending():
    log_data = {"file.py": {"Alice": 1, "Bob": 5, "Charlie": 3}}
    blame_data = {"file.py": {"Alice": 10, "Bob": 60, "Charlie": 30}}

    result = compute_ownership(log_data, blame_data)
    percentages = [e.percentage for e in result["file.py"]]
    assert percentages == sorted(percentages, reverse=True)
