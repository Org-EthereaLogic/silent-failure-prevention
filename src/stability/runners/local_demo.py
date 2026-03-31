"""Local release control demo — the main executable entry point.

Loads sample baseline and drifted data, runs the full detection → gate
evaluation → provenance pipeline, and prints a human-readable report.

Usage:
    PYTHONPATH=src python -m stability.runners
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from stability.detection.baseline import BaselineSnapshot
from stability.detection.drift import detect_drift
from stability.gates.evaluator import evaluate_gates, load_gate_configs
from stability.provenance.builder import build_provenance
from stability.sample_data import MONITORED_COLUMNS, generate_baseline, generate_drifted


def _find_config() -> Path:
    """Locate the gate config file relative to the project root."""
    candidates = [
        Path("config/kpi_thresholds.json"),
        Path(__file__).resolve().parent.parent.parent.parent / "config" / "kpi_thresholds.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("Cannot find config/kpi_thresholds.json")


def run_demo() -> dict:
    """Run the full release control pipeline and return structured results."""
    # Load data
    baseline_rows = generate_baseline()
    drifted_rows = generate_drifted()

    baseline_df = pd.DataFrame(baseline_rows)
    drifted_df = pd.DataFrame(drifted_rows)

    # Build baseline snapshot
    baseline = BaselineSnapshot.from_dataframe(baseline_df, MONITORED_COLUMNS)

    # Detect drift
    drift_result = detect_drift(baseline, drifted_df)

    # Load gate configs and build measured values
    config_path = _find_config()
    gate_configs = load_gate_configs(config_path)

    measured = {
        "stability_health_score": drift_result.health_score,
        "bronze_record_fidelity_ratio": (
            1.0
            if drift_result.row_count_current == drift_result.row_count_baseline
            else drift_result.row_count_current / max(drift_result.row_count_baseline, 1)
        ),
        "silver_quality_pass_ratio": 1.0,  # demo input
        "provenance_field_coverage": 1.0,  # will be verified after build
        "columns_drifted_ratio": drift_result.columns_drifted_ratio,
        "silver_quarantine_ratio": 0.0,  # demo input
    }

    # Evaluate gates
    gate_results, overall_verdict = evaluate_gates(gate_configs, measured)

    # Build provenance
    provenance = build_provenance(drift_result, gate_results, overall_verdict)

    # Update provenance coverage in measured (verify the envelope is complete)
    measured["provenance_field_coverage"] = provenance.provenance_field_coverage

    return {
        "baseline": baseline,
        "drift_result": drift_result,
        "gate_results": gate_results,
        "overall_verdict": overall_verdict,
        "provenance": provenance,
        "measured": measured,
    }


def print_demo_report() -> dict:
    """Run the demo and print a human-readable report."""
    results = run_demo()
    drift = results["drift_result"]
    gate_results = results["gate_results"]
    overall = results["overall_verdict"]

    print("=" * 64)
    print("SILENT FAILURE PREVENTION — Release Control Demo")
    print("=" * 64)
    print()
    print("Distribution Stability")
    print("-" * 44)
    print(f"  Columns checked : {drift.columns_checked}")
    print(f"  Columns drifted : {drift.columns_drifted}")
    print(f"  Health Score    : {drift.health_score:.4f}")
    print(f"  Schema match    : {drift.schema_match}")
    print(f"  Rows (baseline) : {drift.row_count_baseline}")
    print(f"  Rows (current)  : {drift.row_count_current}")
    print()
    print("Per-Column Results")
    print("-" * 44)
    for cr in drift.column_results:
        arrow = "→"
        print(
            f"  {cr.column:20s}  "
            f"{cr.baseline_score:.4f} {arrow} {cr.current_score:.4f}  "
            f"[{cr.classification.value}]"
        )
    print()
    print("Gate Evaluation")
    print("-" * 44)
    for gr in gate_results:
        symbol = {"PASS": "✓", "WARN": "⚠", "FAIL": "✗"}[gr.verdict.value]
        print(
            f"  {symbol} {gr.config.name:36s}  "
            f"{gr.measured_value:.4f} {gr.config.operator} {gr.config.threshold:.2f}  "
            f"[{gr.verdict.value}]"
        )
    print()
    print(f"Overall Verdict: {overall.value}")
    if overall.value == "FAIL":
        print("Gold refresh BLOCKED — distribution stability below threshold.")
    elif overall.value == "WARN":
        print("Gold refresh ALLOWED with warnings.")
    else:
        print("Gold refresh ALLOWED — all gates passed.")
    print()

    return results
