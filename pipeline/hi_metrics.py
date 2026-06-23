"""Health-indicator quality metrics with explicit undefined states."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class MetricResult:
    value: float
    status: str


def monotonicity(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.all(np.isfinite(values)):
        raise ValueError("values must be a finite one-dimensional array with >= 2 points")
    delta = np.diff(values)
    return float(abs((np.count_nonzero(delta > 0) - np.count_nonzero(delta < 0)) / delta.size))


def trendability(trajectories):
    """Minimum absolute pairwise correlation of common-grid trajectories."""
    curves = np.asarray(trajectories, dtype=float)
    if curves.ndim != 2 or curves.shape[0] < 2 or curves.shape[1] < 3:
        raise ValueError("trajectories must be a 2D array with >= 2 lives and >= 3 samples")
    if not np.all(np.isfinite(curves)):
        raise ValueError("trajectories must be finite")
    correlations = []
    for i in range(curves.shape[0]):
        for j in range(i + 1, curves.shape[0]):
            if np.std(curves[i]) == 0 or np.std(curves[j]) == 0:
                raise ValueError("trendability is undefined for constant trajectories")
            correlations.append(abs(float(np.corrcoef(curves[i], curves[j])[0, 1])))
    return float(min(correlations))


def prognosability(starts, ends) -> MetricResult:
    starts = np.asarray(starts, dtype=float)
    ends = np.asarray(ends, dtype=float)
    if starts.ndim != 1 or ends.ndim != 1 or starts.size != ends.size or starts.size < 2:
        raise ValueError("starts and ends must be equal-length one-dimensional arrays")
    if not np.all(np.isfinite(starts)) or not np.all(np.isfinite(ends)):
        raise ValueError("starts and ends must be finite")
    degradation_range = float(np.mean(np.abs(ends - starts)))
    scale = max(float(np.max(np.abs(np.concatenate([starts, ends])))), 1.0)
    if degradation_range <= np.finfo(float).eps * scale:
        return MetricResult(float("nan"), "undefined_no_degradation")
    value = float(np.exp(-np.std(ends, ddof=0) / degradation_range))
    return MetricResult(value, "ok")
