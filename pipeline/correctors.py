"""Phase E — proprioception correctors: static ridge vs dynamic (lagged-input) ARX.

Pressure-only proprioception: estimate the focal actuator's bending curvature from the
shared-manifold pressure and the focal valve command. The Gate-0 prediction is that a
*static* (memoryless) ridge map is blind to the fatigue-induced *dynamic* cross-talk under a
shared manifold, while a *dynamic* corrector with input memory recovers it.

The dynamic model uses **lagged inputs** (an ARX/FIR exogenous form, no autoregressive output
term): the true pose is the estimation target and is not measured online, so feeding back
past outputs would leak ground truth. ``RidgeCorrector(n_lags=0)`` is the static baseline and
``n_lags>0`` is the dynamic corrector — same estimator, the lag count is the only difference.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def lagged_features(X, n_lags):
    """Stack ``[x_t, x_{t-1}, ..., x_{t-n_lags}]`` per row; early rows pad with the first sample.

    ``X``: ``(T, F)`` single trace -> ``(T, F*(n_lags+1))``.
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError("X must be 2-D (T, F)")
    cols = [X]
    for lag in range(1, n_lags + 1):
        shifted = np.empty_like(X)
        shifted[lag:] = X[:-lag]
        shifted[:lag] = X[0]
        cols.append(shifted)
    return np.concatenate(cols, axis=1)


def rmse(pred, true):
    return float(np.sqrt(np.mean((np.asarray(pred, float) - np.asarray(true, float)) ** 2)))


@dataclass
class RidgeCorrector:
    """Ridge corrector. ``n_lags=0`` -> static (memoryless); ``n_lags>0`` -> dynamic (lagged input)."""

    n_lags: int = 0
    alpha: float = 1.0
    _w: np.ndarray = field(default=None, repr=False)
    _mu: np.ndarray = field(default=None, repr=False)
    _sd: np.ndarray = field(default=None, repr=False)
    _ymu: float = field(default=0.0, repr=False)

    def fit(self, traces, targets):
        """``traces``: list of ``(T,F)`` feature arrays; ``targets``: list of ``(T,)`` curvature series."""
        Phi = np.concatenate([lagged_features(x, self.n_lags) for x in traces], axis=0)
        y = np.concatenate([np.asarray(t, float).ravel() for t in targets])
        self._mu = Phi.mean(axis=0)
        self._sd = Phi.std(axis=0) + 1e-12
        Z = (Phi - self._mu) / self._sd
        self._ymu = float(y.mean())
        A = Z.T @ Z + self.alpha * np.eye(Z.shape[1])
        self._w = np.linalg.solve(A, Z.T @ (y - self._ymu))
        return self

    def predict(self, trace):
        if self._w is None:
            raise RuntimeError("call fit() before predict()")
        Z = (lagged_features(trace, self.n_lags) - self._mu) / self._sd
        return Z @ self._w + self._ymu
