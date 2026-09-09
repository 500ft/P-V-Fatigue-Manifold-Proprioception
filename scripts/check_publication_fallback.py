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


def _require_integrity(condition: bool, message: str) -> None:
    """Runtime validation, deliberately independent of Python's assertion mode."""
    if not condition:
        raise ValueError(message)


def check_historical_payload() -> str:
    """Return the archive digest only after all historical checks pass."""
    manifest = json.loads((ROOT / "docs/zenodo-manifest.json").read_text(encoding="utf-8"))
    metadata = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    pdf_path = ROOT / manifest["publication_file"]
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    _require_integrity(manifest["release"] == "preprint-v1.3", "Unexpected archived release.")
    _require_integrity(digest == manifest["sha256"], "Archived PDF SHA-256 mismatch; review changed bytes.")
    _require_integrity(metadata["version"] == "1.3", "Unexpected metadata version.")
    _require_integrity(metadata["publication_type"] == "preprint", "Unexpected publication type.")
    _require_integrity(metadata["license"] == "cc-by-4.0", "Unexpected metadata license.")
    _require_integrity("simulation-only" in metadata["description"].lower(), "Missing simulation-only scope.")
    _require_integrity(metadata["title"].startswith("Pressure-Volume Loop Shape"), "Unexpected archived title.")
    _require_integrity(metadata["creators"][0]["name"] == "Ulziibayar, Mergen", "Unexpected archived creator.")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    _require_integrity("version: 1.3" in citation, "Missing citation version.")
    _require_integrity("date-released: 2026-07-08" in citation, "Missing citation release date.")
    _require_integrity("preprint-v1.3" in citation, "Missing citation release tag.")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--for-publication", action="store_true", help="Fail closed while publication is blocked")
    args = parser.parse_args()
    try:
        digest = check_historical_payload()
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
        print(f"Historical payload integrity: FAIL ({type(exc).__name__}: {exc})")
        print("Publication readiness: BLOCKED")
        return 1
    print("Historical payload integrity: PASS")
    print("PDF SHA-256:", digest)
    blockers = publication_blockers()
    print("Publication readiness: BLOCKED")
    for blocker in blockers:
        print("-", blocker)
    return 2 if args.for_publication else 0


if __name__ == "__main__":
    raise SystemExit(main())
