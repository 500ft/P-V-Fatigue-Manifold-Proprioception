"""Historical integrity must hold even when Python assertion checks are disabled."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def payload(tmp_path):
    """Copy only the historical payload; never edit the committed manuscript."""
    for name in (
        "scripts/check_publication_fallback.py", "docs/zenodo-manifest.json",
        "docs/preprint_v1.pdf", ".zenodo.json", "CITATION.cff",
    ):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return tmp_path


def run_check(payload, optimized, *args):
    return subprocess.run(
        [sys.executable, *(["-O"] if optimized else []),
         str(payload / "scripts/check_publication_fallback.py"), *args],
        cwd=payload, capture_output=True, text=True,
    )


@pytest.mark.parametrize("optimized", [False, True])
@pytest.mark.parametrize("mutation", [
    "pdf_bytes", "release", "version", "publication_type", "license",
    "description", "title", "creator", "citation_version",
    "citation_date", "citation_tag",
])
def test_modified_payload_never_reports_integrity_pass(payload, optimized, mutation):
    if mutation == "pdf_bytes":
        pdf = payload / "docs/preprint_v1.pdf"
        pdf.write_bytes(pdf.read_bytes() + b"\nchanged payload\n")
    elif mutation == "release":
        path = payload / "docs/zenodo-manifest.json"
        record = json.loads(path.read_text())
        record["release"] = "different-release"
        path.write_text(json.dumps(record))
    elif mutation.startswith("citation_"):
        path = payload / "CITATION.cff"
        expected = {
            "citation_version": "version: 1.3",
            "citation_date": "date-released: 2026-07-08",
            "citation_tag": "preprint-v1.3",
        }[mutation]
        assert expected in path.read_text()
        path.write_text(path.read_text().replace(expected, "changed"))
    else:
        path = payload / ".zenodo.json"
        record = json.loads(path.read_text())
        if mutation == "creator":
            record["creators"][0]["name"] = "Different author"
        else:
            record[mutation] = "changed"
        path.write_text(json.dumps(record))
    result = run_check(payload, optimized)
    assert result.returncode != 0, result.stdout
    assert "Historical payload integrity: PASS" not in result.stdout


@pytest.mark.parametrize("optimized", [False, True])
def test_unchanged_archive_pass_is_not_publication_permission(payload, optimized):
    result = run_check(payload, optimized)
    assert result.returncode == 0, result.stderr
    assert "Historical payload integrity: PASS" in result.stdout
    assert "Publication readiness: BLOCKED" in result.stdout
    deposit = run_check(payload, optimized, "--for-publication")
    assert deposit.returncode == 2
    assert "Publication readiness: BLOCKED" in deposit.stdout


@pytest.mark.parametrize("optimized", [False, True])
@pytest.mark.parametrize("mutation", [
    "invalid_json", "missing_pdf", "missing_version", "empty_creators",
    "null_description", "list_metadata",
])
def test_incomplete_payload_fails_with_diagnostic(payload, optimized, mutation):
    path = payload / ".zenodo.json"
    record = json.loads(path.read_text())
    if mutation == "invalid_json":
        path.write_text("{")
    elif mutation == "missing_pdf":
        (payload / "docs/preprint_v1.pdf").unlink()
    elif mutation == "list_metadata":
        path.write_text("[]")
    else:
        if mutation == "missing_version":
            del record["version"]
        elif mutation == "empty_creators":
            record["creators"] = []
        elif mutation == "null_description":
            record["description"] = None
        path.write_text(json.dumps(record))
    result = run_check(payload, optimized)
    assert result.returncode == 1
    assert "Historical payload integrity: FAIL" in result.stdout
    assert "Publication readiness: BLOCKED" in result.stdout
    assert "Traceback" not in result.stderr
