"""Phase E study — static ridge vs dynamic corrector, per-actuator life generalization.

Tests the Gate-0 prediction on the Phase D dataset (``data/sim/phaseD/dataset.npz``): a
*static* (memoryless) ridge map is blind to the fatigue-induced *dynamic* cross-talk under a
shared manifold, while a *dynamic* (lagged-input) corrector recovers it.

Proprioception features = [shared-manifold pressure, every chamber's valve command]
(all observable — you drive every valve); target = focal bending curvature.

Two experiments, both per-actuator to remove the cross-actuator geometry confound:
  A (drift):   a static ridge calibrated on each actuator's youngest stage -> curvature RMSE
               vs life, shared vs isolated. Isolates the compliance-scale drift.
  B (recover): static vs dynamic, each calibrated on YOUNG+MID life and tested on OLD life,
               per actuator -> RMSE by topology. The static-vs-dynamic GAP (controlling for
               the compliance drift) is the cross-talk signature: expect dynamic < static
               under shared, ~equal under isolated.

Writes ``study2_results.json`` and, if matplotlib is available, two figures under
``data/sim/phaseD/``. Run: python -m scripts.run_study2
"""

from __future__ import annotations

import json
import os

import numpy as np

from pipeline.correctors import RidgeCorrector, rmse
from scripts import figstyle
from scripts.phased import DATA, feats, load, pose_rmse

N_LAGS = 8
ALPHA = 1.0
YOUNG_MID = [0.10, 0.30, 0.50]
OLD = [0.70, 0.90]
LIFE_ALL = [0.10, 0.30, 0.50, 0.70, 0.90]


def idx_for(d, aid, lifes, topo=None):
    lifes = [round(x, 3) for x in lifes]
    mask = (d["actuator_id"] == aid) & np.isin(np.round(d["life_frac"], 3), lifes)
    if topo is not None:
        mask &= d["topology"] == topo
    return np.flatnonzero(mask)


def fit(d, idxs, n_lags):
    return RidgeCorrector(n_lags=n_lags, alpha=ALPHA).fit(
        [feats(d, i) for i in idxs], [d["true_kappa"][i] for i in idxs])


def k_rmse(model, d, idxs):
    return float(np.mean([rmse(model.predict(feats(d, i)), d["true_kappa"][i])
                          for i in idxs]))


def main():
    d, m = load()
    test_ids = m["split_by_actuator_identity"]["test_ids"]
    acts_by_id = {a["id"]: a for a in m["actuators"]}

    # --- Experiment B: per-actuator, static vs dynamic, young+mid -> old ---
    perB = {"isolated": {"static": [], "dynamic": [], "pos_static": [], "pos_dynamic": []},
            "shared": {"static": [], "dynamic": [], "pos_static": [], "pos_dynamic": []}}
    for aid in test_ids:
        tr = idx_for(d, aid, YOUNG_MID)
        static = fit(d, tr, 0)
        dynamic = fit(d, tr, N_LAGS)
        for topo, name in [(0, "isolated"), (1, "shared")]:
            te = idx_for(d, aid, OLD, topo)
            if te.size == 0:
                continue
            perB[name]["static"].append(k_rmse(static, d, te))
            perB[name]["dynamic"].append(k_rmse(dynamic, d, te))
            perB[name]["pos_static"].append(pose_rmse(static, d, te, acts_by_id[aid]))
            perB[name]["pos_dynamic"].append(pose_rmse(dynamic, d, te, acts_by_id[aid]))
    expB = {}
    for name, v in perB.items():
        expB[name] = {
            "static_kappa_rmse": float(np.mean(v["static"])),
            "dynamic_kappa_rmse": float(np.mean(v["dynamic"])),
            "static_position_rmse_m": float(np.mean(v["pos_static"])),
            "dynamic_position_rmse_m": float(np.mean(v["pos_dynamic"])),
        }
    for name in ("isolated", "shared"):
        s, dy = expB[name]["static_kappa_rmse"], expB[name]["dynamic_kappa_rmse"]
        expB[name]["dynamic_improvement"] = (s - dy) / s

    # --- Experiment A: per-actuator young-calibrated static, drift over life ---
    young_models = {aid: fit(d, idx_for(d, aid, [0.10]), 0) for aid in test_ids}
    expA = {"life_fractions": LIFE_ALL, "isolated": [], "shared": []}
    for life in LIFE_ALL:
        for topo, name in [(0, "isolated"), (1, "shared")]:
            vals = [k_rmse(young_models[aid], d, idx_for(d, aid, [life], topo))
                    for aid in test_ids if idx_for(d, aid, [life], topo).size]
            expA[name].append(float(np.mean(vals)))

    results = {"n_lags": N_LAGS, "alpha": ALPHA, "test_actuators": test_ids,
               "features": ["manifold_pressure", "all_chamber_commands"],
               "experimentB_static_vs_dynamic_young_to_old": expB,
               "experimentA_static_drift_over_life": expA}
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "study2_results.json"), "w") as fh:
        json.dump(results, fh, indent=2)

    print("=== Experiment B: per-actuator young+mid -> old, static vs dynamic ===")
    for name in ("isolated", "shared"):
        b = expB[name]
        print(f"  {name:9s} kappa RMSE  static {b['static_kappa_rmse']:.4f} | "
              f"dynamic {b['dynamic_kappa_rmse']:.4f}  "
              f"({100*b['dynamic_improvement']:+.1f}%)  | "
              f"pos {b['static_position_rmse_m']*1e3:.2f}->{b['dynamic_position_rmse_m']*1e3:.2f} mm")
    print("=== Experiment A: young-calibrated static ridge, curvature RMSE vs life ===")
    print("  life:    " + "  ".join(f"{lf:.2f}" for lf in LIFE_ALL))
    print("  shared:  " + "  ".join(f"{v:.3f}" for v in expA["shared"]))
    print("  isolated:" + "  ".join(f"{v:.3f}" for v in expA["isolated"]))

    plot(results)
    print(f"figures + results -> {DATA}/")



def plot(results):
    """Drift and corrector figures from a saved or fresh result dict."""
    plt = figstyle.setup()
    if plt is None:  # pragma: no cover
        print("(matplotlib unavailable, skipped figures)")
        return
    C, S = figstyle.COLOR, figstyle.SIZE
    expA = results["experimentA_static_drift_over_life"]
    expB = results["experimentB_static_vs_dynamic_young_to_old"]
    n = len(results["test_actuators"])
    life = expA["life_fractions"]

    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.6))
    for key, label, color, style in (("shared", "shared manifold", C["supply"], "o-"),
                                     ("isolated", "isolated supply", C["isolated"], "s--")):
        ax.plot(life, expA[key], style, color=color, ms=4)
    figstyle.end_label(ax, life[-1], expA["isolated"][-1], "isolated\nsupply", C["isolated"], dx=6)
    figstyle.end_label(ax, life[-1], expA["shared"][-1], "shared\nmanifold", C["supply"], dx=6, dy=-4)
    ax.set_xticks(life)
    ax.set_xlabel("Normalized life")
    ax.set_ylabel("Curvature RMSE (1/m)")
    ax.set_title("A young calibration stays close until\n0.7 of life, then its error jumps")
    ax.set_ylim(0, None)
    ax.margins(x=0.05)
    figstyle.footnote(fig, f"Simulation: Phase D cohort, {n} held-out actuators; static ridge calibrated on each "
                      "actuator at 0.10 of life; mean over actuators.")
    figstyle.save(fig, os.path.join(DATA, "study2_fig1_drift")); plt.close(fig)

    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.6))
    topo = ["isolated", "shared"]
    x = np.arange(len(topo)); w = 0.36
    for off, key, label, color in ((-w / 2, "static_kappa_rmse", "static ridge", C["fixed"]),
                                   (w / 2, "dynamic_kappa_rmse", f"dynamic, {results['n_lags']} lags", C["always"])):
        vals = [expB[t][key] for t in topo]
        ax.bar(x + off, vals, w * 0.95, color=color, label=label)
        for xi, v in zip(x + off, vals):
            ax.text(xi, v + 0.006, f"{v:.4f}", ha="center", va="bottom", fontsize=S["tick"], color="#222222")
    ax.set_xticks(x, ["isolated supply", "shared manifold"])
    ax.set_ylabel("Curvature RMSE (1/m)")
    gain = max(expB[t]["dynamic_improvement"] for t in topo)
    ax.set_title(f"Lagged inputs change the old-life error\nby under {max(gain * 100, 0.1):.1f} %"
                 if gain < 0.01 else "Static versus dynamic corrector at old life")
    ax.set_ylim(0, max(expB[t]["static_kappa_rmse"] for t in topo) * 1.3)
    ax.legend(loc="upper right")
    figstyle.footnote(fig, f"Simulation: Phase D cohort, {n} held-out actuators; correctors fitted on 0.1–0.5 of "
                      "life and tested at 0.7 and 0.9; mean over actuators. Improvement: "
                      + ", ".join(f"{t} {expB[t]['dynamic_improvement'] * 100:.3f} %" for t in topo) + ".")
    figstyle.save(fig, os.path.join(DATA, "study2_fig2_static_vs_dynamic")); plt.close(fig)

if __name__ == "__main__":
    import sys
    if "--replot" in sys.argv:                      # redraw from the saved result, no recomputation
        plot(json.load(open(os.path.join(DATA, "study2_results.json"))))
        print("replotted from the saved result")
    else:
        main()
