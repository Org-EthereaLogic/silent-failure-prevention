# Contributing

This repository demonstrates a release-control pattern for detecting silent
distribution drift before Gold publication.

## Scope

Contributions should stay within that scope:

- improve entropy scoring or drift classification,
- strengthen gate evaluation and provenance behavior,
- expand deterministic sample data and test coverage,
- improve notebooks or documentation without overstating evidence.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src pytest -q
ruff check src tests
```

## Pull request guidelines

1. Keep claims in docs tied to executable evidence.
2. Add or update tests when changing control behavior.
3. Keep `config/kpi_thresholds.json` and documentation in sync.
4. Use conventional commit messages.
