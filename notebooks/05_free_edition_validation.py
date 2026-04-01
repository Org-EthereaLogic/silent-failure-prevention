# Databricks notebook source
# MAGIC %md
# MAGIC # Silent Failure Prevention — Free Edition Validation
# MAGIC
# MAGIC **Enterprise Data Trust, Chapter 2**
# MAGIC
# MAGIC This notebook validates the release-control pattern in a live Databricks
# MAGIC workspace. It generates baseline and drifted datasets, detects per-column
# MAGIC distribution collapse, evaluates 6 release gates, and produces the same
# MAGIC evidence as the local CLI runner.
# MAGIC
# MAGIC **Expected outcome:** Health score 0.20, 4 of 5 columns drifted, verdict FAIL,
# MAGIC Gold refresh blocked.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Install the package from GitHub

# COMMAND ----------

import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "git+https://github.com/Org-EthereaLogic/silent-failure-prevention.git"])
print("Package installed successfully.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Generate baseline and drifted datasets

# COMMAND ----------

import pandas as pd
from stability.sample_data import generate_baseline, generate_drifted, MONITORED_COLUMNS

baseline_rows = generate_baseline()
drifted_rows = generate_drifted()

baseline_df = pd.DataFrame(baseline_rows)
drifted_df = pd.DataFrame(drifted_rows)

print(f"Baseline: {len(baseline_df)} rows, {len(MONITORED_COLUMNS)} monitored columns")
print(f"Current:  {len(drifted_df)} rows")
print(f"Monitored: {MONITORED_COLUMNS}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Baseline data — diverse distributions across all 5 business columns

# COMMAND ----------

display(baseline_df[["record_id"] + MONITORED_COLUMNS].head(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Drifted data — 4 of 5 columns collapsed to a single value
# MAGIC
# MAGIC Same schema, same row count, same record_ids. But the business signal is gone.

# COMMAND ----------

display(drifted_df[["record_id"] + MONITORED_COLUMNS].head(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Run drift detection — per-column stability comparison

# COMMAND ----------

from stability.detection.baseline import BaselineSnapshot
from stability.detection.drift import detect_drift

baseline_snap = BaselineSnapshot.from_dataframe(baseline_df, MONITORED_COLUMNS)
drift_result = detect_drift(baseline_snap, drifted_df)

column_evidence = pd.DataFrame([
    {
        "column": cr.column,
        "baseline_score": cr.baseline_score,
        "current_score": cr.current_score,
        "delta": cr.delta,
        "classification": cr.classification.value,
    }
    for cr in drift_result.column_results
])

display(column_evidence)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Health score and drift summary

# COMMAND ----------

summary = pd.DataFrame([{
    "columns_checked": drift_result.columns_checked,
    "columns_drifted": drift_result.columns_drifted,
    "health_score": drift_result.health_score,
    "schema_match": drift_result.schema_match,
    "rows_baseline": drift_result.row_count_baseline,
    "rows_current": drift_result.row_count_current,
}])

display(summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Gate evaluation — 6 release control thresholds

# COMMAND ----------

from stability.gates.evaluator import load_gate_configs, evaluate_gates
from pathlib import Path
import json

config_data = {
    "gates": [
        {"name": "stability_health_score", "type": "FAIL", "operator": ">=",
         "threshold": 0.70, "description": "Block Gold when stability degrades"},
        {"name": "bronze_record_fidelity_ratio", "type": "FAIL", "operator": ">=",
         "threshold": 0.99, "description": "Protect against row loss"},
        {"name": "silver_quality_pass_ratio", "type": "FAIL", "operator": ">=",
         "threshold": 0.95, "description": "Rule-based quality pass rate"},
        {"name": "provenance_field_coverage", "type": "FAIL", "operator": ">=",
         "threshold": 1.0, "description": "Complete audit envelope"},
        {"name": "columns_drifted_ratio", "type": "WARN", "operator": "<=",
         "threshold": 0.20, "description": "Broad instability warning"},
        {"name": "silver_quarantine_ratio", "type": "WARN", "operator": "<=",
         "threshold": 0.10, "description": "Quarantine volume threshold"},
    ]
}

config_path = Path("/tmp/kpi_thresholds.json")
config_path.write_text(json.dumps(config_data))
gate_configs = load_gate_configs(config_path)

measured = {
    "stability_health_score": drift_result.health_score,
    "bronze_record_fidelity_ratio": 1.0,
    "silver_quality_pass_ratio": 1.0,
    "provenance_field_coverage": 1.0,
    "columns_drifted_ratio": drift_result.columns_drifted_ratio,
    "silver_quarantine_ratio": 0.0,
}

gate_results, overall_verdict = evaluate_gates(gate_configs, measured)

gate_evidence = pd.DataFrame([
    {
        "gate": gr.config.name,
        "type": gr.config.gate_type,
        "threshold": f"{gr.config.operator} {gr.config.threshold}",
        "measured": gr.measured_value,
        "verdict": gr.verdict.value,
    }
    for gr in gate_results
])

display(gate_evidence)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Publication decision

# COMMAND ----------

print(f"Overall Verdict: {overall_verdict.value}")
print()
if overall_verdict.value == "FAIL":
    print("Gold refresh BLOCKED — distribution stability below threshold.")
    print("The data looks structurally healthy, but 4 of 5 business columns")
    print("have collapsed. Executive dashboards will NOT be refreshed.")
elif overall_verdict.value == "WARN":
    print("Gold refresh ALLOWED with warnings.")
else:
    print("Gold refresh ALLOWED — all gates passed.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Provenance envelope (audit record)

# COMMAND ----------

from stability.provenance.builder import build_provenance

provenance = build_provenance(drift_result, gate_results, overall_verdict)

provenance_summary = pd.DataFrame([{
    "run_ts": provenance.run_ts,
    "health_score": provenance.health_score,
    "overall_verdict": provenance.overall_verdict,
    "columns_checked": provenance.columns_checked,
    "columns_drifted": provenance.columns_drifted,
    "provenance_coverage": provenance.provenance_field_coverage,
}])

display(provenance_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Expected Results
# MAGIC
# MAGIC | Metric | Expected |
# MAGIC |--------|----------|
# MAGIC | Columns checked | 5 |
# MAGIC | Columns drifted | 4 (department, region, product_category, status) |
# MAGIC | Health score | 0.2000 |
# MAGIC | Schema match | True |
# MAGIC | Overall verdict | FAIL |
# MAGIC | Publication decision | Gold refresh BLOCKED |
# MAGIC | Provenance coverage | 1.0 |
# MAGIC
# MAGIC **Scope:** This validates the release-control pattern using deterministic
# MAGIC sample data in a Free Edition workspace. It does not constitute production
# MAGIC deployment or multi-source verification.
