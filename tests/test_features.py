"""Phase C tests for P-V loop feature extraction."""

import numpy as np
import pytest

from pipeline.features import extract_loop_features, resample_loop
from sim.plant import SLSParams, pv_loop, sls_loss_energy_analytic


def triangular_loop(k=2.0e10, offset=0.0, n=101):
    up = np.linspace(3e-6, 7e-6, n)
    down = np.linspace(7e-6, 3e-6, n)[1:]
    V = np.concatenate([up, down])
    branch = np.concatenate([np.ones(n), -np.ones(n - 1)])
    P = k * (V - 5e-6) + offset * branch
    return V, P


def test_extracts_known_linear_compliance_and_zero_asymmetry():
    k = 2.0e10
    V, P = triangular_loop(k=k)
    features = extract_loop_features(V, P)

    assert np.isclose(features.inflation_compliance, 1 / k, rtol=1e-10)
    assert abs(features.loop_area) < 1e-12
    assert abs(features.asymmetry) < 1e-12
    assert np.isclose(features.peak_pressure, 40_000.0)


def test_area_matches_sls_analytic_ground_truth():
    sls = SLSParams()
    amplitude = 2e-6
    loop = pv_loop(sls.f_loss_peak, amplitude, sls)
    features = extract_loop_features(loop["V"], loop["P"])
    expected = sls_loss_energy_analytic(
        amplitude, 2 * np.pi * sls.f_loss_peak, sls
    )
    assert abs(features.loop_area - expected) / expected < 0.02


def test_asymmetry_detects_branch_pressure_separation():
    V, P = triangular_loop(offset=2_000.0)
    features = extract_loop_features(V, P)
    assert features.asymmetry > 0
    assert features.loop_area > 0


def test_resampling_has_fixed_shape_and_preserves_finite_values():
    V, P = triangular_loop(offset=1_000.0)
    vector = resample_loop(V, P, n_grid=64)
    assert vector.shape == (128,)
    assert np.all(np.isfinite(vector))


@pytest.mark.parametrize(
    "V,P",
    [
        ([1, 2], [1]),
        ([1, 2, np.nan], [1, 2, 3]),
        ([1, 2, 3], [1, 2, 3]),
        ([1, 1, 1, 1], [1, 2, 1, 2]),
    ],
)
def test_rejects_malformed_or_single_branch_loops(V, P):
    with pytest.raises(ValueError):
        extract_loop_features(V, P)
