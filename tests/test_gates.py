"""Tests for the gate evaluator."""

from stability.gates.evaluator import (
    GateConfig,
    GateVerdict,
    evaluate_gates,
    load_gate_configs,
)


def _gate(
    name: str = "test",
    gate_type: str = "FAIL",
    op: str = ">=",
    threshold: float = 0.7,
):
    return GateConfig(
        name=name, gate_type=gate_type, operator=op,
        threshold=threshold, description="",
    )


class TestGateEvaluation:
    def test_pass_gte(self):
        configs = [_gate(threshold=0.7)]
        results, overall = evaluate_gates(configs, {"test": 0.8})
        assert results[0].verdict == GateVerdict.PASS
        assert overall == GateVerdict.PASS

    def test_fail_gte(self):
        configs = [_gate(threshold=0.7)]
        results, overall = evaluate_gates(configs, {"test": 0.5})
        assert results[0].verdict == GateVerdict.FAIL
        assert overall == GateVerdict.FAIL

    def test_warn_lte(self):
        configs = [_gate(gate_type="WARN", op="<=", threshold=0.2)]
        results, overall = evaluate_gates(configs, {"test": 0.8})
        assert results[0].verdict == GateVerdict.WARN
        assert overall == GateVerdict.WARN

    def test_pass_lte(self):
        configs = [_gate(gate_type="WARN", op="<=", threshold=0.2)]
        results, overall = evaluate_gates(configs, {"test": 0.1})
        assert results[0].verdict == GateVerdict.PASS
        assert overall == GateVerdict.PASS

    def test_fail_overrides_warn(self):
        configs = [
            _gate(name="g1", gate_type="FAIL", threshold=0.9),
            _gate(name="g2", gate_type="WARN", op="<=", threshold=0.1),
        ]
        results, overall = evaluate_gates(configs, {"g1": 0.5, "g2": 0.5})
        assert overall == GateVerdict.FAIL

    def test_missing_measured_defaults_zero(self):
        configs = [_gate(threshold=0.7)]
        results, overall = evaluate_gates(configs, {})
        assert results[0].measured_value == 0.0
        assert results[0].verdict == GateVerdict.FAIL

    def test_all_pass(self):
        configs = [
            _gate(name="g1", threshold=0.5),
            _gate(name="g2", gate_type="WARN", op="<=", threshold=0.5),
        ]
        results, overall = evaluate_gates(configs, {"g1": 0.8, "g2": 0.2})
        assert overall == GateVerdict.PASS

    def test_exact_threshold_passes(self):
        configs = [_gate(threshold=0.7)]
        results, _ = evaluate_gates(configs, {"test": 0.7})
        assert results[0].verdict == GateVerdict.PASS


class TestLoadGateConfigs:
    def test_load_from_file(self, tmp_path):
        import json
        config = {
            "gates": [
                {
                    "name": "test_gate",
                    "type": "FAIL",
                    "operator": ">=",
                    "threshold": 0.5,
                    "description": "A test gate",
                }
            ]
        }
        path = tmp_path / "gates.json"
        path.write_text(json.dumps(config))
        configs = load_gate_configs(path)
        assert len(configs) == 1
        assert configs[0].name == "test_gate"
        assert configs[0].threshold == 0.5
