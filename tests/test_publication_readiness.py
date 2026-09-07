"""Publication readiness is not historical PDF byte consistency."""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_SHA = "6a6681fe1a77f7d972048dddc99a0a07b55e5d89dca1a83c11ba5b5cefd0777d"


def test_historical_pdf_remains_unchanged():
    assert hashlib.sha256((ROOT / "docs/preprint_v1.pdf").read_bytes()).hexdigest() == HISTORICAL_SHA


def test_historical_integrity_is_not_publication_permission():
    run = subprocess.run(
        [sys.executable, "-m", "scripts.check_publication_fallback", "--for-publication"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert run.returncode != 0, "Uncorrected, unreviewed payload was cleared for publication"
    assert "BLOCKED" in run.stdout


def test_default_check_explicitly_limits_its_claim():
    run = subprocess.run(
        [sys.executable, "-m", "scripts.check_publication_fallback"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert run.returncode == 0
    assert "Historical payload integrity: PASS" in run.stdout
    assert "Publication readiness: BLOCKED" in run.stdout


def test_candidate_states_actual_probe_and_endpoint():
    text = (ROOT / "docs/preprint_v1_4_candidate.md").read_text()
    assert "idealized model-derived" in text
    assert "zero rest input" in text
    assert "macro-average of stage-level pose RMSE" in text
    assert "noisy, quantized,\n  decimated volumetric probe" not in text
    assert "CI half-width (±0.06) measures" not in text
    assert "not released or submitted" in text
