# Completion reconciliation and author return
Refreshed 2026-09-29 for the updated v1.4 candidate. This is a review handoff, not an author signature or a publication clearance. Task status authority: [SPRINT_TASKS.csv](SPRINT_TASKS.csv), especially PV-08 and PV-COR-01.

## Each recommendation, separately

| Recommendation | What is implemented | What is not completed |
| --- | --- | --- |
| Explain the correction and statistical choice | [Author packet](AUTHOR_REVIEW_DAY3.md), [candidate](preprint_v1_4_candidate.md), [correction notice](corrections/v1.3-methods-2026-09-05.md) | Actual author draft reconciliation and acceptance |
| Verify reported numbers | [Numeric checker](../scripts/check_manuscript_numbers.py) checks historical and candidate text; baseline passed | This does not judge every scientific sentence |
| Make a corrected submission artifact | Corrected Markdown candidate is present; an unapproved preview can be rendered through the existing safe route | Reviewed release PDF is pending; the archive and previews are not approved correction artifacts |
| Clear publication | [Readiness checker](../scripts/check_publication_fallback.py) correctly blocks publication | Artifact-bound author approval, corrected-PDF review, deposit decision and identifier |
| Incorporate completed research into the candidate | §4.6 links the completed observability results and their corrections | Reviewer assessment and author acceptance; Study C2 has no executed result |

Calling the packet complete must never be shortened to “PV-08 complete.” The unfilled response below cannot populate the approval fields in [publication-readiness.json](publication-readiness.json).

## Recommended decisions and why

Retain the actuator-cluster interval and delete-one Fisher-z sensitivity from the [committed result](../data/sim/phaseD/study3_cluster_ci_results.json). Stage observations are repeated measures within actuator identities, not independent devices. The original indicator-invariance diagnostic is a limitation, not evidence of device discrimination.

Preserve the [historical deployed threshold and its nonpositive lead](../data/sim/phaseD/study3_results.json); do not replace it with an already-inspected frontier setting. Review the later observability findings as a separate life-estimation task, not as a replacement pose-policy evaluation.

Approve the corrected text only after reconciling the author's actual drafts; then render a separately versioned PDF, compare it to the accepted source, and obtain a PDF-bound approval. An approval of text is not an approval of a later file that was never seen.

## Artifact identity for this sitting

Use `candidate_manuscript` and `candidate_manuscript_sha256` in the
[readiness record](publication-readiness.json) for this sitting. That record also binds the
unchanged methods-correction notice. The candidate links each later result to its canonical
JSON; the review should identify the repository revision inspected alongside the source hash.
Earlier preview PDFs and historical hash tables refer to older text, not this sitting.

If an artifact changes, rebind the review to its new hash; do not reuse an old approval.

## Owner response — not submitted

Use the review sequence in [AUTHOR_REVIEW_DAY3.md](AUTHOR_REVIEW_DAY3.md). Return these fields in a reply or separate reviewed record:

- Reviewer identity and actual review date: **unfilled**.
- Candidate source hash reviewed: **unfilled**.
- Other author draft paths/commits compared, or explicit confirmation there are none: **unfilled**.
- Text decision: **unfilled** (accept / request changes, with exact changes).
- Statistical wording decision and reasons: **unfilled**.
- Later-study interpretation (baseline assumption, no precision claim, C-FAIL, scope of diagnostics): **unfilled**.
- Historical threshold wording decision and reasons: **unfilled**.
- Whether to prepare a separately versioned PDF after text acceptance: **unfilled**.
- Posting/deposit decision: **unfilled**; no publication account action is implied.
- Eventual PDF path/hash and approval: **not yet available**.

Smallest unblock action: supply the authoritative draft locations and a candidate-bound text decision. Agent can apply specified changes and prepare the next artifact; only an actual author decision closes author review.

## Verification

From repository root:

```sh
python -m scripts.check_manuscript_numbers
python -m scripts.check_publication_fallback
python -m scripts.check_publication_fallback --for-publication
```

Expected: first two exit 0; publication exits 2 until real approval and artifact requirements are satisfied.
The manuscript and its source hash changed in this refresh; study outputs, archived PDF and
author approval fields did not. Current validation is recorded in the accompanying PR.
