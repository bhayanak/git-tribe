# Contributing to git-tribe

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/git-tribe/git-tribe.git
cd git-tribe
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
# All tests with coverage
pytest --cov=git_tribe --cov-report=term-missing

# Specific test file
pytest tests/metrics/test_bus_factor.py

# Verbose output
pytest -v
```

## Code Quality

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for issues
ruff check src/ tests/

# Auto-fix
ruff check --fix src/ tests/

# Format
ruff format src/ tests/
```

## Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass and linting is clean
6. Update CHANGELOG.md under `[Unreleased]`
7. Submit a pull request

## Pull Request Guidelines

- Keep PRs focused on a single change
- Include tests for new features or bug fixes
- Update documentation if behavior changes
- Follow existing code style (enforced by Ruff)
- Reference related issues in the PR description

## Architecture

```
src/git_tribe/
├── cli.py              # Typer commands (entry point)
├── config.py           # Configuration loading
├── analyzers/          # Git data extraction
│   ├── blame_analyzer  # Per-line authorship
│   ├── log_analyzer    # Commit frequency
│   └── diff_analyzer   # Lines added/removed
├── metrics/            # Computation engines
│   ├── ownership       # Weighted ownership scores
│   ├── bus_factor      # Bus factor calculation
│   ├── silos           # Knowledge silo detection
│   └── turnover        # Stale ownership detection
└── output/             # Formatters
    ├── terminal        # Rich console output
    ├── codeowners      # CODEOWNERS generation
    ├── json_output     # JSON export
    ├── markdown_output # Markdown export
    └── csv_output      # CSV export
```

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include reproduction steps for bugs
- Mention your Python version and OS
