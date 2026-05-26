"""JSON output formatter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.console import Console

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
