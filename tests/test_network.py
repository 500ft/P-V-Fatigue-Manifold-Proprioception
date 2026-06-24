import numpy as np

from sim.fatigue import FatigueParams, degraded_sls, fatigue_state
from sim.network import probe_coupling, simulate_network
from sim.plant import NetworkParams, SLSParams, linear_network_crosstalk


def test_isolated_has_no_crosstalk_shared_does():
    sls = [SLSParams() for _ in range(3)]
    net = NetworkParams(n_chambers=3)
    iso = probe_coupling(sls, net, "isolated")
    shared = probe_coupling(sls, net, "shared")
    # isolated: structurally decoupled -> coupling is solver-noise small
    assert iso < 1e-6
    # shared: real, and orders of magnitude above the isolated floor
    assert shared > 1e-4
    assert shared > 100 * iso


def test_gate0_dc_compliance_independent_ac_drifts_with_fatigue():
    """Gate 0: DC cross-talk is compliance-independent; actuation-band cross-talk drifts."""
    net = NetworkParams(n_chambers=3)
    young = SLSParams()
    fp = FatigueParams()
    late = fatigue_state(0.95 * fp.rupture_cycles, 0.0, fp)
    old = degraded_sls(young, late)

    w_dc = 2.0 * np.pi * 1e-4
    w_ac = 2.0 * np.pi * 2.0
    dc_young = linear_network_crosstalk(w_dc, net, young)
    dc_old = linear_network_crosstalk(w_dc, net, old)
    ac_young = linear_network_crosstalk(w_ac, net, young)
    ac_old = linear_network_crosstalk(w_ac, net, old)

    # near-DC ratio is essentially independent of the (fatigue-changed) compliance
    assert abs(dc_young - dc_old) <= 1e-4 * max(dc_young, 1e-12)
    # actuation-band ratio moves measurably with fatigue
    assert abs(ac_young - ac_old) > 1e-3 * ac_young


def test_single_chamber_shared_equals_isolated():
    sls = [SLSParams()]
    net = NetworkParams(n_chambers=1)
    freq = 2.0
    t = np.linspace(0.0, 4.0, 801)
    gv0 = 1.0 / net.R_v

    def gv(tt):
        return np.array([gv0 * (1.0 + 0.2 * np.sin(2.0 * np.pi * freq * tt))])

    a = simulate_network(t, gv, "shared", sls, net)["P"]
    b = simulate_network(t, gv, "isolated", sls, net)["P"]
    np.testing.assert_allclose(a, b, rtol=1e-5, atol=1e-3)


def test_shared_coupling_drifts_with_fatigue_in_time_domain():
    """The end-to-end time-domain probe (not just the analytic check) drifts with life."""
    net = NetworkParams(n_chambers=3)
    young = [SLSParams() for _ in range(3)]
    fp = FatigueParams()
    late_state = fatigue_state(0.95 * fp.rupture_cycles, 0.0, fp)
    old = [degraded_sls(SLSParams(), late_state) for _ in range(3)]
    leak = np.full(3, late_state.leak_multiplier)

    c_young = probe_coupling(young, net, "shared")
    c_old = probe_coupling(old, net, "shared", leak_multiplier=leak)
    assert abs(c_old - c_young) > 1e-3 * c_young
