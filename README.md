# Silent Failure Prevention

**Enterprise Data Trust — Chapter 2**

This repository implements a release-control pattern for the Silver-to-Gold
boundary: compare a current load against a trusted baseline, measure
distribution stability across monitored business columns, evaluate explicit
publication gates, and emit an audit envelope before any Gold refresh is
allowed.

## Verified demo outcome

The current checked-in implementation produces the following output when run
locally with `PYTHONPATH=src python -m stability.runners`:

| Metric | Observed value |
| ------ | -------------- |
| Columns checked | `5` |
| Columns drifted | `4` |
| Health score | `0.2000` |
| Schema match | `True` |
| Baseline rows | `25` |
| Current rows | `25` |
| Overall verdict | `FAIL` |
| Publication decision | Gold refresh blocked |

This is the intended control behavior: the data shape still looks healthy, but
the business signal has collapsed in four monitored columns.

## How the control works

1. `BaselineSnapshot.from_dataframe(...)` captures a trusted baseline across the
   monitored business columns.
2. `detect_drift(...)` recomputes normalized entropy scores for the current
   load, compares them to baseline scores, and classifies each column as
   `stable`, `collapsed`, or `spiked`.
3. `evaluate_gates(...)` loads six threshold rules from
   `config/kpi_thresholds.json` and produces per-gate verdicts plus an overall
   verdict.
4. `build_provenance(...)` assembles the run timestamp, drift evidence, row
   counts, and gate outcomes into an audit-friendly envelope.

Technical details, formulas, and file-level architecture are in
[docs/technical-approach.md](docs/technical-approach.md).

## Repository map

- `src/stability/detection/`: entropy scoring, baseline snapshots, drift logic
- `src/stability/gates/`: configurable pass/warn/fail gate evaluation
- `src/stability/provenance/`: audit envelope builder
- `src/stability/runners/`: local demo entry point
- `src/stability/sample_data.py`: deterministic baseline and drifted datasets
- `config/kpi_thresholds.json`: six release-control thresholds
- `data/sample/`: checked-in CSVs for the baseline and drifted loads
- `notebooks/04_stability_deep_dive.py`: Databricks-style walkthrough notebook
- `tests/`: 50 tests spanning entropy, baseline, drift, gates, provenance, and
  integration behavior

## Reproducibility

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m stability.runners
```

To regenerate the checked-in sample CSVs:

```bash
PYTHONPATH=src python -m stability.sample_data
```

## Notebook walkthrough

The notebook at [notebooks/04_stability_deep_dive.py](notebooks/04_stability_deep_dive.py)
mirrors the local runner in a Databricks-friendly format: load baseline and
drifted data, inspect per-column results, review gate outcomes, and inspect the
provenance envelope.

## Part of a series

This is **Chapter 2** of the *Enterprise Data Trust* portfolio.

| Chapter | Focus | Repository |
| ------- | ----- | ---------- |
| 1. Trusted Source Intake | Validate and certify data before downstream consumption | [trusted-source-intake](https://github.com/Org-EthereaLogic/trusted-source-intake) |
| **2. Silent Failure Prevention** | Detect distribution drift before it reaches executive dashboards | Current repository |
| 3. Measurable Control Effectiveness | Prove that data controls hold against known challenge cases | [measurable-control-effectiveness](https://github.com/Org-EthereaLogic/measurable-control-effectiveness) |

MIT License. See [LICENSE.md](LICENSE.md) for details.
