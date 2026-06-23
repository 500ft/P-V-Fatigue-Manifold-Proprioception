import numpy as np

from pipeline.correctors import RidgeCorrector, lagged_features, rmse


def test_lagged_features_shape_and_padding():
    X = np.arange(12.0).reshape(6, 2)
    L = lagged_features(X, 2)
    assert L.shape == (6, 6)
    # row 0 pads its lags with the first sample
    np.testing.assert_array_equal(L[0], [0, 1, 0, 1, 0, 1])
    # row 2 lag-1 is row 1, lag-2 is row 0
    np.testing.assert_array_equal(L[2], [4, 5, 2, 3, 0, 1])


def test_static_ridge_recovers_linear_map():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(500, 2))
    y = X @ np.array([2.0, -1.0]) + 3.0
    model = RidgeCorrector(n_lags=0, alpha=1e-6).fit([X], [y])
    assert rmse(model.predict(X), y) < 1e-2


def test_dynamic_beats_static_on_delayed_signal():
    # target depends on a LAGGED input -> a memoryless map cannot capture it, a lagged one can
    rng = np.random.default_rng(1)
    u = rng.normal(size=(2000, 1))
    y = (0.8 * np.roll(u[:, 0], 2) + 0.2 * np.roll(u[:, 0], 4))
    y[:4] = 0.0
    static = RidgeCorrector(n_lags=0, alpha=1e-3).fit([u], [y])
    dynamic = RidgeCorrector(n_lags=6, alpha=1e-3).fit([u], [y])
    assert rmse(dynamic.predict(u), y) < 0.5 * rmse(static.predict(u), y)
