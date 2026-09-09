# PV-D01 — Historical payload validation without removable assertions

Date: 2026-09-08. Development/regression evidence, not scientific evaluation.

## Starting point and priority

- Repository: `500ft/P-V-Fatigue-Manifold-Proprioception`.
- Base: `3dba7aeb664c93bfc6c1a74d7c3462ea1cc96738`, clean worktree.
- Branch: `task/priority-one-20260908`.
- Working directory for commands below:
  `/Users/redhose/Developer/daily-prs/2026-09-08/P-V-Fatigue-Manifold-Proprioception`.
- Runtime: `/Users/redhose/ENTER/bin/python`, Python 3.11.8.
- Commit identity checked: `500ft <153922251+500ft@users.noreply.github.com>`.
- Initial `python3` selected Python 3.13.7, without pytest (`ModuleNotFoundError`,
  exit 1). This is an interpreter/dependency mismatch, not a repository failure.
  All completed checks use the existing Python 3.11.8 environment below.

The [CI workflow](../../.github/workflows/ci.yml) treats the default publication
checker as a gate. At the base commit, every historical integrity requirement in
[the checker](../../scripts/check_publication_fallback.py) used `assert`, including
the frozen PDF hash. Python optimization removes these checks entirely. This
allows a corrupted archive to print `Historical payload integrity: PASS` and exit
0. It does **not** bypass the separate publication block; the defect is a false
integrity verdict, not an observed unauthorized deposit.

This is the highest-priority bounded unblocked follow-up selected today because
the historical release gate must be trustworthy before publication work. Existing
PV-08 author reconciliation and approval remain blocked; the proposed v2 study
and conditional CAD pilot are not started to sidestep those dependencies.

## Task and acceptance contract

Replace removable assertions with ordinary runtime validation. Test copied
payloads in fresh subprocesses with and without `-O`: modified bytes or required
metadata must not print integrity PASS; malformed/missing input must fail with a
diagnostic; unchanged input must retain integrity PASS and publication BLOCKED.
Preserve the historical PDF bytes, scientific results and owner approval gate.

The only production file changed is the checker. The
[new subprocess tests](../../tests/test_publication_integrity_cli.py) copy the
script, manifest, PDF, metadata and citation into pytest temporary directories.
They do not edit committed artifacts. The tests execute the actual CLI, not a
mocked return value.

## Commands and observed evidence

No standalone typecheck, lint or package-build command is configured in this
repository's CI. `git diff --check` is a whitespace check, not a typechecker.
The existing manuscript/PDF/metadata checks are retained without rewriting the PDF.

Use this documented local workaround for pytest (stub readline before importing
pytest):

```sh
python -c 'import sys, types; sys.modules["readline"] = types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["-q"]))'
python -m scripts.check_manuscript_numbers
python -m scripts.check_pdf_arxiv
python -m scripts.check_publication_fallback
python -O -m scripts.check_publication_fallback
python -O -m scripts.check_publication_fallback --for-publication
git diff --check
```

| Check | Baseline / red | Corrected candidate |
|---|---|---|
| Full existing suite | 141 passed in 6.05 s, exit 0 | 177 passed in 7.17 s, exit 0 |
| First regression run, before implementation | 11 failed, 13 passed in 1.08 s, exit 1 | First green: 28 passed in 1.01 s including 4 existing readiness tests, exit 0 |
| Added malformed-input boundaries | Added after first green | 12 cases included in final 177 |
| Final focused regression suite | — | 36 passed in 1.35 s, exit 0 |
| Manuscript numbers | PASS, exit 0 | PASS, exit 0 |
| Historical PDF preflight | PASS, exit 0 | PASS, exit 0; 10 pages, 5 embedded fonts, no encryption/JavaScript |
| Default historical check | integrity PASS; publication BLOCKED; exit 0 | Same, exit 0 |
| Optimized historical check, unchanged payload | Valid-payload control passed in red suite | integrity PASS; publication BLOCKED; exit 0 |
| Publication request | Blocked by existing tests | Normal and optimized copied-payload tests require exit 2; real optimized CLI also returned 2 and BLOCKED |
| Whitespace / task ledger | Clean initial tree | `git diff --check` exit 0; CSV parse passed; original eight rows byte-preserved, original 30 h unchanged |

The first regression command was the pytest invocation above with arguments
`["-q", "tests/test_publication_integrity_cli.py"]` and only the first 24 test
cases present. Each of the 11 optimized mutation cases failed the intended
nonzero-exit assertion; its normal-Python counterpart passed. The mutations were
PDF bytes, release tag, version, publication type, license, description, title,
creator, citation version, citation date and citation tag. Representative observed
bad output before correction:

```text
Historical payload integrity: PASS
PDF SHA-256: 199077cba2f7f675c99d24db18cc621dc18a6a45ae6dedd9cd97e0f45f48b5fd
Publication readiness: BLOCKED
returncode=0
```

That hash belongs to the temporary PDF with `\nchanged payload\n` appended. The
committed PDF remains SHA-256
`6a6681fe1a77f7d972048dddc99a0a07b55e5d89dca1a83c11ba5b5cefd0777d`.

To repeat just the original corruption regression, run pytest with arguments
`["-q", "tests/test_publication_integrity_cli.py", "-k", "modified_payload"]`.
Those 22 cases directly cover all original checks under both interpreter modes.
Additional tests exercise invalid JSON, a missing PDF, absent version, empty
creators, null description and list-shaped metadata. The production checker now
returns exit 1 and an integrity FAIL diagnostic rather than an uncaught traceback
for these inputs. Publication requests remain blocked with exit 2 for otherwise
intact archives.

## Limits and review

These are developer-selected mutation tests, not held-out research results or
independent external review. Citation matching and manifest trust retain their
existing scope; this task does not introduce full metadata-schema validation or
protect against coordinated edits to both the artifact and its expected hash.
No v1.4 PDF was generated, approved, published or deposited. No model, measurement,
preregistration, CAD release or scientific claim changed.

The PR commit supplies the candidate identity without a circular self-hash.
Review the checker diff, reproduce the mutation cases and confirm PV-08 stays
blocked. Next project action remains author review of the corrected manuscript.
