"""Figure S9. Known-truth simulations.

Input
  work/sim_summary.csv  one row per replicate: scenario, rep, n, true_ate, est_ate,
                        ate_cover, cor, ...
Scenarios A1, B0, A3, A4, A5, A6, A7 are shown in that order when present; missing
scenarios are skipped. Rows share the scenario labels across the three panels. In
panel B, scenarios without individual heterogeneity have an undefined correlation and
carry a note instead of points.
"""
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import _common as C
from _common import plt

ORDER = ["A1", "B0", "A3", "A4", "A5", "A6", "A7"]
NAMES = {"A1": "No effect",
         "B0": "Common benefit",
         "A3": "Crossing effects",
         "A4": "Covariate-dependent\ncensoring",
         "A5": "Poor censoring\nsupport",
         "A6": "Crossing effects,\nno censoring",
         "A7": "Favorable\nconditions"}

s = pd.read_csv(C.work("sim_summary.csv"))
s["scenario"] = s["scenario"].astype(str)
present = [k for k in ORDER if k in set(s["scenario"])]
if not present:
    raise SystemExit("no S9 scenarios in sim_summary.csv")
missing = [k for k in ORDER if k not in present]
if missing:
    print("skip scenarios not yet in sim_summary.csv: " + ", ".join(missing))
s = s[s["scenario"].isin(present)]
n_mode = int(s["n"].mode().iloc[0])


def label(k):
    d = s[s["scenario"] == k]
    extra = f"R={d['rep'].nunique()}"
    n = int(d["n"].median())
    if n != n_mode:
        extra += f", n={n}"
    return f"{NAMES.get(k, k)}\n{extra}"


rows = {k: i for i, k in enumerate(present)}
m = len(present)
rng = np.random.default_rng(20261106)

fig, axes = plt.subplots(1, 3, sharey=True, figsize=(7.5, 0.47 * m + 1.75),
                         layout="constrained", gridspec_kw={"width_ratios": [1.45, 1, 0.95]})
fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.05)
axA, axB, axC = axes
for ax in axes:
    for i in range(1, m):
        ax.axhline(i - 0.5, color="0.88", lw=0.6, zorder=0)

# ------------------------------------------------------------ A average effect
for k in present:
    d = s[s["scenario"] == k]
    i = rows[k]
    e = d["est_ate"].to_numpy(float)
    e = e[np.isfinite(e)]
    jy = i + rng.uniform(-0.22, 0.22, len(e))
    axA.scatter(e, jy, s=6, color=C.FOREST, alpha=0.35, lw=0, zorder=2)
    if len(e):
        axA.plot(e.mean(), i, "D", ms=5, mfc="white", mec=C.FOREST, mew=1.3, zorder=4)
    axA.plot(d["true_ate"].mean(), i, "|", ms=15, mew=2.0, color=C.INK, zorder=3)
axA.axvline(0, color="0.6", lw=0.7, zorder=1)
axA.set_xlabel("Average effect of 3-month DAPT, days")
axA.set_yticks(range(m), [label(k) for k in present])
axA.tick_params(axis="y", length=0, pad=4)
axA.set_ylim(m - 0.5, -0.5)
C.title(axA, "A", "Average effect recovery")

# ------------------------------------------------------------ B correlation
for k in present:
    d = s[s["scenario"] == k]
    i = rows[k]
    r = d["cor"].to_numpy(float)
    r = r[np.isfinite(r)]
    if len(r) == 0:
        axB.text(0, i, "not defined,\nno heterogeneity", ha="center", va="center",
                 fontsize=C.FS_NOTE, color="0.4", style="italic")
        continue
    jy = i + rng.uniform(-0.22, 0.22, len(r))
    axB.scatter(r, jy, s=6, color=C.FOREST, alpha=0.35, lw=0, zorder=2)
    med = np.median(r)
    axB.plot([med, med], [i - 0.32, i + 0.32], color=C.INK, lw=2.0, zorder=3)
axB.axvline(0, color="0.6", lw=0.7, zorder=1)
axB.set_xlim(-1.05, 1.05)
axB.set_xticks([-1, -0.5, 0, 0.5, 1], ["−1", "−0.5", "0", "0.5", "1"])
axB.set_xlabel("Correlation of predicted\nwith true individual effects")
axB.tick_params(axis="y", left=False)
C.title(axB, "B", "Individual effects")

# ------------------------------------------------------------ C coverage
for k in present:
    d = s[s["scenario"] == k]
    i = rows[k]
    cv = d["ate_cover"].to_numpy(float)
    cv = cv[np.isfinite(cv)]
    if len(cv) == 0:
        continue
    p = cv.mean()
    se = C.mc_se(p, len(cv))
    axC.barh(i, 100 * p, height=0.55, color=C.GREY, zorder=2)
    axC.errorbar(100 * p, i, xerr=[[100 * min(se, p)], [100 * min(se, 1 - p)]],
                 fmt="none", ecolor=C.INK, elinewidth=1.0, capsize=2.2, capthick=1.0, zorder=3)
axC.axvline(95, color=C.INK, lw=0.9, ls=(0, (1.2, 1.6)), zorder=4)
axC.set_xlim(0, 100)
axC.set_xlabel("Coverage of the 95%\ninterval, % of replicates")
axC.tick_params(axis="y", left=False)
C.title(axC, "C", "Interval coverage")

handles = [Line2D([], [], ls="", marker="o", ms=4, color=C.FOREST, alpha=0.5,
                  label="Replicate"),
           Line2D([], [], ls="", marker="D", ms=5, mfc="white", mec=C.FOREST, mew=1.3,
                  label="Mean of replicates"),
           Line2D([], [], ls="", marker="|", ms=11, mew=2.0, color=C.INK, label="True value"),
           Line2D([], [], color=C.INK, lw=2.0, label="Median correlation"),
           Line2D([], [], ls="", marker="s", ms=6, color=C.GREY,
                  label="Coverage \u00b1 Monte Carlo SE"),
           Line2D([], [], color=C.INK, lw=0.9, ls=(0, (1.2, 1.6)), label="Nominal 95%")]
fig.legend(handles=handles, loc="outside lower center", ncol=3, handlelength=1.3,
           columnspacing=1.2, handletextpad=0.5)

C.save(fig, "FigureS9.png")
