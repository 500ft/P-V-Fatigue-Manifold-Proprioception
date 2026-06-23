"""Causal, unit-carrying features extracted from one closed P-V loop."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from sim.plant import loop_area


@dataclass(frozen=True)
class LoopFeatures:
    loop_area: float
    inflation_compliance: float
    peak_pressure: float
    asymmetry: float


def _validated_branches(V, P):
    V = np.asarray(V, dtype=float)
    P = np.asarray(P, dtype=float)
    if V.ndim != 1 or P.ndim != 1 or V.size != P.size or V.size < 8:
        raise ValueError("V and P must be equal-length one-dimensional loop arrays")
    if not np.all(np.isfinite(V)) or not np.all(np.isfinite(P)):
        raise ValueError("V and P must contain only finite values")
    if np.ptp(V) <= 0:
        raise ValueError("loop must span a nonzero volume range")

    direction = np.gradient(V)
    inflation = direction > 0
    deflation = direction < 0
    if inflation.sum() < 4 or deflation.sum() < 4:
        raise ValueError("loop must contain both inflation and deflation branches")
    return V, P, inflation, deflation


def _sorted_unique(x, y):
    order = np.argsort(x)
    x = np.asarray(x)[order]
    y = np.asarray(y)[order]
    unique, inverse = np.unique(x, return_inverse=True)
    sums = np.zeros(unique.size)
    counts = np.zeros(unique.size)
    np.add.at(sums, inverse, y)
    np.add.at(counts, inverse, 1)
    return unique, sums / counts


def _branch_pressures(V, P, inflation, deflation, n_grid):
    vi, pi = _sorted_unique(V[inflation], P[inflation])
    vd, pd = _sorted_unique(V[deflation], P[deflation])
    low = max(vi.min(), vd.min())
    high = min(vi.max(), vd.max())
    if high <= low:
        raise ValueError("inflation and deflation branches do not overlap in volume")
    grid = np.linspace(low, high, n_grid)
    return grid, np.interp(grid, vi, pi), np.interp(grid, vd, pd)


def extract_loop_features(V, P) -> LoopFeatures:
    """Extract scalar features without using cycle count or future loops."""
    V, P, inflation, deflation = _validated_branches(V, P)
    vmin, vmax = float(V.min()), float(V.max())
    lo = vmin + 0.70 * (vmax - vmin)
    hi = vmin + 0.90 * (vmax - vmin)
    window = inflation & (V >= lo) & (V <= hi)
    if window.sum() < 3 or np.ptp(P[window]) <= 0:
        raise ValueError("insufficient inflation samples in the 70-90% volume window")
    compliance = float(np.polyfit(P[window], V[window], 1)[0])

    _, p_in, p_out = _branch_pressures(V, P, inflation, deflation, n_grid=101)
    pressure_span = float(np.ptp(P))
    asymmetry = float(np.mean(np.abs(p_in - p_out)) / pressure_span) if pressure_span else 0.0
    return LoopFeatures(
        loop_area=float(loop_area(V, P)),
        inflation_compliance=compliance,
        peak_pressure=float(np.max(P)),
        asymmetry=asymmetry,
    )


def resample_loop(V, P, n_grid=100):
    """Return inflation then deflation pressure vectors on a common volume grid."""
    if not isinstance(n_grid, (int, np.integer)) or n_grid < 4:
        raise ValueError("n_grid must be an integer >= 4")
    V, P, inflation, deflation = _validated_branches(V, P)
    _, p_in, p_out = _branch_pressures(V, P, inflation, deflation, n_grid=n_grid)
    return np.concatenate([p_in, p_out])
