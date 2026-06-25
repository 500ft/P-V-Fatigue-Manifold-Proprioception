"""Phase F study — P-V-triggered recalibration vs fixed vs always-on.

The Phase E headline: pressure-only proprioception is dominated by the fatigue compliance-scale
drift (a young calibration's pose error grows ~100x over life; ``scripts/run_study2.py``). The
operational question is *when to recalibrate*. The thesis: the observable P-V loop area
(``pipeline.coupling``) is a leading indicator of that drift, so a P-V-health-triggered
recalibration holds accuracy near an always-on policy at far fewer recalibrations.

Three policies, each starting from one calibration at the youngest life stage:
  * fixed       — never recalibrate.
  * always      — recalibrate at every life stage.
  * triggered   — recalibrate when fractional P-V loop-area growth since the last calibration
                  exceeds tau. **tau is selected on TRAIN actuators only**, then applied to the
                  held-out TEST actuators.

Honesty rule (non-negotiable): report estimation error **and** recalibration count together, so
a "savings" cannot hide degraded accuracy. The estimator is the static ridge (Phase E showed
the dynamic corrector adds nothing).

Writes ``study3_results.json`` and two figures under ``data/sim/phaseD/``.
Run: python -m scripts.run_study3
"""

from __future__ import annotations

import json
import os

import numpy as np

from pipeline.correctors import RidgeCorrector, rmse
from pipeline.coupling import (
    apply_schedule,
    bootstrap_correlation,
    health_trajectory,
    recalibration_schedule,
)
from sim.kinematics import pcc_transform
from sim.plant import SLSParams

DATA = "data/sim/phaseD"
LIFE = [0.10, 0.30, 0.50, 0.70, 0.90]
ALPHA = 1.0
CAL_REPS = {0, 1, 2}        # calibration split
EVAL_REPS = {3, 4}          # evaluation split
TAU_GRID = np.round(np.linspace(0.0, 1.0, 21), 3)   # fractional loop-area growth thresholds
# Operational accuracy budget: tolerate this fraction of the way from the best-achievable
# (always-on) pose error toward the never-recalibrate (fixed) error. Selected on TRAIN
# actuators, then the triggering threshold is applied unchanged to held-out TEST actuators.
BUDGET_FRAC = 0.5


def load():
    d = dict(np.load(os.path.join(DATA, "dataset.npz")))
    m = json.load(open(os.path.join(DATA, "manifest.json")))
    return d, m


def feats(d, i):
    return np.concatenate([d["meas_manifold_pressure"][i][:, None], d["cmd_all"][i]], axis=-1)


def idxs(d, aid, life, reps):
    mask = (d["actuator_id"] == aid) & np.isclose(d["life_frac"], life)
    mask &= np.isin(d["rep"], list(reps))
    return np.flatnonzero(mask)


def calibrate(d, aid, life):
    ix = idxs(d, aid, life, CAL_REPS)
    return RidgeCorrector(n_lags=0, alpha=ALPHA).fit(
        [feats(d, i) for i in ix], [d["true_kappa"][i] for i in ix])


def pose_rmse(model, d, aid, life, act):
    ix = idxs(d, aid, life, EVAL_REPS)
    errs = []
    for i in ix:
        kp = np.clip(model.predict(feats(d, i)), 0.0, None)
        pred = np.array([pcc_transform(float(k), act["plane_azimuth_rad"], act["length_m"])[:3, 3]
                         for k in kp])
        errs.append(rmse(pred, d["true_position"][i]))
    return float(np.mean(errs))


def error_matrix(d, aid, act):
    """err[i][j] = pose RMSE at life i using the calibration fitted at life j (mm)."""
    models = [calibrate(d, aid, lf) for lf in LIFE]
    n = len(LIFE)
    err = [[pose_rmse(models[j], d, aid, LIFE[i], act) * 1e3 for j in range(n)]
           for i in range(n)]
    return np.asarray(err)


def realized(err, flags):
    fresh = [err[i][i] for i in range(len(flags))]
    stale = [[err[i][j] for j in range(len(flags))] for i in range(len(flags))]
    return apply_schedule(flags, fresh, stale)


def policy_metrics(err, hn, policy, tau=None):
    flags = recalibration_schedule(hn, policy, tau=tau)
    realized_err, n_recal = realized(err, flags)
    return float(np.mean(realized_err)), n_recal, realized_err


def main():
    d, m = load()
    train_ids = m["split_by_actuator_identity"]["train_ids"]
    test_ids = m["split_by_actuator_identity"]["test_ids"]
    acts = {a["id"]: a for a in m["actuators"]}

    # per-actuator error matrices + normalized health trajectories
    err = {}
    hn = {}
    for aid in train_ids + test_ids:
        a = acts[aid]
        err[aid] = error_matrix(d, aid, a)
        h = health_trajectory(SLSParams(k1=a["k1"], k2=a["k2"], tau=a["tau"]),
                              a["rupture_cycles"], LIFE)
        hn[aid] = h / h[0]                         # fractional growth, starts at 1.0

    # --- threshold selection on TRAIN actuators only, against an accuracy budget ---
    train_always = np.mean([policy_metrics(err[a], hn[a], "always")[0] for a in train_ids])
    train_fixed = np.mean([policy_metrics(err[a], hn[a], "fixed")[0] for a in train_ids])
    budget_mm = train_always + BUDGET_FRAC * (train_fixed - train_always)
    sweep = []
    for tau in TAU_GRID:
        em = [policy_metrics(err[a], hn[a], "triggered", tau) for a in train_ids]
        sweep.append({"tau": float(tau),
                      "train_error_mm": float(np.mean([x[0] for x in em])),
                      "train_recal": float(np.mean([x[1] for x in em]))})
    ok = [s for s in sweep if s["train_error_mm"] <= budget_mm]
    selected = max(ok, key=lambda s: s["tau"]) if ok else sweep[0]   # fewest recals within budget
    tau_star = selected["tau"]

    # --- apply to held-out TEST actuators ---
    def agg(policy, tau=None):
        es, rs = [], []
        for a in test_ids:
            e, r, _ = policy_metrics(err[a], hn[a], policy, tau)
            es.append(e); rs.append(r)
        return {"mean_pose_rmse_mm": float(np.mean(es)),
                "total_recalibrations": int(np.sum(rs)),
                "recal_per_actuator": float(np.mean(rs))}

    results = {
        "estimator": "static ridge (Phase E: dynamic adds nothing)",
        "life_fractions": LIFE, "tau_selected": tau_star,
        "accuracy_budget_mm": float(budget_mm), "budget_frac": BUDGET_FRAC,
        "train_fixed_error_mm": float(train_fixed), "train_always_error_mm": float(train_always),
        "train_actuators": train_ids, "test_actuators": test_ids,
        "policies_on_heldout": {
            "fixed": agg("fixed"),
            "triggered": agg("triggered", tau_star),
            "always": agg("always"),
        },
        "threshold_sweep_train": sweep,
    }

    # --- leading-indicator: P-V health drift vs fixed-calibration pose error (held-out) ---
    hx, ey = [], []
    for a in test_ids:
        for i in range(len(LIFE)):
            hx.append(hn[a][i] - 1.0)           # fractional loop-area growth from young
            ey.append(err[a][i][0])             # fixed (young) calibration error at life i
    results["leading_indicator_corr"] = bootstrap_correlation(np.array(hx), np.array(ey),
                                                              n_boot=2000, seed=7)

    os.makedirs(DATA, exist_ok=True)
    json.dump(results, open(os.path.join(DATA, "study3_results.json"), "w"), indent=2)

    pol = results["policies_on_heldout"]
    print(f"accuracy budget = {budget_mm:.3f} mm (train fixed {train_fixed:.2f} / always {train_always:.2f})")
    print(f"selected tau* = {tau_star} (fractional P-V loop-area growth; train-selected)")
    print("=== held-out actuators: error vs recalibration count ===")
    for name in ("fixed", "triggered", "always"):
        p = pol[name]
        print(f"  {name:9s} pose RMSE {p['mean_pose_rmse_mm']:.2f} mm | "
              f"recal/actuator {p['recal_per_actuator']:.1f} | total {p['total_recalibrations']}")
    lc = results["leading_indicator_corr"]
    print(f"leading indicator (P-V growth vs fixed-cal error): "
          f"r={lc['r']:.3f} [{lc['ci_low']:.3f}, {lc['ci_high']:.3f}]")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from scripts import figstyle
        figstyle.apply()
    except Exception as exc:  # pragma: no cover
        print(f"(matplotlib unavailable, skipped figures: {exc})")
        return

    # Fig 3: leading indicator — health drift & fixed-cal error over life (mean over test acts)
    mean_h = np.mean([hn[a] for a in test_ids], axis=0)
    mean_fixed = np.mean([[err[a][i][0] for i in range(len(LIFE))] for a in test_ids], axis=0)
    fig, ax1 = plt.subplots()
    ax1.plot(LIFE, mean_h, "o-", color="#0072B2", label="P-V loop-area growth")
    ax1.set_xlabel("normalized life"); ax1.set_ylabel("P-V loop area (×young)", color="#0072B2")
    ax1.tick_params(axis="y", labelcolor="#0072B2")
    ax2 = ax1.twinx()
    ax2.plot(LIFE, mean_fixed, "s--", color="#D55E00", label="fixed-cal pose error")
    ax2.set_ylabel("fixed-cal pose RMSE [mm]", color="#D55E00")
    ax2.tick_params(axis="y", labelcolor="#D55E00"); ax2.grid(False)
    plt.title(f"P-V loop area leads pose degradation (r = {results['leading_indicator_corr']['r']:.2f})")
    fig.tight_layout(); figstyle.save(fig, os.path.join(DATA, "study3_fig3_leading_indicator"))
    plt.close(fig)

    # Fig 4: the trade-off — pose error vs recalibration count per policy
    plt.figure()
    for name, mk in [("fixed", "o"), ("triggered", "D"), ("always", "s")]:
        p = pol[name]
        plt.scatter(p["recal_per_actuator"], p["mean_pose_rmse_mm"], s=110, marker=mk, label=name)
    plt.xlabel("recalibrations per actuator (over life)")
    plt.ylabel("pose RMSE [mm]")
    plt.title("Recalibration trade-off (held-out actuators)")
    plt.legend(); plt.tight_layout()
    figstyle.save(plt.gcf(), os.path.join(DATA, "study3_fig4_recal_tradeoff"))
    plt.close()
    print(f"figures + results -> {DATA}/")


if __name__ == "__main__":
    main()
