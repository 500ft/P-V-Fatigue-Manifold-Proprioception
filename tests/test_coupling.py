import numpy as np

from pipeline.coupling import (
    apply_schedule,
    bootstrap_correlation,
    health_trajectory,
    pv_loop_area,
    recalibration_schedule,
)
from sim.plant import SLSParams


def test_health_signal_grows_with_life():
    base = SLSParams()
    h = health_trajectory(base, rupture_cycles=3500.0,
                          life_fractions=[0.1, 0.3, 0.5, 0.7, 0.9])
    # loop area (loss modulus) increases monotonically with fatigue life
    assert np.all(np.diff(h) > 0)
    assert h[-1] > h[0]


def test_pv_loop_area_positive():
    assert pv_loop_area(SLSParams()) > 0.0


def test_bootstrap_correlation_detects_strong_link():
    x = np.linspace(0, 1, 30)
    y = 2 * x + 0.001 * np.arange(30)
    res = bootstrap_correlation(x, y, n_boot=200, seed=0)
    assert res["r"] > 0.99
    assert res["ci_low"] <= res["r"] <= res["ci_high"]


def test_schedule_policies_count_recalibrations():
    health = np.array([1.0, 1.05, 1.15, 1.4, 2.0])
    assert recalibration_schedule(health, "fixed") == [True, False, False, False, False]
    assert recalibration_schedule(health, "always") == [True] * 5
    tight = recalibration_schedule(health, "triggered", tau=0.05)
    loose = recalibration_schedule(health, "triggered", tau=0.5)
    assert sum(tight) > sum(loose)          # smaller tau -> more recalibrations
    assert tight[0] is True and loose[0] is True


def test_apply_schedule_uses_last_calibration():
    flags = [True, False, True, False]
    fresh = [0.1, 0.2, 0.1, 0.2]                       # error when calibrated AT stage i (diagonal)
    # stale[i][j] = error at stage i using the calibration fitted at stage j (j <= i)
    stale = [[0.1],
             [0.5, 0.2],
             [0.9, 0.6, 0.1],
             [1.0, 0.7, 0.3, 0.2]]
    realized, n = apply_schedule(flags, fresh, stale)
    # stage0 fresh(0.1); stage1 uses cal@0 (0.5); stage2 fresh(0.1); stage3 uses cal@2 (0.3)
    np.testing.assert_allclose(realized, [0.1, 0.5, 0.1, 0.3])
    assert n == 2
