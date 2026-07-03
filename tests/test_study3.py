"""Sanity checks for the Study 3 lead/recalibration frontier."""

import numpy as np

from scripts.run_study3 import LIFE, lead_frontier


def _err_matrix():
    """Synthetic err[i][j] matrix where fresh calibrations are always best."""
    fresh = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
    young_stale = np.array([0.01, 0.05, 0.12, 0.22, 0.34])
    err = np.zeros((len(LIFE), len(LIFE)))
    for i in range(len(LIFE)):
        for j in range(len(LIFE)):
            err[i, j] = fresh[i] if i == j else young_stale[max(i - j, 0)]
    return err


def test_lead_frontier_monotonic_with_threshold():
    test_ids = [101, 102]
    err = {aid: _err_matrix() for aid in test_ids}
    hn = {aid: np.array([1.0, 1.006, 1.014, 1.03, 1.06]) for aid in test_ids}
    acts = {101: {"rupture_cycles": 3000.0}, 102: {"rupture_cycles": 4000.0}}
    frontier = lead_frontier(test_ids, err, hn, acts, budget_mm=0.15,
                             tau_values=[0.005, 0.01, 0.05])
    points = frontier["points"]

    assert [p["tau"] for p in points] == [0.005, 0.01, 0.05]
    assert points[0]["trigger_life_median"] < points[1]["trigger_life_median"] < points[2]["trigger_life_median"]
    assert points[0]["recal_per_actuator"] >= points[1]["recal_per_actuator"] >= points[2]["recal_per_actuator"]
    assert points[0]["n_positive_lead"] >= points[1]["n_positive_lead"] >= points[2]["n_positive_lead"]
    assert all("status_counts" in p for p in points)
