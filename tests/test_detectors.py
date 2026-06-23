"""Tests for causal slow-drift detectors and false-alarm calibration."""

import numpy as np

from pipeline.degradation import (
    calibrate_cusum_to_sustained,
    cusum_alarm,
    false_alarm_rate,
    sustained_sigma_alarm,
)


def test_sustained_rule_alarms_on_second_consecutive_crossing():
    values = np.array([0.0, 3.2, 2.9, 3.1, 3.4, 4.0])
    result = sustained_sigma_alarm(values, baseline_mean=0, baseline_std=1)
    assert result.status == "alarm"
    assert result.alarm_index == 4


def test_sustained_rule_rejects_zero_baseline_sigma():
    result = sustained_sigma_alarm([0, 1, 2], baseline_mean=0, baseline_std=0)
    assert result.status == "undefined_zero_baseline_sigma"
    assert result.alarm_index is None


def test_cusum_accumulates_slow_ramp_before_sustained_rule():
    values = np.linspace(0, 3.05, 30)
    cusum = cusum_alarm(values, reference=0.5, threshold=8.0)
    sustained = sustained_sigma_alarm(values, baseline_mean=0, baseline_std=1)
    assert cusum.status == "alarm"
    assert sustained.status == "no_alarm"


def test_cusum_calibration_matches_null_false_alarm_order():
    rng = np.random.default_rng(12)
    calibration = rng.normal(0, 1, (5000, 20))
    fitted = calibrate_cusum_to_sustained(calibration, reference=0.5)
    evaluation = rng.normal(0, 1, (4000, 20))
    sustained_fa = false_alarm_rate(
        evaluation, lambda row: sustained_sigma_alarm(row, 0, 1)
    )
    cusum_fa = false_alarm_rate(
        evaluation, lambda row: cusum_alarm(row, 0.5, fitted.threshold)
    )
    assert fitted.threshold > 0
    assert abs(cusum_fa - sustained_fa) < 0.01


def test_future_change_does_not_move_existing_alarm():
    values = np.array([0, 1, 3.1, 3.2, 3.4, 3.5], dtype=float)
    original = sustained_sigma_alarm(values, 0, 1)
    changed = values.copy()
    changed[-1] = -1000
    assert sustained_sigma_alarm(changed, 0, 1).alarm_index == original.alarm_index
