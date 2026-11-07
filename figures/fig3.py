"""Figure 3. Predicted benefit distributions and score by predicted benefit group.

Inputs
  work/primary_patients.csv  tau, tau_pw, tau_pwf
  work/primary.json          groups, calib
"""
import numpy as np
import pandas as pd

import _common as C
from _common import plt

pp = pd.read_csv(C.work("primary_patients.csv"))
pj = C.load_json(C.work("primary.json"))
N = len(pp)

fig, axes = plt.subplots(1, 3, figsize=(7.5, 3.05), layout="constrained",
                         gridspec_kw={"width_ratios": [0.8, 1.14, 1.12]})
fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.06)

# ------------------------------------------------------------ A forest
ax = axes[0]
tau = pp["tau"].to_numpy(float)
w = C.nice_width(tau.max() - min(tau.min(), 0), 40)
bins = np.arange(np.floor(min(tau.min(), 0) / w) * w, tau.max() + w, w)
cnt, _, _ = ax.hist(tau, bins=bins, color=C.FOREST, edgecolor="white", linewidth=0.3)
ax.set_ylim(0, cnt.max() * 1.42)
ax.axvline(0, ymax=0.74, color=C.INK, lw=1)  # stops below the annotation
ax.set_xlim(min(tau.min(), 0) - 1.5, tau.max() + 1.5)
nneg = int((tau < 0).sum())
neg_txt = "no participant below zero" if nneg == 0 else \
    f"{nneg} participants ({100 * nneg / N:.1f}%) below zero"
C.note(ax, 0.97, 0.97, f"range {C.f(tau.min(), 1)} to {C.f(tau.max(), 1)} days\n{neg_txt}",
       ha="right")
ax.set_xlabel("Forest predicted benefit, days")
ax.set_ylabel("Held-out participants")
C.title(ax, "A", "Causal survival forest")

# ------------------------------------------------------------ B comparators
ax = axes[1]
pw = pp["tau_pw"].to_numpy(float)
pwf = pp["tau_pwf"].to_numpy(float)
lo = min(pw.min(), pwf.min(), 0)
hi = max(pw.max(), pwf.max())
w = 2.0  # days; narrow enough to show the spread of the penalized comparator
bins = np.arange(np.floor(lo / w) * w, hi + w, w)
c1, _, _ = ax.hist(pw, bins=bins, histtype="step", color=C.COMP, lw=1.4,
                   label="Restricted comparator")
c2, _, _ = ax.hist(pwf, bins=bins, histtype="stepfilled", color=C.DARK, alpha=0.30,
                   lw=0)
ax.hist(pwf, bins=bins, histtype="step", color=C.DARK, lw=1.0)
ymax = max(c1.max(), c2.max())
ax.set_ylim(0, ymax * 1.45)
ax.axvline(0, ymax=0.72, color=C.INK, lw=1)
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
handles = [Line2D([], [], color=C.COMP, lw=1.4, label="Restricted"),
           Patch(facecolor=(0.25, 0.25, 0.25, 0.30), edgecolor=C.DARK, lw=1.0,
                 label="Minimally\npenalized")]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 1.0),
          handlelength=1.4, borderaxespad=0.2, labelspacing=0.5)
nneg = int((pwf < 0).sum())
C.note(ax, 0.98, 0.97,
       f"minimally penalized,\n{nneg} of {N}\n({100 * nneg / N:.1f}%) below zero", ha="right")
ax.set_xlabel("Comparator predicted benefit, days")
ax.set_ylabel("Held-out participants")
C.title(ax, "B", "Piecewise comparators")

# ------------------------------------------------------------ C groups
ax = axes[2]
g = pd.DataFrame(pj["groups"], columns=["group", "n", "mean", "lo", "hi", "mean_tau"])
names = {3: ["Lowest", "Middle", "Highest"], 2: ["Lower", "Higher"]}.get(
    len(g), [f"Group {i}" for i in g["group"]])
x = np.arange(len(g))
ax.axhline(0, color=C.INK, lw=0.9)
ax.errorbar(x, g["mean"], yerr=[g["mean"] - g["lo"], g["hi"] - g["mean"]], fmt="o",
            color=C.FOREST, ms=5.5, capsize=3, elinewidth=1.3, capthick=1.3)
labels = [f"{nm}\nn={int(r.n)}\nmean {C.f(r.mean_tau, 1)} d" for nm, r in zip(names, g.itertuples())]
ax.set_xticks(x, labels, fontsize=C.FS_NOTE)
ax.tick_params(axis="x", length=0, pad=4)
ax.set_xlim(-0.5, len(g) - 0.5)
span = g["hi"].max() - min(g["lo"].min(), 0)
ax.set_ylim(min(g["lo"].min(), 0) - 0.08 * span, g["hi"].max() + 0.30 * span)
ax.set_ylabel("Mean evaluation score, days")
ax.set_xlabel("Predicted benefit group")
cal = pj["calib"]
C.title(ax, "C", "Score by benefit group")
# calibration note sits just below the title, in head room above the intervals
C.note(ax, 0.03, 0.98, f"calibration slope {C.f(cal['slope'])}\n(95% CI {C.f(cal['slope_lo'])} "
       f"to {C.f(cal['slope_hi'])})")

C.save(fig, "Figure3.png")
