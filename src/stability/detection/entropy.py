"""Shannon entropy as a distribution stability signal.

The public function is ``column_stability_score``, which returns a normalized
score in [0.0, 1.0] where 1.0 means full diversity and 0.0 means the column
has collapsed to a constant.

Shannon entropy formula: H(X) = −Σ p(xᵢ) × log₂(p(xᵢ))
"""

from __future__ import annotations

import math

import pandas as pd


def _shannon_entropy(series: pd.Series) -> float:
    """Compute Shannon entropy for a pandas Series."""
    counts = series.value_counts(dropna=False)
    total = counts.sum()
    if total == 0:
        return 0.0
    probs = counts / total
    return -sum(p * math.log2(p) for p in probs if p > 0)


def _max_entropy(n_values: int) -> float:
    """Maximum possible entropy for n distinct values: log₂(n)."""
    if n_values <= 1:
        return 0.0
    return math.log2(n_values)


def column_stability_score(series: pd.Series) -> float:
    """Compute a normalized stability score for a single column.

    Returns a value in [0.0, 1.0]:
      - 1.0 = full diversity (entropy at maximum for the observed cardinality)
      - 0.0 = collapsed to a single value (zero entropy)

    The normalization uses the baseline cardinality (number of unique values
    in the series) so the score reflects how evenly distributed the column is
    relative to its own diversity potential.
    """
    n_unique = series.nunique(dropna=False)
    if n_unique <= 1:
        return 0.0
    h = _shannon_entropy(series)
    h_max = _max_entropy(n_unique)
    if h_max == 0:
        return 0.0
    return round(min(h / h_max, 1.0), 4)
