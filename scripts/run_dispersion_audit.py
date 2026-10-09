"""Audit the generator's dispersion assumption — literature/gaps.md item 1.

Two questions, one raised by the literature and one a correction to how that item was written.

A. **Is there an implicit random failure threshold?** The item as filed said to "compute the implied
   rupture-life distribution from the dispersed degradation-law parameters and compare against the
   imposed Weibull", citing Bae, Kuo & Kvam 2007. On reading the generator that framing is not
   well-posed: rupture life here is *definitional*, not a threshold crossing. `fatigue_state` takes
   `rupture_cycles` as an input and expresses every multiplier in normalised life u = cycles/rupture,
   so there is no absolute failure threshold to invert. Bae/Kuo/Kvam applies to threshold-crossing
   models and this is not one.

   The real, checkable version: because rupture is imposed rather than derived, the *degradation state
   reached at rupture* is free to vary across units. If it does, the generator contains an implicit
   random failure threshold (Wang, Chen & Cai 2020), which is a modelling choice worth stating rather
   than an inconsistency.

B. **Does the transfer result survive lower dispersion?** Study A assumes rupture-life CV 0.30,
   citing Torzini 2024 as its order of magnitude, but Torzini measures CoV 3.9 % and 6.1 % and the
   highest measured value found anywhere is 17.5 %. Since R1 found transfer error tracks a unit's
   distance from the training median, an overstated CV would inflate that effect. This re-runs the
   Study C evaluation at several CVs and reports whether the verdict and the effect survive.

   None of the three CVs is "the realistic one". The published values are small cohorts of particular
   materials, geometries and loading protocols, and none of them measures this project's future
   apparatus; they anchor a *lower* end, they do not establish a universal lifetime CV. 0.30 stays an
   assumed stress case. The result worth having is the direction of travel across the sweep, not a
   verdict at any single CV.

Writes data/sim/dispersion_audit/. Changes no committed study output.
"""

from __future__ import annotations

import json
import os

import numpy as np

from pipeline.dispersion import RUPTURE_CV, SEED, sample_units
from scripts import figstyle
from scripts.run_studyC import (LAMBDAS, N_TRAIN, N_UNITS, PASS_RMSE, choose_lambda, evaluate,
                                ridge_fit, rmse, stack, unit_records)
from sim.fatigue import fatigue_state

DATA = "data/sim/dispersion_audit"
# two literature-anchored low values and Study A's assumed stress case; see the docstring on why none
# of them is "the realistic" dispersion for this project's apparatus
CV_GRID = [0.05, 0.15, RUPTURE_CV]
MEASURED = {"Torzini 2024 TPU": 0.039, "Torzini 2024 silicone": 0.061, "Du 2025 composite": 0.175}
N_STATE = 200                            # cohort size for the failure-state question (cheap, no simulation)


def state_at_rupture(n=N_STATE, cv=RUPTURE_CV):
    """Degradation state each unit has reached at u = 1, i.e. at its own rupture."""
    rows = []
    for i, unit in enumerate(sample_units(n, SEED, rupture_cv=cv)):
        fp = unit.fatigue
        s = fatigue_state(fp.rupture_cycles, 0.0, fp)
        rows.append({"unit": i, "rupture_cycles": fp.rupture_cycles,
                     "compliance_multiplier": s.compliance_multiplier,
                     "loss_multiplier": s.loss_multiplier,
                     "leak_multiplier": s.leak_multiplier,
                     "fatigue_total": s.fatigue_total})
    return rows


def spread(rows, key):
    v = np.array([r[key] for r in rows], float)
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)),
            "cv": float(v.std(ddof=1) / v.mean()) if v.mean() else None,
            "min": float(v.min()), "max": float(v.max()),
            "range_over_mean": float((v.max() - v.min()) / v.mean()) if v.mean() else None}


def transfer_at_cv(cv):
    """Re-run the Study C transfer evaluation on a cohort drawn with this rupture-life CV."""
    units = sample_units(N_UNITS, SEED, rupture_cv=cv)
    order = np.random.default_rng(SEED + 1).permutation(N_UNITS)
    train_idx, test_idx = sorted(order[:N_TRAIN].tolist()), sorted(order[N_TRAIN:].tolist())
    records = [unit_records(u, i) for i, u in enumerate(units)]
    train = [records[i] for i in train_idx]
    lam, _ = choose_lambda(train)
    X, y = stack([r for rows in train for r in rows])
    model = ridge_fit(X, y, lam)
    model["lam"] = lam
    median_rupture = float(np.median([units[i].fatigue.rupture_cycles for i in train_idx]))
    heldout = evaluate([units[i] for i in test_idx], [records[i] for i in test_idx], model, median_rupture)

    err = np.array([h["rmse"] for h in heldout])
    clk = np.array([h["rmse_clock"] for h in heldout])
    dev = np.array([abs(h["rupture_cycles"] - median_rupture) / median_rupture for h in heldout])
    n_within, n_beats = int((err <= PASS_RMSE).sum()), int((err < clk).sum())
    r_dev = float(np.corrcoef(err, dev)[0, 1]) if err.std() > 0 and dev.std() > 0 else None
    return {
        "rupture_cv": cv, "lambda_selected": lam, "median_training_rupture_cycles": median_rupture,
        "rupture_spread_heldout": {"min": float(min(h["rupture_cycles"] for h in heldout)),
                                   "max": float(max(h["rupture_cycles"] for h in heldout))},
        "mean_rmse": float(err.mean()), "mean_rmse_clock": float(clk.mean()),
        "n_within_target": n_within, "n_beats_clock": n_beats,
        "verdict": "C-PASS" if (n_within >= 8 and n_beats >= 8) else "C-FAIL",
        "error_vs_rupture_deviation": r_dev,
        "mean_abs_rupture_deviation": float(dev.mean()),
        "per_unit": [{"rupture_cycles": h["rupture_cycles"], "rmse": h["rmse"],
                      "rmse_clock": h["rmse_clock"], "deviation": float(d)} for h, d in zip(heldout, dev)],
    }


def main():
    print("A. degradation state reached at rupture (u = 1), %d units\n" % N_STATE)
    rows = state_at_rupture()
    state = {k: spread(rows, k) for k in ("compliance_multiplier", "loss_multiplier",
                                          "leak_multiplier", "fatigue_total")}
    for k, v in state.items():
        print(f"   {k:24s} mean {v['mean']:8.4f}  sd {v['sd']:8.4f}  CV {v['cv']:6.3f}  "
              f"range {v['min']:.4f}-{v['max']:.4f}")
    implicit = state["compliance_multiplier"]["cv"] > 1e-9
    print(f"\n   implicit random failure threshold: {implicit} "
          f"(the state at rupture is {'not ' if implicit else ''}constant across units)")

    print("\nB. transfer sensitivity to the assumed rupture-life CV")
    print(f"   published cohorts for reference: " + ", ".join(f"{k} {v:.3f}" for k, v in MEASURED.items())
          + "  (specific designs, not this project's apparatus)")
    transfer = []
    for cv in CV_GRID:
        t = transfer_at_cv(cv)
        transfer.append(t)
        print(f"   CV {cv:.2f}: {t['verdict']}  within {t['n_within_target']}/10  "
              f"beats clock {t['n_beats_clock']}/10  mean u-RMSE {t['mean_rmse']:.3f} "
              f"(clock {t['mean_rmse_clock']:.3f})  corr(error, deviation) "
              f"{t['error_vs_rupture_deviation']:+.3f}")

    baseline = next(t for t in transfer if t["rupture_cv"] == RUPTURE_CV)
    lower_cv = [t for t in transfer if t["rupture_cv"] < RUPTURE_CV]
    verdict_stable = all(t["verdict"] == baseline["verdict"] for t in lower_cv)
    effect_weakens = all((t["error_vs_rupture_deviation"] or 0) < (baseline["error_vs_rupture_deviation"] or 0)
                         for t in lower_cv)

    results = {
        "task": "literature/gaps.md item 1",
        "correction_to_the_filed_item": (
            "The item asked for the rupture-life distribution 'implied' by the dispersed degradation-law "
            "parameters, citing Bae, Kuo & Kvam 2007. That framing does not apply here: rupture life is an "
            "input to fatigue_state and every multiplier is expressed in normalised life, so the generator "
            "has no absolute failure threshold to invert. Bae/Kuo/Kvam concerns threshold-crossing models. "
            "The well-posed version, reported below, is whether the degradation state reached at rupture "
            "varies across units, i.e. whether the generator has an implicit random failure threshold."),
        "A_state_at_rupture": {"n_units": N_STATE, "spread": state,
                               "implicit_random_failure_threshold": bool(implicit),
                               "reading": ("rupture is imposed rather than derived, so the state at rupture "
                                           "is free to vary; the spread above is that variation")},
        "B_transfer_sensitivity": {
            "cv_grid": CV_GRID, "measured_reference_values": MEASURED,
            "study_a_assumption": RUPTURE_CV,
            "results": transfer,
            "verdict_stable_at_lower_cv": bool(verdict_stable),
            "distance_from_median_effect_weakens_at_lower_cv": bool(effect_weakens),
            "dispersion_interpretation": (
                "0.05 and 0.15 are anchored to published cohorts (Torzini 2024, Du 2025); 0.30 is Study A's "
                "assumed stress case. None is a measurement of this project's apparatus, and three small "
                "cohorts of particular materials and loading protocols do not establish a universal "
                "lifetime CV. Read the trend across the sweep, not a verdict at any one CV."),
        },
        "does_not_change": "no committed study output; Study A/B/C verdicts and artifacts are untouched",
    }
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "dispersion_audit.json")
    tmp = out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(results, fh, indent=2)
    os.replace(tmp, out)
    print(f"\n   verdict stable at the lower CVs: {verdict_stable} | "
          f"distance-from-median effect weakens: {effect_weakens}")
    plot(results)
    print(f"results + figure -> {DATA}/")


def plot(results):
    plt = figstyle.setup()
    if plt is None:  # pragma: no cover
        return
    C, S = figstyle.COLOR, figstyle.SIZE
    t = results["B_transfer_sensitivity"]["results"]
    refs = results["B_transfer_sensitivity"]["measured_reference_values"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(figstyle.FULL, 2.7), gridspec_kw={"wspace": 0.42})
    cvs = [x["rupture_cv"] for x in t]
    for ax in (a, b):
        for name, v in refs.items():
            ax.axvline(v, ls="-", lw=0.7, color="#C8C8C8", zorder=0)
            if ax is a:                                 # name the published cohorts once
                ax.text(v, 1.0, name.split(" ", 2)[-1], transform=ax.get_xaxis_transform(), rotation=90,
                        ha="right", va="top", fontsize=S["tick"], color=C["muted"])
        ax.set_xticks(cvs)
        ax.set_xlim(0, 0.33)
        ax.set_xlabel("Assumed rupture-life CV")
    est = [x["mean_rmse"] for x in t]
    clk = [x["mean_rmse_clock"] for x in t]
    a.plot(cvs, est, "o-", color=C["pv"])
    a.plot(cvs, clk, "s--", color=C["clock"])
    figstyle.end_label(a, cvs[-1], est[-1], "transferred\nestimator", C["pv"], dy=-8)
    figstyle.end_label(a, cvs[-1], clk[-1], "clock only", C["clock"], dy=4)
    a.axhline(PASS_RMSE, ls=":", color=C["ref"], lw=0.8)
    a.text(0.005, PASS_RMSE + 0.003, f"target {PASS_RMSE:.2f}", fontsize=S["note"], color=C["ref"], va="bottom")
    a.set_ylim(0, 0.14)
    a.set_ylabel("Mean held-out life-estimate\nRMSE (life)")
    a.set_title("The clock is as good or better until CV 0.30")
    within = [x["n_within_target"] for x in t]
    beats = [x["n_beats_clock"] for x in t]
    b.plot(cvs, within, "o-", color=C["always"])
    b.plot(cvs, beats, "s--", color=C["fixed"])
    figstyle.end_label(b, cvs[-1], within[-1], "within 0.10 life", C["always"], dy=-7)
    figstyle.end_label(b, cvs[-1], beats[-1], "beats the clock", C["fixed"], dy=7)
    b.axhline(8, ls=":", color=C["ref"], lw=0.8)
    b.text(0.005, 7.8, "rule: 8 of 10 on both", fontsize=S["note"], color=C["ref"], va="top")
    b.set_ylim(0, 10.5)
    b.set_yticks(range(0, 11, 2))
    b.set_ylabel("Held-out units (of 10)")
    passed = [w >= 8 and c >= 8 for w, c in zip(within, beats)]
    b.set_title("No dispersion level passes both counts" if not any(passed) else "Rule outcome by dispersion level")
    figstyle.panel_letter(a, "a", dx=-44)
    figstyle.panel_letter(b, "b", dx=-30)
    figstyle.footnote(fig, "Simulation: the Study C evaluation repeated on cohorts drawn at each assumed CV, 10 "
                      "held-out units each. Gray lines: coefficients of variation measured in published cohorts ("
                      + "; ".join(f"{k} {v:g}" for k, v in refs.items()) + ").")
    figstyle.save(fig, os.path.join(DATA, "dispersion_audit_fig"))
    plt.close(fig)


if __name__ == "__main__":
    import sys
    if "--replot" in sys.argv:
        plot(json.load(open(os.path.join(DATA, "dispersion_audit.json"))))
        print("replotted from the saved result")
    else:
        main()
