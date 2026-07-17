"""Verify that the frozen Zenodo fallback describes the tagged v1.3 bytes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
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
    print("Publication fallback: PASS")
    print("PDF SHA-256:", digest)


if __name__ == "__main__":
    main()
