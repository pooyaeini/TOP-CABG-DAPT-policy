"""Shared style, paths and helpers for the TOP-CABG revision figures.

Every figure script imports this module. Inputs are always read from files,
so the scripts can be rerun unchanged after background jobs finish.
"""
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# ---------------------------------------------------------------- paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TOPCABG_WORK", os.path.join(ROOT, "work"))
FIGS = os.environ.get("TOPCABG_FIGS", os.path.join(ROOT, "work"))
OUT = os.environ.get("TOPCABG_OUT", os.path.join(ROOT, "figures", "out"))


def work(*p):
    return os.path.join(WORK, *p)


def figs(*p):
    return os.path.join(FIGS, *p)


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------------- palette
FOREST = (0.12, 0.47, 0.71)      # causal survival forest
COMP = "#1aa37a"                 # comparator models
GREY = "0.45"                    # neutral bars
DARK = "0.25"                    # secondary series, reference marks
INK = "0.15"                     # text
VERM = (0.84, 0.37, 0.00)        # uniform 12-month DAPT
ORANGE = "#e69f00"               # second graft-risk model
ARM3 = FOREST                    # 3-month DAPT arm
ARM12 = VERM                     # 12-month DAPT arm

FS = 8          # base font size
FS_TITLE = 9    # panel titles
FS_NOTE = 7.5   # in-panel annotations

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": FS,
    "axes.titlesize": FS_TITLE,
    "axes.labelsize": FS,
    "xtick.labelsize": FS,
    "ytick.labelsize": FS,
    "legend.fontsize": FS_NOTE,
    "legend.frameon": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "text.color": INK,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "lines.linewidth": 1.3,
    "axes.unicode_minus": True,
    "savefig.dpi": 300,
    "figure.dpi": 100,
    "axes.titlelocation": "left",
    "axes.titlepad": 6,
})

MINUS = "−"


def f(x, d=2):
    """Format a number with a true minus sign; never print negative zero."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "NA"
    s = f"{x:.{d}f}"
    if float(s) == 0:
        s = f"{0:.{d}f}"
    return s.replace("-", MINUS)


def ci_text(est, lo, hi, d=2):
    return f"{f(est, d)} ({f(lo, d)} to {f(hi, d)})"


def title(ax, letter, text, **kw):
    """Panel title in the style of the originals, e.g. 'A  Causal survival forest'."""
    ax.set_title(f"{letter}  {text}", loc="left", fontsize=FS_TITLE, **kw)


def note(ax, x, y, s, ha="left", va="top", **kw):
    kw.setdefault("fontsize", FS_NOTE)
    kw.setdefault("color", INK)
    return ax.text(x, y, s, ha=ha, va=va, transform=ax.transAxes, **kw)


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, metadata={"Software": None, "Author": "Admin"})
    plt.close(fig)
    print(f"saved {path}")
    return path


def centered_bins(x, width, pad=1):
    """Histogram edges with a bin centered on zero, so exact zeros sit in one bar."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    lo = math.floor(x.min() / width - 0.5) - pad
    hi = math.ceil(x.max() / width + 0.5) + pad
    return (np.arange(lo, hi + 1) + 0.5) * width


def nice_width(span, target_bins=30):
    """A round bin width giving roughly target_bins bins over span."""
    if span <= 0:
        return 1.0
    raw = span / target_bins
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def text_size_in(fig, s, **kw):
    """Rendered width and height of a text string, in inches."""
    kw.setdefault("fontsize", FS)
    r = fig.canvas.get_renderer()
    t = fig.text(0, 0, s, **kw)
    bb = t.get_window_extent(renderer=r)
    t.remove()
    return bb.width / fig.dpi, bb.height / fig.dpi


def max_width_in(fig, strings, **kw):
    return max(text_size_in(fig, s, **kw)[0] for s in strings) if len(strings) else 0.0


def mc_se(p, r):
    return math.sqrt(max(p * (1 - p), 0) / r) if r > 0 else float("nan")
