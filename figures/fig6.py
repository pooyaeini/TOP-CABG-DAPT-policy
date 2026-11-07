"""Figure 6. Sensitivity analyses, average effect and learned rule contrast.

Inputs
  figs/fig6_rows.csv   key, label, n, mean, lo, hi, contrast, clo, chi, n12, model
  work/primary.json    policy.csf[0] is the primary mean score (dotted reference line)
Rows with model == "comparator" are drawn in teal, forest rows in blue.
Column widths are measured from the rendered text, so headers cannot collide.
"""
import textwrap

import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

import _common as C
from _common import plt

ROW_IN = 0.33
GAP_IN = 0.20
W_IN = 7.5
WRAP = 30

d = pd.read_csv(C.figs("fig6_rows.csv"))
n = len(d)
pj = C.load_json(C.work("primary.json"))
try:
    primary = float(pj["policy"]["csf"][0])
except (KeyError, IndexError, TypeError):
    primary = float(pd.read_csv(C.work("primary_patients.csv"))["gamma"].mean())

col = [C.COMP if str(m).lower().startswith("comp") else C.FOREST for m in d["model"]]
def balanced_wrap(s, width=WRAP):
    """One line when short; otherwise two lines split at the most even space."""
    if len(s) <= width:
        return s
    sp = [i for i, ch in enumerate(s) if ch == " "]
    if not sp:
        return s
    i = min(sp, key=lambda k: max(k, len(s) - k - 1))
    a, b = s[:i], s[i + 1:]
    if max(len(a), len(b)) > width + 8:
        return textwrap.fill(s, width)
    return f"{a}\n{b}"


labels = [balanced_wrap(s) for s in d["label"]]

con_txt = [C.f(v) for v in d["contrast"]]
n12_txt = ["NA" if pd.isna(v) else f"{int(round(v))}" for v in d["n12"]]
nev_txt = ["NA" if pd.isna(v) else f"{int(round(v))}" for v in d["n"]]
HEADS = ["Contrast,\ndays", "Assigned to\n12 months, n", "Participants\nevaluated"]
COLS = [con_txt, n12_txt, nev_txt]

TOP_UNITS = 1.55
H_IN = ROW_IN * (n + TOP_UNITS) + 0.95
fig = plt.figure(figsize=(W_IN, H_IN))
bold = dict(fontweight="bold")
w_lab = C.max_width_in(fig, labels) + 0.10
w_cols = [max(C.max_width_in(fig, v), C.max_width_in(fig, [h], **bold)) for h, v in zip(HEADS, COLS)]
w_tab = sum(w_cols) + GAP_IN * (len(w_cols) - 1)
left, right = 0.04, 0.14
w_b = 0.90
gap_ab = 0.40
w_a = W_IN - left - w_lab - gap_ab - w_b - GAP_IN - w_tab - right
if w_a < 1.5:
    print(f"warning: panel A only {w_a:.2f} in wide")
bottom_in, top_in = 0.62, 0.30
hh = (H_IN - bottom_in - top_in) / H_IN
xa = left + w_lab
xb = xa + w_a + gap_ab
xt = xb + w_b + GAP_IN
axA = fig.add_axes([xa / W_IN, bottom_in / H_IN, w_a / W_IN, hh])
axB = fig.add_axes([xb / W_IN, bottom_in / H_IN, w_b / W_IN, hh], sharey=axA)
tx = fig.add_axes([xt / W_IN, bottom_in / H_IN, w_tab / W_IN, hh], sharey=axA)
tx.set_axis_off()
y = np.arange(n)

# ------------------------------------------------------------ A average effect
lo = min(d["lo"].min(), 0)
hi = max(d["hi"].max(), primary)
span = hi - lo
xlimA = (lo - 0.05 * span, hi + 0.05 * span)
axA.set_xlim(*xlimA)
axA.xaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 5, 10]))
axA.plot([0, 0], [-0.5, n - 0.5], color=C.INK, lw=0.9, zorder=1)
axA.plot([primary, primary], [-0.75, n - 0.5], color="0.35", lw=1.0, ls=(0, (1.2, 1.6)),
         zorder=1)
axA.text(primary, -0.85, f"primary {C.f(primary)} days", ha="center", va="bottom",
         fontsize=C.FS_NOTE, color="0.35")
for i, r in d.iterrows():
    axA.errorbar(r["mean"], i, xerr=[[r["mean"] - r["lo"]], [r["hi"] - r["mean"]]], fmt="o",
                 color=col[i], ms=5, capsize=2.2, elinewidth=1.2, capthick=1.2, zorder=3)
axA.set_yticks(y, labels)
axA.tick_params(axis="y", length=0, pad=4)
axA.spines["left"].set_visible(False)
axA.spines["bottom"].set_bounds(*xlimA)
axA.set_ylim(n - 0.5, -TOP_UNITS)
axA.set_xlabel("Average benefit of 3-month\nDAPT, days")

# ------------------------------------------------------------ B contrast
clo = np.nanmin(np.r_[d["clo"], d["contrast"], 0])
chi = np.nanmax(np.r_[d["chi"], d["contrast"], 0])
cspan = chi - clo
if cspan < 0.5:
    pad = (0.5 - cspan) / 2
    clo, chi, cspan = clo - pad, chi + pad, 0.5
xlimB = (clo - 0.12 * cspan, chi + 0.12 * cspan)
axB.set_xlim(*xlimB)
axB.xaxis.set_major_locator(MaxNLocator(nbins=3, steps=[1, 2, 5, 10]))
axB.plot([0, 0], [-0.5, n - 0.5], color=C.INK, lw=0.9, zorder=1)
for i, r in d.iterrows():
    xe = [[max(r.contrast - r.clo, 0)], [max(r.chi - r.contrast, 0)]]
    axB.errorbar(r.contrast, i, xerr=xe, fmt="o", color=col[i], ms=5, capsize=2.2,
                 elinewidth=1.2, capthick=1.2, zorder=3)
axB.tick_params(axis="y", left=False, labelleft=False)
axB.spines["left"].set_visible(False)
axB.spines["bottom"].set_bounds(*xlimB)
axB.set_xlabel("Learned rule minus\nuniform 3 months, days")

# ------------------------------------------------------------ text columns
tx.set_xlim(0, w_tab)
BASE = -0.62
x = 0.0
for h, vals, w in zip(HEADS, COLS, w_cols):
    c = x + w / 2
    tx.text(c, BASE, h, ha="center", va="bottom", linespacing=1.15, **bold)
    for i, v in enumerate(vals):
        tx.text(c, i, v, ha="center", va="center")
    x += w + GAP_IN

# ------------------------------------------------------------ panel titles
ty = 1 - (top_in - 0.06) / H_IN
fig.text(left / W_IN, ty, "A  Average effect in each analysis", fontsize=C.FS_TITLE,
         ha="left", va="bottom")
fig.text(xb / W_IN, ty, "B  Learned rule versus uniform 3 months", fontsize=C.FS_TITLE,
         ha="left", va="bottom")

C.save(fig, "Figure6.png")
