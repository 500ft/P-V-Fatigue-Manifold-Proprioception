import numpy as np

from pipeline.coupling import (
    apply_schedule,
    bootstrap_correlation,
    cycle_schedule,
    health_trajectory,
    lead_time,
    per_group_correlations,
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


def test_cycle_schedule_counts_and_period_monotonicity():
    cycles = np.array([350.0, 1050.0, 1750.0, 2450.0, 3150.0])   # 0.1..0.9 of 3500
    assert cycle_schedule(cycles, 1e9) == [True, False, False, False, False]
    assert cycle_schedule(cycles, 0.0) == [True] * 5             # any advance triggers
    short = cycle_schedule(cycles, 600.0)
    long = cycle_schedule(cycles, 2500.0)
    assert sum(short) > sum(long)            # shorter period -> more recalibrations
    assert short[0] is True and long[0] is True


def test_cycle_schedule_misaligns_across_rupture_lives():
    # The same global period lands at different life fractions for different
    # rupture lives - the misalignment that lets the P-V trigger beat the clock.
    period = 2700.0
    short_lived = cycle_schedule(np.array([0.1, 0.3, 0.5, 0.7, 0.9]) * 3000.0, period)
    long_lived = cycle_schedule(np.array([0.1, 0.3, 0.5, 0.7, 0.9]) * 4000.0, period)
    assert short_lived != long_lived


def test_lead_time_interpolates_known_crossing_gap():
    life = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    health = np.array([1.0, 1.025, 1.075, 1.2, 1.4])
    err = np.array([0.02, 0.06, 0.10, 0.20, 0.35])
    res = lead_time(health, err, tau=0.05, budget_mm=0.15, life_fractions=life)
    assert res["status"] == "ok"
    np.testing.assert_allclose(res["trigger_life"], 0.4)
    np.testing.assert_allclose(res["budget_violation_life"], 0.6)
    np.testing.assert_allclose(res["lead_life"], 0.2)


def test_lead_time_handles_exact_stage_crossing():
    life = np.array([0.1, 0.3, 0.5])
    health = np.array([1.0, 1.05, 1.2])
    err = np.array([0.01, 0.02, 0.15])
    res = lead_time(health, err, tau=0.05, budget_mm=0.15, life_fractions=life)
    assert res["status"] == "ok"
    np.testing.assert_allclose(res["trigger_life"], 0.3)
    np.testing.assert_allclose(res["budget_violation_life"], 0.5)


def test_lead_time_reports_degenerate_statuses():
    life = np.array([0.1, 0.3, 0.5])
    assert lead_time([1.0, 1.01, 1.02], [0.0, 0.2, 0.3], 0.05, 0.1, life)["status"] == "never_triggers"
    assert lead_time([1.0, 1.1, 1.2], [0.0, 0.02, 0.03], 0.05, 0.1, life)["status"] == "never_violates"
    assert lead_time([1.0, 1.2, 1.3], [0.2, 0.3, 0.4], 0.05, 0.1, life)["status"] == "nonpositive_lead"


def test_per_group_correlations_reports_deviant_group():
    groups = np.repeat([10, 11, 12], 5)
    x = np.tile(np.arange(5, dtype=float), 3)
    y = np.concatenate([x[:5], x[:5] * 2.0, -x[:5]])
    res = per_group_correlations(groups, x, y)
    assert len(res["values"]) == 3
    vals = {rec["group"]: rec["r"] for rec in res["values"]}
    assert vals[10] > 0.99
    assert vals[11] > 0.99
    assert vals[12] < -0.99
    np.testing.assert_allclose(res["median"], vals[10])
