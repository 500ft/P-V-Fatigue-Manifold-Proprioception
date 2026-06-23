# Phase B Fatigue Model — Test Report

Date: 2026-06-21
Suite: `python3 -c '<readline stub>; pytest.main(["tests", "-q"])'`

## Acceptance coverage

| Criterion | Test or artifact | Status |
|---|---|---|
| Cycle-zero Phase A identity | `test_cycle_zero_is_exact_identity` | PASS |
| Mullins saturation and 30% floor | `test_mullins_stabilizes_by_cycle_ten`, `test_recovery_removes_recoverable_part_but_leaves_floor` | PASS |
| Rest leaves fatigue/leak unchanged | `test_rest_does_not_change_fatigue_or_leak` | PASS |
| Canonical 16% drift and 20x leak | `test_canonical_onset_and_terminal_values`, P-V integration test | PASS |
| Immutable parameter adapters | `test_adapters_are_immutable_and_map_conductance_correctly` | PASS |
| Analytic pressure decay at `k2=0` | `test_pressure_decay_matches_relaxed_spring_analytic_solution` | PASS |
| Operational half-life vs conductance | two pressure-decay half-life tests | PASS |
| Invalid inputs rejected | parameterized validation tests | PASS |
| Phase B artifacts and consistency report | `scripts/phaseB_fatigue_demo.py` | PASS |
| Phase A regression suite | `tests/test_plant.py` | PASS |

## Deviations and environment

- The active Python 3.11 environment's `readline` extension segfaults during pytest
  startup. Verification injects an in-memory empty `readline` module before importing
  pytest; repository/runtime code is unaffected.
- Pre-onset pressure half-life can rise slightly as compliance increases at unchanged
  leak conductance. The monotonic half-life assertion therefore controls SLS state and
  varies conductance, matching the design requirement.

## Deferred

Noise, cohort variability, linear-drift detection, and curvature-onset recovery remain
Phase C/D work under the pre-registered identifiability grid.
