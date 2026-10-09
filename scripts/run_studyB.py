"""Study B — identifiability map of the latent life coordinate from pressure-only features.

Preregistered in docs/specs/observability-program/studyB-identifiability.md. Writes data/sim/studyB/.
"""

from __future__ import annotations

import json
import os

import numpy as np
from scipy.linalg import block_diag

from pipeline.dispersion import SEED, sample_units
from pipeline.identifiability import (FEATURES, PARAMS, bound_u, fim, jacobian, noise_covariance,
                                      whitened_angles_deg)
from sim.fatigue import FatigueParams
from sim.plant import SLSParams
from scripts import figstyle

DATA = "data/sim/studyB"
U_GRID = [round(x, 2) for x in np.arange(0.1, 0.91, 0.1)]
U_BASE = 0.05
NOISE_SCALES = [0.5, 1.0, 4.0]
AMPS = [0.05, 0.1, 0.2]
N_REP = 24
SIGMA_TARGET, SIGMA_KILL = 0.10, 0.25


def theta_of(unit, u):
    fp, sls = unit.fatigue, unit.sls
    return np.array([u, sls.k1, sls.k2, sls.tau, fp.terminal_leak_multiplier,
                     fp.acceleration_onset_fraction, fp.fatigue_exponent])


def evaluate(unit, u, amp, noise, seed, J_base, sigma_base):
    th = theta_of(unit, u)
    J = jacobian(th, unit.fatigue, unit.sls, amp)
    sigma = noise_covariance(th, unit.fatigue, unit.sls, seed, N_REP, noise, amp)
    b1 = bound_u(J, sigma)
    Jb = J_base.copy(); Jb[:, 0] = 0.0                              # the young baseline does not move with u
    b2 = bound_u(np.vstack([Jb, J]), block_diag(sigma_base, sigma))
    F = fim(J, sigma)
    b3 = float(1.0 / np.sqrt(F[0, 0])) if F[0, 0] > 0 else float("inf")
    return {"u": u, "amp_frac": amp, "noise_scale": noise,
            "B1_sigma_u": b1[0], "B1_rank": b1[1], "B1_n_active": b1[2],
            "B2_sigma_u": b2[0], "B2_rank": b2[1], "B2_n_active": b2[2],
            "B3_sigma_u": b3,
            "aliasing_angle_deg": dict(zip(PARAMS[1:], whitened_angles_deg(J, sigma)))}


def main():
    units = [("canonical", type("U", (), {"fatigue": FatigueParams(), "sls": SLSParams()})())]
    units += [(f"dispersed_{i}", u) for i, u in enumerate(sample_units(5, SEED))]
    points = []
    for name, unit in units:
        for amp in AMPS:
            thb = theta_of(unit, U_BASE)
            J_base = jacobian(thb, unit.fatigue, unit.sls, amp)
            for noise in NOISE_SCALES:
                sigma_base = noise_covariance(thb, unit.fatigue, unit.sls, 7, N_REP, noise, amp)
                for u in U_GRID:
                    rec = evaluate(unit, u, amp, noise, 100 + int(1000 * u), J_base, sigma_base)
                    rec["unit"] = name
                    points.append(rec)
                    print(f"{name:12s} amp={amp:<5} noise={noise:<4} u={u:.1f} "
                          f"B1={rec['B1_sigma_u']:.3g} B2={rec['B2_sigma_u']:.3g} B3={rec['B3_sigma_u']:.3g}")

    def frac(pred, sel):
        rows = [p for p in points if sel(p)]
        return float(np.mean([pred(p) for p in rows])) if rows else float("nan")
    default = lambda p: p["noise_scale"] == 1.0 and p["amp_frac"] == 0.1
    per_unit_pass = {name: frac(lambda p: p["B2_sigma_u"] <= SIGMA_TARGET, lambda p, n=name: default(p) and p["unit"] == n)
                     for name, _ in units}
    kill_frac = frac(lambda p: p["B2_sigma_u"] > SIGMA_KILL, lambda p: True)
    dispersed_ok = sum(v >= 0.5 for k, v in per_unit_pass.items() if k != "canonical")
    if per_unit_pass["canonical"] >= 0.5 and dispersed_ok >= 3:
        v = "B-PASS"
    elif kill_frac >= 0.5:
        v = "B-KILL"
    else:
        v = "B-CONDITIONAL"
    out = {"preregistration": "docs/specs/observability-program/studyB-identifiability.md", "seed": SEED,
           "features": FEATURES, "parameters": PARAMS, "u_grid": U_GRID, "u_baseline": U_BASE,
           "noise_scales": NOISE_SCALES, "amplitude_fracs": AMPS, "n_rep": N_REP,
           "sigma_target": SIGMA_TARGET, "sigma_kill": SIGMA_KILL,
           "verdict": v, "per_unit_fraction_within_target_B2_default": per_unit_pass,
           "fraction_of_envelope_above_kill_B2": kill_frac, "points": points}
    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(os.path.join(DATA, "studyB_results.json"), "w"), indent=2,
              default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x)
    print(f"Study B verdict: {v} | per-unit fraction within target (B2, default): {per_unit_pass} | "
          f"envelope fraction above kill: {kill_frac:.2f}")

    plot(out)
    print(f"results + figure -> {DATA}/")



def plot(out):
    """Identifiability map from a saved or fresh result dict; infinite bounds are drawn as 'not identifiable'."""
    plt = figstyle.setup()
    if plt is None:  # pragma: no cover
        return
    import matplotlib.colors as mcolors
    C, S = figstyle.COLOR, figstyle.SIZE
    points, u_grid, amps = out["points"], out["u_grid"], out["amplitude_fracs"]
    target, kill, v = out["sigma_target"], out["sigma_kill"], out["verdict"]
    default = lambda p: p["noise_scale"] == 1.0 and p["amp_frac"] == 0.1
    fig, (a, b) = plt.subplots(1, 2, figsize=(figstyle.FULL, 2.8), gridspec_kw={"width_ratios": [1, 1.15],
                                                                                 "wspace": 0.45})
    top = 1.0
    designs = (("B1_sigma_u", "B1 single snapshot", C["supply"], "s"),
               ("B2_sigma_u", "B2 with young baseline", C["pv"], "o"),
               ("B3_sigma_u", "B3 nuisance known", C["ref"], "^"))
    for key, lab, col, mk in designs:
        ys = np.array([next(p[key] for p in points if default(p) and p["unit"] == "canonical" and p["u"] == u)
                       for u in u_grid], dtype=float)
        fin = np.isfinite(ys)
        if fin.any():
            a.plot(np.array(u_grid)[fin], ys[fin], mk + "-", color=col, ms=3.5)
        if (~fin).any():
            a.plot(np.array(u_grid)[~fin], np.full((~fin).sum(), top), mk, color=col, mfc="white", ms=4.5,
                   clip_on=False)
    a.set_yscale("log")
    a.set_ylim(1e-4, top)
    a.set_yticks([1e-4, 1e-3, 1e-2, 1e-1, 1], ["0.0001", "0.001", "0.01", "0.1", "∞"])
    a.yaxis.set_minor_formatter(plt.NullFormatter())
    for y, lab in ((target, f"target {target:g}"), (kill, f"kill {kill:g}")):
        a.axhline(y, ls="--" if y == target else ":", lw=0.8, color=C["ref"])
        a.text(u_grid[0], y * 1.12, lab, fontsize=S["note"], color=C["ref"], va="bottom")
    a.text(0.03, 0.04, "open marks: bound infinite", transform=a.transAxes, ha="left",
           va="bottom", fontsize=S["note"], color=C["muted"])
    a.text(u_grid[0], 0.035, "B2 with young baseline", fontsize=S["note"], color=figstyle.ink(C["pv"]), va="bottom")
    a.text(u_grid[0], 0.009, "B3 nuisance known", fontsize=S["note"], color=C["ref"], va="top")
    a.text(u_grid[-1], 0.55, "B1 single snapshot", fontsize=S["note"], color=figstyle.ink(C["supply"]),
           ha="right", va="top")
    a.set_xlabel("Normalized life u")
    a.set_ylabel("Cramér–Rao bound σ_u (life)")
    a.set_title("With a young baseline σ_u stays\nnear 0.02–0.03 until onset")
    a.margins(x=0.04)

    grid = np.array([[next(p["B2_sigma_u"] for p in points if p["unit"] == "canonical" and p["noise_scale"] == 1.0
                           and p["amp_frac"] == amp and p["u"] == u) for u in u_grid] for amp in amps], dtype=float)
    shown = np.where(np.isfinite(grid), grid, np.nan)
    norm = mcolors.LogNorm(vmin=np.nanmin(shown), vmax=np.nanmax(shown))
    im = b.imshow(shown, aspect="auto", origin="lower", cmap="cividis", norm=norm,
                  extent=[u_grid[0] - 0.05, u_grid[-1] + 0.05, -0.5, len(amps) - 0.5])
    for i, amp in enumerate(amps):
        for j, u in enumerate(u_grid):
            val = grid[i, j]
            if np.isfinite(val):
                light = norm(val) > 0.6
                b.text(u, i, f"{val * 100:.2g}", ha="center", va="center", fontsize=S["tick"],
                       color="#222222" if light else "white")
            else:
                b.add_patch(plt.Rectangle((u - 0.05, i - 0.5), 0.1, 1, facecolor="#F0F0F0", edgecolor="#BDBDBD",
                                          hatch="///", lw=0.4))
                b.text(u, i, "∞", ha="center", va="center", fontsize=S["note"], color="#222222")
    b.set_yticks(range(len(amps)), [f"{a_:g} V0" for a_ in amps])
    b.set_xticks(u_grid, [f"{u:.1f}" for u in u_grid])
    b.tick_params(length=0)
    for s in b.spines.values():
        s.set_visible(False)
    b.set_xlabel("Normalized life u")
    b.set_ylabel("Probe amplitude")
    b.set_title("Doubling the probe amplitude halves σ_u;\nafter onset no amplitude bounds it")
    cb = fig.colorbar(im, ax=b, fraction=0.05, pad=0.03)
    cticks = [t for t in (0.015, 0.02, 0.03, 0.04, 0.06) if norm.vmin <= t <= norm.vmax]
    cb.set_ticks(cticks, labels=[f"{t * 100:g}" for t in cticks])
    cb.ax.yaxis.set_minor_formatter(plt.NullFormatter())
    cb.set_label("B2 bound σ_u (10⁻² life)", fontsize=S["note"])
    cb.ax.tick_params(labelsize=S["tick"])
    figstyle.panel_letter(a, "a", dx=-40)
    figstyle.panel_letter(b, "b", dx=-46)
    figstyle.footnote(fig, f"Simulation: local Cramér–Rao bounds from pressure-only features of the canonical "
                      f"synthetic unit, {out['n_rep']} sensor repeats per point, noise ×1; panel a at 0.1 V0 "
                      f"amplitude; cells in b show σ_u × 100. Hatched ∞: bound infinite. Study B verdict {v} (preregistered rule).")
    figstyle.save(fig, os.path.join(DATA, "studyB_fig_identifiability_map")); plt.close(fig)

if __name__ == "__main__":
    import sys
    if "--replot" in sys.argv:                      # redraw from the saved result, no recomputation
        plot(json.load(open(os.path.join(DATA, "studyB_results.json"))))
        print("replotted from the saved result")
    else:
        main()
