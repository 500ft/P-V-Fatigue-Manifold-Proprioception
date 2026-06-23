# Phase C Health Indicators — Design

Status: approved
Date: 2026-06-23

## Goal

Build a causal P-V analysis pipeline and prove its feature, recovery, health-metric,
detection, and onset-estimation code against synthetic ground truth before Phase D
introduces a realistic joint-variability dataset.

## Scientific boundaries

- The 20-life cohort is a validation fixture, not a physical population.
- Noise-free data supports structural/onset checks, not alarm or AUC metrics.
- Area and compliance are correlated reads of one latent state; fusion is compared
  against the best single feature and is not assumed to win.
- Segmented-quadratic onset recovery on the quadratic generator is an inverse-crime
  identifiability ceiling. Logistic generators with sharpness 8/20/50 test mismatch.
- Slow-drift alarms and acceleration-onset estimates are different outputs.
- Routine five-minute-rest loops require no recovery correction; correction is only
  for the cross-rest recovery arm.

## Canonical protocol

- Baseline at cycle 20, 20 independently perturbed loops per noisy trial.
- Pressure noise: Gaussian sigma 0.1/0.25/0.5% of 80 kPa FS for detection; zero noise
  is included only in structural/onset analysis.
- Reference cadence: 100/250/500 cycles; 200 evaluation trials per condition.
- Primary HI: physics-oriented baseline-z mean of loop area and compliance.
- Comparators: best early feature and baseline-fit PCA PC1.
- Detectors: sustained 3-sigma and one-sided CUSUM calibrated to matched false-alarm
  rate on true null trajectories.
- Onset models: null linear, segmented quadratic, logistic, and double logistic.

## Acceptance

Analytic feature recovery within 2%; recovery tau within 1% noise-free; exact null;
metric ground-truth fixtures recovered; causal outputs invariant to future changes;
matched noise-free onset error within 0.02 life fraction when identifiable; explicit
undefined states for sparse AICc/breakpoint/prognosability cases; full regression green.
