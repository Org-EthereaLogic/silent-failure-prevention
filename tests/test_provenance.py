"""Tests for provenance envelope builder."""

import pandas as pd

from stability.detection.baseline import BaselineSnapshot
from stability.detection.drift import detect_drift
from stability.gates.evaluator import GateConfig, evaluate_gates
from stability.provenance.builder import ProvenanceEnvelope, build_provenance


def _make_drift_result():
    baseline_df = pd.DataFrame({"a": ["X", "Y", "Z", "X", "Y"] * 5})
    drifted_df = pd.DataFrame({"a": ["X"] * 25})
    baseline = BaselineSnapshot.from_dataframe(baseline_df, ["a"])
    return detect_drift(baseline, drifted_df)


def _make_gate_config():
    return GateConfig(
        name="test", gate_type="FAIL", operator=">=",
        threshold=0.7, description="test gate"
    )


class TestBuildProvenance:
    def test_produces_envelope(self):
        drift = _make_drift_result()
        configs = [_make_gate_config()]
        gate_results, verdict = evaluate_gates(configs, {"test": 0.5})
        env = build_provenance(drift, gate_results, verdict)
        assert isinstance(env, ProvenanceEnvelope)

    def test_envelope_has_run_ts(self):
        drift = _make_drift_result()
        configs = [_make_gate_config()]
        gate_results, verdict = evaluate_gates(configs, {"test": 0.5})
        env = build_provenance(drift, gate_results, verdict)
        assert env.run_ts is not None
        assert "T" in env.run_ts  # ISO format

    def test_envelope_captures_verdict(self):
        drift = _make_drift_result()
        configs = [_make_gate_config()]
        gate_results, verdict = evaluate_gates(configs, {"test": 0.5})
        env = build_provenance(drift, gate_results, verdict)
        assert env.overall_verdict == "FAIL"

    def test_envelope_to_dict(self):
        drift = _make_drift_result()
        configs = [_make_gate_config()]
        gate_results, verdict = evaluate_gates(configs, {"test": 0.5})
        env = build_provenance(drift, gate_results, verdict)
        d = env.to_dict()
        assert "health_score" in d
        assert "gate_results" in d

    def test_provenance_field_coverage(self):
        drift = _make_drift_result()
        configs = [_make_gate_config()]
        gate_results, verdict = evaluate_gates(configs, {"test": 0.5})
        env = build_provenance(drift, gate_results, verdict)
        assert env.provenance_field_coverage == 1.0

    def test_immutable(self):
        drift = _make_drift_result()
        configs = [_make_gate_config()]
        gate_results, verdict = evaluate_gates(configs, {"test": 0.5})
        env = build_provenance(drift, gate_results, verdict)
        try:
            env.health_score = 0.99
            assert False, "Should raise"
        except AttributeError:
            pass
