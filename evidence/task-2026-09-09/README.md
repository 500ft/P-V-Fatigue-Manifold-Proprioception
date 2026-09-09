
# PV-D02 verification — 2026-09-09

Base: head of `task/priority-one-20260908` (PR #8). Deliverables: [`tests/test_figure_manifest.py`](../../tests/test_figure_manifest.py)
and two additions to [`docs/figure-manifest.json`](../../docs/figure-manifest.json). Authoritative status:
[SPRINT_TASKS.csv](../../docs/SPRINT_TASKS.csv).

The manifest is what `docs/data-and-figures.md` calls the machine-readable companion and what an
external regeneration audit runs from. Nothing checked it. Now seven tests hold it to the tree in
both directions — every declared output tracked *and present on disk*, every generator and
`python -m` module resolving, every committed figure under `data/gate0` and `data/sim` declared —
plus a `numeric` source per figure (the results JSON it derives from, must exist and parse) and a
`generated_inputs` block for `data/sim/phaseD/dataset.npz`, which is consumed by three entries,
produced by `scripts.phaseD_dataset`, and not committed because its bytes vary with the numpy/zip
stack even when every array is identical (audit, 2026-09-02). A consumer's command must run that
generator first; the test enforces it.

| Check | Observed |
| --- | --- |
| `python -m pytest -q` | **184 passed** (7 new) |
| `python -m scripts.check_manuscript_numbers` | exit 0 |
| `python -m scripts.check_publication_fallback` | exit 0 |
| `python -m scripts.check_pdf_arxiv` | not runnable in this sandbox (`pypdf` absent); fails identically on the base branch; nothing here touches a PDF |
| negative control: drop a manifest entry | 1 of 7 fails (undeclared committed figure) |
| negative control: point a generator at a missing script | 1 of 7 fails |
| negative control: delete a tracked output from disk | 1 of 7 fails — added after a first version passed this, because `git ls-files` reports tracked paths whether or not they exist |
| negative control: `git add` an undeclared PNG | 1 of 7 fails |

Tree restored byte-identical after each control. Generators are not run; no figure, number or
document text changes. The author-review gate PV-08 is untouched.
