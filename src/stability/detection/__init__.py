"""Detection subpackage — entropy computation, baseline management, drift detection."""

from stability.detection.baseline import BaselineSnapshot
from stability.detection.drift import DriftResult, detect_drift
from stability.detection.entropy import column_stability_score

__all__ = [
    "column_stability_score",
    "BaselineSnapshot",
    "DriftResult",
    "detect_drift",
]
