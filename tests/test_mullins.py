"""Phase C tests for cross-rest Mullins recovery normalization."""

import numpy as np
import pytest

from pipeline.mullins import fit_recovery, normalize_recovery


REST_S = np.array([0, 3600, 86400, 259200, 604800], dtype=float)


def test_recovers_noise_free_time_constant_and_amplitude():
    h_inf = 1.2
    amplitude = 2.8
    tau = 86400.0
    values = h_inf + amplitude * np.exp(-REST_S / tau)
    fit = fit_recovery(REST_S, values)

    assert fit.success
    assert abs(fit.tau_s - tau) / tau < 0.01
    assert abs(fit.amplitude - amplitude) / amplitude < 0.01
    assert abs(fit.asymptote - h_inf) < 0.01


def test_normalization_maps_cross_rest_values_to_five_minutes():
    h_inf = 1.2
    amplitude = 2.8
    tau = 86400.0
    values = h_inf + amplitude * np.exp(-REST_S / tau)
    fit = fit_recovery(REST_S, values)
    normalized = normalize_recovery(values, REST_S, fit, target_rest_s=300.0)
    expected = h_inf + amplitude * np.exp(-300.0 / tau)

    assert np.max(np.abs(normalized - expected)) / np.ptp(values) < 0.01


def test_target_rest_measurement_is_unchanged():
    fit = fit_recovery(REST_S, 1.2 + 2.8 * np.exp(-REST_S / 86400.0))
    value = 3.0
    assert normalize_recovery(value, 300.0, fit, target_rest_s=300.0) == value


@pytest.mark.parametrize(
    "times,values",
    [
        ([0, 1], [1]),
        ([0, 1, 2], [1, np.nan, 2]),
        ([0, 1, 1], [3, 2, 1]),
        ([0, -1, 2], [3, 2, 1]),
    ],
)
def test_invalid_recovery_data_is_rejected(times, values):
    with pytest.raises(ValueError):
        fit_recovery(times, values)
