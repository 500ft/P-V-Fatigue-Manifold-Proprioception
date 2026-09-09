# P-V manifest review — 2026-09-09

Review base: `b0b23185983d452cf7e0f87352b71d05941cba3d`. Candidate is the containing commit / PR head.
Python 3.11.8 at `/Users/redhose/ENTER/bin/python`; all checks run from this
repository root unless the test explicitly creates an external temporary directory.

## Findings and amendments

Day 1's optimization-safe publication integrity checker remains useful and its archived PDF is unchanged. Day 2's manifest gate had a local-state bypass: if an input existed on disk, it skipped both commitment and generated-input provenance. Three original-function counterexamples incorrectly accepted an undeclared local input, a missing generation command and a missing consumer declaration.

The gate now obtains the full tracked-file inventory using NUL-separated Git output, rejects local-only undeclared inputs, checks committed-input presence, and enforces generated-input declarations even after a local regeneration. Six added cases include correct before/after-regeneration and committed-input boundaries. The file is a manifest consistency gate, not execution of every generator.

## Verification and boundaries

Original baseline: 184 tests passed. Revised suite: 190 passed. Manuscript-number, historical-payload and PDF preflight checkers all exit 0 in this environment. Historical archive integrity does not authorize publication: the separate readiness result remains BLOCKED. No figures, numeric results, paper bytes, preregistration or publication gates were changed.

[Original-function counterexample output](counterexamples.json). New regression
inputs live in the tests; they are development material, not unseen scientific
or independent-human evaluation. No typecheck/lint task is configured; existing
suite, syntax and CI checks are used. Hosted status is recorded after push.

## Direction

Keep the manifest and publication split. Next useful research work is the existing corrected-release/author-review gate and bounded degradation stress-testing, not more manifest fields. Full figure regeneration remains separate and was not performed.
