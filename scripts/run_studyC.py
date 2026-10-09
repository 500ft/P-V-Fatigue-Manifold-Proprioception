"""Study C — unseen-unit transfer of a pressure-only life estimator (preregistered; amended 2026-09-16).

Writes data/sim/studyC/. Design: docs/specs/observability-program/studyC-transfer.md.
"""

from __future__ import annotations

import json
import os

import numpy as np

from pipeline.dispersion import SEED, sample_units
from pipeline.identifiability import measured_features
from scripts import figstyle
from scripts.run_studyB import theta_of

DATA = "data/sim/studyC"
N_UNITS, N_TRAIN = 30, 20
PROBE_START, PROBE_STEP = 100.0, 250.0
LAMBDAS = (0.01, 0.1, 1.0)
N_BOOT = 2000
ADVERSARIAL_SEED, ADVERSARIAL_N = 20260918, 200
PASS_RMSE = 0.10


def probes(unit):
    """(cycles, u) at every scheduled probe before rupture."""
    n = np.arange(PROBE_START, unit.fatigue.rupture_cycles, PROBE_STEP)
    return n, n / unit.fatigue.rupture_cycles


def unit_records(unit, index):
    """Per-probe rows: inputs x (11), target u, cycles, onset flag."""
    cycles, us = probes(unit)
    seed = lambda k: int(np.random.SeedSequence([SEED, 7, index, k]).generate_state(1)[0])
    base = measured_features(theta_of(unit, us[0]), unit.fatigue, unit.sls, seed(0))
    rows, prev = [], None
    for k, (n, u) in enumerate(zip(cycles, us)):
        y = measured_features(theta_of(unit, u), unit.fatigue, unit.sls, seed(k + 1))
        lr = np.log(y / base)
        lag = lr if prev is None else prev
        rows.append({"x": np.concatenate([lr, lag, [n / 1000.0]]), "u": float(u), "cycles": float(n),
                     "post_onset": bool(u >= unit.fatigue.acceleration_onset_fraction)})
        prev = lr
    return rows


def ridge_fit(X, y, lam, scaler=None):
    """Ridge on standardised inputs; ``scaler`` (mu, sd) reuses another fit's standardisation."""
    mu, sd = scaler if scaler else (X.mean(axis=0), X.std(axis=0) + 1e-12)
    Z = (X - mu) / sd
    A = Z.T @ Z + lam * np.eye(Z.shape[1])
    w = np.linalg.solve(A, Z.T @ (y - y.mean()))
    return {"mu": mu, "sd": sd, "w": w, "b": float(y.mean())}


def ridge_predict(model, X):
    return ((X - model["mu"]) / model["sd"]) @ model["w"] + model["b"]


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def stack(records):
    return np.array([r["x"] for r in records]), np.array([r["u"] for r in records])


def choose_lambda(train):
    """Leave-one-unit-out on the training units."""
    scores = {}
    for lam in LAMBDAS:
        errs = []
        for i in range(len(train)):
            X, y = stack([r for j, rows in enumerate(train) if j != i for r in rows])
            Xi, yi = stack(train[i])
            errs.append(rmse(ridge_predict(ridge_fit(X, y, lam), Xi), yi))
        scores[lam] = float(np.mean(errs))
    return min(scores, key=scores.get), scores


def evaluate(units, records, model, median_rupture):
    out = []
    for unit, rows in zip(units, records):
        X, y = stack(rows)
        pred = ridge_predict(model, X)
        clock = np.clip(np.array([r["cycles"] for r in rows]) / median_rupture, 0.0, 1.0)
        own = (ridge_fit(X[:3], y[:3], model["lam"], scaler=(model["mu"], model["sd"]))   # same ridge, own labels
               if len(rows) >= 3 else None)
        post = np.array([r["post_onset"] for r in rows])
        out.append({
            "rupture_cycles": unit.fatigue.rupture_cycles, "onset": unit.fatigue.acceleration_onset_fraction,
            "n_probes": len(rows),
            "rmse": rmse(pred, y), "rmse_clock": rmse(clock, y),
            "rmse_per_unit_calibration": rmse(ridge_predict(own, X), y) if own else None,
            "rmse_pre_onset": rmse(pred[~post], y[~post]) if (~post).any() else None,
            "rmse_post_onset": rmse(pred[post], y[post]) if post.any() else None,
        })
    return out


def main():
    units = sample_units(N_UNITS, SEED)
    order = np.random.default_rng(SEED + 1).permutation(N_UNITS)
    train_idx, test_idx = sorted(order[:N_TRAIN].tolist()), sorted(order[N_TRAIN:].tolist())
    records = [unit_records(u, i) for i, u in enumerate(units)]
    train = [records[i] for i in train_idx]
    lam, lam_scores = choose_lambda(train)
    X, y = stack([r for rows in train for r in rows])
    model = ridge_fit(X, y, lam); model["lam"] = lam
    median_rupture = float(np.median([units[i].fatigue.rupture_cycles for i in train_idx]))

    heldout = evaluate([units[i] for i in test_idx], [records[i] for i in test_idx], model, median_rupture)
    r = np.array([h["rmse"] for h in heldout]); rc = np.array([h["rmse_clock"] for h in heldout])
    n_within = int((r <= PASS_RMSE).sum()); n_beats_clock = int((r < rc).sum())
    verdict = "C-PASS" if (n_within >= 8 and n_beats_clock >= 8) else "C-FAIL"
    rng = np.random.default_rng(SEED + 2)
    boot = np.array([r[rng.integers(0, len(r), len(r))].mean() for _ in range(N_BOOT)])
    loo = [float(np.delete(r, i).mean()) for i in range(len(r))]

    adv_units = sample_units(ADVERSARIAL_N, ADVERSARIAL_SEED)
    adv = evaluate(adv_units, [unit_records(u, 10_000 + i) for i, u in enumerate(adv_units)], model, median_rupture)
    worst = max(range(len(adv)), key=lambda i: adv[i]["rmse"])
    wu = adv_units[worst]

    results = {
        "preregistration": "docs/specs/observability-program/studyC-transfer.md (amended 2026-09-16)",
        "seed": SEED, "train_units": train_idx, "test_units": test_idx,
        "probe_schedule_cycles": {"start": PROBE_START, "step": PROBE_STEP},
        "lambda_selected": lam, "lambda_loo_scores": lam_scores, "median_training_rupture_cycles": median_rupture,
        "heldout": heldout,
        "heldout_mean_rmse": float(r.mean()), "heldout_mean_rmse_clock": float(rc.mean()),
        "cluster_bootstrap_ci": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        "leave_one_unit_out_range": [min(loo), max(loo)],
        "n_within_target": n_within, "n_beats_clock": n_beats_clock, "verdict": verdict,
        "adversarial": {"n_units": ADVERSARIAL_N, "seed": ADVERSARIAL_SEED, "worst_rmse": adv[worst]["rmse"],
                        "worst_rmse_clock": adv[worst]["rmse_clock"], "fraction_within_target": float(np.mean([a["rmse"] <= PASS_RMSE for a in adv])),
                        "worst_unit": {"rupture_cycles": wu.fatigue.rupture_cycles, "onset": wu.fatigue.acceleration_onset_fraction,
                                       "fatigue_exponent": wu.fatigue.fatigue_exponent, "terminal_leak_multiplier": wu.fatigue.terminal_leak_multiplier,
                                       "mullins_amplitude": wu.fatigue.mullins_amplitude, "k1": wu.sls.k1, "k2": wu.sls.k2, "tau": wu.sls.tau,
                                       "temperature_c": wu.temperature_c, "thickness_ratio": wu.thickness_ratio}},
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(results, open(os.path.join(DATA, "studyC_results.json"), "w"), indent=2)
    print(f"Study C verdict: {verdict} | held-out u-RMSE mean {r.mean():.3f} (clock {rc.mean():.3f}); "
          f"{n_within}/10 within {PASS_RMSE}, {n_beats_clock}/10 beat the clock; lambda={lam}")
    print(f"  pre-onset mean {np.nanmean([h['rmse_pre_onset'] or np.nan for h in heldout]):.3f} | "
          f"post-onset mean {np.nanmean([h['rmse_post_onset'] or np.nan for h in heldout]):.3f} | "
          f"per-unit calibration mean {np.mean([h['rmse_per_unit_calibration'] for h in heldout]):.3f}")
    print(f"  adversarial worst RMSE {adv[worst]['rmse']:.3f} (clock {adv[worst]['rmse_clock']:.3f}); "
          f"{results['adversarial']['fraction_within_target']:.2f} of 200 within target")

    plot(results)
    print(f"results + figure -> {DATA}/")



def plot(results):
    """Per-unit transfer figure from a saved or fresh result dict."""
    plt = figstyle.setup()
    if plt is None:  # pragma: no cover
        return
    C, S = figstyle.COLOR, figstyle.SIZE
    heldout, test_idx = results["heldout"], results["test_units"]
    r = np.array([h["rmse"] for h in heldout]); rc = np.array([h["rmse_clock"] for h in heldout])
    n = len(heldout)
    fig, ax = plt.subplots(figsize=(figstyle.WIDE, 2.6))
    ids = np.arange(n)
    for i in ids:
        ax.plot([i, i], [r[i], rc[i]], color="#BDBDBD", lw=1.2, zorder=1)
    ax.plot(ids, rc, "s", color=C["clock"], ms=5, zorder=2)
    ax.plot(ids, r, "o", color=C["pv"], ms=5.5, zorder=3)
    ax.axhline(PASS_RMSE, ls="--", color=C["ref"], lw=0.8)
    ax.text(-0.5, PASS_RMSE + 0.006, f"target {PASS_RMSE:.2f} life", ha="left", va="bottom",
            fontsize=S["note"], color=C["ref"])
    j = int(np.argmax(rc))
    figstyle.end_label(ax, j, rc[j], "clock only", C["clock"], dx=7)
    figstyle.end_label(ax, j, r[j], "pressure features + clock\n(transferred)", C["pv"], dx=7)
    ax.set_xticks(ids, [str(i) for i in test_idx])
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(0, max(rc.max(), r.max()) * 1.12)
    ax.set_xlabel("Held-out unit")
    ax.set_ylabel("Life-estimate RMSE (life)")
    ax.set_title(f"The transferred estimator meets the target on {results['n_within_target']} of {n} units\n"
                 f"and beats the clock on {results['n_beats_clock']}")
    ax.text(1.0, 0.98, "lower is better", transform=ax.transAxes, ha="right", va="top", fontsize=S["note"],
            color=C["muted"])
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    figstyle.footnote(fig, f"Simulation: one ridge estimator trained on {len(results['train_units'])} dispersed "
                      f"synthetic units, applied unchanged to {n} unseen units. Verdict {results['verdict']}: the "
                      "preregistered rule needs 8 of 10 on both counts.")
    figstyle.save(fig, os.path.join(DATA, "studyC_fig_transfer")); plt.close(fig)

if __name__ == "__main__":
    import sys
    if "--replot" in sys.argv:                      # redraw from the saved result, no recomputation
        plot(json.load(open(os.path.join(DATA, "studyC_results.json"))))
        print("replotted from the saved result")
    else:
        main()
