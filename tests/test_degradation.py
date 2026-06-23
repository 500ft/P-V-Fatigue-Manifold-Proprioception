"""Tests for Phase C degradation models and sample-size guards."""

import numpy as np

from pipeline.degradation import (
    corrected_aic,
    fit_double_logistic,
    fit_linear,
    fit_logistic,
    fit_segmented_quadratic,
)


def test_corrected_aic_rejects_underdetermined_sample_count():
    value, status = corrected_aic(n=5, k=4, rss=1.0)
    assert status == "undefined_insufficient_samples"
    assert np.isinf(value)


def test_segmented_quadratic_recovers_noise_free_onset_ceiling():
    u = np.linspace(0, 1, 36)
    true_onset = 0.70
    y = 0.04 * u + 0.08 * np.maximum(0, (u - true_onset) / (1 - true_onset)) ** 2
    fit = fit_segmented_quadratic(u, y)
    assert fit.status == "ok"
    assert abs(fit.onset - true_onset) < 0.02
    assert fit.form_matched_ceiling


def test_segmented_quadratic_reports_sparse_onset_unidentifiable():
    u = np.array([0.02, 0.25, 0.5, 0.75, 1.0])
    y = u**2
    fit = fit_segmented_quadratic(u, y)
    assert fit.status == "undefined_insufficient_breakpoint_support"


def test_linear_and_logistic_fits_return_predictions():
    u = np.linspace(0, 1, 40)
    linear = fit_linear(u, 1 + 2 * u)
    assert linear.status == "ok"
    assert np.max(np.abs(linear.predicted - (1 + 2 * u))) < 1e-10

    true_onset = 0.65
    y = 0.2 + 1.5 / (1 + np.exp(-20 * (u - true_onset)))
    logistic = fit_logistic(u, y)
    assert logistic.status == "ok"
    assert abs(logistic.onset - true_onset) < 0.03


def test_double_logistic_has_global_aicc_guard():
    u = np.linspace(0, 1, 8)
    fit = fit_double_logistic(u, u**2)
    assert fit.status == "undefined_insufficient_samples"
    assert np.isinf(fit.aicc)
