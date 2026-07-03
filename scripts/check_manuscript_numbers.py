#!/usr/bin/env python3
"""Assert load-bearing manuscript numbers against committed study JSONs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "docs" / "preprint_v1.md"
STUDY3 = ROOT / "data" / "sim" / "phaseD" / "study3_results.json"
STUDY4 = ROOT / "data" / "sim" / "phaseD" / "study4_results.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(text: str, snippet: str):
    normalized_text = " ".join(text.split())
    normalized_snippet = " ".join(snippet.split())
    normalized_text = normalized_text.replace("*", "")
    normalized_snippet = normalized_snippet.replace("*", "")
    if normalized_snippet not in normalized_text:
        raise AssertionError(f"missing manuscript snippet: {snippet!r}")


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def main():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    s3 = load_json(STUDY3)
    s4 = load_json(STUDY4)

    corr = s3["leading_indicator_corr"]
    require(text, f"Pearson *r* = {corr['r']:.3f}, 95% CI [{corr['ci_low']:.3f}, {corr['ci_high']:.3f}]")

    per = s3["per_actuator_r"]
    require(text, f"per-actuator *r* median {per['median']:.3f}, range [{per['min']:.4f}, {per['max']:.4f}]")

    lead = s3["lead_time_heldout"]
    require(text, f"life {lead['median_trigger_life']:.2f}")
    require(text, f"median {lead['median_budget_violation_life']:.2f}, range "
                  f"{lead['min_budget_violation_life']:.2f}-{lead['max_budget_violation_life']:.2f}")
    require(text, f"median lead = {lead['median_lead_life']:.3f} normalized life")
    require(text, f"range [{lead['min_lead_life']:.3f}, {lead['max_lead_life']:.3f}]")
    require(text, f"{lead['status_counts']['nonpositive_lead']}/6 held-out")
    require(text, "no positive temporal lead")
    require(text, f"{round(lead['min_lead_cycles']):,} to {round(lead['max_lead_cycles']):,} cycles")

    policies = s3["policies_on_heldout"]
    budget = s3["accuracy_budget_mm"]
    tau = s3["tau_selected"]
    period = s3["period_selected_cycles"]
    require(text, f"{budget:.3f} mm accuracy budget")
    require(text, f"τ\\*={tau:.2f}")
    require(text, f"*T*\\* = {period:,.0f} cycles")
    for name in ("fixed", "scheduled", "triggered", "always"):
        pol = policies[name]
        require(text, f"{pol['mean_pose_rmse_mm']:.2f} mm")
        recal = pol["recal_per_actuator"]
        recal_str = f"{recal:.1f}".rstrip("0").rstrip(".")
        require(text, f"| {recal_str} |")
    savings = 1.0 - policies["triggered"]["recal_per_actuator"] / policies["always"]["recal_per_actuator"]
    require(text, f"{savings:.0%} fewer recalibrations")

    require(text, pct(s4["default_coupling"]))
    rs = s4["softness_multiplier_at_threshold"]["R_s"]
    require(text, f"≈{rs['0.10']:.1f}×")
    require(text, f"≈{rs['0.20']:.1f}×")
    cm_vals = s4["coupling_vs_multiplier"]["C_m"]
    require(text, f"{100 * min(cm_vals):.1f}–{100 * max(cm_vals):.1f}%")

    print("manuscript numbers match study JSONs")


if __name__ == "__main__":
    main()
