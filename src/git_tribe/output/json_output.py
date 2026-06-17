"""JSON output formatter."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from rich.console import Console

from git_tribe.config import Config
from git_tribe.metrics.bus_factor import compute_directory_bus_factor
from git_tribe.metrics.ownership import OwnershipEntry

console = Console()


def render_json(report: dict[str, Any], output_path: Path | None = None) -> None:
    """Render report as JSON."""
    serializable = _make_serializable(report)
    json_str = json.dumps(serializable, indent=2)

    if output_path:
        output_path.write_text(json_str)
        console.print(f"[green]✓[/green] JSON report written to {output_path}")
    else:
        console.print(json_str)


def _make_serializable(report: dict[str, Any]) -> dict[str, Any]:
    """Convert report to JSON-serializable dict."""
    result: dict[str, Any] = {"repo_path": report["repo_path"]}

    # Ownership
    result["ownership"] = {}
    for file_path, entries in report["ownership"].items():
        result["ownership"][file_path] = [
            {"author": e.author, "percentage": e.percentage} for e in entries
        ]

    # Bus factors
    result["bus_factors"] = report["bus_factors"]

    # Silos
    result["silos"] = [
        {
            "file_path": s.file_path,
            "num_contributors": s.num_contributors,
            "authors": [{"author": a.author, "percentage": a.percentage} for a in s.authors],
        }
        for s in report["silos"]
    ]

    # Turnover
    result["turnover"] = [
        {
            "file_path": t.file_path,
            "author": t.author,
            "ownership_pct": t.ownership_pct,
            "last_commit_date": t.last_commit_date,
            "months_inactive": t.months_inactive,
        }
        for t in report["turnover"]
    ]

    return result


def render_summary_json(
    report: dict[str, Any],
    config: Config,
    output_path: Path | None = None,
) -> None:
    """Render a concise directory-level JSON summary (mirrors terminal output)."""
    ownership = report["ownership"]
    bus_factors = report["bus_factors"]
    silos = report["silos"]
    turnover = report["turnover"]
    repo_path = report["repo_path"]

    repo_name = PurePosixPath(repo_path).name
    bf_values = list(bus_factors.values())
    overall_bf = sorted(bf_values)[len(bf_values) // 2] if bf_values else 0

    # Directory-level aggregation
    dir_bus = compute_directory_bus_factor(ownership)
    dir_ownership = _aggregate_dir_ownership(ownership)

    directories = []
    for dir_path in sorted(dir_bus.keys()):
        if dir_path.count("/") > 2:
            continue
        owners = dir_ownership.get(dir_path, [])
        primary = owners[0] if owners else OwnershipEntry("unknown", 0)
        bf = dir_bus.get(dir_path, 0)
        directories.append({
            "path": dir_path,
            "primary_owner": primary.author,
            "share_pct": round(primary.percentage),
            "bus_factor": bf,
            "risk": "high" if bf <= config.thresholds.bus_factor_warning else "low",
        })

    silo_list = [
        {
            "file": s.file_path,
            "authors": [{"name": a.author, "pct": round(a.percentage)} for a in s.authors],
        }
        for s in silos[:10]
    ]

    turnover_list = [
        {
            "file": t.file_path,
            "author": t.author,
            "ownership_pct": round(t.ownership_pct),
            "months_inactive": t.months_inactive,
        }
        for t in turnover[:5]
    ]

    recommendations: list[str] = []
    critical_bf = [f for f, bf in bus_factors.items() if bf <= 1]
    if critical_bf:
        recommendations.append(
            f"{len(critical_bf)} file(s) have bus factor 1 — schedule pair review sessions"
        )
    single_author = [s for s in silos if s.num_contributors == 1]
    if single_author:
        recommendations.append(
            f"{len(single_author)} file(s) are single-author"
            " — assign cross-review in next sprint"
        )

    summary = {
        "repo": repo_name,
        "bus_factor": overall_bf,
        "directories": directories,
        "silos": silo_list,
        "turnover_risk": turnover_list,
        "recommendations": recommendations,
    }

    json_str = json.dumps(summary, indent=2)
    if output_path:
        output_path.write_text(json_str)
        console.print(f"[green]✓[/green] Summary JSON written to {output_path}")
    else:
        console.print(json_str)


def _aggregate_dir_ownership(
    ownership: dict[str, list[OwnershipEntry]],
) -> dict[str, list[OwnershipEntry]]:
    """Aggregate file ownership to directory level."""
    from collections import defaultdict

    dir_authors: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for file_path, entries in ownership.items():
        parts = PurePosixPath(file_path).parts
        for i in range(1, len(parts)):
            dir_path = str(PurePosixPath(*parts[:i])) + "/"
            for entry in entries:
                dir_authors[dir_path][entry.author] += entry.percentage

    results: dict[str, list[OwnershipEntry]] = {}
    for dir_path, authors in dir_authors.items():
        total = sum(authors.values()) or 1
        entries = [
            OwnershipEntry(author=a, percentage=round((s / total) * 100, 1))
            for a, s in authors.items()
        ]
        entries.sort(key=lambda e: e.percentage, reverse=True)
        results[dir_path] = entries
    return results
