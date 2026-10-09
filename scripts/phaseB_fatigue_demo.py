#!/usr/bin/env python3
"""Phase B canonical-fatigue demonstration and consistency report.

Produces separate observables for (a) volumetric P-V probing and (b) closed-valve
pressure decay. All trajectories are synthetic model outputs, not experimental data.
"""

from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]

from sim.fatigue import FatigueParams, degraded_network, degraded_sls, fatigue_state
from sim.plant import (
    NetworkParams,
    SLSParams,
    operational_half_life,
    pv_loop,
    simulate_pressure_decay,
    sls_loss_energy_analytic,
)

from scripts import figstyle

plt = figstyle.setup(style=False)


LIFE_STAGES = [0, 5, 10, 250, 1000, 2000, 2450, 2800, 3200, 3500]
RECOVERY_HOURS = [0, 1, 24, 72, 168]
ONSET_SWEEP = [0.50, 0.70, 0.85]
LEAK_SWEEP = [10.0, 20.0, 40.0]


def main(write_results=True):
    outdir = REPO / "data" / "sim" / "phaseB"
    outdir.mkdir(parents=True, exist_ok=True)
    params = FatigueParams()
    base_sls = SLSParams()
    base_net = NetworkParams()
    frequency = base_sls.f_loss_peak
    amplitude = 2.0e-6
    initial_pressure = 60_000.0

    cycles = np.linspace(0, params.rupture_cycles, 141)
    states = [fatigue_state(float(n), 0, params) for n in cycles]
    compliance = np.array([s.compliance_multiplier for s in states])
    loss = np.array([s.loss_multiplier for s in states])
    leak = np.array([s.leak_multiplier for s in states])
    base_area = sls_loss_energy_analytic(amplitude, 2 * np.pi * frequency, base_sls)
    loop_area = base_area * loss

    life_records = []
    loops = {}
    for n in LIFE_STAGES:
        state = fatigue_state(float(n), 0, params)
        sls = degraded_sls(base_sls, state)
        loop = pv_loop(frequency, amplitude, sls)
        loops[n] = loop
        life_records.append(
            {
                "cycles": n,
                **asdict(state),
                "relaxed_compliance_m3_per_pa": sls.C_relaxed,
                "pv_loop_area_j": float(loop["area"]),
            }
        )

    decay_t = np.linspace(0, 3.0, 3001)
    decay_cycles = [0, 2450, 2975, 3500]
    decays = {}
    decay_records = []
    for n in decay_cycles:
        state = fatigue_state(float(n), 0, params)
        sls = degraded_sls(base_sls, state)
        net = degraded_network(base_net, state)
        decay = simulate_pressure_decay(decay_t, initial_pressure, sls, net.R_l)
        half_life = operational_half_life(decay["t"], decay["P"], initial_pressure)
        decays[n] = decay
        decay_records.append(
            {
                "cycles": n,
                "leak_multiplier": state.leak_multiplier,
                "half_life_s": half_life,
            }
        )

    recovery_cycle = 2000.0
    recovery_records = []
    for hours in RECOVERY_HOURS:
        state = fatigue_state(recovery_cycle, hours * 3600, params)
        recovery_records.append(
            {
                "rest_hours": hours,
                "mullins_permanent": state.mullins_permanent,
                "mullins_recoverable": state.mullins_recoverable,
                "compliance_multiplier": state.compliance_multiplier,
            }
        )

    onset_sensitivity = {}
    for onset in ONSET_SWEEP:
        p = replace(params, acceleration_onset_fraction=onset)
        onset_sensitivity[str(onset)] = [
            fatigue_state(float(n), 0, p).fatigue_accelerating for n in cycles
        ]

    leak_sensitivity = []
    for terminal in LEAK_SWEEP:
        p = replace(params, terminal_leak_multiplier=terminal)
        end = fatigue_state(params.rupture_cycles, 0, p)
        end_sls = degraded_sls(base_sls, end)
        end_net = degraded_network(base_net, end)
        decay = simulate_pressure_decay(decay_t, initial_pressure, end_sls, end_net.R_l)
        leak_sensitivity.append(
            {
                "terminal_multiplier": terminal,
                "rupture_half_life_s": operational_half_life(
                    decay["t"], decay["P"], initial_pressure
                ),
            }
        )

    rupture = fatigue_state(params.rupture_cycles, 0, params)
    at_three_tau = fatigue_state(100, 3 * params.recovery_tau_s, params)
    at_no_rest = fatigue_state(100, 0, params)
    leak_sweep_half_lives = [record["rupture_half_life_s"] for record in leak_sensitivity]
    checks = {
        "cycle_zero_identity": fatigue_state(0, 0, params).compliance_multiplier == 1.0,
        "mullins_stable_by_cycle_10": (
            fatigue_state(10, 0, params).mullins_total / params.mullins_amplitude >= 0.95
        ),
        "three_tau_removes_95pct_recoverable": (
            at_three_tau.mullins_recoverable <= 0.05 * at_no_rest.mullins_recoverable
        ),
        "canonical_compliance_rise_16pct": bool(
            np.isclose(rupture.compliance_multiplier, 1.16)
        ),
        "canonical_loop_area_rise_16pct": bool(np.isclose(rupture.loss_multiplier, 1.16)),
        "terminal_leak_20x": bool(np.isclose(rupture.leak_multiplier, 20.0)),
        "compliance_monotone_by_construction": bool(np.all(np.diff(compliance) >= 0)),
        "loop_area_monotone_by_construction": bool(np.all(np.diff(loop_area) >= 0)),
        "pressure_half_life_decreases_with_conductance_at_fixed_sls": bool(
            np.all(np.diff(leak_sweep_half_lives) < 0)
        ),
    }
    verdict = "PASS" if all(checks.values()) else "CHECK"

    results = {
        "label": "SYNTHETIC SIMULATION — not experimental validation",
        "canonical_parameters": asdict(params),
        "parameter_anchor": {
            "target_no_rest_terminal_compliance_rise_fraction": 0.16,
            "target_no_rest_terminal_loop_area_rise_fraction": 0.16,
            "note": (
                "Order-of-magnitude synthetic anchor motivated by Libby's 96% to 80% "
                "FEM-agreement change; not a conversion from accuracy to compliance."
            ),
        },
        "rupture_cycle": params.rupture_cycles,
        "acceleration_onset_cycle": (
            params.rupture_cycles * params.acceleration_onset_fraction
        ),
        "injected_acceleration_window_cycles": (
            params.rupture_cycles * (1 - params.acceleration_onset_fraction)
        ),
        "injected_acceleration_window_note": (
            "Structural model interval only; not a warning time or predicted lead time."
        ),
        "probe": {
            "frequency_hz": frequency,
            "volume_amplitude_m3": amplitude,
            "pv_leak_observability": (
                "None under imposed-volume probing; leakage is measured by pressure decay."
            ),
            "pressure_decay_initial_pa": initial_pressure,
        },
        "life_stages": life_records,
        "pressure_decay": decay_records,
        "recovery": recovery_records,
        "sensitivity": {
            "acceleration_onset_fractions": ONSET_SWEEP,
            "terminal_leak_multipliers": leak_sensitivity,
        },
        "checks_kind": "numerical and model-consistency checks, not empirical validation",
        "checks": checks,
        "verdict": verdict,
    }
    if write_results:
        (outdir / "phaseB_results.json").write_text(json.dumps(results, indent=2))

    if plt is not None:
        _plots(
            outdir,
            params,
            cycles,
            states,
            compliance,
            loop_area,
            leak,
            loops,
            decays,
            recovery_records,
            onset_sensitivity,
            leak_sensitivity,
            base_area,
        )

    print("=" * 72)
    print("PHASE B — synthetic fatigue + partial recovery + leak observability")
    print("=" * 72)
    print(f"Rupture / acceleration onset       : {params.rupture_cycles:.0f} / "
          f"{params.rupture_cycles * params.acceleration_onset_fraction:.0f} cycles")
    print(f"No-rest terminal compliance/area  : +{(rupture.compliance_multiplier-1)*100:.1f}% / "
          f"+{(rupture.loss_multiplier-1)*100:.1f}%")
    print(f"Recovery tau / permanent floor     : {params.recovery_tau_s/3600:.0f} h / "
          f"{params.mullins_permanent_fraction*100:.0f}%")
    print(f"Terminal leak conductance          : {rupture.leak_multiplier:.0f}x baseline")
    print("-" * 72)
    print(f"VERDICT: {verdict} (consistency only; no empirical validation)")
    print(f"Wrote {outdir}/phaseB_results.json + figures")


def _plots(
    outdir,
    params,
    cycles,
    states,
    compliance,
    loop_area,
    leak,
    loops,
    decays,
    recovery_records,
    onset_sensitivity,
    leak_sensitivity,
    base_area,
):
    figstyle.apply()
    C, S = figstyle.COLOR, figstyle.SIZE
    onset_cycle = params.rupture_cycles * params.acceleration_onset_fraction
    model = (f"Simulation: deterministic fatigue laws (sim/fatigue.py), rupture at {params.rupture_cycles:,.0f} "
             f"cycles,\nacceleration onset at {params.acceleration_onset_fraction:.2f} of life, no rest unless stated.")

    # P-V loops over life (imposed volume): ordered life stages on one vermillion ramp
    shown = [0, 10, 2000, 2450, 3200, 3500]
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 3.0))
    for n, col in zip(shown, figstyle.ramp(C["pv"], len(shown))):
        loop = loops[n]
        ax.plot(loop["V"] * 1e6, loop["P"] / 1e3, color=col, lw=1.0, label=f"{n:,}")
    ax.set_xlabel("Chamber volume (mL)")
    ax.set_ylabel("Chamber pressure (kPa)")
    ax.set_title("At imposed volume the loop barely changes")
    ax.legend(title="Cycles", loc="upper left", alignment="left", handlelength=1.2)
    ax.margins(0.05)
    figstyle.footnote(fig, model + "\nImposed-volume probing cannot see the leak; pressure decay measures it.")
    figstyle.save(fig, outdir / "fig_pv_loops_over_life", formats=("png",)); plt.close(fig)

    # life trajectory: three stacked panels sharing the cycle axis
    fig, axes = plt.subplots(3, 1, figsize=(figstyle.SINGLE, 4.6), sharex=True,
                             gridspec_kw={"hspace": 0.18})
    series = [((compliance - 1) * 100, "Compliance\nrise (%)", C["compliance"]),
              ((loop_area / base_area - 1) * 100, "Loop area\nrise (%)", C["pv"]),
              (leak, "Leak conductance\n(× healthy)", C["leak"])]
    for ax, (y, lab, col) in zip(axes, series):
        ax.plot(cycles, y, color=col)
        ax.axvline(onset_cycle, ls="--", lw=0.8, color=C["ref"])
        ax.set_ylabel(lab)
        ax.margins(x=0.02, y=0.08)
    axes[0].annotate(f"onset {onset_cycle:,.0f} cycles", (onset_cycle, 1), xycoords=("data", "axes fraction"),
                     xytext=(-4, -2), textcoords="offset points", ha="right", va="top",
                     fontsize=S["note"], color=C["ref"])
    axes[-1].set_xlabel("Cycles")
    axes[0].set_title("Compliance and loop area rise together;\nthe leak grows only after onset")
    figstyle.footnote(fig, model)
    figstyle.save(fig, outdir / "fig_fatigue_trajectory", formats=("png",)); plt.close(fig)

    # closed-valve pressure decay at four life stages
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.6))
    shades = figstyle.ramp(C["leak"], len(decays) + 1)[1:]
    for (n, decay), col in zip(decays.items(), shades):
        ax.plot(decay["t"], decay["P"] / decay["P"][0], color=col, label=f"{n:,}")
    ax.axhline(0.5, ls="--", lw=0.8, color=C["ref"])
    ax.text(0.35, 0.52, "half pressure", ha="left", va="bottom", fontsize=S["note"], color=C["ref"])
    ax.set_xlabel("Hold time with valve closed (s)")
    ax.set_ylabel("Pressure / initial pressure")
    ax.set_title("Hold pressure falls faster once the leak grows")
    ax.legend(title="Cycles", loc="upper right", alignment="left", bbox_to_anchor=(1.0, 1.04))
    ax.margins(x=0.02, y=0.04)
    figstyle.footnote(fig, model + " Initial pressure 60 kPa.")
    figstyle.save(fig, outdir / "fig_pressure_decay_over_life", formats=("png",)); plt.close(fig)

    # partial Mullins recovery during rest
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.6))
    hours = [r["rest_hours"] for r in recovery_records]
    permanent = np.array([r["mullins_permanent"] * 100 for r in recovery_records])
    recoverable = np.array([r["mullins_recoverable"] * 100 for r in recovery_records])
    green = figstyle.ramp(C["compliance"], 5)
    ax.stackplot(hours, permanent, recoverable, colors=[green[3], green[1]], lw=0)
    ax.plot(hours, permanent + recoverable, "o", color=green[3], ms=3.5)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xticks([0, 1, 10, 100], ["0", "1", "10", "100"])
    ax.text(1.5, permanent[0] / 2, "permanent", fontsize=S["note"], color="white", va="center")
    ax.text(1.5, permanent[0] + recoverable[1] / 2, "recoverable", fontsize=S["note"],
            color=figstyle.ink(C["compliance"]), va="center")
    ax.set_xlabel("Rest time (h)")
    ax.set_ylabel("Mullins compliance rise (%)")
    ax.set_title("Rest recovers Mullins softening down to its floor")
    ax.set_ylim(0, None)
    ax.margins(x=0.02)
    figstyle.footnote(fig, f"Simulation: state after 2,000 cycles; recovery τ = {params.recovery_tau_s / 3600:.0f} h, "
                      f"permanent fraction\n{params.mullins_permanent_fraction:.0%}. Dots mark the {len(hours)} "
                      "sampled rest times.")
    figstyle.save(fig, outdir / "fig_rest_recovery", formats=("png",)); plt.close(fig)

    # injected acceleration-onset sensitivity
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.6))
    blues = figstyle.ramp(C["onset"], len(onset_sensitivity) + 2)[2:]
    for (onset, trajectory), col in zip(onset_sensitivity.items(), blues):
        y = np.asarray(trajectory) * 100
        ax.plot(cycles, y, color=col, label=f"{float(onset):.2f}")
    ax.set_xlabel("Cycles")
    ax.set_ylabel("Accelerating compliance term (%)")
    ax.set_title("A later onset packs the same rise into fewer cycles")
    ax.legend(title="Onset (fraction of life)", loc="upper left", alignment="left")
    ax.margins(x=0.02, y=0.05)
    figstyle.footnote(fig, model.split(",\n")[0] + ". The onset is an injected model\n"
                      "parameter; the curves are not detected lead times.")
    figstyle.save(fig, outdir / "fig_onset_sensitivity", formats=("png",)); plt.close(fig)

    # leak-magnitude sensitivity
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.4))
    multipliers = [r["terminal_multiplier"] for r in leak_sensitivity]
    half_lives = [r["rupture_half_life_s"] * 1e3 for r in leak_sensitivity]
    ax.plot(multipliers, half_lives, "o-", color=C["leak"])
    for x, y in zip(multipliers, half_lives):
        ax.annotate(f"{y:.1f} ms", (x, y), xytext=(6, 4), textcoords="offset points",
                    fontsize=S["note"], color=figstyle.ink(C["leak"]))
    ax.set_xticks(multipliers, [f"{m:g}×" for m in multipliers])
    ax.set_xlabel("Leak conductance at rupture (× healthy)")
    ax.set_ylabel("Hold half-life at rupture (ms)")
    ax.set_title("Doubling the terminal leak halves the half-life")
    ax.set_ylim(0, max(half_lives) * 1.2)
    ax.margins(x=0.08)
    figstyle.footnote(fig, model.split(",\n")[0] + ".\nInitial hold pressure 60 kPa.")
    figstyle.save(fig, outdir / "fig_leak_sensitivity", formats=("png",)); plt.close(fig)


if __name__ == "__main__":
    import sys
    # --replot recomputes the deterministic curves and redraws the figures without
    # rewriting phaseB_results.json (a full run would also record fatigue_exponent there).
    main(write_results="--replot" not in sys.argv)
