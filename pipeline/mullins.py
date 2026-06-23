"""Fit and normalize the time-dependent part of Mullins recovery."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit


@dataclass(frozen=True)
class RecoveryFit:
    asymptote: float
    amplitude: float
    tau_s: float
    success: bool


def _recovery_model(t, asymptote, amplitude, tau_s):
    return asymptote + amplitude * np.exp(-t / tau_s)


def fit_recovery(rest_s, values) -> RecoveryFit:
    """Fit ``h_inf + A exp(-t/tau)`` to one cross-rest recovery arm."""
    rest_s = np.asarray(rest_s, dtype=float)
    values = np.asarray(values, dtype=float)
    if rest_s.ndim != 1 or values.ndim != 1 or rest_s.size != values.size or rest_s.size < 3:
        raise ValueError("rest_s and values must be equal-length arrays with >= 3 points")
    if not np.all(np.isfinite(rest_s)) or not np.all(np.isfinite(values)):
        raise ValueError("recovery data must be finite")
    if np.any(rest_s < 0) or np.any(np.diff(rest_s) <= 0):
        raise ValueError("rest_s must be nonnegative and strictly increasing")

    amplitude0 = max(float(values[0] - values[-1]), np.finfo(float).eps)
    asymptote0 = float(values[-1])
    tau0 = max(float(rest_s[len(rest_s) // 2]), 1.0)
    try:
        popt, _ = curve_fit(
            _recovery_model,
            rest_s,
            values,
            p0=[asymptote0, amplitude0, tau0],
            bounds=([-np.inf, 0.0, 1e-9], [np.inf, np.inf, np.inf]),
            maxfev=20_000,
        )
    except (RuntimeError, ValueError):
        return RecoveryFit(float("nan"), float("nan"), float("nan"), False)
    return RecoveryFit(float(popt[0]), float(popt[1]), float(popt[2]), True)


def normalize_recovery(values, rest_s, fit: RecoveryFit, target_rest_s=300.0):
    """Map cross-rest measurements to a common rest duration.

    Routine measurements already made at ``target_rest_s`` need no correction.
    """
    if not fit.success or fit.tau_s <= 0:
        raise ValueError("a successful recovery fit with positive tau_s is required")
    if not np.isfinite(target_rest_s) or target_rest_s < 0:
        raise ValueError("target_rest_s must be finite and nonnegative")
    values_arr = np.asarray(values, dtype=float)
    rest_arr = np.asarray(rest_s, dtype=float)
    if np.any(~np.isfinite(values_arr)) or np.any(~np.isfinite(rest_arr)) or np.any(rest_arr < 0):
        raise ValueError("values and rest_s must be finite; rest_s must be nonnegative")
    correction = fit.amplitude * (
        np.exp(-rest_arr / fit.tau_s) - np.exp(-target_rest_s / fit.tau_s)
    )
    result = values_arr - correction
    return float(result) if result.ndim == 0 else result
