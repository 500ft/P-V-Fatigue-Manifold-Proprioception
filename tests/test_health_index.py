"""Tests for causal baseline normalization and HI comparators."""

import numpy as np
import pytest

from pipeline.health_index import (
    fit_baseline,
    fit_baseline_pca,
    fused_hi,
    pca_scores,
    transform_features,
)


def test_noisy_baseline_z_scores_and_fusion_are_causal():
    baseline = np.array([[10.0, 2.0], [11.0, 2.2], [9.0, 1.8], [10.5, 2.1]])
    model = fit_baseline(baseline, names=("area", "compliance"), directions=(1, 1))
    observed = np.array([[11.0, 2.2], [12.0, 2.4], [30.0, 9.0]])
    before = fused_hi(transform_features(observed, model))

    changed_future = observed.copy()
    changed_future[-1] = [-1000, -1000]
    after = fused_hi(transform_features(changed_future, model))
    assert np.allclose(before[:-1], after[:-1])
    assert np.allclose(before, transform_features(observed, model).mean(axis=1))


def test_noise_free_mode_uses_fractional_change_not_artificial_sigma():
    baseline = np.array([[10.0, 2.0]] * 20)
    model = fit_baseline(
        baseline,
        names=("area", "compliance"),
        directions=(1, 1),
        noise_free=True,
    )
    transformed = transform_features(np.array([[11.0, 2.2]]), model)
    assert np.allclose(transformed, [[0.1, 0.1]])


def test_zero_variance_noisy_baseline_is_rejected_not_floored():
    with pytest.raises(ValueError, match="zero variance"):
        fit_baseline(
            np.array([[10.0, 2.0]] * 20),
            names=("area", "compliance"),
            directions=(1, 1),
        )


def test_baseline_pca_does_not_depend_on_future_loops():
    baseline = np.array(
        [[1.0, 0.0, 0.1], [0.9, 0.1, 0.0], [1.1, -0.1, 0.0], [1.0, 0.05, -0.1]]
    )
    model = fit_baseline_pca(baseline)
    early = np.array([[1.0, 0.2, 0.0], [1.1, 0.3, 0.1]])
    future_a = np.vstack([early, [10, 10, 10]])
    future_b = np.vstack([early, [-10, -10, -10]])
    assert np.allclose(pca_scores(future_a, model)[:2], pca_scores(future_b, model)[:2])


def test_pca_sign_is_deterministic():
    baseline = np.array([[1.0, 0.0], [0.0, 1.0], [1.1, -0.1], [-0.1, 1.1]])
    model = fit_baseline_pca(baseline)
    largest = np.argmax(np.abs(model.component))
    assert model.component[largest] > 0
