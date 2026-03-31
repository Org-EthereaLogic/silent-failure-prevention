"""Tests for the entropy-based stability scoring."""

import pandas as pd

from stability.detection.entropy import column_stability_score


class TestColumnStabilityScore:
    def test_uniform_distribution(self):
        """Perfectly uniform distribution should score 1.0."""
        series = pd.Series(["A", "B", "C", "D", "E"])
        assert column_stability_score(series) == 1.0

    def test_collapsed_to_constant(self):
        """Single-value column should score 0.0."""
        series = pd.Series(["A", "A", "A", "A", "A"])
        assert column_stability_score(series) == 0.0

    def test_empty_series(self):
        series = pd.Series([], dtype=str)
        assert column_stability_score(series) == 0.0

    def test_single_element(self):
        series = pd.Series(["A"])
        assert column_stability_score(series) == 0.0

    def test_two_values_equal(self):
        series = pd.Series(["A", "B", "A", "B"])
        assert column_stability_score(series) == 1.0

    def test_two_values_skewed(self):
        series = pd.Series(["A", "A", "A", "B"])
        score = column_stability_score(series)
        assert 0.0 < score < 1.0

    def test_score_bounded(self):
        series = pd.Series(["A", "B", "C", "A", "A", "B"])
        score = column_stability_score(series)
        assert 0.0 <= score <= 1.0

    def test_with_nulls(self):
        """Nulls should be treated as a category."""
        series = pd.Series(["A", None, "B", None, "C"])
        score = column_stability_score(series)
        assert 0.0 < score <= 1.0

    def test_numeric_series(self):
        series = pd.Series([1, 2, 3, 4, 5])
        assert column_stability_score(series) == 1.0

    def test_numeric_collapsed(self):
        series = pd.Series([42, 42, 42, 42])
        assert column_stability_score(series) == 0.0
