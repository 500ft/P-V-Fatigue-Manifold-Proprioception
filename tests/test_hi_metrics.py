"""Ground-truth fixtures for Phase C health-indicator metrics."""

import numpy as np

from pipeline.hi_metrics import monotonicity, prognosability, trendability


def test_clean_monotone_trajectory_has_unit_monotonicity():
    assert monotonicity(np.linspace(0, 1, 21)) == 1.0


def test_recovery_dip_reduces_monotonicity():
    clean = np.linspace(0, 1, 21)
    dipped = clean.copy()
    dipped[8:13] -= np.array([0.0, 0.25, 0.45, 0.25, 0.0])
    assert monotonicity(dipped) < monotonicity(clean)


def test_self_similar_curves_have_unit_trendability():
    u = np.linspace(0, 1, 101)
    curves = np.vstack([u + u**2, 2 * (u + u**2), 0.5 * (u + u**2)])
    assert np.isclose(trendability(curves), 1.0)


def test_genuinely_dissimilar_shape_lowers_trendability():
    u = np.linspace(0, 1, 101)
    normal = 0.08 * (u + u**2)  # 0.16 terminal range, matching the canonical scale
    corrupted = normal - 0.06 * np.exp(-0.5 * ((u - 0.55) / 0.08) ** 2)
    value = trendability(np.vstack([normal, normal, corrupted]))
    expected = abs(np.corrcoef(normal, corrupted)[0, 1])
    assert np.isclose(value, expected)
    assert value < 0.95


def test_prognosability_matches_direct_formula_and_boundary():
    starts = np.zeros(4)
    ends = np.array([0.8, 0.9, 1.1, 1.2])
    result = prognosability(starts, ends)
    expected = np.exp(-np.std(ends) / np.mean(np.abs(ends - starts)))
    assert result.status == "ok"
    assert np.isclose(result.value, expected)

    boundary = prognosability(starts, np.ones(4))
    assert boundary.status == "ok"
    assert boundary.value == 1.0


def test_prognosability_is_explicitly_undefined_for_null_lives():
    result = prognosability(np.ones(4), np.ones(4))
    assert result.status == "undefined_no_degradation"
    assert np.isnan(result.value)
