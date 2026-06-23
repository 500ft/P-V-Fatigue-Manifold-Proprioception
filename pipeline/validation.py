"""Known-ground-truth fixtures for Phase C estimator validation."""

from __future__ import annotations

from dataclasses import replace
import math
import numpy as np
from scipy.optimize import brentq
from scipy.special import expit, gamma
from scipy.stats import truncnorm

from sim.fatigue import FatigueParams, FatigueState, fatigue_state


def make_null_params(base=None):
    """Return a first-class no-Mullins, no-fatigue, no-leak control."""
    base = FatigueParams() if base is None else base
    return replace(
        base,
        mullins_amplitude=0.0,
        slow_fatigue_amplitude=0.0,
        accelerating_fatigue_amplitude=0.0,
        terminal_leak_multiplier=1.0,
    )


def add_pressure_noise(pressure, sigma_percent_fs, rng, full_scale_pa=80_000.0):
    pressure = np.asarray(pressure, dtype=float)
    if np.any(~np.isfinite(pressure)):
        raise ValueError("pressure must be finite")
    if not np.isfinite(sigma_percent_fs) or sigma_percent_fs < 0:
        raise ValueError("sigma_percent_fs must be finite and nonnegative")
    if not np.isfinite(full_scale_pa) or full_scale_pa <= 0:
        raise ValueError("full_scale_pa must be finite and positive")
    if sigma_percent_fs == 0:
        return pressure.copy()
    sigma = sigma_percent_fs / 100.0 * full_scale_pa
    return pressure + rng.normal(0.0, sigma, pressure.shape)


def _weibull_shape_for_cv(target_cv):
    def residual(shape):
        ratio = gamma(1 + 2 / shape) / gamma(1 + 1 / shape) ** 2
        return math.sqrt(ratio - 1) - target_cv

    return float(brentq(residual, 0.2, 100.0))


def _lognormal_draws(rng, mean, cv, n):
    sigma2 = math.log(1 + cv**2)
    mu = math.log(mean) - sigma2 / 2
    return rng.lognormal(mu, math.sqrt(sigma2), n)


def _truncated_normal_draws(rng, mean, sd, low, high, n):
    a, b = (low - mean) / sd, (high - mean) / sd
    return truncnorm.rvs(a, b, loc=mean, scale=sd, size=n, random_state=rng)


def sample_validation_cohort(n=20, seed=20260623, vary=("rupture_cycles",)):
    """Sample registered parameter axes; unspecified axes stay canonical."""
    if not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("n must be a positive integer")
    allowed = {
        "rupture_cycles",
        "acceleration_onset_fraction",
        "amplitudes",
        "mullins_permanent_fraction",
        "terminal_leak_multiplier",
    }
    vary = set(vary)
    if not vary <= allowed:
        raise ValueError(f"unknown variability axes: {sorted(vary - allowed)}")
    rng = np.random.default_rng(seed)
    base = FatigueParams()

    values = {name: np.full(n, getattr(base, name), dtype=float) for name in base.__dataclass_fields__}
    if "rupture_cycles" in vary:
        shape = _weibull_shape_for_cv(0.30)
        scale = 3500.0 / gamma(1 + 1 / shape)
        values["rupture_cycles"] = rng.weibull(shape, n) * scale
    if "acceleration_onset_fraction" in vary:
        values["acceleration_onset_fraction"] = _truncated_normal_draws(
            rng, 0.70, 0.08, 0.40, 0.90, n
        )
    if "amplitudes" in vary:
        for name in (
            "mullins_amplitude",
            "slow_fatigue_amplitude",
            "accelerating_fatigue_amplitude",
        ):
            values[name] = _lognormal_draws(rng, getattr(base, name), 0.20, n)
    if "mullins_permanent_fraction" in vary:
        values["mullins_permanent_fraction"] = _truncated_normal_draws(
            rng, 0.30, 0.08, 0.05, 0.70, n
        )
    if "terminal_leak_multiplier" in vary:
        values["terminal_leak_multiplier"] = _lognormal_draws(rng, 20.0, 0.30, n)

    return [FatigueParams(**{name: float(array[i]) for name, array in values.items()}) for i in range(n)]


def logistic_fatigue_state(cycles, rest_s, params: FatigueParams, sharpness=20.0) -> FatigueState:
    """Alternative acceleration form used to expose inverse-crime dependence."""
    if not np.isfinite(sharpness) or sharpness <= 0:
        raise ValueError("sharpness must be finite and positive")
    state = fatigue_state(cycles, rest_s, params)
    u = state.normalized_life
    onset = params.acceleration_onset_fraction
    low = expit(-sharpness * onset)
    high = expit(sharpness * (1 - onset))
    q = float((expit(sharpness * (u - onset)) - low) / (high - low))
    q = min(1.0, max(0.0, q))
    accelerating = params.accelerating_fatigue_amplitude * q
    fatigue_total = state.fatigue_slow + accelerating
    compliance = 1.0 + state.mullins_total + fatigue_total
    loss = (
        1.0
        + params.mullins_loss_coupling * state.mullins_total
        + params.fatigue_loss_coupling * fatigue_total
    )
    leak = 1.0 + (params.terminal_leak_multiplier - 1.0) * q
    return replace(
        state,
        acceleration_coordinate=q,
        fatigue_accelerating=accelerating,
        fatigue_total=fatigue_total,
        compliance_multiplier=compliance,
        loss_multiplier=loss,
        leak_multiplier=leak,
    )


def apply_shared_state_dip(state: FatigueState, params: FatigueParams, amplitude=0.06,
                           center=0.55, width=0.08):
    """Deliberately corrupt both compliance and loss shapes for trendability tests."""
    dip = amplitude * math.exp(-0.5 * ((state.normalized_life - center) / width) ** 2)
    compliance = state.compliance_multiplier - dip
    loss = state.loss_multiplier - dip * params.fatigue_loss_coupling
    return replace(state, compliance_multiplier=compliance, loss_multiplier=loss)


def resample_life(cycles, values, rupture_cycles, n_grid=101):
    cycles = np.asarray(cycles, dtype=float)
    values = np.asarray(values, dtype=float)
    if cycles.ndim != 1 or values.ndim != 1 or cycles.size != values.size or cycles.size < 2:
        raise ValueError("cycles and values must be equal-length one-dimensional arrays")
    if rupture_cycles <= 0 or np.any(np.diff(cycles) <= 0):
        raise ValueError("rupture_cycles and increasing cycle samples are required")
    u = cycles / rupture_cycles
    return np.interp(np.linspace(0, 1, n_grid), u, values)
