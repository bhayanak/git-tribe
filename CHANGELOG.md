# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-26

### Added

- **Ownership analysis** combining git blame (60% weight) and commit frequency (40% weight)
- **Bus factor calculation** per file, directory, and repository level
- **Knowledge silo detection** with configurable contributor thresholds
- **CODEOWNERS file generation** supporting GitHub and GitLab formats
- **Turnover risk detection** identifying stale ownership from inactive contributors
- **Team aggregation** via `.git-tribe.toml` configuration file
- **Rich terminal output** with colored tables, risk indicators, and recommendations
- **JSON export** for CI/CD integration and programmatic consumption
- **Markdown export** for documentation and reporting
- **CSV export** for spreadsheet analysis
- **Time-bounded analysis** via `--since` flag
- **Path filtering** to analyze specific directories
- **Configurable ignore patterns** for paths and bot authors
- **Full CI pipeline** with multi-version testing, security scanning, and SBOM generation
- **PyPI packaging** with automated release via GitHub Actions

### Commands

- `git-tribe scan` — Full ownership scan with all metrics
- `git-tribe bus-factor` — Standalone bus factor analysis
- `git-tribe silos` — Knowledge silo detection report
- `git-tribe codeowners` — Auto-generate CODEOWNERS file

[1.0.0]: https://github.com/git-tribe/git-tribe/releases/tag/v1.0.0
