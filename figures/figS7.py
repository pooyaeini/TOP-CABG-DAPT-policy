"""Figure S7. Out-of-fold performance of the two vein graft occlusion risk models.

Inputs
  work/graft_pred.csv    occ (0/1), p_ridge, p_xgb (out-of-fold predicted risk)
  work/graft_models.json calibration slope per model (shown in the legend of A)
AUC and AUPRC are recomputed from graft_pred.csv; a mismatch with the JSON is reported.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, precision_recall_curve,
                             roc_auc_score, roc_curve)

import _common as C
from _common import plt

g = pd.read_csv(C.work("graft_pred.csv")).dropna(subset=["occ"])
try:
    gm = C.load_json(C.work("graft_models.json"))
except FileNotFoundError:
    gm = {}
y = g["occ"].astype(int).to_numpy()
prev = y.mean()
MODELS = [("p_ridge", "ridge", "Ridge logistic", C.COMP, "o"),
          ("p_xgb", "xgb", "XGBoost", C.ORANGE, "s")]


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return c - h, c + h


fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.6), layout="constrained")
fig.get_layout_engine().set(w_pad=0.04, wspace=0.07)
axA, axB, axC = axes

# ------------------------------------------------------------ A calibration
pts = []
for j, (colname, key, name, col, mk) in enumerate(MODELS):
    p = g[colname].to_numpy(float)
    dec = pd.qcut(p, 10, labels=False, duplicates="drop")
    t = pd.DataFrame({"p": p, "y": y, "d": dec}).groupby("d").agg(
        pred=("p", "mean"), k=("y", "sum"), n=("y", "size"))
    lo, hi = wilson(t["k"].to_numpy(float), t["n"].to_numpy(float))
    obs = t["k"] / t["n"]
    slope = gm.get(key, {}).get("slope")
    lab = name if slope is None else f"{name}, slope {C.f(slope)}"
    axA.errorbar(t["pred"], obs, yerr=[obs - lo, hi - obs], fmt=mk, color=col, ms=3.8,
                 capsize=1.8, elinewidth=0.9, capthick=0.9, alpha=0.95, label=lab)
    pts += list(t["pred"]) + list(lo) + list(hi)
lo_ax = max(0, np.floor(min(pts) / 0.05) * 0.05)
hi_ax = min(1, np.ceil(max(pts) / 0.05) * 0.05)
axA.plot([lo_ax, hi_ax], [lo_ax, hi_ax], color=C.INK, lw=0.9, ls=(0, (4, 3)), zorder=0)
axA.set_xlim(lo_ax, hi_ax)
axA.set_ylim(lo_ax, hi_ax)
axA.set_aspect("equal", adjustable="box")
axA.legend(loc="upper left", handlelength=1.2, borderaxespad=0.2)
axA.set_xlabel("Mean predicted risk")
axA.set_ylabel("Observed occlusion proportion")
C.title(axA, "A", "Calibration, deciles")

# ------------------------------------------------------------ B ROC
for colname, key, name, col, mk in MODELS:
    p = g[colname].to_numpy(float)
    fpr, tpr, _ = roc_curve(y, p)
    auc = roc_auc_score(y, p)
    ref = gm.get(key, {}).get("auc")
    if ref is not None and abs(ref - auc) > 1e-3:
        print(f"note: {name} AUC from predictions {auc:.4f} differs from JSON {ref:.4f}")
    axB.plot(fpr, tpr, color=col, lw=1.3, label=f"{name.split()[0]}, AUC {auc:.3f}")
axB.plot([0, 1], [0, 1], color=C.INK, lw=0.9, ls=(0, (4, 3)), zorder=0)
axB.set_xlim(-0.01, 1.01)
axB.set_ylim(-0.01, 1.01)
axB.set_aspect("equal", adjustable="box")
axB.legend(loc="upper left", handlelength=1.4, borderaxespad=0.2)
axB.set_xlabel("False positive rate")
axB.set_ylabel("True positive rate")
C.title(axB, "B", "Discrimination")

# ------------------------------------------------------------ C precision and recall
ytop = 0
for colname, key, name, col, mk in MODELS:
    p = g[colname].to_numpy(float)
    pr, rc, _ = precision_recall_curve(y, p)
    ap = average_precision_score(y, p)
    axC.plot(rc, pr, color=col, lw=1.2, label=f"{name.split()[0]}, AUPRC {ap:.3f}")
    ytop = max(ytop, pr[rc >= 0.05].max())
axC.axhline(prev, color=C.INK, lw=0.9, ls=(0, (4, 3)), label=f"Prevalence {prev:.3f}")
axC.set_xlim(-0.01, 1.01)
axC.set_ylim(0, max(ytop * 1.55, prev * 2.5))
axC.set_box_aspect(1)
axC.legend(loc="upper right", handlelength=1.4, borderaxespad=0.2)
axC.set_xlabel("Recall")
axC.set_ylabel("Precision")
C.title(axC, "C", "Precision and recall")

C.save(fig, "FigureS7.png")
