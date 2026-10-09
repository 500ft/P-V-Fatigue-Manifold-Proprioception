"""Study A — does between-unit dispersion break the normalised-indicator invariance?

Preregistered in docs/specs/observability-program/studyA-preregistration.md. Writes data/sim/studyA/.
"""

from __future__ import annotations

import json
import os

import numpy as np

from pipeline.dispersion import AXES, SEED, sample_units
from sim.fatigue import degraded_sls, fatigue_state
from sim.plant import first_crossing, loop_area, pv_loop
from sim.sensors import SensorModel, SensorParams
from scripts import figstyle

DATA = "data/sim/studyA"
N_UNITS = 30
LIFE = [round(x, 3) for x in np.arange(0.05, 0.951, 0.05)]
F_PROBE_HZ = 2.0          # fixed: the operator does not know each unit's loss peak
AMP_FRAC = 0.1
TAU_TRIGGER = 0.05
REPEATS = 5


def probe_loop(unit, u):
    fs = fatigue_state(u * unit.fatigue.rupture_cycles, 0.0, unit.fatigue)
    sls = degraded_sls(unit.sls, fs)
    lp = pv_loop(F_PROBE_HZ, AMP_FRAC * sls.V0, sls)
    return lp["V"], lp["P"]


def measured_area(V, P, seed):
    m = SensorModel(SensorParams(), seed).measure(pressure=P, volume=V)
    return loop_area(m["volume"], m["pressure"])


def trajectories(unit, index):
    """(ideal normalised indicator [S], measured normalised indicator [S, R]) for one unit."""
    ideal, meas = [], []
    for s, u in enumerate(LIFE):
        V, P = probe_loop(unit, u)
        ideal.append(loop_area(V, P))
        meas.append([measured_area(V, P, int(np.random.SeedSequence([SEED, index, s, r]).generate_state(1)[0]))
                     for r in range(REPEATS)])
    ideal, meas = np.asarray(ideal), np.asarray(meas)
    return ideal / ideal[0], meas / meas[0].mean()


def spread_metrics(h):
    """h: [units, stages, repeats] -> per-stage between/within SD, ratio, ICC(1)."""
    means = h.mean(axis=2)
    sd_between = means.std(axis=0, ddof=1)
    within_var = h.var(axis=2, ddof=1)
    sd_within = np.sqrt(within_var.mean(axis=0))
    r = h.shape[2]
    ms_b, ms_w = r * means.var(axis=0, ddof=1), within_var.mean(axis=0)
    icc = (ms_b - ms_w) / (ms_b + (r - 1) * ms_w)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(sd_within > 0, sd_between / sd_within, np.inf)
    return {"sd_between": sd_between, "sd_within": sd_within, "ratio": ratio, "icc": icc}


def verdict(ideal_sd_between_end, ratio, icc, trigger_sd, amended=False):
    """Preregistered rule (criteria i, ii, iii); ``amended=True`` applies the 2026-09-16 owner amendment
    that withdraws criterion iii (see the preregistration's amendment section)."""
    late = np.asarray(LIFE) >= 0.30
    if ideal_sd_between_end < 1e-6:
        return "A-DEGENERATE"
    ok = np.median(ratio[late]) >= 2.0 and np.median(icc[late]) >= 0.5 and (amended or trigger_sd >= 0.10)
    return "A-PASS" if ok else "A-FAIL"


def main():
    units = sample_units(N_UNITS, SEED)
    ideal, meas = zip(*(trajectories(unit, i) for i, unit in enumerate(units)))
    ideal, meas = np.asarray(ideal), np.asarray(meas)                  # [N,S], [N,S,R]
    m = spread_metrics(meas)
    trig = [first_crossing(LIFE, h, 1.0 + TAU_TRIGGER) for h in meas.mean(axis=2)]
    finite = [t for t in trig if t is not None]
    trigger_sd = float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0
    ideal_sd = ideal.std(axis=0, ddof=1)

    ablation = {}
    for axis in ("none",) + AXES:
        axes = () if axis == "none" else (axis,)
        ab = np.asarray([trajectories(u, i)[0] for i, u in enumerate(sample_units(N_UNITS, SEED, axes))])
        ablation[axis] = {"ideal_sd_between_u050": float(ab[:, LIFE.index(0.5)].std(ddof=1)),
                          "ideal_sd_between_u090": float(ab[:, LIFE.index(0.9)].std(ddof=1))}

    v = verdict(ideal_sd[-1], m["ratio"], m["icc"], trigger_sd)
    results = {
        "preregistration": "docs/specs/observability-program/studyA-preregistration.md",
        "seed": SEED, "n_units": N_UNITS, "life_fractions": LIFE, "probe_hz": F_PROBE_HZ,
        "amplitude_frac": AMP_FRAC, "repeats": REPEATS, "tau_trigger": TAU_TRIGGER,
        "ideal_sd_between": ideal_sd.tolist(),
        "measured": {k: [None if not np.isfinite(x) else float(x) for x in val] for k, val in m.items()},
        "trigger_life_per_unit": trig, "trigger_life_sd": trigger_sd,
        "trigger_life_range": [float(min(finite)), float(max(finite))] if finite else None,
        "n_never_trigger": int(sum(t is None for t in trig)),
        "ablation_one_axis": ablation,
        "verdict": v,
        "verdict_amended_2026_09_16": verdict(ideal_sd[-1], m["ratio"], m["icc"], trigger_sd, amended=True),
        "verdict_inputs": {"ideal_sd_between_u095": float(ideal_sd[-1]),
                           "median_ratio_u_ge_030": float(np.median(m["ratio"][np.asarray(LIFE) >= 0.3])),
                           "median_icc_u_ge_030": float(np.median(m["icc"][np.asarray(LIFE) >= 0.3]))},
        "units": [{"rupture_cycles": u.fatigue.rupture_cycles, "onset": u.fatigue.acceleration_onset_fraction,
                   "fatigue_exponent": u.fatigue.fatigue_exponent, "k1": u.sls.k1, "k2": u.sls.k2,
                   "tau": u.sls.tau, "temperature_c": u.temperature_c, "thickness_ratio": u.thickness_ratio}
                  for u in units],
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(results, open(os.path.join(DATA, "studyA_results.json"), "w"), indent=2)
    print(f"Study A verdict: {v} (preregistered rule) | {results['verdict_amended_2026_09_16']} (2026-09-16 amendment)")
    print(f"  ideal SD_between at u=0.95: {ideal_sd[-1]:.4g} | median ratio (u>=0.3): "
          f"{results['verdict_inputs']['median_ratio_u_ge_030']:.2f} | median ICC: "
          f"{results['verdict_inputs']['median_icc_u_ge_030']:.2f} | trigger-life SD: {trigger_sd:.3f} "
          f"(range {results['trigger_life_range']}, never: {results['n_never_trigger']})")
    for axis, ab in ablation.items():
        print(f"  ablation {axis:12s} SD_between(u=0.9) = {ab['ideal_sd_between_u090']:.3g}")

    plt = figstyle.setup()
    if plt is None:  # pragma: no cover
        return
    C, S = figstyle.COLOR, figstyle.SIZE
    life = np.asarray(LIFE)
    mid = life >= 0.5
    fig = plt.figure(figsize=(figstyle.FULL, 3.0))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], wspace=0.42, hspace=0.6)
    a = fig.add_subplot(gs[:, 0])
    b = fig.add_subplot(gs[0, 1])
    c = fig.add_subplot(gs[1, 1], sharex=b)
    for h in meas.mean(axis=2):
        a.plot(LIFE, h, "-", lw=0.7, color=C["unit"], alpha=0.8)
    a.axhline(1.0 + TAU_TRIGGER, ls="--", color=C["pv"], lw=0.9)
    a.text(LIFE[0], 1.0 + TAU_TRIGGER + 0.002, f"trigger at τ = {TAU_TRIGGER:g}", fontsize=S["note"],
           color=figstyle.ink(C["pv"]), va="bottom")
    a.set_xlabel("Normalized life")
    a.set_ylabel("Measured P-V loop area / young")
    a.set_title(f"{N_UNITS} dispersed units fan out after mid-life")
    a.margins(x=0.02)
    ratio, icc = np.asarray(m["ratio"]), np.asarray(m["icc"])
    b.plot(LIFE, ratio, "o-", color=C["always"], ms=3)
    b.axhline(2.0, ls=":", color=C["ref"], lw=0.8)
    b.text(LIFE[-1], 2.6, "criterion 2", fontsize=S["note"], color=C["ref"], ha="right", va="bottom")
    b.set_ylabel("SD ratio,\nbetween / within")
    b.set_title(f"From mid-life units differ {ratio[mid].min():.0f}–{ratio[mid].max():.0f}× more than noise")
    c.plot(LIFE, icc, "o-", color=C["always"], ms=3)
    c.axhline(0.5, ls=":", color=C["ref"], lw=0.8)
    c.text(LIFE[-1], 0.42, "criterion 0.5", fontsize=S["note"], color=C["ref"], ha="right", va="top")
    c.set_ylabel("ICC(1)")
    c.set_ylim(-0.35, 1.1)
    c.set_xlabel("Normalized life")
    plt.setp(b.get_xticklabels(), visible=False)
    c.set_title(f"ICC stays at or above {np.floor(icc[mid].min() * 100) / 100:.2f} from mid-life")
    figstyle.panel_letter(a, "a", dx=-40)
    figstyle.panel_letter(b, "b", dx=-60)
    figstyle.panel_letter(c, "c", dx=-60)
    figstyle.footnote(fig, f"Simulation: {N_UNITS} synthetic units with assumed degradation-law and plant dispersion, "
                      f"fixed {F_PROBE_HZ:g} Hz probe, {REPEATS} repeats per stage. Preregistered verdict {v} on its "
                      f"timing criterion: trigger-life SD {trigger_sd:.3f} life.")
    figstyle.save(fig, os.path.join(DATA, "studyA_fig_indicator_spread")); plt.close(fig)

    names = {"none": "none (all canonical)", "rupture": "rupture life", "mullins": "Mullins softening",
             "fatigue_law": "degradation law", "leak": "leak", "tau": "time constant τ", "stiffness": "stiffness",
             "thickness": "wall thickness", "temperature": "temperature"}
    rows = sorted(ablation, key=lambda k: -ablation[k]["ideal_sd_between_u090"])
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.8))
    for y, k in enumerate(rows):
        val = ablation[k]["ideal_sd_between_u090"]
        ax.plot([0, val], [y, y], color="#BDBDBD", lw=1.0, zorder=1)
        ax.plot(val, y, "o", color=C["pv"] if val > 1e-9 else C["fixed"], ms=5, zorder=2)
        ax.annotate(f"{val:.2g}" if val > 1e-9 else "≈ 0", (val, y), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=S["note"], color="#222222")
    ax.set_yticks(range(len(rows)), [names.get(k, k) for k in rows])
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(-0.0004, max(ablation[k]["ideal_sd_between_u090"] for k in rows) * 1.3)
    ax.set_xlabel("Noise-free SD between units at u = 0.9")
    ax.set_title("The degradation law drives the spread;\nplant parameters add nothing")
    figstyle.footnote(fig, f"Simulation: {N_UNITS} units, one dispersion axis switched on at a time, all others "
                      "canonical; values below 10⁻⁹ shown as ≈ 0.")
    figstyle.save(fig, os.path.join(DATA, "studyA_fig_ablation")); plt.close(fig)
    print(f"results + figures -> {DATA}/")


if __name__ == "__main__":
    main()
