# Databricks notebook source
# MAGIC %md
# MAGIC # Silent Failure Prevention
# MAGIC
# MAGIC This notebook mirrors the local Chapter 2 runner:
# MAGIC
# MAGIC 1. Generate deterministic baseline and drifted datasets.
# MAGIC 2. Build a trusted baseline snapshot.
# MAGIC 3. Detect per-column distribution drift.
# MAGIC 4. Evaluate release gates.
# MAGIC 5. Inspect the provenance envelope before publication.

# COMMAND ----------
from pathlib import Path
import sys

import pandas as pd

ROOT = Path.cwd()
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stability.runners.local_demo import run_demo
from stability.sample_data import generate_baseline, generate_drifted


def show_table(frame: pd.DataFrame) -> None:
    """Display DataFrames in Databricks and fall back to plain text locally."""
    try:
        display(frame)
    except NameError:
        print(frame.to_string(index=False))


# COMMAND ----------
baseline_df = pd.DataFrame(generate_baseline())
drifted_df = pd.DataFrame(generate_drifted())

print("Baseline rows:", len(baseline_df))
print("Current rows :", len(drifted_df))

show_table(baseline_df.head())

# COMMAND ----------
results = run_demo()
drift_result = results["drift_result"]
gate_results = results["gate_results"]
provenance = results["provenance"]

summary_df = pd.DataFrame(
    [
        {
            "columns_checked": drift_result.columns_checked,
            "columns_drifted": drift_result.columns_drifted,
            "health_score": drift_result.health_score,
            "schema_match": drift_result.schema_match,
            "row_count_baseline": drift_result.row_count_baseline,
            "row_count_current": drift_result.row_count_current,
            "overall_verdict": results["overall_verdict"].value,
        }
    ]
)

show_table(summary_df)

# COMMAND ----------
column_df = pd.DataFrame(
    [
        {
            "column": item.column,
            "baseline_score": item.baseline_score,
            "current_score": item.current_score,
            "delta": item.delta,
            "classification": item.classification.value,
        }
        for item in drift_result.column_results
    ]
)

show_table(column_df)

# COMMAND ----------
gate_df = pd.DataFrame(
    [
        {
            "gate": item.config.name,
            "type": item.config.gate_type,
            "operator": item.config.operator,
            "threshold": item.config.threshold,
            "measured": item.measured_value,
            "verdict": item.verdict.value,
        }
        for item in gate_results
    ]
)

show_table(gate_df)

# COMMAND ----------
provenance_df = pd.DataFrame([provenance.to_dict()])
show_table(provenance_df)
