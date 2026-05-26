"""Markdown output formatter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()


def render_markdown(report: dict[str, Any], output_path: Path | None = None) -> None:
    """Render report as Markdown."""
    lines: list[str] = []
    lines.append("# Git Tribe — Code Ownership Report")
    lines.append("")
    lines.append(f"**Repository**: `{report['repo_path']}`")
    lines.append("")

    # Ownership table
    lines.append("## Ownership")
    lines.append("")
    lines.append("| File | Primary Owner | Share | Bus Factor |")
    lines.append("|------|---------------|-------|------------|")

    ownership = report["ownership"]
    bus_factors = report["bus_factors"]

    for file_path in sorted(ownership.keys()):
        entries = ownership[file_path]
        if not entries:
            continue
        primary = entries[0]
        bf = bus_factors.get(file_path, 0)
        lines.append(f"| {file_path} | {primary.author} | {primary.percentage:.0f}% | {bf} |")

    lines.append("")

    # Silos
    silos = report["silos"]
    if silos:
        lines.append("## Knowledge Silos")
        lines.append("")
        for silo in silos:
            authors_str = ", ".join(f"{a.author} ({a.percentage:.0f}%)" for a in silo.authors)
            lines.append(f"- **{silo.file_path}** → {authors_str}")
        lines.append("")

    # Turnover
    turnover = report["turnover"]
    if turnover:
        lines.append("## Turnover Risk")
        lines.append("")
        lines.append("| File | Author | Ownership | Last Active | Months Inactive |")
        lines.append("|------|--------|-----------|-------------|-----------------|")
        for t in turnover:
            lines.append(
                f"| {t.file_path} | {t.author} | {t.ownership_pct:.0f}% "
                f"| {t.last_commit_date} | {t.months_inactive} |"
            )
        lines.append("")

    content = "\n".join(lines)

    if output_path:
        output_path.write_text(content)
        console.print(f"[green]✓[/green] Markdown report written to {output_path}")
    else:
        console.print(content)
