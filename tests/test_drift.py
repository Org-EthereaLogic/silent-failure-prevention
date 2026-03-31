"""Tests for drift detection."""

import pandas as pd

from stability.detection.baseline import BaselineSnapshot
from stability.detection.drift import DriftClassification, detect_drift


class TestDetectDrift:
    def setup_method(self):
        self.baseline_df = pd.DataFrame({
            "dept": ["A", "B", "C", "D", "E"] * 5,
            "region": ["X", "Y", "Z", "X", "Y"] * 5,
        })
        self.columns = ["dept", "region"]
        self.baseline = BaselineSnapshot.from_dataframe(
            self.baseline_df, self.columns
        )

    def test_no_drift(self):
        """Same data should produce no drift."""
        result = detect_drift(self.baseline, self.baseline_df)
        assert result.columns_drifted == 0
        expected = round(
            sum(self.baseline.scores.values()) / len(self.baseline.scores), 4
        )
        assert result.health_score == expected

    def test_full_collapse(self):
        collapsed_df = pd.DataFrame({
            "dept": ["A"] * 25,
            "region": ["X"] * 25,
        })
        result = detect_drift(self.baseline, collapsed_df)
        assert result.columns_drifted == 2
        assert result.health_score == 0.0

    def test_partial_collapse(self):
        partial_df = pd.DataFrame({
            "dept": ["A"] * 25,
            "region": ["X", "Y", "Z", "X", "Y"] * 5,
        })
        result = detect_drift(self.baseline, partial_df)
        assert result.columns_drifted == 1

    def test_classification_collapsed(self):
        collapsed_df = pd.DataFrame({
            "dept": ["A"] * 25,
            "region": ["X", "Y", "Z", "X", "Y"] * 5,
        })
        result = detect_drift(self.baseline, collapsed_df)
        dept_result = [r for r in result.column_results if r.column == "dept"][0]
        assert dept_result.classification == DriftClassification.COLLAPSED

    def test_classification_stable(self):
        result = detect_drift(self.baseline, self.baseline_df)
        for cr in result.column_results:
            assert cr.classification == DriftClassification.STABLE

    def test_schema_match_true(self):
        result = detect_drift(self.baseline, self.baseline_df)
        assert result.schema_match is True

    def test_schema_match_false(self):
        missing_df = pd.DataFrame({"dept": ["A"] * 25})
        result = detect_drift(self.baseline, missing_df)
        assert result.schema_match is False

    def test_row_counts(self):
        result = detect_drift(self.baseline, self.baseline_df)
        assert result.row_count_baseline == 25
        assert result.row_count_current == 25

    def test_drifted_ratio(self):
        collapsed_df = pd.DataFrame({
            "dept": ["A"] * 25,
            "region": ["X"] * 25,
        })
        result = detect_drift(self.baseline, collapsed_df)
        assert result.columns_drifted_ratio == 1.0

    def test_health_score_range(self):
        partial_df = pd.DataFrame({
            "dept": ["A"] * 25,
            "region": ["X", "Y", "Z", "X", "Y"] * 5,
        })
        result = detect_drift(self.baseline, partial_df)
        assert 0.0 <= result.health_score <= 1.0
