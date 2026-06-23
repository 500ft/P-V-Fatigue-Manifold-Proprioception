"""Phase B consistency and numerical tests for fatigue and leak observability."""

from dataclasses import replace

import numpy as np
import pytest

from sim.fatigue import (
    FatigueParams,
    degraded_network,
    degraded_sls,
    fatigue_state,
)
from sim.plant import (
    NetworkParams,
    SLSParams,
    operational_half_life,
    pv_loop,
    simulate_pressure_decay,
)


def test_cycle_zero_is_exact_identity():
    params = FatigueParams()
    base_sls = SLSParams()
    base_net = NetworkParams()
    state = fatigue_state(0, 0, params)

    assert state.compliance_multiplier == 1.0
    assert state.loss_multiplier == 1.0
    assert state.leak_multiplier == 1.0
    assert degraded_sls(base_sls, state) == base_sls
    assert degraded_network(base_net, state) == base_net


def test_mullins_stabilizes_by_cycle_ten():
    params = FatigueParams()
    state = fatigue_state(10, 0, params)
    assert state.mullins_total / params.mullins_amplitude >= 0.95


def test_recovery_removes_recoverable_part_but_leaves_floor():
    params = FatigueParams()
    fresh = fatigue_state(100, 0, params)
    rested = fatigue_state(100, 3 * params.recovery_tau_s, params)

    assert rested.mullins_recoverable <= 0.05 * fresh.mullins_recoverable
    expected_floor = params.mullins_amplitude * params.mullins_permanent_fraction
    saturation = 1 - np.exp(-100 / params.mullins_cycles_tau)
    assert np.isclose(rested.mullins_permanent, expected_floor * saturation)
    assert rested.mullins_total > rested.mullins_permanent


def test_rest_does_not_change_fatigue_or_leak():
    params = FatigueParams()
    no_rest = fatigue_state(3000, 0, params)
    rested = fatigue_state(3000, 7 * 86400, params)

    assert rested.fatigue_slow == no_rest.fatigue_slow
    assert rested.fatigue_accelerating == no_rest.fatigue_accelerating
    assert rested.leak_multiplier == no_rest.leak_multiplier


def test_canonical_onset_and_terminal_values():
    params = FatigueParams()
    onset_cycles = params.rupture_cycles * params.acceleration_onset_fraction
    onset = fatigue_state(onset_cycles, 0, params)
    after = fatigue_state(onset_cycles + 1, 0, params)
    rupture = fatigue_state(params.rupture_cycles, 0, params)

    assert onset.acceleration_coordinate == 0.0
    assert onset.fatigue_accelerating == 0.0
    assert onset.leak_multiplier == 1.0
    assert after.acceleration_coordinate > 0.0
    assert after.fatigue_accelerating > 0.0
    assert after.leak_multiplier > 1.0
    assert np.isclose(rupture.compliance_multiplier, 1.16)
    assert np.isclose(rupture.loss_multiplier, 1.16)
    assert np.isclose(rupture.leak_multiplier, 20.0)


def test_adapters_are_immutable_and_map_conductance_correctly():
    params = FatigueParams()
    base_sls = SLSParams()
    base_net = NetworkParams()
    state = fatigue_state(params.rupture_cycles, 0, params)
    changed_sls = degraded_sls(base_sls, state)
    changed_net = degraded_network(base_net, state)

    assert base_sls == SLSParams()
    assert base_net == NetworkParams()
    assert np.isclose(changed_sls.k1, base_sls.k1 / 1.16)
    assert np.isclose(changed_sls.k2, base_sls.k2 * 1.16)
    assert np.isclose(changed_net.R_l, base_net.R_l / 20.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rupture_cycles": 0},
        {"acceleration_onset_fraction": 0},
        {"acceleration_onset_fraction": 1},
        {"mullins_cycles_tau": 0},
        {"mullins_permanent_fraction": -0.1},
        {"mullins_permanent_fraction": 1.1},
        {"recovery_tau_s": 0},
        {"terminal_leak_multiplier": 0.5},
    ],
)
def test_invalid_parameters_are_rejected(kwargs):
    with pytest.raises(ValueError):
        FatigueParams(**kwargs)


@pytest.mark.parametrize("cycles, rest_s", [(-1, 0), (0, -1), (3501, 0)])
def test_invalid_queries_are_rejected(cycles, rest_s):
    with pytest.raises(ValueError):
        fatigue_state(cycles, rest_s, FatigueParams())


def test_pressure_decay_matches_relaxed_spring_analytic_solution():
    sls = SLSParams(k2=0.0)
    resistance = 8.0e9
    initial_pressure = 60_000.0
    t = np.linspace(0, 2.0, 1001)
    out = simulate_pressure_decay(t, initial_pressure, sls, resistance)
    expected = initial_pressure * np.exp(-(sls.k1 / resistance) * t)

    assert np.max(np.abs(out["P"] - expected)) / initial_pressure < 1e-5


def test_operational_half_life_is_monotone_with_leak_conductance():
    sls = SLSParams()
    initial_pressure = 60_000.0
    t = np.linspace(0, 3.0, 3001)
    half_lives = []
    for multiplier in [1.0, 10.0, 20.0]:
        out = simulate_pressure_decay(t, initial_pressure, sls, 8.0e9 / multiplier)
        half_lives.append(operational_half_life(out["t"], out["P"], initial_pressure))

    assert np.all(np.isfinite(half_lives))
    assert half_lives[0] > half_lives[1] > half_lives[2]


def test_operational_half_life_uses_first_interpolated_half_pressure_crossing():
    t = np.array([0.0, 1.0, 2.0])
    pressure = np.array([100.0, 60.0, 40.0])
    assert operational_half_life(t, pressure, 100.0) == 1.5


def test_canonical_pv_loop_area_tracks_loss_multiplier():
    params = FatigueParams()
    base = SLSParams()
    rupture = degraded_sls(base, fatigue_state(params.rupture_cycles, 0, params))
    base_loop = pv_loop(base.f_loss_peak, 2e-6, base)
    rupture_loop = pv_loop(base.f_loss_peak, 2e-6, rupture)

    assert np.isclose(rupture.C_relaxed / base.C_relaxed, 1.16)
    assert np.isclose(rupture_loop["area"] / base_loop["area"], 1.16, rtol=1e-3)


def test_custom_parameters_change_ground_truth_without_changing_defaults():
    defaults = FatigueParams()
    custom = replace(defaults, acceleration_onset_fraction=0.5, terminal_leak_multiplier=40)
    custom_end = fatigue_state(custom.rupture_cycles, 0, custom)

    assert defaults.acceleration_onset_fraction == 0.7
    assert defaults.terminal_leak_multiplier == 20.0
    assert custom_end.leak_multiplier == 40.0
