"""Figure S6. Evaluation scores, censoring weights and timing of censoring.

Inputs
  work/primary_patients.csv  gamma (score), chat (censoring survival)
  work/patients.csv          t_raw, event_raw, W
"""
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import _common as C
from _common import plt

pp = pd.read_csv(C.work("primary_patients.csv"))
pt = pd.read_csv(C.work("patients.csv"))
CLIP = 1000.0
H = 365

fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.75), layout="constrained")
fig.get_layout_engine().set(w_pad=0.04, wspace=0.06)

# ------------------------------------------------------------ A scores
ax = axes[0]
g = pp["gamma"].to_numpy(float)
N = len(g)
gc = np.clip(g, -CLIP, CLIP)
lim = min(CLIP, np.ceil(np.abs(g).max() * 1.05 / 100) * 100)
bins = np.arange(-lim, lim + 25, 25)
cnt, _, _ = ax.hist(gc, bins=bins, color=C.GREY, edgecolor="white", linewidth=0.2)
ax.set_ylim(0, cnt.max() * 1.5)
for v in (-H, H):
    ax.axvline(v, ymax=0.66, color=C.INK, lw=0.8, ls=(0, (3, 2)))
nlo, nhi = int((g < -H).sum()), int((g > H).sum())
txt = (f"beyond ±{H} days, {nlo + nhi} ({100 * (nlo + nhi) / N:.1f}%)\n"
       f"{nlo} below, {nhi} above")
nclip = int((np.abs(g) > CLIP).sum())
if nclip:
    txt += f"\n{nclip} beyond ±{int(CLIP)} shown at the edges"
C.note(ax, 0.03, 0.98, txt)
ax.set_xlim(-lim, lim)
ax.set_xlabel("Evaluation score, days")
ax.set_ylabel("Participants")
C.title(ax, "A", "Doubly robust scores")

# ------------------------------------------------------------ B censoring survival
ax = axes[1]
ch = pp["chat"].to_numpy(float)
cnt, _, _ = ax.hist(ch, bins=np.linspace(0, 1, 51), color=C.GREY,
                    edgecolor="white", linewidth=0.2)
ax.set_xlim(0, 1)
ax.set_ylim(0, cnt.max() * 1.5)
n10 = int((ch < 0.10).sum())
C.note(ax, 0.03, 0.98, f"minimum {ch.min():.3f}\nmaximum {ch.max():.3f}\n"
       + ("no participant below 0.10" if n10 == 0 else f"{n10} participants below 0.10"))
ax.set_xlabel("Censoring survival probability")
ax.set_ylabel("Participants")
C.title(ax, "B", "Censoring support")

# ------------------------------------------------------------ C timing of censoring
ax = axes[2]
c = pt[(pt["event_raw"] == 0) & (pt["t_raw"] < H)]
bins = np.arange(0, H + 5, 5)
ymax = 0
for w, name, col in ((1, "3-month DAPT", C.ARM3), (0, "12-month DAPT", C.ARM12)):
    t = c.loc[c["W"] == w, "t_raw"]
    h, _, _ = ax.hist(t, bins=bins, histtype="step", color=col, lw=1.3)
    ymax = max(ymax, h.max() if len(h) else 0)
ax.set_xlim(0, H + 5)
ax.set_ylim(0, ymax * 1.6 if ymax else 1)
handles = [Line2D([], [], color=C.ARM3, lw=1.3,
                  label=f"3-month DAPT, n={int((c['W'] == 1).sum())}"),
           Line2D([], [], color=C.ARM12, lw=1.3,
                  label=f"12-month DAPT, n={int((c['W'] == 0).sum())}")]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, 1.0), borderaxespad=0.2,
          handlelength=1.6)
if len(c):
    C.note(ax, 0.03, 0.70, f"all censoring before day {H}\nfalls on days "
           f"{int(c['t_raw'].min())} to {int(c['t_raw'].max())}")
ax.set_xlabel("Day of censoring")
ax.set_ylabel("Participants")
C.title(ax, "C", f"Censoring before day {H}")

C.save(fig, "FigureS6.png")
