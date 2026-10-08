# Completion reconciliation and author return

The study is closed. The [acceptance withdrawal](#acceptance-withdrawn-2026-10-02)
supersedes the review and release actions recorded below. v1.4 will not be
released; [ROADMAP.md](../ROADMAP.md) holds the current scope.

Refreshed 2026-09-29 for the updated v1.4 candidate. This is a review handoff, not an author signature or a publication clearance. Historical task record: [SPRINT_TASKS.csv](history/SPRINT_TASKS.csv), especially PV-08 and PV-COR-01.

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

## Owner response — submitted 2026-09-30

The owner delegated the review decisions on 2026-09-30 ("make a decision for
the other repos"). They were made by Claude on the owner's behalf; the owner
remains the accountable author.

- **Reviewer and date:** Claude (AI assistant) under the owner's delegation,
  2026-09-30. The whole manuscript was read against the correction notice and
  the linked result files.
- **Candidate source hash reviewed:** `a9b1111d401c2dc4254744712c5daaf0824f4ec1e0436624b88d58a9c6d6f75e`. After the two text changes below,
  the accepted text is `fd6204bc71c5816f5712208e25d861fd64a4394276a0e38d29c6357952314cd4`, which the
  [readiness record](publication-readiness.json) now carries.
- **Other author drafts:** none were supplied, and whether any exist is
  unknown. Decision: the repository candidate is the authoritative v1.4 text;
  content in any outside draft is not part of v1.4.
- **Text decision:** accepted with two changes, both applied. In §4.4 and the
  Figure 3 caption, "observable" became "idealized", because the correction
  establishes that the Study 3 signal is an idealized model output, not an
  observed one. A clarifying clause in §5 says the 6.3% cross-talk figure is a
  response ratio, not the ≈4% curvature share in §4.2.
- **Statistical wording:** keep the actuator-cluster interval [0.853, 0.950]
  and the delete-one sensitivity [0.576, 0.973]. Stage readings are repeated
  measures within six actuators, not independent devices.
- **Later studies:** accepted as written. Study A passes only under an amended
  rule, Study B establishes no post-onset precision, Study C fails transfer,
  and the diagnostics are post-hoc. They restrict the policy result without
  replacing it. Study C2 stays out of v1.4.
- **Historical threshold:** keep the deployed τ = 0.05 and its non-positive
  lead. The τ = 0.01 frontier stays descriptive, because it was chosen after
  inspection.
- **Separately versioned PDF:** yes. Render it from the accepted text through
  the existing safe route.
- **Posting and deposit:** after the PDF is approved by its hash, deposit it as
  a new Zenodo record that links the v1.3 release and the correction notice.
  Submit to arXiv as well only if an endorser is found. The deposit is an owner
  account action; nothing is posted by this decision.
- **Eventual PDF path, hash and approval:** not yet available.

## Acceptance withdrawn, 2026-10-02

The 2026-09-30 acceptance above is withdrawn. It checked wording, hashes and
intervals, but not whether a clock at matched recalibration cost ties the P-V
trigger. It does: a clock every 2,400 cycles gives the trigger's exact schedule
on all 20 actuators. The owner chose on 2026-10-02 to stop the paper and keep
the code. v1.4 will not be rendered for release, approved or deposited. The
findings and what still stands are in the [withdrawal note](corrections/v1.4-withdrawn-2026-10-02.md).

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
