#!/usr/bin/env python3
"""Render docs/preprint_v1.md to a formatted PDF (reportlab).

Self-contained: no pandoc / LaTeX needed. Handles the markdown subset the preprint uses
(headings, paragraphs, **bold**/*italic*/`code`, bullet lists, pipe tables, --- rules,
![img](path) figures + italic captions) and embeds the figures. Unicode (Greek/math) is
supported by registering matplotlib's bundled DejaVuSans TTFs.

Run: python -m scripts.make_preprint_pdf   ->  docs/preprint_v1.pdf
"""

from __future__ import annotations

import os
import re

import matplotlib
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Image, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MD = os.path.join(REPO, "docs", "preprint_v1.md")
OUT = os.path.join(REPO, "docs", "preprint_v1.pdf")

# ── Unicode fonts (DejaVu ships with matplotlib) ────────────────────────────────
_FONTDIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(_FONTDIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(_FONTDIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Italic", os.path.join(_FONTDIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", os.path.join(_FONTDIR, "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                              italic="DejaVu-Italic", boldItalic="DejaVu-BoldItalic")

BLUE = HexColor("#1a5276")
_B = getSampleStyleSheet()["Normal"]
TITLE = ParagraphStyle("title", parent=_B, fontName="DejaVu-Bold", fontSize=15, leading=19,
                       alignment=TA_CENTER, spaceAfter=8)
H1 = ParagraphStyle("h1", parent=_B, fontName="DejaVu-Bold", fontSize=12.5, leading=15,
                    spaceBefore=12, spaceAfter=4, textColor=BLUE)
H2 = ParagraphStyle("h2", parent=_B, fontName="DejaVu-Bold", fontSize=10.5, leading=13,
                    spaceBefore=7, spaceAfter=3)
BODY = ParagraphStyle("body", parent=_B, fontName="DejaVu", fontSize=9.3, leading=13,
                      alignment=TA_JUSTIFY, spaceAfter=5)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=16, firstLineIndent=-9, spaceAfter=2)
CAPTION = ParagraphStyle("caption", parent=_B, fontName="DejaVu-Italic", fontSize=8.3,
                         leading=11, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=8)
CELL = ParagraphStyle("cell", parent=_B, fontName="DejaVu", fontSize=8.5, leading=11)
CELLH = ParagraphStyle("cellh", parent=CELL, fontName="DejaVu-Bold")


def inline(s: str) -> str:
    """Markdown inline -> reportlab mini-markup (escape, then bold/italic/code/links)."""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"!\[.*?\]\(.*?\)", "", s)                       # strip stray image md
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", s)                 # links -> text
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', s)
    s = s.replace(r"\*", "*").replace(r"\[", "[").replace(r"\]", "]")
    return s


def make_table(rows):
    grid = []
    for r, cells in enumerate(rows):
        style = CELLH if r == 0 else CELL
        grid.append([Paragraph(inline(c), style) for c in cells])
    tbl = Table(grid, hAlign="CENTER", repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#d6eaf8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#f2f3f4")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tbl


def figure(relpath):
    path = os.path.normpath(os.path.join(os.path.dirname(MD), relpath))
    iw, ih = ImageReader(path).getSize()
    w = 4.3 * inch
    img = Image(path, width=w, height=w * ih / iw)
    img.hAlign = "CENTER"
    return img


def build():
    lines = open(MD, encoding="utf-8").read().splitlines()
    story, para, tbl = [], [], []

    def flush_para():
        if para:
            story.append(Paragraph(inline(" ".join(para)), BODY))
            para.clear()

    def flush_tbl():
        if tbl:
            rows = [[c.strip() for c in row.strip().strip("|").split("|")] for row in tbl
                    if not re.match(r"^\|[\s:|-]+\|?\s*$", row)]
            story.append(make_table(rows)); story.append(Spacer(1, 6)); tbl.clear()

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("|"):
            flush_para(); tbl.append(line); continue
        flush_tbl()
        if not line.strip():
            flush_para(); continue
        m_img = re.match(r"^!\[.*?\]\((.+?)\)\s*$", line)
        if m_img:
            flush_para(); story.append(Spacer(1, 4)); story.append(figure(m_img.group(1))); continue
        if line.startswith("### "):
            flush_para(); story.append(Paragraph(inline(line[4:]), H2)); continue
        if line.startswith("## "):
            flush_para(); story.append(Paragraph(inline(line[3:]), H1)); continue
        if line.startswith("# "):
            flush_para(); story.append(Paragraph(inline(line[2:]), TITLE)); continue
        if line.strip() == "---":
            flush_para(); story.append(HRFlowable(width="100%", thickness=0.5,
                                                  color=colors.lightgrey, spaceBefore=4, spaceAfter=6)); continue
        if re.match(r"^\*[^*].*[^*]\*$", line.strip()):           # whole-line italic = caption
            flush_para(); story.append(Paragraph(inline(line.strip()[1:-1]), CAPTION)); continue
        if line.lstrip().startswith(("- ", "> ")):
            flush_para(); story.append(Paragraph("•&nbsp;" + inline(line.lstrip()[2:]), BULLET)); continue
        para.append(line.strip())
    flush_para(); flush_tbl()

    SimpleDocTemplate(OUT, pagesize=LETTER, leftMargin=0.9*inch, rightMargin=0.9*inch,
                      topMargin=0.9*inch, bottomMargin=0.9*inch,
                      title="P-V Loop Shape as a Fatigue Leading Indicator (preprint draft)").build(story)
    print(f"PDF written: {OUT}")


if __name__ == "__main__":
    build()
