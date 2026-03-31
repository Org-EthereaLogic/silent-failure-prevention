"""Tests for baseline snapshot creation."""

import pandas as pd

from stability.detection.baseline import BaselineSnapshot


class TestBaselineSnapshot:
    def test_from_dataframe(self):
        df = pd.DataFrame({
            "dept": ["A", "B", "C", "D", "E"],
            "region": ["X", "Y", "Z", "X", "Y"],
        })
        snap = BaselineSnapshot.from_dataframe(df, ["dept", "region"])
        assert snap.row_count == 5
        assert snap.columns == ("dept", "region")
        assert snap.scores["dept"] == 1.0
        assert 0.0 < snap.scores["region"] <= 1.0

    def test_missing_column_scores_zero(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        snap = BaselineSnapshot.from_dataframe(df, ["a", "nonexistent"])
        assert snap.scores["nonexistent"] == 0.0

    def test_immutable(self):
        snap = BaselineSnapshot(scores={"a": 0.5}, row_count=10, columns=("a",))
        try:
            snap.row_count = 20
            assert False, "Should raise"
        except AttributeError:
            pass

    def test_empty_dataframe(self):
        df = pd.DataFrame({"a": pd.Series([], dtype=str)})
        snap = BaselineSnapshot.from_dataframe(df, ["a"])
        assert snap.row_count == 0
        assert snap.scores["a"] == 0.0
