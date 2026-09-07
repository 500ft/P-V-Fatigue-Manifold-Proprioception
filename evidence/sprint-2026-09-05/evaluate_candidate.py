"""Publication blocker replay; temporary files are synthetic metadata only."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scripts.check_publication_fallback import publication_blockers
candidate = json.loads((HERE / "candidate.json").read_text())
for name, digest in candidate["files"].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "Candidate drift: " + name
original = json.loads((ROOT / "docs/publication-readiness.json").read_text())
cases = [("missing", None), ("malformed", "{"), ("non_object", "[]")]
for name, key, value in [
    ("forged_ready", "status", "ready"),
    ("missing_attachment", "correction_notice", "docs/no-such-correction.md"),
    ("stale_hash", "candidate_manuscript_sha256", "0" * 64),
    ("escaping_attachment", "candidate_manuscript", "../../outside.md"),
]:
    record = copy.deepcopy(original)
    record[key] = value
    cases.append((name, json.dumps(record)))
results = []
with tempfile.TemporaryDirectory(prefix="pv-counterexamples-") as tmp:
    for name, payload in cases:
        path = Path(tmp) / (name + ".json")
        if payload is not None:
            path.write_text(payload)
        blockers = publication_blockers(path)
        results.append(dict(id=name, expected="BLOCKED", observed="BLOCKED" if blockers else "CLEAR",
                            matches=bool(blockers), reasons=blockers))
print(json.dumps(dict(kind="developer metadata counterexamples", denominator=len(results),
    all_matched=all(r["matches"] for r in results), cases=results), indent=2))
raise SystemExit(0 if all(r["matches"] for r in results) else 1)
