# Simulation + Analysis Pipeline — Build Plan

**Goal of the remote period (~8 weeks, laptop-only):** turn the Gate 0 lumped-RC core
into (1) a full **coupled forward simulator** that emits synthetic P-V loops, cross-talk
matrices, and pose under a fatigue trajectory, and (2) the **complete analysis pipeline**
that consumes them — so that when hardware comes online in NYC, real data flows through an
already-validated pipeline and becomes figures in days.

**Triple duty of this work:**
1. **Insurance** — a standalone, honestly-framed modeling paper if hardware slips.
2. **Design** — fixes the exact pressures, frequencies (~1–5 Hz from Gate 0), cycle
   cadence, and trace counts for the hardware protocol; no more guessing.
3. **Preparation** — the pipeline is built and *verified against known ground truth*
   before any noisy real data exists. This is the methodological win: the sim tells us the
   true answer, so we can prove each estimator recovers it.

**Honesty constraint (non-negotiable):** every synthetic result is labeled as simulation.
The paper claims no experimental validation from this work. Modeling assumptions (PCC
kinematics, viscoelastic loop model, fatigue parameterization) are stated as choices. The
real contributions are the pipeline, the design, and — if framed as a prediction — the
modeling result.

---

## Architecture

```
sim/                         # the forward model (#1)
  plant.py        nonlinear lumped pneumatic network; viscoelastic P-V -> real hysteresis;
                  time integration (solve_ivp). Reduces to gate0 linear model small-signal.
  fatigue.py      degradation trajectory C(N), leak-conductance growth (micro-tear->leak),
                  Mullins fast-softening + partial rest recovery (reversible vs irreversible).
  kinematics.py   chamber pressure/curvature -> finger bending -> tip SE(3) (PCC model).
  sensors.py      pressure-sensor noise (±0.5% FS), 100 Hz sampling, quantization, volume
                  estimate (volumetric-drive exact OR oscillation-observer ~0.6% RMS),
                  contact events (binary + force).
  dataset.py      scenario generator -> labeled traces (free bend + contact), across fatigue
                  levels, shared-manifold vs isolated-supply control. Target ~2000 traces.

pipeline/                    # the analysis (#2)
  features.py     P-V loop features: loop area (hysteresis energy), peak pressure,
                  pressure@80%-volume slope (compliance), inflation/deflation asymmetry,
                  PCA PC1 of loop shape.
  degradation.py  logistic / double-logistic fits to each feature trajectory; HI construction.
  hi_metrics.py   monotonicity, trendability, prognosability (Lei 2018); lead-time (cycles),
                  early-warning AUC, false-alarm rate.
  mullins.py      separate reversible (rest-recoverable) from irreversible fatigue drift.
  correctors.py   ridge (static baseline), ARX (explicit cross-talk decoupling), ESN
                  (dynamic black-box). Pose RMSE / contact F1 / latency.
  coupling.py     cross-talk-drift vs P-V-compliance-feature correlation; P-V-triggered
                  recalibration policy vs fixed vs always-on continual learning.
  validation.py   ground-truth recovery harness: assert each estimator recovers the sim's
                  known answer within tolerance.

scripts/
  gate0_lumped_rc.py   (existing)
  run_full_sim.py      generate the synthetic dataset -> data/sim/
  run_study1.py        fatigue leading-indicator analysis -> figures + metrics
  run_study2.py        cross-talk corrector comparison
  run_study3.py        coupling + recalibration

tests/                 unit tests + ground-truth recovery tests (pytest)
data/sim/              generated datasets + per-study results/figures
```

Dependencies kept minimal: numpy, scipy, matplotlib (already in `requirements.txt`).
Ridge/PCA/ARX implemented in numpy; ESN from scratch (~50 lines). `scikit-learn` optional
(only if convenient); no hard dependency.

---

## Build order (each phase is committable, testable, and produces a figure)

### Phase A — Forward plant + realistic P-V loops  *(start here)*
- `sim/plant.py`: time-domain nonlinear lumped network; pressure-dependent compliance
  C(P); viscoelastic element (standard-linear-solid) so the P-V relation forms a real
  **rate-dependent hysteresis loop**.
- **Validation:** (i) loop area grows with actuation frequency (viscoelastic signature);
  (ii) small-signal linearization reproduces the Gate 0 cross-talk transfer functions
  (regression test against `gate0_lumped_rc.py`).
- **Deliverable:** one clean synthetic P-V loop + a Bode/cross-talk check vs Gate 0.

### Phase B — Fatigue trajectory + Mullins/recovery  **DONE — PASS (2026-06-21)**
- `sim/fatigue.py`: C(N) degradation (Mullins fast-stabilize over ~5–10 cycles → slow
  irreversible drift → accelerating end-of-life), leak-conductance growth, rest recovery.
- **Consistency checks:** injected acceleration onset is recorded as ground truth but is
  not claimed recoverable in Phase B; loop features follow their designed trajectories;
  rest removes only the recoverable Mullins component.
- **Deliverable:** a sequence of P-V loops along one actuator's life; feature drift plot.

Implemented with a deterministic canonical actuator (`sim/fatigue.py`) and explicit
assumption labeling. Defaults inject 16 % no-rest terminal compliance/loop-area drift,
a 30 % permanent Mullins floor, a 24 h recovery time constant, curvature acceleration
from 70 % life, and leak-conductance growth to 20x at rupture. Because Gate 1's
volumetric probe imposes volume and cannot observe `R_l`, leak is measured independently
through a closed-valve pressure-decay simulation. The PASS verdict covers numerical and
model-consistency checks only; it is not empirical fatigue validation. See
`data/sim/phaseB/phaseB_results.json` and `docs/specs/phase-b-fatigue/`.

### Phase C — Feature extraction + degradation + HI metrics  **DONE — PASS (2026-06-23)**
- `pipeline/features.py`, `degradation.py`, `hi_metrics.py`, `mullins.py`.
- **Validation (the payoff):** run Study-1 analysis on synthetic loops where the true
  failure onset is known → confirm the fitted **lead-time recovers it**, and the HI
  monotonicity/trendability/prognosability match the injected ground truth. Confirm the
  Mullins separator removes the reversible component.
- **Deliverable:** `run_study1.py` end-to-end → lead-time distribution (with CIs) + AUC.

Implemented as a causal, ground-truth recovery study rather than a physical lead-time
claim. The registered run covers 144 onset/noise/cadence/generator conditions, 200 noisy
trials per condition, and 5,000-path CUSUM calibration. The segmented estimator is
reported as a form-matched identifiability ceiling and is stress-tested against logistic
onsets with sharpness 8/20/50. Noise-free alarm metrics are omitted as undefined. The
canonical comparison found that two-feature fusion did not beat loop area monotonicity
(0.657 vs 0.714), confirming that fusion value must be tested rather than assumed. See
`data/sim/study1/study1_results.json` and `docs/specs/phase-c-health-indicators/`.

### Phase D — Kinematics + sensors + dataset
- `sim/kinematics.py` (pressure→PCC→tip SE(3)), `sim/sensors.py` (noise/contact),
  `sim/dataset.py` (~2000 labeled traces; shared-manifold vs isolated control).
- **Validation:** noise-free pose is recoverable exactly; isolated-supply control shows
  near-zero cross-talk vs shared-manifold.
- **Deliverable:** `run_full_sim.py` → `data/sim/` dataset.

### Phase E — Proprioception correctors  *(pipeline #2 core)*
- `pipeline/correctors.py`: ridge / ARX / ESN; pose RMSE, contact F1, latency.
- **Validation:** confirm the **Gate 0 prediction** — static ridge is blind to the
  fatigue-induced (dynamic) cross-talk drift; ARX/ESN recover it. ARX coefficients track
  the injected coupling.
- **Deliverable:** `run_study2.py` → corrector comparison table + degradation-vs-fatigue plot.

### Phase F — Coupling + recalibration  *(Study 3, the spine)*
- `pipeline/coupling.py`: cross-talk-drift vs P-V-compliance correlation (the §4 prediction)
  on synthetic aging; P-V-triggered recalibration vs fixed vs always-on.
- **Deliverable:** `run_study3.py` → correlation r over life + recalibration-trigger savings.

Testing runs alongside every phase (`tests/`, ground-truth recovery harness). Commit +
push at the end of each phase.

---

## How this maps onto the hardware experiment (the "design" duty)

| Sim output | Fixes this hardware decision |
|---|---|
| Loop-area-vs-frequency curve (Phase A) | actuation frequency for P-V probing (confirms ~1–5 Hz) |
| Feature drift trajectories (Phase B/C) | reference-loop cadence (every N cycles) and which features to log |
| HI lead-time/AUC vs noise (Phase C + sensors) | required sensor resolution; whether ±0.5% FS suffices |
| Cross-talk vs isolated control (Phase D) | the shared-vs-isolated experimental contrast design |
| Corrector sensitivity (Phase E) | trace count needed for ARX/ESN to converge (validates the ~2000 target) |
| Recalibration-trigger threshold (Phase F) | the health-signal threshold to deploy on hardware |

---

## Sequencing for the 8 weeks (indicative)
- Wk 1–2: Phase A · Wk 2–3: Phase B · Wk 3–5: Phase C · Wk 5–6: Phase D ·
  Wk 6–8: Phase E + F. Paper-skeleton drafting and the ARX prior-art search slot into the
  gaps (they need no code). Land in NYC with the pipeline done and verified.
