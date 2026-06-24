"""Phase F — P-V health trajectories and recalibration policy primitives.

The Phase E finding is that pressure-only proprioception is dominated by the fatigue
*compliance-scale drift* (a young calibration's pose error grows ~100x over life). The Phase F
question is operational: when should you recalibrate? The thesis is that the **observable P-V
loop** (its hysteresis loop area / shape) is a leading indicator of that drift, so a
P-V-health-triggered recalibration can hold accuracy near an always-on policy at a fraction of
the recalibration count.

This module provides the *observable* health signal (the P-V loop area from a volumetric
probe — Gate 1's acquisition method, not the ground-truth compliance multiplier), per-actuator
health-vs-life trajectories, a bootstrap correlation for the leading-indicator claim, and the
recalibration-schedule policies. Threshold selection lives in ``scripts/run_study3.py`` and
uses training/validation actuators only.
"""

from __future__ import annotations

import numpy as np

from sim.fatigue import FatigueParams, degraded_sls, fatigue_state
from sim.plant import SLSParams, pv_loop


def pv_loop_area(sls: SLSParams, *, frequency=None, amplitude_frac=0.1, n_periods=8):
    """Observable P-V hysteresis loop area from a volumetric probe (energy/cycle).

    Uses a fixed sinusoidal volume drive at (by default) the loss-peak frequency; the enclosed
    P-V area grows with the fatigue loss modulus. This is the measurable loop-shape signal, not
    a ground-truth state.
    """
    f = sls.f_loss_peak if frequency is None else frequency
    amplitude = amplitude_frac * sls.V0
    return float(pv_loop(f, amplitude, sls, n_periods=n_periods)["area"])


def health_trajectory(base_sls: SLSParams, rupture_cycles, life_fractions,
                      fp: FatigueParams | None = None, **probe):
    """P-V loop-area health signal at each normalized life fraction for one actuator."""
    fp = fp or FatigueParams(rupture_cycles=float(rupture_cycles))
    out = []
    for lf in life_fractions:
        state = fatigue_state(lf * rupture_cycles, 0.0, fp)
        out.append(pv_loop_area(degraded_sls(base_sls, state), **probe))
    return np.asarray(out, dtype=float)


def bootstrap_correlation(x, y, n_boot=1000, seed=0, ci=0.95):
    """Pearson r between ``x`` and ``y`` with a bootstrap confidence interval.

    Used to quantify the leading-indicator claim: P-V health drift vs pose error over life.
    """
    x = np.asarray(x, float); y = np.asarray(y, float)
    if x.shape != y.shape or x.ndim != 1 or x.size < 3:
        raise ValueError("x and y must be matching 1-D arrays with >= 3 points")
    rng = np.random.default_rng(seed)
    point = float(np.corrcoef(x, y)[0, 1])
    n = x.size
    boot = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        xb, yb = x[idx], y[idx]
        if xb.std() < 1e-15 or yb.std() < 1e-15:
            boot[b] = 0.0
        else:
            boot[b] = np.corrcoef(xb, yb)[0, 1]
    lo = float(np.quantile(boot, (1 - ci) / 2))
    hi = float(np.quantile(boot, 1 - (1 - ci) / 2))
    return {"r": point, "ci_low": lo, "ci_high": hi}


def recalibration_schedule(health, policy, tau=None):
    """Per-life-stage calibrate? flags for one actuator's health trajectory.

    ``policy`` in {"fixed", "always", "triggered"}. Stage 0 always calibrates. "triggered"
    recalibrates when the health drift since the last calibration exceeds ``tau``.
    Returns a boolean list (True = (re)calibrate at this stage).
    """
    health = np.asarray(health, float)
    n = health.size
    if n == 0:
        return []
    flags = [True] + [False] * (n - 1)        # always calibrate once at the start
    if policy == "fixed":
        return flags
    if policy == "always":
        return [True] * n
    if policy == "triggered":
        if tau is None:
            raise ValueError("triggered policy requires tau")
        last = health[0]
        for i in range(1, n):
            if abs(health[i] - last) > tau:
                flags[i] = True
                last = health[i]
        return flags
    raise ValueError(f"unknown policy {policy!r}")


def apply_schedule(flags, errors_if_recalibrated, errors_if_stale):
    """Resolve realized per-stage error given a calibrate? schedule.

    ``errors_if_recalibrated[i]`` = error when calibrated AT stage i (fresh).
    ``errors_if_stale[i][j]`` = error at stage i using the calibration fitted at stage j (j<=i).
    Returns ``(realized_errors, n_recal)``.
    """
    realized = []
    last_cal = None
    for i, do_cal in enumerate(flags):
        if do_cal:
            last_cal = i
            realized.append(errors_if_recalibrated[i])
        else:
            realized.append(errors_if_stale[i][last_cal])
    return np.asarray(realized, float), int(sum(flags))
