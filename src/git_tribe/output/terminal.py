"""Rich terminal output for git-tribe reports."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from git_tribe.config import Config
from git_tribe.metrics.bus_factor import compute_directory_bus_factor
from git_tribe.metrics.ownership import OwnershipEntry
from git_tribe.metrics.silos import SiloEntry

console = Console()


def render_report(report: dict[str, Any], config: Config) -> None:
    """Render a full ownership report to the terminal."""
    ownership = report["ownership"]
    bus_factors = report["bus_factors"]
    silos = report["silos"]
    turnover = report["turnover"]
    repo_path = report["repo_path"]

    repo_name = PurePosixPath(repo_path).name

    # Overall bus factor (median of file bus factors)
    bf_values = list(bus_factors.values())
    overall_bf = sorted(bf_values)[len(bf_values) // 2] if bf_values else 0

    # Header
    console.print()
    console.print(
        Panel(
            f"[bold]🔍 git-tribe · Code Ownership Report[/bold]\n"
            f"[dim]{repo_name}[/dim]  ·  Bus Factor: {overall_bf}",
            border_style="bright_blue",
        )
    )
    console.print()

    # Directory ownership table
    dir_ownership = _aggregate_directory_ownership(ownership)
    dir_bus = compute_directory_bus_factor(ownership)

    table = Table(title="📁 Directory Ownership", show_header=True, header_style="bold cyan")
    table.add_column("Path", style="white", min_width=20)
    table.add_column("Primary Owner", style="green")
    table.add_column("Share", justify="right")
    table.add_column("Bus Factor", justify="center")

    for dir_path in sorted(dir_bus.keys()):
        if dir_path.count("/") > 2:
            continue  # Only show top-level dirs
        owners = dir_ownership.get(dir_path, [])
        primary = owners[0] if owners else OwnershipEntry("unknown", 0)
        bf = dir_bus.get(dir_path, 0)
        bf_str = f"{bf} ⚠️" if bf <= config.thresholds.bus_factor_warning else f"{bf} ✅"
        table.add_row(dir_path, primary.author, f"{primary.percentage:.0f}%", bf_str)

    console.print(table)
    console.print()

    # Knowledge silos
    if silos:
        render_silos(silos[:10])
        console.print()

    # Turnover risk
    if turnover:
        _render_turnover(turnover[:5])
        console.print()

    # Recommendations
    _render_recommendations(bus_factors, silos, config)


def render_bus_factor(bus_factors: dict[str, int], config: Config) -> None:
    """Render bus factor analysis."""
    table = Table(title="🚌 Bus Factor Analysis", show_header=True, header_style="bold cyan")
    table.add_column("File", style="white", min_width=30)
    table.add_column("Bus Factor", justify="center")
    table.add_column("Risk", justify="center")

    for file_path, bf in sorted(bus_factors.items(), key=lambda x: x[1]):
        if bf <= config.thresholds.bus_factor_warning:
            risk = Text("HIGH", style="bold red")
        elif bf <= config.thresholds.bus_factor_warning + 1:
            risk = Text("MEDIUM", style="yellow")
        else:
            risk = Text("LOW", style="green")
        table.add_row(file_path, str(bf), risk)

    console.print(table)


def render_silos(silos: list[SiloEntry]) -> None:
    """Render knowledge silo report."""
    console.print("[bold yellow]⚠️  Knowledge Silos[/bold yellow] (single/few-author files):")
    for silo in silos:
        authors_str = ", ".join(f"{e.author} ({e.percentage:.0f}%)" for e in silo.authors)
        console.print(f"  [dim]•[/dim] {silo.file_path} → {authors_str}")


def _render_turnover(turnover: list) -> None:
    """Render turnover risk entries."""
    console.print("[bold red]🔄 Turnover Risk[/bold red] (inactive top contributors):")
    for entry in turnover:
        console.print(
            f"  [dim]•[/dim] {entry.file_path} → {entry.author} "
            f"({entry.ownership_pct:.0f}%, inactive {entry.months_inactive}mo)"
        )


def _render_recommendations(
    bus_factors: dict[str, int], silos: list[SiloEntry], config: Config
) -> None:
    """Render actionable recommendations."""
    recs: list[str] = []

    critical_bf = [f for f, bf in bus_factors.items() if bf <= 1]
    if critical_bf:
        recs.append(f"{len(critical_bf)} file(s) have bus factor 1 — schedule pair review sessions")

    single_author = [s for s in silos if s.num_contributors == 1]
    if single_author:
        recs.append(
            f"{len(single_author)} file(s) are single-author — assign cross-review in next sprint"
        )

    if recs:
        console.print("[bold blue]💡 Recommendations:[/bold blue]")
        for i, rec in enumerate(recs, 1):
            console.print(f"  {i}. {rec}")


def _aggregate_directory_ownership(
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
