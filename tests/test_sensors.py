import numpy as np

from sim.sensors import (
    SensorModel,
    SensorParams,
    contact_observation,
    decimate,
    quantize,
)


def test_noise_free_passthrough_is_exact():
    params = SensorParams(pressure_sigma_pa=0.0, pressure_lsb_pa=0.0,
                          position_sigma_m=0.0, position_lsb_m=0.0, sample_decimation=1)
    model = SensorModel(params=params, seed=3)
    p = np.linspace(0, 1e5, 50)
    pos = np.random.default_rng(0).normal(size=(50, 3))
    out = model.measure(pressure=p, position=pos)
    np.testing.assert_array_equal(out["pressure"], p)
    np.testing.assert_array_equal(out["position"], pos)


def test_determinism_same_seed_identical():
    params = SensorParams()
    p = np.linspace(0, 1e5, 32)
    a = SensorModel(params=params, seed=11).measure(pressure=p)["pressure"]
    b = SensorModel(params=params, seed=11).measure(pressure=p)["pressure"]
    np.testing.assert_array_equal(a, b)
    c = SensorModel(params=params, seed=12).measure(pressure=p)["pressure"]
    assert not np.array_equal(a, c)


def test_quantize_grid_and_bound():
    x = np.linspace(-5, 5, 101)
    lsb = 0.25
    q = quantize(x, lsb)
    np.testing.assert_allclose(q / lsb, np.round(q / lsb), atol=1e-9)
    assert np.max(np.abs(q - x)) <= lsb / 2 + 1e-12


def test_decimation_length_and_axis():
    s = np.arange(100)
    assert decimate(s, 4).size == 25
    pos = np.zeros((100, 3))
    assert decimate(pos, 5).shape == (20, 3)


def test_contact_threshold_and_force():
    params = SensorParams(contact_threshold_m=0.0, contact_force_gain_n_per_m=1.0e3,
                          contact_force_sigma_n=0.0)
    pen = np.array([-0.01, 0.0, 0.002, 0.005])
    contact, force = contact_observation(pen, params)
    np.testing.assert_array_equal(contact, [False, False, True, True])
    np.testing.assert_allclose(force, [0.0, 0.0, 2.0, 5.0])
