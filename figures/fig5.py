"""Figure 5. Saphenous vein graft outcomes and the effect of missing imaging.

Run from the repository root after analysis/build.py. Uses the released graft-level file data/raw/svg_occ_main.csv.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('figures/out', exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})
B3, A12, INK = '#0072b2', '#d55e00', '#222222'

d = pd.read_csv('work/patients.csv', dtype={'site': str})
g = pd.read_csv('data/raw/svg_occ_main.csv', dtype={'site': str})
p = g.groupby('pid').agg(occ=('occluded_status', 'max'), arm=('COL_INV', 'first')).reset_index()


def wilson(k, n, z=1.96):
    ph = k / n; den = 1 + z ** 2 / n
    c = (ph + z ** 2 / (2 * n)) / den; h = z * np.sqrt(ph * (1 - ph) / n + z ** 2 / (4 * n ** 2)) / den
    return c - h, c + h


arms = [('A', '12-month', A12), ('B', '3-month', B3)]
S = {}
for a, lab, col in arms:
    N = int((d.COL_INV == a).sum()); m = int((p.arm == a).sum()); k = int(p[p.arm == a].occ.sum())
    S[a] = dict(N=N, m=m, k=k, u=N - m, lab=lab, col=col)

fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(7.5, 2.9), dpi=600, gridspec_kw={'width_ratios': [1, 1, 1.3]})

# A, assessed participants
for i, (a, lab, col) in enumerate(arms):
    s = S[a]; r = s['k'] / s['m']; lo, hi = wilson(s['k'], s['m'])
    a1.bar(i, 100 * r, 0.6, color=col)
    a1.errorbar(i, 100 * r, yerr=[[100 * (r - lo)], [100 * (hi - r)]], color=INK, capsize=4, lw=1)
    a1.text(i, 100 * hi + 1.2, f"{s['k']}/{s['m']}\n{100 * r:.1f}%", ha='center', va='bottom', fontsize=7, color=INK)
a1.set_xticks([0, 1]); a1.set_xticklabels([f"{S[a]['lab']}" for a, _, _ in arms])
a1.set_ylim(0, 34); a1.set_ylabel('Any vein graft occlusion, %')
a1.set_title('A  Assessed participants', loc='left', fontsize=8.5)

# B, identification bounds among all randomized participants
for i, (a, lab, col) in enumerate(arms):
    s = S[a]; low = 100 * s['k'] / s['N']; high = 100 * (s['k'] + s['u']) / s['N']
    a2.bar(i, low, 0.6, color=col)
    a2.bar(i, high - low, 0.6, bottom=low, color='0.85', edgecolor='0.55', hatch='///', lw=0.6)
    a2.text(i, high + 1.0, f"{low:.1f}% to\n{high:.1f}%", ha='center', va='bottom', fontsize=7, color=INK)
a2.set_xticks([0, 1]); a2.set_xticklabels([S[a]['lab'] for a, _, _ in arms])
a2.set_ylim(0, 38); a2.set_ylabel('Randomized participants, %')
a2.set_title('B  Identification bounds', loc='left', fontsize=8.5)
from matplotlib.patches import Patch
a2.legend(handles=[Patch(color='0.4', label='observed occlusion'),
                   Patch(facecolor='0.85', edgecolor='0.55', hatch='///', label='range spanned by\nunimaged participants')],
          loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=6.5, handlelength=1.2)

# C, tipping analysis
grid = np.arange(0, 101, 2.0)
X, Y = np.meshgrid(grid, grid)       # X, 12-month unimaged risk; Y, 3-month unimaged risk
A, B = S['A'], S['B']
D = 100 * ((B['k'] + Y / 100 * B['u']) / B['N'] - (A['k'] + X / 100 * A['u']) / A['N'])
im = a3.pcolormesh(X, Y, D, cmap='RdBu_r', vmin=-6, vmax=6, shading='nearest')
cs = a3.contour(X, Y, D, levels=[0], colors=INK, linewidths=1)
ref = 100 * (A['k'] + B['k']) / (A['m'] + B['m'])
a3.plot(ref, ref, marker='*', ms=10, color=INK, mec='white', mew=0.6)
a3.set_aspect('equal')
a3.annotate('equal observed\nrisk in both arms', (ref, ref), xytext=(4, 70), fontsize=6.5, color=INK,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=0.85),
            arrowprops=dict(arrowstyle='-', color=INK, lw=0.6))
a3.text(70, 66, 'no difference', rotation=40, fontsize=6.5, color=INK, ha='center', va='center')
a3.set_xlabel('Risk if unimaged, 12-month arm, %'); a3.set_ylabel('Risk if unimaged, 3-month arm, %')
a3.set_title('C  Tipping analysis', loc='left', fontsize=8.5)
cb = fig.colorbar(im, ax=a3, fraction=0.05, pad=0.03); cb.set_label('3-month minus 12-month,\npercentage points', fontsize=6.5)
cb.ax.tick_params(labelsize=6.5)
for ax in (a1, a2):
    ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(w_pad=1.6)
fig.savefig('figures/out/Figure5.png')
print('Figure 5', {a: (S[a]['k'], S[a]['m'], S[a]['N']) for a in S}, f'reference risk {ref:.1f}%')
