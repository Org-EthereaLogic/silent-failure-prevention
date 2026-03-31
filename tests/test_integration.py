"""Integration test — runs the full demo and verifies README-claimed outputs."""

from stability.gates.evaluator import GateVerdict
from stability.runners.local_demo import run_demo


class TestFullDemo:
    def setup_method(self):
        self.results = run_demo()

    def test_columns_checked(self):
        assert self.results["drift_result"].columns_checked == 5

    def test_columns_drifted(self):
        assert self.results["drift_result"].columns_drifted == 4

    def test_health_score(self):
        assert self.results["drift_result"].health_score == 0.2

    def test_overall_verdict_fail(self):
        assert self.results["overall_verdict"] == GateVerdict.FAIL

    def test_row_counts_match(self):
        drift = self.results["drift_result"]
        assert drift.row_count_baseline == 25
        assert drift.row_count_current == 25

    def test_schema_match(self):
        assert self.results["drift_result"].schema_match is True

    def test_six_gates_evaluated(self):
        assert len(self.results["gate_results"]) == 6

    def test_stability_gate_fails(self):
        stability = [
            g for g in self.results["gate_results"]
            if g.config.name == "stability_health_score"
        ]
        assert len(stability) == 1
        assert stability[0].verdict == GateVerdict.FAIL

    def test_fidelity_gate_passes(self):
        fidelity = [
            g for g in self.results["gate_results"]
            if g.config.name == "bronze_record_fidelity_ratio"
        ]
        assert fidelity[0].verdict == GateVerdict.PASS

    def test_provenance_complete(self):
        env = self.results["provenance"]
        assert env.provenance_field_coverage == 1.0
        assert env.overall_verdict == "FAIL"
        assert env.columns_checked == 5
        assert env.columns_drifted == 4


class TestDeterminism:
    def test_repeated_runs_match(self):
        r1 = run_demo()
        r2 = run_demo()
        assert r1["drift_result"].health_score == r2["drift_result"].health_score
        assert r1["overall_verdict"] == r2["overall_verdict"]
        assert r1["drift_result"].columns_drifted == r2["drift_result"].columns_drifted
