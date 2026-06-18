#!/usr/bin/env python3
"""Render Draft 1 (A01+A04 Combined) to a formatted academic PDF."""
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from pathlib import Path

OUT = Path(__file__).parent / "Draft1_A01_A04_Combined.pdf"

# ── Styles ────────────────────────────────────────────────────────────────────
BASE = getSampleStyleSheet()

TITLE = ParagraphStyle("title", parent=BASE["Normal"],
    fontSize=15, leading=20, alignment=TA_CENTER,
    fontName="Helvetica-Bold", spaceAfter=4)

AUTHORS = ParagraphStyle("authors", parent=BASE["Normal"],
    fontSize=10, leading=14, alignment=TA_CENTER,
    fontName="Helvetica", spaceAfter=2)

AFFIL = ParagraphStyle("affil", parent=BASE["Normal"],
    fontSize=9, leading=12, alignment=TA_CENTER,
    fontName="Helvetica-Oblique", spaceAfter=10, textColor=colors.grey)

VENUE = ParagraphStyle("venue", parent=BASE["Normal"],
    fontSize=9, leading=12, alignment=TA_CENTER,
    fontName="Helvetica", spaceAfter=14,
    textColor=HexColor("#1a5276"))

H1 = ParagraphStyle("h1", parent=BASE["Normal"],
    fontSize=11, leading=14, fontName="Helvetica-Bold",
    spaceBefore=14, spaceAfter=4,
    textColor=HexColor("#1a5276"))

H2 = ParagraphStyle("h2", parent=BASE["Normal"],
    fontSize=10, leading=13, fontName="Helvetica-Bold",
    spaceBefore=8, spaceAfter=3)

BODY = ParagraphStyle("body", parent=BASE["Normal"],
    fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY,
    fontName="Helvetica", spaceAfter=6)

ABSTRACT_BOX = ParagraphStyle("abstract", parent=BASE["Normal"],
    fontSize=9, leading=13, alignment=TA_JUSTIFY,
    fontName="Helvetica", leftIndent=18, rightIndent=18,
    spaceBefore=4, spaceAfter=6)

ABSTRACT_HEAD = ParagraphStyle("abstract_head", parent=BASE["Normal"],
    fontSize=9, leading=13, fontName="Helvetica-Bold",
    leftIndent=18, spaceAfter=2)

BULLET = ParagraphStyle("bullet", parent=BASE["Normal"],
    fontSize=9.5, leading=13, fontName="Helvetica",
    leftIndent=18, firstLineIndent=-10, spaceAfter=3)

CAPTION = ParagraphStyle("caption", parent=BASE["Normal"],
    fontSize=8.5, leading=12, fontName="Helvetica-Oblique",
    alignment=TA_CENTER, spaceAfter=6)

NOTE = ParagraphStyle("note", parent=BASE["Normal"],
    fontSize=8.5, leading=12, fontName="Helvetica",
    textColor=colors.grey, leftIndent=18, rightIndent=18, spaceAfter=4)

def p(text, style=None):
    return Paragraph(text, style or BODY)

def h1(text): return Paragraph(text, H1)
def h2(text): return Paragraph(text, H2)
def sp(h=6): return Spacer(1, h)
def hr(): return HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4)

# ── Placeholder result table helper ──────────────────────────────────────────
def result_table(headers, rows, col_widths=None):
    data = [headers] + rows
    style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HexColor("#d6eaf8")),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8.5),
        ("GRID",       (0,0), (-1,-1), 0.4, colors.grey),
        ("ALIGN",      (1,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, HexColor("#f2f3f4")]),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ])
    tbl = Table(data, colWidths=col_widths, style=style, repeatRows=1)
    return tbl

# ── Document content ───────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=LETTER,
        leftMargin=1*inch, rightMargin=1*inch,
        topMargin=1*inch, bottomMargin=1*inch,
        title="P-V Hysteresis as a Fatigue Leading Indicator — Draft",
        author="NYU MechE",
    )

    story = []

    # ── Title block ──
    story += [
        p("ROUGH DRAFT — NOT FOR DISTRIBUTION", ParagraphStyle("warn",
            parent=BASE["Normal"], fontSize=8, alignment=TA_CENTER,
            textColor=colors.red, fontName="Helvetica-Bold", spaceAfter=8)),
        p("P-V Hysteresis as a Fatigue Leading Indicator and Its Degradation of "
          "Pressure-Only Proprioception in Shared-Manifold Soft Grippers", TITLE),
        p("[Author Name] · New York University, Tandon School of Engineering", AUTHORS),
        p("Department of Mechanical and Aerospace Engineering · New York, NY 10012", AFFIL),
        p("Target: <i>Soft Robotics</i> (Mary Ann Liebert) · IEEE RA-L  |  "
          "Est. length: 8 pp + supplementary  |  Hardware: ~$320", VENUE),
        hr(),
    ]

    # ── Abstract ──
    story += [
        p("Abstract", ABSTRACT_HEAD),
        p("Soft pneumatic grippers present two concurrent monitoring challenges: "
          "detecting actuator fatigue before rupture and reconstructing gripper pose "
          "from existing pressure signals without additional sensors. Prior work "
          "addresses each in isolation. We show that a shared pneumatic manifold — "
          "the most practical topology for multi-finger grippers — creates a third, "
          "previously uncharacterized challenge: inter-chamber pressure cross-talk "
          "couples both problems. We fabricate a three-chamber silicone gripper on a "
          "shared manifold and make two primary contributions. First, we demonstrate "
          "that pressure-volume (P-V) hysteresis loop shape is a reliable leading "
          "indicator of silicone actuator fatigue, with measurable loop-shape change "
          "detectable [<i>X</i>] cycles before mechanical rupture (N=10). Second, we show "
          "that shared-manifold cross-talk degrades pressure-only pose reconstruction "
          "accuracy from [<i>A</i>]% to [<i>B</i>]%, and that a cross-talk correction model "
          "recovers accuracy to within [<i>C</i>]% of the isolated-chamber baseline. We "
          "further characterize how fatigue-induced P-V drift and proprioceptive "
          "accuracy degradation are coupled: as an actuator ages, the P-V signature "
          "shift that signals fatigue also shifts the cross-talk correction model, "
          "causing both to fail simultaneously. Joint monitoring from the same "
          "pressure stream is therefore necessary and sufficient for health-aware "
          "soft gripper autonomy.", ABSTRACT_BOX),
        sp(4),
        hr(),
    ]

    # ── 1. Introduction ──
    story += [
        h1("1. Introduction"),
        p("Soft pneumatic actuators are increasingly deployed in grippers, medical "
          "devices, and wearable systems due to their compliance and inherent safety. "
          "Two monitoring problems arise in practice. The first is <b>health monitoring</b>: "
          "silicone actuators fail by cyclic fatigue, but current practice detects "
          "failure only after rupture — a brittle, unrecoverable event. The second is "
          "<b>proprioception</b>: knowing the gripper's pose without expensive external "
          "sensors is essential for closed-loop control."),
        p("Recent work showed that control-loop pressure readings can reconstruct pose "
          "in isolated single-chamber or independently-driven multi-chamber designs "
          "[Wang et al., <i>Soft Robotics</i> 10(4) 2023, DOI 10.1089/soro.2021.0056; "
          "Wang et al., <i>Adv. Intell. Syst.</i> 7(4) 2025, arXiv:2411.07309]. However, "
          "these designs assume each chamber's pressure is independently controllable. "
          "In practice, multi-finger grippers share a pneumatic manifold to reduce "
          "valve count and system complexity — a coupling these prior works do not address."),
        p("We identify a compounded gap. No prior work (1) uses the in-loop P-V "
          "hysteresis signature as a fatigue <i>leading indicator</i>, (2) characterizes "
          "how shared-manifold cross-talk affects pressure-only proprioception, or "
          "(3) shows that these two phenomena are coupled. Roels et al. "
          "(<i>Adv. Intell. Syst.</i> 2026, DOI 10.1002/aisy.202500699) standardized "
          "elastomer characterization but explicitly excluded fatigue; Torzini et al. "
          "(2024, DOI 10.1007/s00170-024-14216-0) and Libby et al. (2022, "
          "arXiv:2212.03420) report only cycles-to-failure or FEM deviation — "
          "neither uses P-V loop shape as a health signal."),
        p("This paper makes three contributions:"),
        p("(1) A cyclic P-V signature dataset for Dragon Skin 20A silicone actuators "
          "showing statistically measurable loop-shape change [<i>X</i>] cycles before "
          "rupture (N=10 actuators).", BULLET),
        p("(2) A cross-talk characterization and correction method for three-chamber "
          "shared-manifold grippers, recovering pose reconstruction accuracy from "
          "[<i>B</i>]% to [<i>C</i>]% (isolated baseline: [<i>A</i>]%).", BULLET),
        p("(3) A joint health-and-pose monitoring framework demonstrating that fatigue "
          "and cross-talk failure modes are coupled and must be tracked from the "
          "same pressure stream.", BULLET),
    ]

    # ── 2. Background ──
    story += [
        h1("2. Background and Related Work"),
        h2("2.1  Soft Actuator Fatigue"),
        p("Cyclic fatigue in soft pneumatic actuators is under-characterized relative "
          "to rigid-body systems. Roels et al. (2026) provide a standardized "
          "framework for elastomer property measurement but explicitly scope out "
          "fatigue. Existing fatigue studies report only cycles-to-failure counts "
          "or FEM-predicted pressure deviation at end-of-life. No prior work "
          "extracts loop-shape features from in-loop P-V data as a health signal, "
          "analogous to acoustic emission in metal fatigue monitoring."),
        h2("2.2  Pressure-Only Proprioception"),
        p("Wang et al. (<i>Soft Robotics</i> 2023) used unified soft-body encoding "
          "with an RNN to reconstruct pose from internal pressure on a single-chamber "
          "finger. Wang et al. (<i>Adv. Intell. Syst.</i> 2025) demonstrated physical "
          "reservoir computing on a fabric arm driven by internal pressures alone. "
          "Both assume isolated, independently driven chambers. The shared-manifold "
          "cross-talk condition — where actuating valve <i>i</i> changes pressure in "
          "chamber <i>j</i> — has not been studied, and constitutes the remaining gap "
          "in pressure-only proprioception."),
    ]

    # ── 3. Hardware ──
    story += [
        h1("3. Hardware Design"),
        h2("3.1  Gripper Fabrication"),
        p("Three-chamber Dragon Skin 20A silicone gripper cast in a [<i>dimensions</i>] "
          "mold using standard two-part molding. Chambers share a single brass manifold "
          "block with one solenoid valve per chamber (Parker or equivalent). One "
          "Honeywell HSC series pressure sensor (±0.5% FS, 0–100 kPa range) is "
          "tee-fitted per chamber. All sensors sampled at 100 Hz via a "
          "microcontroller (Teensy 4.1 or equivalent)."),
        h2("3.2  Pressure Cycling Jig"),
        p("A pneumatic cycling jig inflates and deflates each actuator between 0 and "
          "[<i>P</i><sub>max</sub>] kPa at [<i>f</i>] Hz via a solenoid valve and "
          "regulated supply. P-V loops are recorded continuously; end-of-life is "
          "defined as &gt;20% pressure drop within a single cycle."),
        h2("3.3  Motion Capture Ground Truth"),
        p("A 6-marker OptiTrack (or Vicon) setup records gripper fingertip pose at "
          "120 Hz. Hardware trigger synchronizes pose and pressure streams to "
          "&lt;1 ms jitter."),
    ]

    # ── 4. P-V Fatigue ──
    story += [
        h1("4. P-V Fatigue Signature Study"),
        h2("4.1  Protocol"),
        p("N=10 Dragon Skin actuators are cycled to failure. P-V loops are sampled "
          "in 50-cycle blocks. Five features are extracted per block:"),
        p("• <b>Loop area</b> (hysteresis energy, J)", BULLET),
        p("• <b>Peak pressure</b> at full inflation (kPa)", BULLET),
        p("• <b>Pressure at 80% volume</b> (inflation slope indicator)", BULLET),
        p("• <b>Loop asymmetry ratio</b> (inflation vs. deflation area)", BULLET),
        p("• <b>PC1 score</b> from PCA on loop shape across all actuators", BULLET),
        h2("4.2  Degradation Model"),
        p("For each feature, a logistic degradation model is fit to normalized cycle "
          "count. Lead-time is defined as the number of cycles before rupture at "
          "which the feature first exceeds 2σ from its healthy-baseline distribution. "
          "AUC of an early-warning classifier (feature threshold vs. rupture within "
          "next [<i>K</i>] cycles) is reported."),
        h2("4.3  Results (Placeholder)"),
        sp(4),
        result_table(
            ["Feature", "Lead-time (cycles)", "AUC", "p-value"],
            [
                ["P-V area",        "TBD", "TBD", "TBD"],
                ["Peak pressure",   "TBD", "TBD", "TBD"],
                ["Pressure@80%vol", "TBD", "TBD", "TBD"],
                ["Asymmetry ratio", "TBD", "TBD", "TBD"],
                ["PC1 score",       "TBD", "TBD", "TBD"],
            ],
            col_widths=[2.2*inch, 1.4*inch, 1.0*inch, 1.0*inch],
        ),
        p("Table 1. Fatigue leading indicator comparison across five P-V features. "
          "Lead-time = cycles before rupture at which feature exceeds 2σ from baseline.", CAPTION),
    ]

    # ── 5. Cross-Talk ──
    story += [
        h1("5. Cross-Talk Characterization and Correction"),
        h2("5.1  Cross-Talk Measurement"),
        p("With chambers 2 and 3 sealed and valve 1 actuated across [<i>N</i>] "
          "pressure levels (0–[<i>P</i><sub>max</sub>] kPa), pressure changes in "
          "chambers 2 and 3 are recorded. This is repeated for all three chamber "
          "pairs, yielding a 3×3 cross-talk coupling matrix at each pressure level."),
        h2("5.2  Correction Models"),
        p("Three models are compared for pose reconstruction from all three "
          "chamber pressures under shared-manifold coupling:"),
        p("(1) <b>Uncorrected baseline</b> — direct pressure-to-pose regression "
          "(ridge regression) with no cross-talk compensation.", BULLET),
        p("(2) <b>ARX-corrected</b> — autoregressive model with exogenous inputs "
          "subtracts estimated cross-talk component before regression.", BULLET),
        p("(3) <b>Echo-state network (ESN)</b> — reservoir of 100 nodes implicitly "
          "learns cross-talk dynamics.", BULLET),
        h2("5.3  Results (Placeholder)"),
        sp(4),
        result_table(
            ["Model", "RMSE (mm)", "R²", "Inference (ms)"],
            [
                ["Uncorrected baseline", "TBD", "TBD", "TBD"],
                ["ARX-corrected",        "TBD", "TBD", "TBD"],
                ["Echo-state network",   "TBD", "TBD", "TBD"],
            ],
            col_widths=[2.5*inch, 1.2*inch, 0.9*inch, 1.2*inch],
        ),
        p("Table 2. Pose reconstruction accuracy under shared-manifold cross-talk. "
          "N=2000 pose-labeled traces per condition.", CAPTION),
    ]

    # ── 6. Coupled Failure ──
    story += [
        h1("6. Coupled Failure Analysis"),
        p("At [<i>X</i>]% of actuator life, fatigue-induced P-V drift shifts the "
          "cross-talk correction model coefficients by [<i>Y</i>]%, degrading "
          "proprioceptive RMSE from [<i>C</i>] mm to [<i>D</i>] mm. A joint "
          "recalibration policy — triggered by the P-V health monitor crossing its "
          "2σ threshold — is evaluated: recalibration restores proprioceptive RMSE "
          "to within [<i>E</i>] mm of the fresh-actuator baseline."),
        p("This section is the core contribution distinguishing the combined study "
          "from two independent papers: the coupling is only observable when both "
          "are measured simultaneously on the same pressure stream."),
    ]

    # ── 7. Discussion ──
    story += [
        h1("7. Discussion"),
        p("<b>Scope.</b> N=10 actuators, single material (Dragon Skin 20A), one "
          "gripper geometry, one manifold configuration. Results may not generalize "
          "to different silicone formulations or larger finger counts without "
          "re-characterization."),
        p("<b>Natural extensions.</b> Self-healing elastomers (A05 in outline) would "
          "shift the P-V signature in a way that requires re-validation of the "
          "health monitor. Fatigue-aware adaptive control — adjusting grip force as "
          "actuator life decreases — is a direct follow-on."),
        p("<b>Comparison to external sensing.</b> A future study should benchmark "
          "P-V-based health monitoring against visual inspection and acoustic emission "
          "as a rigorous comparison, rather than treating visual inspection as the "
          "only baseline."),
    ]

    # ── 8. Conclusion ──
    story += [
        h1("8. Conclusion"),
        p("We demonstrated that P-V hysteresis loop shape predicts silicone actuator "
          "fatigue [<i>X</i>] cycles before rupture, that shared-manifold cross-talk "
          "degrades pressure-only proprioception in a characterizable and correctable "
          "way, and that the two phenomena are coupled: joint monitoring from the same "
          "pressure stream is both necessary and sufficient for health-aware soft "
          "gripper control. The contribution is not either experiment alone — both "
          "have partial prior art — but the coupled failure mode and the joint "
          "monitoring framework, which require the combined study to observe."),
        sp(8),
        hr(),
    ]

    # ── References ──
    story += [
        h1("References"),
        p('[1] L. Wang et al., "Soft Robot Proprioception Using Unified Soft Body Encoding '
          'and RNN," <i>Soft Robotics</i> 10(4), 2023. DOI: 10.1089/soro.2021.0056', BULLET),
        p('[2] J. Wang et al., "Fabric Soft Robotic Arm via Physical Reservoir Computing," '
          '<i>Adv. Intell. Syst.</i> 7(4), 2025. arXiv:2411.07309', BULLET),
        p('[3] E. Roels et al., "A Standardized Framework for Elastomer Characterization '
          'in Soft Robotics," <i>Adv. Intell. Syst.</i>, 2026. DOI: 10.1002/aisy.202500699', BULLET),
        p('[4] M. Torzini et al., 2024. DOI: 10.1007/s00170-024-14216-0', BULLET),
        p('[5] T. Libby et al., 2022. arXiv:2212.03420', BULLET),
        sp(12),
        p("— <i>Draft generated 2026-06-17. All result cells marked TBD require "
          "experimental data. Verify all DOIs before submission.</i>", NOTE),
    ]

    doc.build(story)
    print(f"PDF written to: {OUT}")

if __name__ == "__main__":
    build()
