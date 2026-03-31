"""Provenance envelope builder — captures run context for auditability."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from stability.detection.drift import DriftResult
from stability.gates.evaluator import GateResult, GateVerdict


@dataclass(frozen=True)
class ProvenanceEnvelope:
    """Immutable audit record of a release control run."""

    run_ts: str
    health_score: float
    overall_verdict: str
    columns_checked: int
    columns_drifted: int
    row_count_baseline: int
    row_count_current: int
    schema_match: bool
    gate_results: tuple[dict, ...] = ()
    column_details: tuple[dict, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def provenance_field_coverage(self) -> float:
        """Returns 1.0 if all required fields are populated, 0.0 otherwise."""
        required = [
            self.run_ts,
            self.health_score is not None,
            self.overall_verdict,
            self.columns_checked is not None,
        ]
        return 1.0 if all(required) else 0.0


def build_provenance(
    drift_result: DriftResult,
    gate_results: list[GateResult],
    overall_verdict: GateVerdict,
) -> ProvenanceEnvelope:
    """Build an audit-ready provenance envelope from a completed run."""
    gate_dicts = tuple(
        {
            "name": gr.config.name,
            "type": gr.config.gate_type,
            "threshold": gr.config.threshold,
            "measured": gr.measured_value,
            "verdict": gr.verdict.value,
        }
        for gr in gate_results
    )

    column_dicts = tuple(
        {
            "column": cr.column,
            "baseline_score": cr.baseline_score,
            "current_score": cr.current_score,
            "delta": cr.delta,
            "classification": cr.classification.value,
        }
        for cr in drift_result.column_results
    )

    return ProvenanceEnvelope(
        run_ts=datetime.now(timezone.utc).isoformat(),
        health_score=drift_result.health_score,
        overall_verdict=overall_verdict.value,
        columns_checked=drift_result.columns_checked,
        columns_drifted=drift_result.columns_drifted,
        row_count_baseline=drift_result.row_count_baseline,
        row_count_current=drift_result.row_count_current,
        schema_match=drift_result.schema_match,
        gate_results=gate_dicts,
        column_details=column_dicts,
    )
