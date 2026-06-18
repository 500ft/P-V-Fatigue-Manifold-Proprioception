#!/usr/bin/env python3
"""Generate report.md from deep-research JSON results."""
import json
import re
import yaml
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
FIELDS_YAML = Path(__file__).parent / "fields.yaml"
OUTPUT = Path(__file__).parent / "report.md"

CATEGORY_MAPPING = {
    "core": ["core", "Core"],
    "meche_advantage": ["meche_advantage"],
    "cost_and_access": ["cost_and_access"],
    "domain_specific": ["domain_specific"],
}

SKIP_KEYS = {"uncertain", "_source_file"}
TOC_FIELDS = ["difficulty", "hardware_cost_est", "lane"]

RANKINGS = {
    "A01+A04": 1,
    "G02": 2,
    "A01": 3,
    "F01": 4,
    "A02": 5,
    "H01": 6,
}

VERDICTS = {
    "A01": "genuinely open",
    "A02": "reframed — latency-floor trade surface",
    "F01": "narrowed — 'first wet' dead, film-thickness ablation survives",
    "G02": "narrow but clean — safest paper",
    "H01": "high-risk — IPC framing required, sim baseline exists",
    "Pneumatic_Soft_Actuator_Fatigue": "genuinely open",
    "Kirigami_Actuator_ForceStroke": "narrow but clean",
    "LowMeltingPoint_Alloy": "reframed",
    "Incipient_Slip_Detection": "narrowed",
    "PressureOnly_Soft_Robot": "crowded standalone — survives only in A01+A04 combo",
    "Tensegrity_Reservoir": "high-risk — IPC framing required",
}


def load_fields():
    with FIELDS_YAML.open() as f:
        data = yaml.safe_load(f)
    ordered = []
    if "fields" in data and isinstance(data["fields"], dict):
        for cat, items in data["fields"].items():
            if isinstance(items, list):
                for field in items:
                    if isinstance(field, dict) and "name" in field:
                        ordered.append((field["name"], cat))
    return ordered


def flatten(data):
    """Return flat {field: value} regardless of nesting."""
    flat = {}
    skip_top = set(CATEGORY_MAPPING.keys()) | {"field_categories"}
    for k, v in data.items():
        if k in SKIP_KEYS:
            continue
        if isinstance(v, dict) and k in skip_top:
            for sk, sv in v.items():
                if sk not in SKIP_KEYS:
                    flat[sk] = sv
        else:
            flat[k] = v
    return flat


def fmt_value(v, field_name=""):
    if v is None or v == "":
        return None
    if isinstance(v, list):
        if not v:
            return None
        if isinstance(v[0], dict):
            lines = []
            for item in v:
                lines.append(" | ".join(f"{k}: {val}" for k, val in item.items()))
            return "\n".join(f"- {l}" for l in lines)
        joined = ", ".join(str(x) for x in v)
        if len(joined) > 100:
            return "\n".join(f"- {x}" for x in v)
        return joined
    if isinstance(v, dict):
        parts = []
        for k, val in v.items():
            parts.append(f"**{k}**: {val}")
        return "; ".join(parts)
    s = str(v)
    if "[uncertain]" in s:
        return None
    return s


def slug(title):
    s = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


def load_results():
    items = []
    for f in sorted(RESULTS_DIR.glob("*.json")):
        with f.open() as fh:
            data = json.load(fh)
        flat = flatten(data)
        flat["_source_file"] = f.name
        items.append(flat)
    items.sort(key=lambda x: RANKINGS.get(x.get("id", ""), 99))
    return items


def write_report(items, fields):
    field_names = [name for name, _ in fields]
    lines = []

    # Header
    lines.append("# Novel Robotics Research — Deep Research Report\n")
    lines.append("> Generated from deep-research results. All gaps verified against all-timespan prior art.\n")

    # Executive summary
    lines.append("## Executive Summary\n")
    lines.append("| Rank | ID | Title | Lane | Difficulty | Cost Est | Verdict |")
    lines.append("|---|---|---|---|---|---|---|")
    for item in items:
        item_id = item.get("id", "?")
        title = item.get("title", item["_source_file"])
        title_short = title[:50] + "…" if len(title) > 50 else title
        lane = item.get("lane", "—")
        diff = item.get("difficulty", "—")
        cost = item.get("hardware_cost_est", "—")
        cost = cost[:20] if isinstance(cost, str) else str(cost)
        rank = RANKINGS.get(item_id, "—")
        # guess verdict from id or filename
        verdict = "—"
        for key in [item_id] + [item["_source_file"].split(".")[0][:20]]:
            for vk, vv in VERDICTS.items():
                if vk.lower() in key.lower() or key.lower() in vk.lower():
                    verdict = vv
                    break
            if verdict != "—":
                break
        anchor = slug(title)
        lines.append(f"| {rank} | {item_id} | [{title_short}](#{anchor}) | {lane} | {diff}/5 | {cost} | {verdict} |")
    lines.append("")

    # Combined A01+A04 call-out box
    lines.append("## Top Pick: A01+A04 Combined\n")
    lines.append("> **Combined gap (genuinely open):** P-V hysteresis as a fatigue leading indicator (A01) +")
    lines.append("> shared-manifold cross-talk breaking pressure-only proprioception (A04).")
    lines.append("> No paper fuses these two; the coupling between fatigue-induced P-V drift and")
    lines.append("> proprioceptive accuracy degradation is uniquely observable only in the combined study.\n")

    # Detailed sections
    lines.append("## Detailed Entries\n")
    for item in items:
        title = item.get("title", item["_source_file"])
        lines.append(f"### {title}\n")
        lines.append(f"**File:** `{item['_source_file']}`\n")

        # Print fields in definition order, then extras
        covered = set()
        for fname, fcat in fields:
            val = item.get(fname)
            fmtd = fmt_value(val, fname)
            if fmtd is None:
                continue
            covered.add(fname)
            label = fname.replace("_", " ").title()
            if len(fmtd) > 120 or "\n" in fmtd:
                lines.append(f"**{label}:**\n\n{fmtd}\n")
            else:
                lines.append(f"**{label}:** {fmtd}\n")

        # Extra fields not in fields.yaml
        extras = {ek: ev for ek, ev in item.items()
                  if ek not in covered and ek not in SKIP_KEYS
                  and ek != "_source_file" and ek != "uncertain"}
        extra_lines = [(ek, fmt_value(ev, ek)) for ek, ev in extras.items()]
        extra_lines = [(ek, ev) for ek, ev in extra_lines if ev]
        if extra_lines:
            lines.append("**Additional Fields:**\n")
            for ek, ev in extra_lines:
                lines.append(f"- **{ek}:** {ev}")
            lines.append("")

        # Uncertain fields
        uncertain = item.get("uncertain", [])
        if uncertain and isinstance(uncertain, list):
            lines.append(f"**Uncertain fields:** {', '.join(str(u) for u in uncertain)}\n")

        lines.append("---\n")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {OUTPUT}")
    print(f"Items: {len(items)}")


if __name__ == "__main__":
    fields = load_fields()
    items = load_results()
    write_report(items, fields)
