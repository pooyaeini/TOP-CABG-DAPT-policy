"""Figure S8. Stability of forest predicted benefit across reruns.

Inputs
  work/primary_patients.csv  tau (primary forest predicted benefit)
  work/sens/seed2_tau.csv    tau, same row order (second fold seed)
  work/sens/seed3_tau.csv    tau, same row order (third fold seed)
  work/sens/smoke3_tau.csv   tau, same row order (three-level smoking encoding)
Missing files are skipped and the remaining panels are lettered in order.
"""
import os

import numpy as np
import pandas as pd

import _common as C
from _common import plt

prim = pd.read_csv(C.work("primary_patients.csv"))["tau"].to_numpy(float)
SPEC = [("seed2_tau.csv", "Second fold seed", "second fold seed"),
        ("seed3_tau.csv", "Third fold seed", "third fold seed"),
        ("smoke3_tau.csv", "Three-level smoking", "three-level smoking")]

panels = []
for fn, ttl, ylab in SPEC:
    path = C.work("sens", fn)
    if not os.path.exists(path):
        print(f"skip: {path} not found")
        continue
    t = pd.read_csv(path)["tau"].to_numpy(float)
    if len(t) != len(prim):
        print(f"skip: {fn} has {len(t)} rows, primary has {len(prim)}")
        continue
    panels.append((ttl, ylab, t))

if not panels:
    raise SystemExit("no sensitivity predictions available for Figure S8")

allv = np.concatenate([prim] + [p[2] for p in panels])
lo = np.floor(np.nanmin(allv)) - 0.5
hi = np.ceil(np.nanmax(allv)) + 0.5
k = len(panels)
fig, axes = plt.subplots(1, k, figsize=(2.5 * k, 2.8), layout="constrained", squeeze=False)
fig.get_layout_engine().set(w_pad=0.04, wspace=0.07)
for j, (ax, (ttl, ylab, t)) in enumerate(zip(axes[0], panels)):
    ok = np.isfinite(t) & np.isfinite(prim)
    ax.plot([lo, hi], [lo, hi], color=C.INK, lw=0.9, ls=(0, (4, 3)), zorder=1)
    ax.scatter(prim[ok], t[ok], s=3, color=C.DARK, alpha=0.35, lw=0, zorder=2,
               rasterized=False)
    r = np.corrcoef(prim[ok], t[ok])[0, 1]
    mad = np.mean(np.abs(prim[ok] - t[ok]))
    # statistics sit between the title and the axes, clear of the point cloud
    ax.annotate(f"Pearson r = {r:.3f}, mean\nabsolute difference {mad:.2f} days", xy=(0, 1),
                xycoords="axes fraction", xytext=(0, 4), textcoords="offset points",
                ha="left", va="bottom", fontsize=C.FS_NOTE, color=C.INK)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Primary prediction, days")
    ax.set_ylabel("Rerun prediction, days")
    C.title(ax, "ABC"[j], ttl, pad=28)

C.save(fig, "FigureS8.png")
