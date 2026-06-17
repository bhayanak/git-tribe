"""Typer CLI application for git-tribe."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from git_tribe import __version__
from git_tribe.config import Config

app = typer.Typer(
    name="git-tribe",
    help="Code ownership & knowledge map CLI — analyze git history to reveal who owns what.",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"git-tribe {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Git Tribe — Code Ownership & Knowledge Map CLI."""
    if ctx.invoked_subcommand is None:
        scan(path=Path.cwd())


@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Path to analyze (file or directory)")] = Path("."),
    depth: Annotated[
        str, typer.Option("--depth", "-d", help="Analysis depth: quick or full")
    ] = "quick",
    since: Annotated[
        str | None,
        typer.Option("--since", help="Analyze commits since date (e.g. '6 months ago')"),
    ] = None,
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: terminal, json, markdown, csv")
    ] = "terminal",
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output file path")] = None,
    summary: Annotated[
        bool, typer.Option("--summary", "-s", help="Output concise directory-level JSON summary")
    ] = False,
    config_path: Annotated[
        Path | None, typer.Option("--config", "-c", help="Config file path")
    ] = None,
) -> None:
    """Scan repository for code ownership and metrics."""
    from git_tribe.analyzers.blame_analyzer import BlameAnalyzer
    from git_tribe.analyzers.log_analyzer import LogAnalyzer
    from git_tribe.metrics.bus_factor import compute_bus_factor
    from git_tribe.metrics.ownership import compute_ownership
    from git_tribe.metrics.silos import detect_silos
    from git_tribe.metrics.turnover import detect_turnover_risk
    from git_tribe.output.terminal import render_report

    config = Config.load(config_path)
    repo_path = path.resolve()

    with console.status("[bold green]Analyzing git history..."):
        log_analyzer = LogAnalyzer(repo_path, config, since=since)
        log_data = log_analyzer.analyze()

        blame_analyzer = BlameAnalyzer(repo_path, config)

        if depth == "full":
            blame_data = blame_analyzer.analyze(list(log_data.keys()))
        else:
            top_files = sorted(
                log_data.keys(), key=lambda f: sum(log_data[f].values()), reverse=True
            )
            blame_data = blame_analyzer.analyze(top_files[:50])

    ownership = compute_ownership(log_data, blame_data)
    bus_factors = compute_bus_factor(ownership)
    silos = detect_silos(ownership, config.thresholds.silo_max_authors)
    turnover = detect_turnover_risk(log_data, repo_path, config.thresholds.stale_months)

    report = {
        "ownership": ownership,
        "bus_factors": bus_factors,
        "silos": silos,
        "turnover": turnover,
        "repo_path": str(repo_path),
    }

    if summary:
        from git_tribe.output.json_output import render_summary_json

        render_summary_json(report, config, output)
    elif output_format == "terminal":
        render_report(report, config)
    elif output_format == "json":
        from git_tribe.output.json_output import render_json

        render_json(report, output)
    elif output_format == "markdown":
        from git_tribe.output.markdown_output import render_markdown

        render_markdown(report, output)
    elif output_format == "csv":
        from git_tribe.output.csv_output import render_csv

        render_csv(report, output)
    else:
        console.print(f"[red]Unknown format: {output_format}[/red]")
        raise typer.Exit(1)


@app.command(name="bus-factor")
def bus_factor(
    path: Annotated[Path, typer.Argument(help="Path to analyze")] = Path("."),
    config_path: Annotated[
        Path | None, typer.Option("--config", "-c", help="Config file path")
    ] = None,
) -> None:
    """Show bus factor analysis for the repository."""
    from git_tribe.analyzers.blame_analyzer import BlameAnalyzer
    from git_tribe.analyzers.log_analyzer import LogAnalyzer
    from git_tribe.metrics.bus_factor import compute_bus_factor
    from git_tribe.metrics.ownership import compute_ownership
    from git_tribe.output.terminal import render_bus_factor

    config = Config.load(config_path)
    repo_path = path.resolve()

    with console.status("[bold green]Computing bus factor..."):
        log_analyzer = LogAnalyzer(repo_path, config)
        log_data = log_analyzer.analyze()
        blame_analyzer = BlameAnalyzer(repo_path, config)
        blame_data = blame_analyzer.analyze(list(log_data.keys())[:50])

    ownership = compute_ownership(log_data, blame_data)
    bus_factors = compute_bus_factor(ownership)
    render_bus_factor(bus_factors, config)


@app.command()
def silos(
    path: Annotated[Path, typer.Argument(help="Path to analyze")] = Path("."),
    threshold: Annotated[
        int, typer.Option("--threshold", "-t", help="Max contributors to flag as silo")
    ] = 2,
    config_path: Annotated[
        Path | None, typer.Option("--config", "-c", help="Config file path")
    ] = None,
) -> None:
    """Detect knowledge silos — files with too few contributors."""
    from git_tribe.analyzers.blame_analyzer import BlameAnalyzer
    from git_tribe.analyzers.log_analyzer import LogAnalyzer
    from git_tribe.metrics.ownership import compute_ownership
    from git_tribe.metrics.silos import detect_silos
    from git_tribe.output.terminal import render_silos

    config = Config.load(config_path)
    repo_path = path.resolve()

    with console.status("[bold green]Detecting knowledge silos..."):
        log_analyzer = LogAnalyzer(repo_path, config)
        log_data = log_analyzer.analyze()
        blame_analyzer = BlameAnalyzer(repo_path, config)
        blame_data = blame_analyzer.analyze(list(log_data.keys()))

    ownership = compute_ownership(log_data, blame_data)
    silo_list = detect_silos(ownership, threshold)
    render_silos(silo_list)


@app.command()
def codeowners(
    path: Annotated[Path, typer.Argument(help="Path to analyze")] = Path("."),
    output: Annotated[Path, typer.Option("--output", "-o", help="Output file path")] = Path(
        "CODEOWNERS"
    ),
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="Format: github or gitlab")
    ] = "github",
    config_path: Annotated[
        Path | None, typer.Option("--config", "-c", help="Config file path")
    ] = None,
) -> None:
    """Auto-generate CODEOWNERS file from git history."""
    from git_tribe.analyzers.blame_analyzer import BlameAnalyzer
    from git_tribe.analyzers.log_analyzer import LogAnalyzer
    from git_tribe.metrics.ownership import compute_ownership
    from git_tribe.output.codeowners import generate_codeowners

    config = Config.load(config_path)
    repo_path = path.resolve()

    with console.status("[bold green]Generating CODEOWNERS..."):
        log_analyzer = LogAnalyzer(repo_path, config)
        log_data = log_analyzer.analyze()
        blame_analyzer = BlameAnalyzer(repo_path, config)
        blame_data = blame_analyzer.analyze(list(log_data.keys()))

    ownership = compute_ownership(log_data, blame_data)
    generate_codeowners(ownership, output, output_format)
    console.print(f"[green]✓[/green] CODEOWNERS written to {output}")
