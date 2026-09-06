"""Check archived v1.3 integrity, not permission to publish its uncorrected claims."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def publication_blockers(record_path: Path | None = None) -> list[str]:
    """The known v1.3 methods erratum cannot be cleared by a metadata flag.

    A corrected release needs its own reviewed PDF, metadata and checker update.
    This function deliberately cannot authorize a deposit of the archived PDF.
    """
    blockers = ["Archived v1.3 contains a methods erratum; a separately reviewed corrected release is required."]
    path = record_path or ROOT / "docs/publication-readiness.json"
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or record.get("status") != "blocked":
            blockers.append("Readiness record must explicitly preserve the current blocked state.")
            return blockers
        for key in ("correction_notice", "candidate_manuscript"):
            value = record.get(key)
            if not isinstance(value, str):
                blockers.append(f"Missing {key} attachment.")
                continue
            target = (ROOT / value).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
                blockers.append(f"Unavailable or non-repository {key} attachment.")
                continue
            expected = record.get(key + "_sha256")
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                blockers.append(f"Stale or missing {key} SHA-256; review changed text.")
        blockers.append("Corrected PDF, artifact-bound author approval and deposit decision remain pending.")
    except (OSError, ValueError, TypeError) as exc:
        blockers.append(f"Readiness record unavailable or invalid: {type(exc).__name__}.")
    return blockers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--for-publication", action="store_true", help="Fail closed while publication is blocked")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "docs/zenodo-manifest.json").read_text(encoding="utf-8"))
    metadata = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    pdf_path = ROOT / manifest["publication_file"]
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    assert manifest["release"] == "preprint-v1.3"
    assert digest == manifest["sha256"], "publication PDF changed; update and review the frozen deposit"
    assert metadata["version"] == "1.3"
    assert metadata["publication_type"] == "preprint"
    assert metadata["license"] == "cc-by-4.0"
    assert "simulation-only" in metadata["description"].lower()
    assert metadata["title"].startswith("Pressure-Volume Loop Shape")
    assert metadata["creators"][0]["name"] == "Ulziibayar, Mergen"

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert "version: 1.3" in citation
    assert "date-released: 2026-07-08" in citation
    assert "preprint-v1.3" in citation
    print("Historical payload integrity: PASS")
    print("PDF SHA-256:", digest)
    blockers = publication_blockers()
    print("Publication readiness: BLOCKED")
    for blocker in blockers:
        print("-", blocker)
    return 2 if args.for_publication else 0


if __name__ == "__main__":
    raise SystemExit(main())
