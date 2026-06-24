"""Phase D — sensor / observation model: seeded noise, quantization, sampling, contact.

Turns ground-truth observables (chamber pressure, in-loop volume, tip pose, contact) into
*measured* signals with deterministic, reproducible corruption. Given the same seed and
inputs the output is bit-identical (``tests/test_sensors.py``). Channels draw from
independent sub-streams (``SeedSequence.spawn``) so adding or removing one measured channel
does not shift another channel's noise realization.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class SensorParams:
    """Measurement-chain parameters. A zero ``*_sigma`` or ``*_lsb`` disables that effect."""

    pressure_sigma_pa: float = 50.0
    pressure_lsb_pa: float = 10.0
    volume_sigma_m3: float = 1.0e-9
    volume_lsb_m3: float = 0.0
    position_sigma_m: float = 2.0e-4
    position_lsb_m: float = 0.0
    sample_decimation: int = 1          # keep every k-th time sample (>= 1)
    contact_threshold_m: float = 0.0    # tip penetration > threshold -> in contact
    contact_force_gain_n_per_m: float = 1.0e3
    contact_force_sigma_n: float = 0.0

    def __post_init__(self) -> None:
        for name in ("pressure_sigma_pa", "volume_sigma_m3", "position_sigma_m",
                     "contact_force_sigma_n"):
            v = getattr(self, name)
            if not math.isfinite(v) or v < 0:
                raise ValueError(f"{name} must be finite and >= 0")
        for name in ("pressure_lsb_pa", "volume_lsb_m3", "position_lsb_m"):
            v = getattr(self, name)
            if not math.isfinite(v) or v < 0:
                raise ValueError(f"{name} must be finite and >= 0 (0 disables)")
        if self.sample_decimation < 1:
            raise ValueError("sample_decimation must be >= 1")


def quantize(x, lsb):
    """Round to the nearest multiple of ``lsb`` (``lsb`` <= 0 disables, returns a copy)."""
    x = np.asarray(x, dtype=float)
    if lsb is None or lsb <= 0:
        return x.copy()
    return np.round(x / lsb) * lsb


def decimate(series, k: int):
    """Keep every ``k``-th sample along the first (time) axis (``k`` <= 1 returns a copy)."""
    s = np.asarray(series)
    if k <= 1:
        return s.copy()
    return s[::k]


def _noise(shape, sigma: float, rng: np.random.Generator):
    if sigma <= 0:
        return np.zeros(shape)
    return rng.normal(0.0, sigma, size=shape)


def measure_scalar_series(values, sigma: float, lsb: float, rng: np.random.Generator):
    """Add seeded Gaussian noise, then quantize, a 1-D series."""
    v = np.asarray(values, dtype=float)
    return quantize(v + _noise(v.shape, sigma, rng), lsb)


def contact_observation(penetration_m, params: SensorParams, rng: np.random.Generator | None = None):
    """Binary contact flag + synthetic normal force from tip penetration into a plane.

    ``penetration_m`` > 0 means the tip is past the contact plane. Returns
    ``(in_contact, force_n)``.
    """
    pen = np.asarray(penetration_m, dtype=float)
    in_contact = pen > params.contact_threshold_m
    force = np.where(in_contact,
                     params.contact_force_gain_n_per_m * np.clip(pen, 0.0, None),
                     0.0)
    if rng is not None and params.contact_force_sigma_n > 0:
        force = np.clip(force + _noise(force.shape, params.contact_force_sigma_n, rng), 0.0, None)
    return in_contact, force


@dataclass
class SensorModel:
    """Seeded measurement model. Same ``seed`` + inputs -> identical measured output."""

    params: SensorParams
    seed: int = 0

    def measure(self, *, pressure=None, volume=None, position=None, penetration=None):
        """Apply noise + quantization + decimation to whichever observables are supplied.

        Returns a dict with the measured arrays. Deterministic given ``seed``.
        """
        out = {}
        children = np.random.SeedSequence(self.seed).spawn(4)
        if pressure is not None:
            rng = np.random.default_rng(children[0])
            m = measure_scalar_series(pressure, self.params.pressure_sigma_pa,
                                      self.params.pressure_lsb_pa, rng)
            out["pressure"] = decimate(m, self.params.sample_decimation)
        if volume is not None:
            rng = np.random.default_rng(children[1])
            m = measure_scalar_series(volume, self.params.volume_sigma_m3,
                                      self.params.volume_lsb_m3, rng)
            out["volume"] = decimate(m, self.params.sample_decimation)
        if position is not None:
            rng = np.random.default_rng(children[2])
            pos = np.asarray(position, dtype=float)
            noisy = pos + _noise(pos.shape, self.params.position_sigma_m, rng)
            out["position"] = decimate(quantize(noisy, self.params.position_lsb_m),
                                       self.params.sample_decimation)
        if penetration is not None:
            rng = np.random.default_rng(children[3])
            contact, force = contact_observation(penetration, self.params, rng)
            out["contact"] = decimate(contact, self.params.sample_decimation)
            out["contact_force"] = decimate(force, self.params.sample_decimation)
        return out
