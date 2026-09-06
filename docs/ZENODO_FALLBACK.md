# Citable-Release Fallback — Zenodo

> **Superseded operational instruction, 2026-09-05; reviewed 2026-09-06.**
> Do not execute the archived August 2 deposit instruction below. A methods
> correction blocks new posting of v1.3 even when its checksum passes.
> [Correction and explicit rebaseline](corrections/v1.3-methods-2026-09-05.md).
> A separately reviewed corrected PDF and metadata are required; no new date
> or account action is authorized. The remainder preserves historical planning.

Decision registered: 2026-07-17
Fallback decision date: 2026-08-02

The application packet cannot depend on an arXiv endorser replying. Continue
the cs.RO endorsement path, but create a Zenodo draft and reserve its DOI now.
Do not publish the draft before reviewing the rendered record.

If no arXiv identifier exists by **2026-08-02**, publish the checked v1.3
preprint on Zenodo. Add any later arXiv identifier as a related identifier; do
not erase or replace the version history.

## Frozen deposit payload

- PDF: `docs/preprint_v1.pdf`
- Git tag: `preprint-v1.3`
- SHA-256: `6a6681fe1a77f7d972048dddc99a0a07b55e5d89dca1a83c11ba5b5cefd0777d`
- Metadata: `.zenodo.json`
- Citation metadata: `CITATION.cff`
- License for the manuscript: CC BY 4.0, consistent with `LICENSE-docs`

The deposit title and version must match those files exactly. The abstract or
description must say **simulation-only**; no hardware-validation language is
permitted.

## Owner steps

1. Sign in to Zenodo and create a new upload draft.
2. Upload the exact PDF above and copy the committed metadata.
3. Reserve a DOI; record it in `docs/zenodo-manifest.json` and `CITATION.cff`
   without publishing.
4. Preview creators, affiliation, version, dates, license, keywords, related
   GitHub tag, and the simulation-only description.
5. If an arXiv identifier exists by August 2, keep the Zenodo draft as a
   fallback and use arXiv in the packet. Otherwise publish the Zenodo record.
6. After publication, record the DOI in the manifest, README, citation file,
   Progress, portfolio case study, and GitHub repository metadata.

Publishing a Zenodo record is an external, permanent account action and is not
performed by the repository automation.
