# Technical Approach

This document explains the code paths and measurement logic behind the
`silent-failure-prevention` release-control pattern.

## Objective

The control is designed for a specific failure class: a load arrives on time,
its schema still parses, and its row counts still reconcile, but the business
signal inside key dimensions has silently collapsed.

The repository models a Silver-to-Gold checkpoint with four stages:

1. Capture a trusted baseline from a known-good Silver load.
2. Measure the current load against that baseline.
3. Evaluate explicit publication gates.
4. Emit provenance for operator review and auditability.

## Architecture

### Baseline capture

`src/stability/detection/baseline.py` defines `BaselineSnapshot`. It stores:

- the baseline score for each monitored column,
- the baseline row count,
- the ordered set of monitored columns.

The baseline is built from a pandas DataFrame:

```python
BaselineSnapshot.from_dataframe(df, MONITORED_COLUMNS)
```

The monitored columns are defined in `src/stability/sample_data.py`:

- `department`
- `region`
- `product_category`
- `status`
- `priority`

### Entropy-based stability scoring

`src/stability/detection/entropy.py` uses Shannon entropy as the diversity
signal for each column:

`H(X) = -Σ p(x_i) log2(p(x_i))`

Each column score is normalized to `[0.0, 1.0]` by dividing by the maximum
entropy for the observed number of distinct values:

`score = H(X) / log2(n_unique)`

Interpretation:

- `1.0` means the observed values are maximally diverse for that column's
  cardinality.
- `0.0` means the column has collapsed to a constant.

Important nuance: a stable load does not have to score `1.0`. If a column's
distribution is intentionally skewed, its normalized entropy can be below
`1.0` while still matching the baseline closely. Stability is determined by the
delta from the baseline, not by requiring perfect uniformity.

### Drift detection

`src/stability/detection/drift.py` compares the current load against the stored
baseline:

- recompute the current entropy score for each monitored column,
- compute the delta versus the baseline score,
- classify the column as `stable`, `collapsed`, or `spiked`,
- compute an overall `health_score` as the mean of current per-column scores,
- track row counts and schema coverage.

The default drift classification threshold is `0.3`:

- `abs(delta) <= 0.3` => `stable`
- `delta < -0.3` => `collapsed`
- `delta > 0.3` => `spiked`

### Gate evaluation

`src/stability/gates/evaluator.py` loads gate definitions from
`config/kpi_thresholds.json`.

The current configuration defines six gates:

| Gate | Type | Operator | Threshold |
| ---- | ---- | -------- | --------- |
| `stability_health_score` | `FAIL` | `>=` | `0.70` |
| `bronze_record_fidelity_ratio` | `FAIL` | `>=` | `0.99` |
| `silver_quality_pass_ratio` | `FAIL` | `>=` | `0.95` |
| `provenance_field_coverage` | `FAIL` | `>=` | `1.0` |
| `columns_drifted_ratio` | `WARN` | `<=` | `0.20` |
| `silver_quarantine_ratio` | `WARN` | `<=` | `0.10` |

The evaluator returns both per-gate verdicts and the worst overall verdict:

- any failed `FAIL` gate yields overall `FAIL`,
- otherwise any triggered `WARN` gate yields overall `WARN`,
- otherwise the run is `PASS`.

### Provenance

`src/stability/provenance/builder.py` assembles a `ProvenanceEnvelope` with:

- run timestamp,
- health score,
- overall verdict,
- row counts,
- schema match flag,
- per-gate details,
- per-column drift details.

The envelope exposes `provenance_field_coverage`, which is used as one of the
release gates to ensure the audit record itself is populated.

## Demo scenario

The checked-in sample data is generated in `src/stability/sample_data.py`.

- `generate_baseline()` creates 25 rows with five monitored columns distributed
  evenly across five values each.
- `generate_drifted()` keeps row counts and schema intact but collapses
  `department`, `region`, `product_category`, and `status` to single values.
  `priority` remains diverse.

That scenario yields:

- 5 columns checked,
- 4 columns drifted,
- health score `0.2000`,
- row fidelity preserved at 25 baseline rows and 25 current rows,
- overall verdict `FAIL`.

## Execution paths

### Local CLI

`src/stability/runners/local_demo.py` is the main execution path. It:

1. loads the deterministic baseline and drifted datasets,
2. builds the baseline snapshot,
3. detects drift,
4. loads gate configs,
5. evaluates the gates,
6. builds provenance,
7. prints a human-readable report.

`src/stability/runners/__main__.py` exposes the CLI entry point:

```bash
stability-demo
```

### Notebook

`notebooks/04_stability_deep_dive.py` follows the same control path in a
Databricks-style notebook format for interactive review.

### Databricks Free Edition

`notebooks/05_free_edition_validation.py` runs the same control path in a live
Databricks Free Edition workspace. Evidence screenshots are in `docs/images/ch2/`.

## Repository artifacts

- `data/sample/baseline.csv`
- `data/sample/drifted.csv`
- `tests/test_entropy.py`
- `tests/test_baseline.py`
- `tests/test_drift.py`
- `tests/test_gates.py`
- `tests/test_provenance.py`
- `tests/test_integration.py`
- `.github/workflows/ci.yml`

## Local validation commands

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
pytest -q
stability-demo
```
