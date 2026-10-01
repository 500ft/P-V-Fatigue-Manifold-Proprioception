# Author review packet — refreshed 2026-09-29

Status: review decisions recorded 2026-09-30 in the [review form](COMPLETION_RECONCILIATION.md#owner-response--submitted-2026-09-30); text accepted with two changes. The rendered PDF is not yet approved. Review the [v1.4 correction candidate](preprint_v1_4_candidate.md).
Its abstract, §3.10, §4.6 and conclusion now incorporate the completed observability work;
the earlier methods correction and original numerical results remain. This update ran no
new study. The [readiness record](publication-readiness.json) holds the current source hash
and remains blocked. Earlier PDF previews do not represent this revision.

## Recommended decisions, with reasons

1. **Keep actuator-cluster uncertainty and delete-one sensitivity visible.** The [committed cluster results](../data/sim/phaseD/study3_cluster_ci_results.json) resample actuator identities; the individual stage observations are not independent devices. Substituting the old point-bootstrap interval would obscure that limitation.
2. **Do not change the deployed threshold retrospectively.** Keep the deployed threshold and its nonpositive lead from the [canonical Study 3 result](../data/sim/phaseD/study3_results.json). The alternative-threshold frontier was already inspected and is descriptive, not a newly held-out discovery.
3. **Approve correction text before creating a deposit.** Preserve v1.3 bytes and prepare a separately versioned correction after reconciling the author's working drafts. Publication is not authorized by a green integrity check. Do not create a duplicate Zenodo record or assume an account action occurred.
4. **Review the later studies against their actual endpoints.** Study A's amended verdict is a changed criterion; Study B establishes no post-onset precision; Study C fails its declared life-estimation transfer test. These results restrict the original policy interpretation without constituting a rerun of that policy. Study C2 remains unexecuted.

## What changed from the archived interpretation

| Previous interpretation | Corrected scope and evidence |
| --- | --- |
| Noisy acquired P-V probe supports Study 3 | `health_trajectory` in [coupling.py](../pipeline/coupling.py) supplies an idealized analytic probe; noisy pose channels do not make the policy input noisy. |
| Rest/recovery robustness tested | Study 3 fixes rest input to zero; variable rest is a future intervention. |
| Meets accuracy throughout life | [run_study3.py](../scripts/run_study3.py) averages stage RMSE; the budget is a train-derived macro-average, not an all-time safety bound. |
| Fewer calibration events means proportionally less operational cost | The [policy result](../data/sim/phaseD/study3_results.json) counts events including initialization; downtime and total cost were not measured. |
| Transfers across physical actuators | All identities share one synthetic generator. New degradation families are proposed, not evaluated. |
| A closed Study B profile demonstrates precise life estimation | The [corrected profile](../data/sim/studyB/studyB_structural.json) is bound-dependent, has a broad plateau and reports no resolution. Its young baseline assumes a known normalized-life coordinate. |
| Study C evaluates a pressure-only health sensor | Its probe vector includes P-V features and its full estimator includes the clock. The pressure-only pose corrector is a separate component. |

The current script contains `tau_selection_alternatives`, but the committed Study 3 JSON does **not** contain that key. Do not present this code path as a committed comparison result or rerun the historical generator to silently fill it. The [prospective integrity core](specs/v2-integrity-core/design.md) remains a development design pending draft reconciliation.

## Bounded review sitting

- Compare the abstract and original methods with the [correction notice](corrections/v1.3-methods-2026-09-05.md).
- Read §3.10, §4.6 and the conclusion against their linked results. Check the baseline assumption, withdrawn precision, failed transfer and post-hoc status of the diagnostics.
- Reconcile separate local author drafts and identify the exact files/commits supplying accepted edits.
- Return the [review form](COMPLETION_RECONCILIATION.md#owner-response--not-submitted), binding the decision to the current source hash. Scientific feedback from another reviewer informs the author's decision; it does not automatically authorize deposit.

## Reproduce before signing

Run `python -m scripts.check_manuscript_numbers` (checks both historical and candidate Markdown), `python -m scripts.check_publication_fallback`, and `python -m scripts.check_publication_fallback --for-publication`. Expected: numeric check passes, archive integrity passes, publication remains BLOCKED and the publication-mode command exits 2. `python -m scripts.check_pdf_arxiv` inspects the historical PDF by default; pass a preview path explicitly to check that file.

The number checker validates required reported snippets, not every sentence or semantic claim. New regression tests prove that replacing the candidate's cluster interval or calibration saving is detected. Author review remains necessary.
