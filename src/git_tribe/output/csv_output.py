"""CSV output formatter."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()


def render_csv(report: dict[str, Any], output_path: Path | None = None) -> None:
    """Render report as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["file", "author", "ownership_pct", "bus_factor", "is_silo"])

    ownership = report["ownership"]
    bus_factors = report["bus_factors"]
    silo_files = {s.file_path for s in report["silos"]}

    for file_path in sorted(ownership.keys()):
        entries = ownership[file_path]
        bf = bus_factors.get(file_path, 0)
        is_silo = file_path in silo_files
        for entry in entries:
            writer.writerow([file_path, entry.author, entry.percentage, bf, is_silo])

    content = output.getvalue()

    if output_path:
        output_path.write_text(content)
        console.print(f"[green]✓[/green] CSV report written to {output_path}")
    else:
        console.print(content)
