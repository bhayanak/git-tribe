# 🔍 git-tribe

**Code Ownership & Knowledge Map CLI** — Analyze git history to reveal who owns what code, calculate bus factor, identify knowledge silos, and auto-generate CODEOWNERS files.

[![CI](https://github.com/git-tribe/git-tribe/actions/workflows/ci.yml/badge.svg)](https://github.com/git-tribe/git-tribe/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/git-tribe)](https://pypi.org/project/git-tribe/)
[![Python](https://img.shields.io/pypi/pyversions/git-tribe)](https://pypi.org/project/git-tribe/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Why?

- `git blame` shows the **last editor**, not the **true owner**
- No CLI tool calculates **bus factor** — critical for team risk assessment
- CODEOWNERS files are hand-maintained and go stale quickly
- Engineering managers need **knowledge distribution visibility** at a glance
- Useful for onboarding: *"who should I ask about module X?"*

## Features

| Feature | Description |
|---------|-------------|
| **Ownership Map** | Who owns each file/directory by commit volume & line authorship |
| **Bus Factor** | Risk score: how many people must leave before knowledge is lost |
| **Knowledge Silos** | Files/modules where only 1-2 people have contributed |
| **CODEOWNERS Gen** | Auto-generate GitHub/GitLab CODEOWNERS from git history |
| **Turnover Risk** | Highlight files where top contributor is inactive |
| **Team View** | Aggregate ownership by team (configurable mapping) |

## Installation

```bash
pip install git-tribe
```

## Quick Start

```bash
# Run in any git repository
cd your-repo

# Full ownership report
git-tribe scan

# Deep analysis (blame every file)
git-tribe scan --depth full

# Analyze specific directory
git-tribe scan src/auth/

# Bus factor analysis
git-tribe bus-factor

# Detect knowledge silos
git-tribe silos --threshold 2

# Generate CODEOWNERS
git-tribe codeowners --output CODEOWNERS --format github

# JSON output for CI integration
git-tribe scan --format json --output report.json

# Time-bounded analysis
git-tribe scan --since "6 months ago"
```

## Output Example

```
╭─────────────────────────────────────────────────╮
│    🔍 git-tribe · Code Ownership Report          │
│    my-project  ·  Bus Factor: 3                  │
╰─────────────────────────────────────────────────╯

📁 Directory Ownership
┌─────────────────┬──────────────┬────────┬────────────┐
│ Path            │ Primary Owner│ Share  │ Bus Factor │
├─────────────────┼──────────────┼────────┼────────────┤
│ src/auth/       │ alice        │ 72%    │ 1 ⚠️       │
│ src/api/        │ bob          │ 45%    │ 3 ✅       │
│ src/core/       │ charlie      │ 38%    │ 4 ✅       │
│ src/utils/      │ alice        │ 55%    │ 2 ⚠️       │
└─────────────────┴──────────────┴────────┴────────────┘

⚠️  Knowledge Silos (single-author files):
  • src/auth/oauth.py          → alice (100%)
  • src/auth/jwt_handler.py    → alice (97%)

💡 Recommendations:
  1. src/auth/ has bus factor 1 — schedule pair review sessions
  2. 3 files are single-author — assign cross-review in next sprint
```

## Configuration

Create a `.git-tribe.toml` in your repository root:

```toml
[teams]
backend = ["alice", "bob", "charlie"]
frontend = ["diana", "eve"]
devops = ["frank"]

[ignore]
paths = ["vendor/", "node_modules/", "*.generated.*"]
authors = ["dependabot[bot]", "renovate[bot]"]

[thresholds]
bus_factor_warning = 2    # Warn if bus factor ≤ this
silo_max_authors = 2      # Flag files with ≤ this many authors
stale_months = 6          # Author considered inactive after this
```

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Terminal | `--format terminal` (default) | Interactive review |
| JSON | `--format json` | CI/CD pipelines, programmatic use |
| Markdown | `--format markdown` | Documentation, PRs |
| CSV | `--format csv` | Spreadsheet analysis |
| CODEOWNERS | `git-tribe codeowners` | GitHub/GitLab integration |

## How It Works

### Ownership Score

Combines multiple signals with weighted formula:
- **60%** — Blame-based (current lines attributed to author)
- **40%** — Commit frequency (number of commits touching file)

### Bus Factor

Minimum number of contributors whose departure would result in >50% of the code having no active author. Sort authors by contribution %, accumulate until >50% — that count is the bus factor.

## Development

```bash
# Clone and install
git clone https://github.com/git-tribe/git-tribe.git
cd git-tribe
pip install -e ".[dev]"

# Run tests
pytest --cov=git_tribe

# Lint
ruff check src/ tests/
ruff format src/ tests/
```

## Releasing

1. Update version in `src/git_tribe/__init__.py` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit and tag: `git tag v1.0.0`
4. Push: `git push origin main --tags`
5. GitHub Actions handles PyPI publish and GitHub Release

## License

[MIT](LICENSE)
