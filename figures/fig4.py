"""Figure 4. Policy contrasts versus uniform 3-month DAPT.

Input
  figs/fig4_rows.csv  label, est, lo, hi, pct3, n12, method
Rows with no interval (lo or hi missing) are drawn as hollow markers at the
estimate and annotated with their method text (for example "zero by construction").
Colors follow the row label: uniform 12-month rows vermilion, forest rows blue,
other learned rules (comparators) teal. Bootstrap rule rows use a square marker.
Column widths are measured from the rendered text, so headers cannot collide.
"""
import textwrap

import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

import _common as C
from _common import plt

SHOW_ESTIMATE_COLUMN = True
ROW_IN = 0.37          # inches per row
GAP_IN = 0.22          # gap between text columns
W_IN = 7.5

d = pd.read_csv(C.figs("fig4_rows.csv"))
n = len(d)


def group(label):
    s = label.lower()
    if s.startswith("uniform 12"):
        return "uniform"
    if "forest" in s:
        return "forest"
    return "comparator"


COL = {"uniform": C.VERM, "forest": C.FOREST, "comparator": C.COMP}


def wrap(label, width=30):
    if len(label) <= width:
        return label
    if ", " in label:
        a, b = label.split(", ", 1)
        if len(a) <= width + 2 and len(b) <= width + 2:
            return f"{a},\n{b}"
    return textwrap.fill(label, width)


d["grp"] = d["label"].map(group)
d["has_ci"] = d["lo"].notna() & d["hi"].notna()
labels = [wrap(s) for s in d["label"]]

# ------------------------------------------------------------ column content
est_txt = [C.ci_text(r.est, r.lo, r.hi) if r.has_ci else C.f(r.est) for r in d.itertuples()]
p3_txt = ["NA" if pd.isna(v) else f"{v:.1f}" for v in d["pct3"]]
n12_txt = [("mean " + str(int(round(2290 * (1 - p / 100))))) if pd.isna(v) else f"{int(round(v))}" for v, p in zip(d["n12"], d["pct3"])]
H_EST = "Estimate, days\n(95% interval)"
H_SPAN = "Assigned to"
H_P3 = "3 months, %"
H_N12 = "12 months, n"

# ------------------------------------------------------------ geometry (inches)
TOP_UNITS = 1.75                     # header block above row 0, in row units
H_IN = ROW_IN * (n + TOP_UNITS) + 0.80
fig = plt.figure(figsize=(W_IN, H_IN))
bold = dict(fontweight="bold")
w_lab = C.max_width_in(fig, labels) + 0.12
w_est = max(C.max_width_in(fig, est_txt), C.max_width_in(fig, [H_EST], **bold)) \
    if SHOW_ESTIMATE_COLUMN else 0
w_p3 = max(C.max_width_in(fig, p3_txt), C.max_width_in(fig, [H_P3], **bold))
w_n12 = max(C.max_width_in(fig, n12_txt), C.max_width_in(fig, [H_N12], **bold))
w_span = C.max_width_in(fig, [H_SPAN], **bold)
w_p3 = w_n12 = max(w_p3, w_n12, (w_span - GAP_IN) / 2)
w_tab = (w_est + GAP_IN if SHOW_ESTIMATE_COLUMN else 0) + w_p3 + GAP_IN + w_n12
left, right = 0.04, 0.10
w_plot = W_IN - left - w_lab - GAP_IN - w_tab - right
if w_plot < 1.5:
    print(f"warning: forest plot area only {w_plot:.2f} in wide")
bottom_in, top_in = 0.72, 0.06
ax = fig.add_axes([(left + w_lab) / W_IN, bottom_in / H_IN, w_plot / W_IN,
                   (H_IN - bottom_in - top_in) / H_IN])
x0_tab = left + w_lab + w_plot + GAP_IN
tx = fig.add_axes([x0_tab / W_IN, bottom_in / H_IN, w_tab / W_IN,
                   (H_IN - bottom_in - top_in) / H_IN], sharey=ax)
tx.set_axis_off()

# ------------------------------------------------------------ forest plot
vals = np.r_[d["lo"].to_numpy(float), d["hi"].to_numpy(float), d["est"].to_numpy(float), 0]
lo_all, hi_all = np.nanmin(vals), np.nanmax(vals)
span = hi_all - lo_all
xlim = (lo_all - 0.06 * span, hi_all + 0.10 * span)
ax.set_xlim(*xlim)
ax.xaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 5, 10]))
ax.plot([0, 0], [-0.5, n - 0.5], color=C.INK, lw=0.9, zorder=1)

for i, r in d.iterrows():
    col = COL[r.grp]
    mk = "s" if "bootstrap" in str(r.method).lower() and r.grp != "uniform" else "o"
    if r.has_ci:
        ax.errorbar(r.est, i, xerr=[[r.est - r.lo], [r.hi - r.est]], fmt=mk, color=col,
                    ms=5.5 if mk == "o" else 5, capsize=2.5, elinewidth=1.3, capthick=1.3,
                    zorder=3)
    else:
        ax.plot(r.est, i, mk, ms=5.5, mfc="white", mec=col, mew=1.3, zorder=3)
        ax.annotate(str(r.method), xy=(r.est, i), xytext=(-7, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=C.FS_NOTE, color="0.35",
                    style="italic")

# thin separator between the uniform-policy rows and the learned-rule rows
fam = (d["grp"] == "uniform").to_numpy()
for i in range(1, n):
    if fam[i] != fam[i - 1]:
        for a in (ax, tx):
            a.axhline(i - 0.5, color="0.8", lw=0.6, zorder=0)

ax.set_yticks(np.arange(n), labels)
ax.tick_params(axis="y", length=0, pad=4)
ax.spines["left"].set_visible(False)
ax.set_ylim(n - 0.5, -TOP_UNITS)
ax.spines["bottom"].set_bounds(*xlim)
ax.set_xlabel("Difference in restricted mean event-free time\n"
              "versus uniform 3-month DAPT, days")

# ------------------------------------------------------------ text columns
tx.set_xlim(0, w_tab)          # axis units are inches
BASE = -0.62                   # bottom of the lower header line, row units
LINE = 0.40                    # one header line, row units
x = 0.0
if SHOW_ESTIMATE_COLUMN:
    tx.text(x, BASE, H_EST, ha="left", va="bottom", linespacing=1.15, **bold)
    for i, v in enumerate(est_txt):
        tx.text(x, i, v, ha="left", va="center")
    x += w_est + GAP_IN
c_p3 = x + w_p3 / 2
c_n12 = x + w_p3 + GAP_IN + w_n12 / 2
for c, h, vs in ((c_p3, H_P3, p3_txt), (c_n12, H_N12, n12_txt)):
    tx.text(c, BASE, h, ha="center", va="bottom", **bold)
    for i, v in enumerate(vs):
        tx.text(c, i, v, ha="center", va="center")
tx.text((c_p3 + c_n12) / 2, BASE - LINE - 0.14, H_SPAN, ha="center", va="bottom", **bold)
tx.plot([x, x + w_p3 + GAP_IN + w_n12], [BASE - LINE - 0.08] * 2, color=C.INK, lw=0.6,
        clip_on=False)

C.save(fig, "Figure4.png")
