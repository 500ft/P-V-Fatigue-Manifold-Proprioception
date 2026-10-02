"""Audit of Study 3 at matched recalibration cost (2026-10-02).

Study 3 compared the P-V trigger with a cycle-count clock whose period was chosen on train
actuators as the longest period within the error budget. That rule picked T = 2700, which
recalibrates less often than the trigger, so the comparison was not at matched cost. This
script reruns the comparison with the clock at every grid period and records:

  * which clock periods give exactly the trigger's recalibration schedule on every actuator;
  * held-out and train error / recalibration count for the trigger, the matched clock and the
    clock Study 3 reported;
  * how far the normalized loop-area health signal differs between actuators, and from the
    normalized compliance multiplier that drives the pose drift.

It reuses Study 3's functions unchanged and needs the regenerated dataset
(``python -m scripts.phaseD_dataset``). Writes ``matched_clock_audit.json`` next to it.
Run: python -m scripts.audit_matched_clock
"""

from __future__ import annotations

import json
import os

import numpy as np

from scripts.phased import DATA, load
from scripts.run_study3 import (LIFE, PERIOD_GRID, cycle_schedule, policy_metrics, prepare,
                                recalibration_schedule, scheduled_metrics, select_thresholds)
from sim.fatigue import FatigueParams, fatigue_state


def mean_metrics(ids, fn):
    pairs = [fn(a) for a in ids]
    return {"error_mm": float(np.mean([e for e, _ in pairs])),
            "recalibrations": float(np.mean([r for _, r in pairs]))}


def main():
    d, m = load()
    train_ids, test_ids, acts, err, hn, cyc = prepare(d, m)
    sel = select_thresholds(train_ids, err, hn, cyc)
    tau, period_star = sel["tau_star"], sel["period_star"]
    ids = train_ids + test_ids

    trigger = {a: list(recalibration_schedule(hn[a], "triggered", tau=tau)) for a in ids}
    matched = [float(p) for p in PERIOD_GRID
               if all(list(cycle_schedule(cyc[a], p)) == trigger[a] for a in ids)]

    def policies(group):
        out = {"trigger": mean_metrics(group, lambda a: policy_metrics(err[a], hn[a], "triggered", tau))}
        for p in sorted({*matched[:1], period_star}):
            out[f"clock_{int(p)}"] = mean_metrics(group, lambda a, p=p: scheduled_metrics(err[a], cyc[a], p))
        return out

    health = np.array([hn[a] for a in ids])
    compliance = np.array([[fatigue_state(lf * acts[a]["rupture_cycles"], 0.0,
                                          FatigueParams(rupture_cycles=float(acts[a]["rupture_cycles"])))
                            .compliance_multiplier for lf in LIFE] for a in ids])
    compliance /= compliance[:, :1]

    out = {
        "tau_star": float(tau), "period_star_reported": float(period_star),
        "budget_mm": float(sel["budget_mm"]),
        "clock_periods_matching_trigger_schedule_on_all_actuators": matched,
        "heldout": policies(test_ids), "train": policies(train_ids),
        "health_max_spread_across_actuators": float(np.ptp(health, axis=0).max()),
        "health_vs_compliance_max_abs_diff": float(np.abs(health - compliance).max()),
        "life_fractions": LIFE, "n_actuators": len(ids),
    }
    with open(os.path.join(DATA, "matched_clock_audit.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
