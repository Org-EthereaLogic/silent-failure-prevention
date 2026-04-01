# Silent Failure Prevention

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/82de4005e40346929c375feb29e5f97e)](https://app.codacy.com/gh/Org-EthereaLogic/silent-failure-prevention?utm_source=github.com&utm_medium=referral&utm_content=Org-EthereaLogic/silent-failure-prevention&utm_campaign=Badge_Grade)

**Enterprise Data Trust — Chapter 2**

Built by Anthony Johnson | EthereaLogic LLC

---

The most expensive data failures are the ones nobody catches. A source system defaults a business field to a single value. A category mix collapses after an upstream migration. Row counts reconcile. Jobs complete on schedule. Dashboards refresh. And the CFO presents numbers to the board that no longer reflect reality.

This repository implements a **release-control pattern** that detects silent distribution drift and blocks Gold publication before corrupted data reaches executive dashboards.

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

## Decision / KPI contract

**Business decision:** should the current data load be published to executive dashboards?

The release control answers that question with five metrics:

| KPI | Meaning |
|-----|---------|
| `health_score` | Aggregate distribution stability across monitored columns (0.0–1.0) |
| `columns_drifted` | Count of columns whose distribution has shifted beyond threshold |
| `columns_drifted_ratio` | Proportion of monitored columns exhibiting drift |
| `overall_verdict` | PASS / WARN / FAIL based on 6 configurable gates |
| `provenance_field_coverage` | Completeness of the audit envelope (1.0 = all fields populated) |

**Control rule:** Gold publication is blocked when `health_score` falls below `0.70`. The stability gate is the decisive check — all other gates (fidelity, quality pass rate, provenance, quarantine ratio) provide supporting evidence.

## Why this pattern

Traditional pipeline monitoring catches structural failures: missing files, broken schemas, null values, duplicate keys. It does not catch **silent distribution drift** — where data retains its schema and row counts while the underlying business signal degrades.

This pattern addresses three gaps that standard monitoring leaves open:

- **Distribution stability is measured, not assumed.** Each monitored column is scored against a trusted baseline using normalized entropy. A column that collapses from 5 distinct values to 1 scores 0.0 regardless of whether the schema and row count are intact.
- **Publication gates are configurable and auditable.** Six gates with explicit thresholds are evaluated on every run. Each gate emits a PASS, WARN, or FAIL verdict with the measured value recorded alongside the threshold.
- **The audit envelope is built automatically.** Every run produces a provenance record with timestamps, per-column evidence, gate outcomes, and the overall verdict — ready for governance review without manual assembly.

## Databricks Free Edition evidence

The same release-control pattern was validated in a live Databricks Free Edition
workspace by running
[`notebooks/05_free_edition_validation.py`](notebooks/05_free_edition_validation.py).
The notebook installs the package from GitHub, generates identical deterministic
datasets, and reproduces the same drift detection, gate evaluation, and
publication-blocking behavior observed locally.

| Step | Evidence | Screenshot |
| ---- | -------- | ---------- |
| Workspace setup | Notebook loaded in Databricks Free Edition | ![Notebook in workspace](docs/images/ch2/01-notebook-workspace.png) |
| Data generation | Baseline (diverse) vs drifted (collapsed) tables | ![Baseline vs drifted](docs/images/ch2/02-baseline-vs-drifted.png) |
| Drift detection | Per-column stability comparison, 4 of 5 collapsed | ![Drift detection](docs/images/ch2/03-drift-detection.png) |
| Health + gates | Health score 0.20, 6 gate verdicts evaluated | ![Health and gates](docs/images/ch2/04-health-gates.png) |
| Publication decision | Gold refresh BLOCKED | ![Publication blocked](docs/images/ch2/05-publication-blocked.png) |
| Audit record | Provenance envelope with full field coverage | ![Provenance](docs/images/ch2/06-provenance-envelope.png) |

**Scope disclaimer:** This validates the release-control pattern using
deterministic sample data in a Databricks Free Edition workspace. It does not
constitute production deployment, multi-source verification, or live Databricks
production execution.

## How the control works

1. A trusted baseline is captured across the monitored business columns.
2. Each new load is measured against that baseline to determine whether distribution stability has been maintained.
3. Per-column results are aggregated into a table health score.
4. Six configurable release gates evaluate whether Gold publication is allowed, warned, or blocked.
5. A provenance envelope captures the run context, verdict, and drift evidence for auditability.

The measurement technique is Shannon entropy — a well-established information-theoretic measure of distribution diversity. Technical details, formulas, and gate definitions are in [docs/technical-approach.md](docs/technical-approach.md).

## Repository map

- `src/stability/detection/`: entropy scoring, baseline snapshots, drift logic
- `src/stability/gates/`: configurable pass/warn/fail gate evaluation
- `src/stability/provenance/`: audit envelope builder
- `src/stability/runners/`: local demo entry point
- `src/stability/sample_data.py`: deterministic baseline and drifted datasets
- `config/kpi_thresholds.json`: six release-control thresholds
- `data/sample/`: checked-in CSVs for the baseline and drifted loads
- `notebooks/04_stability_deep_dive.py`: Databricks-style walkthrough notebook
- `notebooks/05_free_edition_validation.py`: Free Edition validation with evidence
- `tests/`: 50 tests spanning entropy, baseline, drift, gates, provenance, and
  integration behavior

## Reproducibility

```bash
git clone https://github.com/Org-EthereaLogic/silent-failure-prevention.git
cd silent-failure-prevention

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q          # Expected: 50 passed
PYTHONPATH=src python -m stability.runners  # Expected: Health 0.20, FAIL
```

## Part of a series

This is **Chapter 2** of the *Enterprise Data Trust* portfolio — a three-part body of work addressing the full lifecycle of data reliability in enterprise Databricks platforms.

| Chapter | Focus | Repository |
| ------- | ----- | ---------- |
| 1. Trusted Source Intake | Validate and certify data before downstream consumption | [trusted-source-intake](https://github.com/Org-EthereaLogic/trusted-source-intake) |
| **2. Silent Failure Prevention** | Detect distribution drift before it reaches executive dashboards | ← You are here |
| 3. Measurable Control Effectiveness | Prove that data controls hold against known failure scenarios | [measurable-control-effectiveness](https://github.com/Org-EthereaLogic/measurable-control-effectiveness) |

MIT License. See [LICENSE.md](LICENSE.md) for details.
