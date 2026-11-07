"""Figure S10. Clustered full-pipeline bootstrap.

Input
  work/boot_summary.csv  one row per replicate: learned_minus_all3, frac3, all12_minus_all3
The file may still be growing; the replicate count is read from it.
"""
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

import _common as C
from _common import plt

b = pd.read_csv(C.work("boot_summary.csv"))
R = len(b)
if R == 0:
    raise SystemExit("boot_summary.csv has no replicates")


def pct_interval(x):
    return np.percentile(x, [2.5, 97.5])


fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.8), layout="constrained")
fig.get_layout_engine().set(w_pad=0.04, wspace=0.07)
HEAD = 1.75   # y head room factor for the annotations

# ------------------------------------------------------------ A learned rule contrast
ax = axes[0]
x = b["learned_minus_all3"].dropna().to_numpy(float)
w = C.nice_width(max(x.max() - x.min(), 1.0), 30)
cnt, _, _ = ax.hist(x, bins=C.centered_bins(x, w), color=C.FOREST, edgecolor="white",
                    linewidth=0.3)
ax.set_ylim(0, cnt.max() * HEAD)
ax.axvline(0, ymax=1 / HEAD + 0.02, color=C.INK, lw=0.9)
nz = int((x == 0).sum())
lo, hi = pct_interval(x)
C.note(ax, 0.03, 0.98, f"{nz} of {len(x)} replicates ({100 * nz / len(x):.0f}%)\n"
       f"exactly zero\nmean {C.f(x.mean())}, 95% percentile\ninterval {C.f(lo)} to {C.f(hi)}")
ax.set_xlabel("Learned rule minus uniform\n3-month DAPT, days")
ax.set_ylabel("Bootstrap replicates")
C.title(ax, "A", "Learned rule contrast")

# ------------------------------------------------------------ B rule composition
ax = axes[1]
f3 = 100 * b["frac3"].dropna().to_numpy(float)
lo_b = np.floor(f3.min()) if f3.min() < 100 else 99
w = C.nice_width(100 - lo_b, 30) if lo_b < 100 else 1
bins = np.arange(100, lo_b - w, -w)[::-1]
if len(bins) < 2:
    bins = np.array([99, 100])
bins[-1] = 100 + 1e-9
cnt, _, _ = ax.hist(f3, bins=bins, color=C.GREY, edgecolor="white", linewidth=0.3)
ax.set_ylim(0, cnt.max() * HEAD)
n100 = int((b["frac3"] >= 1 - 1e-12).sum())
C.note(ax, 0.03, 0.98, f"mean {f3.mean():.1f}%, minimum {f3.min():.1f}%\n"
       f"{n100} of {len(f3)} replicates assign\nevery participant to 3 months")
ax.set_xlabel("Assigned to 3-month DAPT, %")
ax.set_ylabel("Bootstrap replicates")
C.title(ax, "B", "Rule composition")

# ------------------------------------------------------------ C uniform 12 versus 3
ax = axes[2]
x = b["all12_minus_all3"].dropna().to_numpy(float)
w = C.nice_width(max(x.max() - x.min(), 1.0), 25)
cnt, _, _ = ax.hist(x, bins=np.arange(np.floor(x.min() / w) * w, x.max() + w, w),
                    color=C.VERM, alpha=0.85, edgecolor="white", linewidth=0.3)
ax.set_ylim(0, cnt.max() * HEAD)
lo, hi = pct_interval(x)
top = 1 / HEAD + 0.04
for v in (lo, hi):
    ax.axvline(v, ymax=top, color=C.INK, lw=0.9, ls=(0, (3, 2)))
ax.axvline(x.mean(), ymax=top, color=C.INK, lw=1.2)
ax.axvline(0, ymax=top, color="0.6", lw=0.7)
C.note(ax, 0.03, 0.98, f"mean {C.f(x.mean())} days\n95% percentile interval\n"
       f"{C.f(lo)} to {C.f(hi)}")
ax.set_xlabel("Uniform 12 months minus\nuniform 3 months, days")
ax.set_ylabel("Bootstrap replicates")
C.title(ax, "C", "Uniform policy contrast")

for ax in axes:
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))

C.save(fig, "FigureS10.png")
