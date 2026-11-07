"""Supplementary Figure S2. Endpoint-specific distributions of the end of follow-up by randomized arm.

Run from the repository root after analysis/build.py. Panel A shows the end of bleeding follow-up among participants
without bleeding, panel B the end of vital-status follow-up among survivors. Medians are reverse Kaplan-Meier estimates.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('figures/out', exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})
B3, A12 = '#0072b2', '#d55e00'
d = pd.read_csv('work/patients.csv', dtype={'site': str})


def reverse_km_median(t, e):
    c = 1 - np.asarray(e); t = np.asarray(t); s = 1.0
    for u in np.unique(t[c == 1]):
        s *= 1 - ((t == u) & (c == 1)).sum() / (t >= u).sum()
        if s <= 0.5:
            return int(u)


bins = np.arange(0, 466, 15)
fig, axs = plt.subplots(1, 2, figsize=(7.5, 2.7), dpi=600)
for ax, (tcol, ecol, title) in zip(axs, [('blood_day', 'blood', 'A  Bleeding follow-up'), ('death_day', 'death', 'B  Vital-status follow-up')]):
    med = {}
    for arm, lab, col in [('B', '3-month', B3), ('A', '12-month', A12)]:
        g = d[d.COL_INV == arm]; med[lab] = reverse_km_median(g[tcol], g[ecol])
        ax.hist(g.loc[g[ecol] == 0, tcol], bins=bins, histtype='step', lw=1.3, color=col, label=f'{lab} (n={len(g)})')
    ax.axvline(365, color='0.4', ls=':', lw=1)
    ax.text(0.02, 0.62, f"reverse Kaplan-Meier median follow-up\n3-month {med['3-month']} days, 12-month {med['12-month']} days",
            transform=ax.transAxes, fontsize=6.5, color='0.25')
    ax.set_title(title, loc='left', fontsize=8.5); ax.set_xlabel('Days since randomization'); ax.set_ylabel('Participants')
    ax.legend(frameon=False, loc='upper left', fontsize=7); ax.spines[['top', 'right']].set_visible(False)
    print(title, med)
fig.tight_layout(); fig.savefig('figures/out/FigureS2.png')
