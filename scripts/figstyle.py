"""Shared style for every result figure under data/gate0 and data/sim.

Usage:
    from scripts import figstyle
    plt = figstyle.setup()
    fig, ax = plt.subplots(figsize=(figstyle.FULL, 2.6))
    ax.plot(life, area, color=figstyle.COLOR["pv"])
    ax.set_title("P-V loop area rises with life")       # left-aligned, regular weight
    figstyle.footnote(fig, "Simulation: 6 held-out actuators.")
    figstyle.save(fig, os.path.join(DATA, "study2_fig1_drift"))   # .png (300 dpi) + .pdf

Fonts use three sizes, picked by role: SIZE["label"] for titles, axis labels and
series names, SIZE["note"] for legends and annotations, SIZE["tick"] for tick
labels. Panel letters are the one exception.

COLOR gives each entity one colour, used in every figure. The hues come from the
Okabe-Ito palette (Wong, Nature Methods 2011), which stays readable with
red-green colour blindness. Vermillion marks anything driven by the pressure or
P-V signal, blue anything driven by cycle count alone, grays the reference
policies. PDF and SVG files carry no creation date, so a rerun writes the same bytes.
"""

from __future__ import annotations

FULL = 7.2      # in, double-column width (183 mm)
WIDE = 5.4      # in, one-and-a-half column
SINGLE = 3.5    # in, single-column width (89 mm)

SIZE = {"label": 9, "note": 8, "tick": 7, "letter": 10}

COLOR = {
    # signals and the methods built on them
    "pv": "#D55E00",            # P-V loop area, the P-V trigger, pressure-feature estimators
    "clock": "#0072B2",         # cycle-count clock and clock-only estimators
    "fixed": "#8C8C8C",         # initial calibration only (never recalibrate)
    "always": "#3B3B3B",        # recalibrate at every life stage
    "fused": "#3B3B3B",         # fused health index (Study 1)
    # physical quantities and model parameters
    "compliance": "#009E73",    # wall compliance and manifold compliance C_m
    "supply": "#CC79A7",        # supply resistance R_s and the shared-manifold topology
    "isolated": "#8C8C8C",      # isolated supply topology
    "leak": "#E69F00",          # leak conductance
    "onset": "#56B4E9",         # acceleration-onset fraction
    "tau": "#8C8C8C",           # viscoelastic time constant
    # neutral marks
    "ref": "#4D4D4D",           # thresholds, budgets and other reference lines
    "muted": "#595959",         # footnotes and secondary text
    "unit": "#9A9A9A",          # individual simulated units drawn as context
}

_DARKEN = 0.72  # text in a series colour is drawn darker so it reads on white


def ink(color: str) -> str:
    """Darker variant of ``color`` for text labels (lines keep the full colour)."""
    h = color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#{:02X}{:02X}{:02X}".format(*(round(c * _DARKEN) for c in (r, g, b)))


def ramp(color: str, n: int):
    """``n`` shades of one hue, light to dark, for an ordered variable (life stage, compliance step)."""
    h = color.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    out = []
    for k in range(n):
        t = k / max(n - 1, 1)                      # 0 = light tint, 0.5 = the colour, 1 = dark shade
        if t <= 0.5:
            mix = [c + (1 - c) * 0.6 * (1 - t / 0.5) for c in rgb]
        else:
            mix = [c * (1 - 0.45 * (t - 0.5) / 0.5) for c in rgb]
        out.append("#{:02X}{:02X}{:02X}".format(*(round(255 * c) for c in mix)))
    return out


def apply():
    import matplotlib as mpl

    mpl.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "font.family": "DejaVu Sans",
        "font.size": SIZE["label"],
        "axes.titlesize": SIZE["label"],
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.titlepad": 6,
        "axes.labelsize": SIZE["label"],
        "axes.linewidth": 0.6,
        "axes.edgecolor": "#222222",
        "axes.labelcolor": "#222222",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "grid.color": "#E3E3E3",
        "grid.linewidth": 0.5,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.size": 1.8,
        "ytick.minor.size": 1.8,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.labelsize": SIZE["tick"],
        "ytick.labelsize": SIZE["tick"],
        "xtick.color": "#222222",
        "ytick.color": "#222222",
        "legend.frameon": False,
        "legend.fontsize": SIZE["note"],
        "legend.title_fontsize": SIZE["note"],
        "legend.handlelength": 1.8,
        "legend.borderaxespad": 0.3,
        "lines.linewidth": 1.4,
        "lines.markersize": 4.5,
        "lines.markeredgewidth": 0.8,
        "patch.linewidth": 0.6,
        "image.cmap": "cividis",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "soft-actuator-figures",
        "axes.prop_cycle": mpl.cycler(color=[COLOR[k] for k in ("clock", "pv", "compliance", "supply", "leak", "onset")]),
    })


def setup(style: bool = True):
    """Headless pyplot (with the shared style unless ``style=False``), or None if matplotlib is unavailable."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:  # pragma: no cover
        return None
    if style:
        apply()
    return plt


def panel_letter(ax, letter: str, dx: float = -26):
    """Bold panel letter above the top-left corner of ``ax``; ``dx`` (points) clears the tick labels."""
    ax.annotate(letter, xy=(0, 1), xycoords="axes fraction", xytext=(dx, 6),
                textcoords="offset points", fontsize=SIZE["letter"], fontweight="bold",
                ha="left", va="bottom")


def footnote(fig, text: str):
    """Evidence note under everything else on the figure: what was simulated, n, what was held fixed.

    Call it last, just before save(), so it lands below the lowest axis label.
    """
    import textwrap

    fig.canvas.draw()
    box = fig.get_tightbbox(fig.canvas.get_renderer())
    w, h = fig.get_size_inches()
    chars = int(box.width * 72 / (0.56 * SIZE["note"]))     # DejaVu Sans averages ~0.56 em per character
    wrapped = textwrap.fill(" ".join(text.split()), width=max(chars, 40))
    fig.text(box.x0 / w, (box.y0 - 4 / 72) / h, wrapped, fontsize=SIZE["note"], color=COLOR["muted"],
             ha="left", va="top")


def end_label(ax, x, y, text: str, color: str, dx: float = 4, dy: float = 0, ha: str = "left"):
    """Direct label at the end of a line, in a darker shade of the line colour."""
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=SIZE["note"],
                color=ink(color), va="center", ha=ha, annotation_clip=False)


def save(fig, path_stem, formats=("png", "pdf")):
    """Write ``path_stem.<fmt>`` for each format: 300-dpi PNG, dateless PDF/SVG."""
    meta = {"pdf": {"CreationDate": None}, "svg": {"Date": None}}
    for fmt in formats:
        out = f"{path_stem}.{fmt}"
        fig.savefig(out, metadata=meta.get(fmt))
        if fmt == "svg":
            with open(out) as fh:
                lines = [line.rstrip() for line in fh.read().splitlines()]
            with open(out, "w") as fh:
                fh.write("\n".join(lines) + "\n")
