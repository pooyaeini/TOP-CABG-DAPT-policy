"""Figure S11. Detectability of a known policy gain (scenarios B0 to B6).

Input
  work/sim_summary.csv  scenario, rep, oracle_gain, v_hat, cor, ...
Detection means the estimated gain v_hat exceeds the 95th percentile of v_hat in the
null scenario B0 (computed from the data). Error bars are one Monte Carlo standard
error, sqrt(p(1 - p) / R). Missing scenarios are skipped.
"""
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import _common as C
from _common import plt

ORDER = ["B0", "B1", "B2", "B3", "B4", "B5", "B6"]
NAMES = {"B0": "No heterogeneity",
         "B1": "5% favor 12 months",
         "B2": "10% favor 12 months",
         "B3": "20% favor 12 months",
         "B4": "40% favor 12 months",
         "B5": "20%, doubled effect",
         "B6": "40%, doubled effect"}

s = pd.read_csv(C.work("sim_summary.csv"))
s["scenario"] = s["scenario"].astype(str)
present = [k for k in ORDER if k in set(s["scenario"])]
if not present:
    raise SystemExit("no B scenarios in sim_summary.csv")
missing = [k for k in ORDER if k not in present]
if missing:
    print("skip scenarios not yet in sim_summary.csv: " + ", ".join(missing))
s = s[s["scenario"].isin(present)].copy()
gain = s.groupby("scenario")["oracle_gain"].mean()
thr = None
if "B0" in present:
    v0 = s.loc[s["scenario"] == "B0", "v_hat"].dropna().to_numpy(float)
    if len(v0):
        thr = float(np.percentile(v0, 95))
rows = {k: i for i, k in enumerate(present)}
m = len(present)
rng = np.random.default_rng(20261106)


def label(k):
    d = s[s["scenario"] == k]
    return f"{NAMES.get(k, k)}\nR={d['rep'].nunique()}, gain {C.f(gain[k], 1)} d"


fig = plt.figure(figsize=(7.5, max(0.46 * m + 1.75, 3.6)), layout="constrained")
gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 0.85])
axA = fig.add_subplot(gs[0])
axB = fig.add_subplot(gs[1])
axC = fig.add_subplot(gs[2], sharey=axB)
fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.05)

# ------------------------------------------------------------ A recovery of gain
xs_all, ys_all = [], []
gmax = max(gain.max(), 1.0)
jit = 0.012 * gmax
for k in present:
    d = s[s["scenario"] == k]
    v = d["v_hat"].to_numpy(float)
    g = d["oracle_gain"].to_numpy(float)
    ok = np.isfinite(v) & np.isfinite(g)
    x = g[ok] + rng.uniform(-jit, jit, ok.sum())
    axA.scatter(x, v[ok], s=7, color=C.FOREST, alpha=0.35, lw=0, zorder=2)
    if ok.any():
        gm = g[ok].mean()
        axA.plot([gm - 0.035 * gmax, gm + 0.035 * gmax], [v[ok].mean()] * 2, color=C.INK,
                 lw=2.0, zorder=3, solid_capstyle="butt")
    xs_all += list(x)
    ys_all += list(v[ok])
lo = min(min(ys_all, default=0), 0)
hi = max(max(ys_all, default=1), gmax)
pad = 0.06 * (hi - lo)
axA.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color=C.INK, lw=0.9, ls=(0, (4, 3)),
         zorder=1)
axA.axhline(0, color="0.6", lw=0.7, zorder=0)
axA.set_xlim(-0.08 * gmax, 1.08 * gmax)
axA.set_ylim(lo - pad, hi + pad)
axA.set_xlabel("Available gain of the oracle rule\nover uniform 3 months, days")
axA.set_ylabel("Estimated gain of learned rule, days")
C.title(axA, "A", "Recovery of a known gain")

# ------------------------------------------------------------ B probability of recovery
H = 0.36
for k in present:
    d = s[s["scenario"] == k]
    i = rows[k]
    v = d["v_hat"].dropna().to_numpy(float)
    R = len(v)
    if R == 0:
        continue
    bars = []
    if thr is not None:
        bars.append((np.mean(v > thr), C.FOREST, -H / 2))
    bars.append((np.mean(v > 0), "0.72", H / 2 if thr is not None else 0))
    for p, col, off in bars:
        se = C.mc_se(p, R)
        axB.barh(i + off, 100 * p, height=H, color=col, zorder=2)
        axB.errorbar(100 * p, i + off, xerr=[[100 * min(se, p)], [100 * min(se, 1 - p)]],
                     fmt="none", ecolor=C.INK, elinewidth=0.9, capsize=1.8, capthick=0.9,
                     zorder=3)
axB.axvline(80, color=C.INK, lw=0.9, ls=(0, (1.2, 1.6)), zorder=4)
axB.set_xlim(0, 100)
axB.set_yticks(range(m), [label(k) for k in present])
axB.tick_params(axis="y", length=0, pad=4)
axB.set_ylim(m - 0.5, -0.5)
for ax in (axB, axC):
    for i in range(1, m):
        ax.axhline(i - 0.5, color="0.88", lw=0.6, zorder=0)
axB.set_xlabel("Replicates, %")
C.title(axB, "B", "Probability of recovery")

# ------------------------------------------------------------ C individual effects
for k in present:
    d = s[s["scenario"] == k]
    i = rows[k]
    r = d["cor"].to_numpy(float)
    r = r[np.isfinite(r)]
    if len(r) == 0:
        axC.text(0.5, i, "not defined,\nno heterogeneity", transform=axC.get_yaxis_transform(),
                 ha="center", va="center", fontsize=C.FS_NOTE, color="0.4", style="italic")
        continue
    jy = i + rng.uniform(-0.22, 0.22, len(r))
    axC.scatter(r, jy, s=7, color=C.FOREST, alpha=0.35, lw=0, zorder=2)
    med = np.median(r)
    axC.plot([med, med], [i - 0.32, i + 0.32], color=C.INK, lw=2.0, zorder=3)
cr = s["cor"].to_numpy(float)
cr = cr[np.isfinite(cr)]
clo = min(-0.2, np.floor((cr.min() if len(cr) else -0.2) * 10) / 10)
chi = max(0.6, np.ceil((cr.max() if len(cr) else 0.6) * 10) / 10)
axC.set_xlim(clo - 0.02, chi + 0.02)
axC.axvline(0, color="0.6", lw=0.7, zorder=1)
axC.tick_params(axis="y", left=False, labelleft=False)
axC.set_xlabel("Correlation of predicted\nwith true individual effects")
C.title(axC, "C", "Individual effects")

handles = [Line2D([], [], ls="", marker="o", ms=4, color=C.FOREST, alpha=0.5, label="Replicate"),
           Line2D([], [], color=C.INK, lw=2.0, label="Scenario mean or median"),
           Line2D([], [], color=C.INK, lw=0.9, ls=(0, (4, 3)), label="Perfect recovery")]
if thr is not None:
    handles.append(Patch(color=C.FOREST,
                         label=f"Exceeds null 95th percentile, {C.f(thr)} d"))
handles += [Patch(color="0.72", label="Estimated gain above zero"),
            Line2D([], [], color=C.INK, lw=0.9, ls=(0, (1.2, 1.6)), label="80% reference")]
fig.legend(handles=handles, loc="outside lower center", ncol=3, handlelength=1.4,
           columnspacing=1.4, handletextpad=0.5)

C.save(fig, "FigureS11.png")
