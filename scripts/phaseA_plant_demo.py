#!/usr/bin/env python3
"""
Phase A demo + validation for sim/plant.py.

Produces:
  data/sim/phaseA/fig_pv_loops.png            P-V loops below/at/above the loss peak
  data/sim/phaseA/fig_loop_area_vs_freq.png   numerical vs analytical loop area
  data/sim/phaseA/fig_gate0_consistency.png   SLS network cross-talk vs Gate 0
  data/sim/phaseA/phaseA_results.json

Validation checks (printed):
  1. Numerical loop area matches the closed-form SLS dissipation across frequency.
  2. Loop area peaks at f = 1/(2*pi*tau) and -> 0 at both frequency extremes.
  3. The linearized SLS network with a CONSTANT compliance = 1/k1 reproduces the Gate 0
     cross-talk model to machine precision (regression tie-back to the validated core).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
from sim.plant import (SLSParams, NetworkParams, pv_loop,
                       sls_loss_energy_analytic, linear_network_crosstalk)
from scripts import gate0_lumped_rc as g0  # Gate 0 model for the consistency check

from scripts import figstyle

plt = figstyle.setup(style=False)


def main():
    outdir = REPO / "data" / "sim" / "phaseA"
    outdir.mkdir(parents=True, exist_ok=True)
    sls = SLSParams()
    net = NetworkParams()
    A = 2.0e-6  # 2 mL volume amplitude
    fpk = sls.f_loss_peak

    # ---- (1)+(2) loop area vs frequency: numerical vs analytic ----
    freqs = np.logspace(-1.5, 1.5, 25)
    area_num, area_ana = [], []
    for f in freqs:
        lp = pv_loop(f, A, sls)
        area_num.append(lp["area"])
        area_ana.append(sls_loss_energy_analytic(A, 2 * np.pi * f, sls))
    area_num = np.array(area_num); area_ana = np.array(area_ana)
    area_rel_err = np.abs(area_num - area_ana) / np.maximum(area_ana, 1e-30)
    f_peak_num = freqs[int(np.argmax(area_num))]

    # ---- (3) Gate 0 consistency: constant-compliance SLS network == Gate 0 ----
    test_freqs = np.logspace(-2, 2, 60)
    omegas = 2 * np.pi * test_freqs
    ct_const, ct_g0, ct_sls = [], [], []
    for w in omegas:
        ct_const.append(linear_network_crosstalk(w, net, sls,
                                                 compliance_override=sls.C_relaxed))
        A0, B0, C0o, D0, *_ = g0.build_state_space(g0.Params(C0=sls.C_relaxed), 1.0)
        ct_g0.append(g0.crosstalk_metric(g0.transfer_matrix(A0, B0, C0o, D0, w)))
        ct_sls.append(linear_network_crosstalk(w, net, sls))   # full SLS complex compliance
    ct_const = np.array(ct_const); ct_g0 = np.array(ct_g0); ct_sls = np.array(ct_sls)
    g0_max_err = float(np.max(np.abs(ct_const - ct_g0)))

    # ---- verdict ----
    pass_area = bool(float(np.median(area_rel_err)) < 0.02)
    pass_peak = bool(abs(np.log2(f_peak_num / fpk)) < 0.5)   # within a half-octave
    pass_g0 = bool(g0_max_err < 1e-9)
    verdict = "PASS" if (pass_area and pass_peak and pass_g0) else "CHECK"

    results = {
        "sls": {"k1": sls.k1, "k2": sls.k2, "tau": sls.tau,
                "C_relaxed": sls.C_relaxed, "C_instant": sls.C_instant,
                "f_loss_peak_hz": fpk},
        "loop_area": {"median_rel_err_vs_analytic": float(np.median(area_rel_err)),
                      "max_rel_err": float(np.max(area_rel_err)),
                      "f_peak_numeric_hz": float(f_peak_num),
                      "f_peak_analytic_hz": float(fpk)},
        "gate0_consistency": {"max_abs_crosstalk_err": g0_max_err,
                              "note": "constant-compliance(1/k1) SLS network vs Gate 0 model"},
        "checks": {"area_matches_analytic": pass_area, "peak_at_1over2pitau": pass_peak,
                   "reduces_to_gate0": pass_g0},
        "verdict": verdict,
    }
    (outdir / "phaseA_results.json").write_text(json.dumps(results, indent=2))

    if plt is not None:
        _plots(outdir, sls, A, fpk, freqs, area_num, area_ana,
               test_freqs, ct_const, ct_g0, ct_sls)

    print("=" * 68)
    print("PHASE A — viscoelastic (SLS) plant + P-V loops")
    print("=" * 68)
    print(f"SLS loss peak f = 1/(2*pi*tau)      : {fpk:.2f} Hz "
          f"(numeric peak {f_peak_num:.2f} Hz)")
    print(f"Loop area vs analytic, median err   : {np.median(area_rel_err)*100:.2f}%  "
          f"(max {np.max(area_rel_err)*100:.2f}%)")
    print(f"SLS-network(const C) vs Gate 0, err : {g0_max_err:.2e}  "
          f"(== reduces to validated core)")
    print(f"Relaxed/instant compliance          : {sls.C_relaxed:.2e} / {sls.C_instant:.2e} m^3/Pa")
    print("-" * 68)
    print(f"VERDICT: {verdict}  "
          f"[area:{pass_area} peak:{pass_peak} gate0:{pass_g0}]")
    print(f"Wrote {outdir}/phaseA_results.json + figures")


def _plots(outdir, sls, A, fpk, freqs, area_num, area_ana,
           tf, ct_const, ct_g0, ct_sls):
    figstyle.apply()
    C = figstyle.COLOR
    note = (f"Simulation: standard-linear-solid wall, {A * 1e6:.0f} mL volume amplitude, "
            f"τ = {sls.tau:g} s. No physical measurement.")

    # P-V loops at 0.1x, 1x, 10x the loss peak
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 3.0))
    shades = dict(zip((0.1, 10.0, 1.0), (figstyle.ramp(C["pv"], 5)[1], C["ref"], C["pv"])))
    styles = {0.1: "--", 1.0: "-", 10.0: ":"}
    for mult in (0.1, 10.0, 1.0):
        lp = pv_loop(fpk * mult, A, sls)
        ax.plot(np.array(lp["V"]) * 1e6, np.array(lp["P"]) / 1e3, styles[mult], color=shades[mult],
                lw=1.6 if mult == 1.0 else 1.2,
                label=f"{fpk * mult:.2f} Hz: {lp['area'] * 1e3:.1f} mJ")
    ax.set_xlabel("Chamber volume (mL)")
    ax.set_ylabel("Chamber pressure (kPa)")
    ax.set_title("The loop is widest at the viscoelastic corner")
    h, lab = ax.get_legend_handles_labels()
    order = [0, 2, 1]                                  # list by frequency; the corner loop is drawn last
    ax.legend([h[i] for i in order], [lab[i] for i in order], loc="upper left",
              title="Drive frequency: loop area", alignment="left")
    ax.margins(0.05)
    figstyle.footnote(fig, note.replace(", τ", ",\nτ") + f" Corner f = 1/(2πτ) = {fpk:.2f} Hz.")
    figstyle.save(fig, outdir / "fig_pv_loops", formats=("png",)); plt.close(fig)

    # loop area vs frequency: numeric vs analytic
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.6))
    ax.plot(freqs, area_ana * 1e3, "-", color=C["ref"], lw=1.2, zorder=1)
    ax.plot(freqs, area_num * 1e3, "o", color=C["pv"], ms=4, mec="white", mew=0.5, zorder=2)
    ax.set_xscale("log")
    ax.set_xticks([0.1, 1, 10], ["0.1", "1", "10"])
    ax.axvline(fpk, ls="--", c=C["ref"], lw=0.8)
    ax.annotate(f"corner {fpk:.2f} Hz", (fpk, 0.02), xycoords=("data", "axes fraction"), xytext=(4, 0),
                textcoords="offset points", fontsize=figstyle.SIZE["note"], color=C["ref"])
    i = int(np.argmin(np.abs(freqs - 8)))
    figstyle.end_label(ax, freqs[i], area_ana[i] * 1e3, "analytic SLS\ndissipation", C["ref"], dx=8, dy=10)
    j = int(np.argmin(np.abs(freqs - 0.55)))
    figstyle.end_label(ax, freqs[j], area_num[j] * 1e3, "numerical ∮P dV", C["pv"], dx=-7, dy=4, ha="right")
    ax.set_xlabel("Drive frequency (Hz)")
    ax.set_ylabel("Loop area (mJ per cycle)")
    ax.set_title("Numerical loop area matches the analytic dissipation")
    ax.set_ylim(0, None)
    ax.margins(x=0.04)
    rel = np.abs(area_num - area_ana) / np.maximum(area_ana, 1e-30)
    figstyle.footnote(fig, note.replace(", τ", ",\nτ") + f" {len(freqs)} frequencies; "
                      f"largest relative error {rel.max() * 100:.2f} %.")
    figstyle.save(fig, outdir / "fig_loop_area_vs_freq", formats=("png",)); plt.close(fig)

    # Gate 0 consistency
    fig, ax = plt.subplots(figsize=(figstyle.SINGLE, 2.6))
    ax.plot(tf, ct_g0 * 100, "-", color=C["ref"], lw=2.6, zorder=1)
    ax.plot(tf, ct_const * 100, "--", color=C["compliance"], lw=1.3, zorder=2)
    ax.plot(tf, ct_sls * 100, "-", color=C["pv"], lw=1.3, zorder=3)
    ax.set_xscale("log")
    ax.set_xticks([0.01, 0.1, 1, 10, 100], ["0.01", "0.1", "1", "10", "100"])
    k = int(np.argmin(np.abs(tf - 1.2)))
    ax.annotate("Gate 0 model and\nSLS network with\nconstant C = 1/k1", (tf[k], ct_g0[k] * 100), xytext=(0.012, 10.0),
                fontsize=figstyle.SIZE["note"], color=C["ref"], ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=C["ref"], shrinkA=2, shrinkB=2))
    m = int(np.argmin(np.abs(tf - 5)))
    figstyle.end_label(ax, tf[m], ct_sls[m] * 100, "SLS network,\nfrequency-dependent C(ω)", C["pv"], dx=6, dy=-14)
    ax.set_xlabel("Drive frequency (Hz)")
    ax.set_ylabel("Cross-talk |H21/H11| (%)")
    ax.set_title("With constant compliance the SLS network is Gate 0")
    ax.margins(x=0.03)
    err = float(np.max(np.abs(ct_const - ct_g0)))
    figstyle.footnote(fig, "Simulation: three-chamber network with an SLS wall. Largest gap between\n"
                      f"Gate 0 and the constant-C network: {err:.1e} (cross-talk ratio).")
    figstyle.save(fig, outdir / "fig_gate0_consistency", formats=("png",)); plt.close(fig)


if __name__ == "__main__":
    main()
