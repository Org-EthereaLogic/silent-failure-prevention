# Claude Code Instructions — Silent Failure Prevention

## Workspace Intent

This repository is Chapter 2 of the Enterprise Data Trust portfolio. It is a public, evidence-driven repository proving a local release-control pattern that measures distribution stability, evaluates six gates, and blocks publication when business signal collapses.

## Decision Order

1. `CLAUDE.md`
2. `CONSTITUTION.md`
3. `DIRECTIVES.md`
4. `AGENTS.md`
5. `SECURITY.md`
6. `README.md`
7. `docs/technical-approach.md`
8. `config/kpi_thresholds.json`

## Non-Negotiable Rules

- Keep Chapter 2 claim-limited to the checked-in local release-control behavior.
- Keep docs, notebook, and tests aligned with the runner output and gate config.
- Shannon entropy is allowed and expected in this repository.
- Do not add proprietary UMIF formulas, hidden scoring logic, or protected IP terms.
- Do not claim live Databricks execution without separate evidence.

## Common Commands

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
python -m ruff check src tests
PYTHONPATH=src python -m stability.runners
PYTHONPATH=src python -m stability.sample_data
```

## What Exists Today

- `src/stability/` contains entropy scoring, baseline snapshots, drift detection, gate evaluation, provenance building, and the local runner.
- `config/kpi_thresholds.json` contains six gate definitions.
- `data/sample/` contains the checked-in baseline and drifted CSV datasets.
- `notebooks/04_stability_deep_dive.py` provides a Databricks-style walkthrough.
- `tests/` contains 50 tests across entropy, baseline, drift, gates, provenance, and integration behavior.
- `.github/workflows/ci.yml` runs lint, tests, coverage, and security checks.

## What Does Not Exist Yet

- Databricks Free Edition execution evidence is captured in `docs/images/ch2/`. Production Databricks execution is not yet evidenced.
- No production dataset validation or external telemetry proof.
- No justification for claims beyond the checked-in local release-control surface.
