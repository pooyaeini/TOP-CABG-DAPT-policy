"""Figure S5. Fold-averaged targeting operator characteristic (TOC) curves.

Inputs
  work/toc.csv       priority (forest or comparator), fold, q, est, se
  work/primary.json  autoc_csf, autoc_pw {estimate, se}
Folds are near-equal in size, so the curve is the unweighted mean of the fold
estimates; its standard error is sqrt(mean(se^2)) / sqrt(number of folds).
"""
import numpy as np
import pandas as pd

import _common as C
from _common import plt

toc = pd.read_csv(C.work("toc.csv"))
pj = C.load_json(C.work("primary.json"))

SPEC = [("forest", "Causal survival forest", C.FOREST, "autoc_csf"),
        ("comparator", "Restricted comparator", C.COMP, "autoc_pw")]

fig, ax = plt.subplots(figsize=(5.0, 3.45), layout="constrained")
ax.axhline(0, color=C.INK, lw=0.9, zorder=1)
for key, name, col, akey in SPEC:
    t = toc[toc["priority"] == key]
    if t.empty:
        print(f"warning: no TOC rows for {key}")
        continue
    g = t.groupby("q").agg(est=("est", "mean"), v=("se", lambda s: np.mean(s ** 2)),
                           k=("fold", "nunique")).reset_index()
    se = np.sqrt(g["v"]) / np.sqrt(g["k"])
    ax.fill_between(g["q"], g["est"] - 1.96 * se, g["est"] + 1.96 * se, color=col,
                    alpha=0.16, lw=0, zorder=2)
    a = pj.get(akey)
    lab = name
    if a:
        e, s = a["estimate"], a["se"]
        lab = f"{name}, AUTOC {C.f(e)} (95% CI {C.f(e - 1.96 * s)} to {C.f(e + 1.96 * s)})"
    ax.plot(g["q"], g["est"], "-o", color=col, ms=3.5, lw=1.4, label=lab, zorder=3)

ax.set_xlim(0, 1.02)
ax.set_xticks(np.linspace(0, 1, 6), [f"{int(v * 100)}" for v in np.linspace(0, 1, 6)])
ax.set_xlabel("Participants prioritized by predicted benefit, %")
ax.set_ylabel("Targeting operator characteristic, days")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1, handlelength=2.2)
ax.set_title("Fold-averaged TOC curves with 95% bands", loc="left", fontsize=C.FS_TITLE)

C.save(fig, "FigureS5.png")
