import json, subprocess, matplotlib
import os
os.makedirs('figures/out', exist_ok=True)
matplotlib.use('Agg'); import matplotlib.pyplot as plt
vals = json.load(open('work/aj.json'))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, ax = plt.subplots(figsize=(4.9, 3.3), dpi=300)
x = [0, 1]; w = 0.34
b1 = ax.bar([i - w / 2 for i in x], [vals['b12'], vals['b3']], w, color=['#d55e00', '#0072b2'], label='BARC 2/3/5 bleeding')
b2 = ax.bar([i + w / 2 for i in x], [vals['d12'], vals['d3']], w, color='#bdbdbd', label='death before bleeding')
for bars in (b1, b2):
    for r in bars: ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.25, f"{r.get_height():.2f}%", ha='center', va='bottom', fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(['12-month (A)', '3-month (B)']); ax.set_ylim(0, 15.5)
ax.set_ylabel('Aalen-Johansen cumulative incidence\nthrough day 365 (%)'); ax.set_title('Bleeding with death treated as a competing event', fontsize=10)
h = [plt.Rectangle((0, 0), 1, 1, color='#d55e00'), plt.Rectangle((0, 0), 1, 1, color='#bdbdbd')]
ax.legend(h, ['BARC 2/3/5 bleeding', 'death before bleeding'], frameon=False, loc='upper right', fontsize=8)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('figures/out/FigureS3.png'); print('ok')
