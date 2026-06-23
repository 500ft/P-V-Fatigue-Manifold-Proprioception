# Phase C Health Indicators — Test Report

Date: 2026-06-23
Suite: in-memory `readline` stub + `pytest tests -q`
Study: `python3 scripts/run_study1.py --trials 200 --calibration 5000`

## Acceptance coverage

| Criterion | Evidence | Status |
|---|---|---|
| Analytic loop area and compliance | `tests/test_features.py` | PASS |
| Recovery tau and five-minute normalization | `tests/test_mullins.py`; max tau error 2.9e-7 | PASS |
| Null actuator and registered cohort axes | `tests/test_validation.py` | PASS |
| Monotonicity/trendability/prognosability fixtures | `tests/test_hi_metrics.py`; Study 1 fixtures | PASS |
| Causal baseline and future invariance | `tests/test_health_index.py` | PASS |
| Sustained 3σ and matched-FA CUSUM | `tests/test_detectors.py`; registered grid | PASS |
| Onset models, AICc, and sparse guards | `tests/test_degradation.py` | PASS |
| Quadratic/logistic inverse-crime grid | 144 conditions, k=8/20/50 | PASS |
| Noise-free alarm omission | `study1_results.json` check | PASS |
| Full Phase A–C regression | 69 tests | PASS |

## Main synthetic findings

- Form-matched quadratic onset at ud=0.70, cadence 100: median error 0.0025 life
  fraction at zero and 0.25% FS noise.
- The same segmented estimator on logistic k=20 returns 0.40 median onset error,
  directly exposing model-form dependence.
- At 0.25% FS and cadence 100, both detectors alarm on every canonical trial; sustained
  3σ alarms at median cycle 400 and CUSUM at 500. Their true-null false-alarm rates are
  0.0036 and 0.0052; all registered detector pairs match within 0.2 percentage points.
- Fused-HI monotonicity is 0.657 versus 0.714 for area and 0.143 for compliance;
  fusion does not win this synthetic comparison.

## Environment and limits

- The active Python environment's `readline` extension segfaults during pytest startup;
  tests inject an in-memory empty module before importing pytest. Project code is
  unaffected.
- The validation cohort and every result remain synthetic. Trendability and
  prognosability become study results only after Phase D applies them to its realistic
  population.
