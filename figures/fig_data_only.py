"""Figure 1 (flow), Figure 2 (Kaplan-Meier and censoring timing), Supplementary Figure S4, regenerated for the revision."""
import json, numpy as np, pandas as pd, matplotlib
import os
os.makedirs('figures/out', exist_ok=True)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5})
B3, A12, INK = '#0072b2', '#d55e00', '#222222'
d = pd.read_csv('work/patients.csv', dtype={'site': str})

def km(t, e):
    t = np.asarray(t, float); e = np.asarray(e, int); ut = np.unique(t[e == 1]); s = 1.0; xs, ys = [0], [1.0]
    for u in ut:
        n = (t >= u).sum(); dd = ((t == u) & (e == 1)).sum(); s *= 1 - dd / n; xs.append(u); ys.append(s)
    return np.array(xs), np.array(ys)

# ---------- Figure 1 ----------
fig = plt.figure(figsize=(7.5, 6.3), dpi=300); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
def box(x, y, w, h, txt, fc='#f2f2f2', ec=INK, bold=False, fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.25,rounding_size=1.2', fc=fc, ec=ec, lw=0.9))
    ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', linespacing=1.35)
def arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='-|>', color=INK, lw=0.9, shrinkA=0, shrinkB=0))
box(30, 91, 40, 6.5, 'TOP-CABG randomized participants\n2300 (trial report)')
box(28, 79.5, 44, 7, 'Public Dryad release analyzed\n2290 modified intention-to-treat participants', bold=True)
box(74.5, 79.5, 24, 7, '10 participants not in\nthe public release,\nnot reconstructed', fc='white', ec='#888888', fs=7.3)
arrow(50, 91, 50, 86.6); arrow(72, 83, 74.5, 83)
box(3, 66, 36, 8.5, '12-month DAPT (arm A)\nn = 1138\n154 composite events by day 365', fc='#fdebe0')
box(61, 66, 36, 8.5, '3-month DAPT (arm B)\nn = 1152\n99 composite events by day 365', fc='#e3f0f8')
ax.plot([21, 79], [77.5, 77.5], color=INK, lw=0.9); arrow(50, 79.5, 50, 77.5); arrow(21, 77.5, 21, 74.6); arrow(79, 77.5, 79, 74.6)
ax.plot([21, 79], [62.5, 62.5], color=INK, lw=0.9); arrow(21, 66, 21, 62.5); arrow(79, 66, 79, 62.5); arrow(50, 62.5, 50, 59.6)
box(14, 47.5, 72, 12, 'Primary endpoint, first BARC 2/3/5 bleeding or all-cause death\n253 first events; 803 participants censored before day 365\n'
    'Secondary endpoints, net adverse clinical events and ischemic composite\nEstimand, restricted mean event-free time through day 365\n'
    'Reference policy, uniform 3-month DAPT, fixed before model fitting', fs=8)
arrow(50, 47.5, 50, 43.6)
box(3, 26, 45, 17.5, 'Cross-fitted discovery\n5 outer folds stratified by released site and arm\nCausal survival forest and penalized\n'
    'piecewise-exponential comparators fitted on 4 folds\nHeld-out assignments frozen before evaluation', fc='white')
box(52, 26, 45, 17.5, 'Honest policy evaluation\nFold-specific evaluation forest supplying doubly\nrobust RMST scores for held-out participants\n'
    'Policy value, mean of (rule minus reference) x score\n500-replicate participant-clustered bootstrap', fc='white')
arrow(48, 34.75, 52, 34.75); arrow(25.5, 26, 25.5, 21.6); arrow(74.5, 26, 74.5, 21.6)
box(3, 3, 45, 18.5, 'Graft substudy\n2070 participants with scheduled imaging\n220 without imaging handled by identification\n'
    'bounds and tipping scenarios, never imputed\nas occlusion; graft causal forest', fc='#f7f7f7')
box(52, 3, 45, 18.5, 'Reported analyses\nPrimary contrast, learned rule minus uniform\n3-month DAPT; calibration and rank-weighted\n'
    'treatment effect; secondary endpoints; decision\nat day 85; 21 sensitivity analyses; simulations', fc='#f7f7f7')
fig.savefig('figures/out/Figure1.png'); plt.close(fig)

# ---------- Figure 2 ----------
fig = plt.figure(figsize=(7.5, 4.0), dpi=300)
axA = fig.add_axes([0.13, 0.33, 0.50, 0.6]); axB = fig.add_axes([0.73, 0.33, 0.25, 0.6]); axR = fig.add_axes([0.13, 0.03, 0.50, 0.16]); axR.axis('off')
for w, col, ls, lab in [(1, B3, '-', '3-month DAPT (n=1152)'), (0, A12, '--', '12-month DAPT (n=1138)')]:
    s = d[d.W == w]; x, y = km(np.minimum(s.t_raw, 366), np.where(s.t_raw <= 365, s.event_raw, 0))
    x = np.append(x, 365); y = np.append(y, y[-1]); axA.step(x, y, where='post', color=col, ls=ls, lw=1.4, label=lab)
axA.axvline(85, color='#666666', ls=':', lw=0.9); axA.text(88, 0.996, 'regimens diverge\nabout day 85', fontsize=7.3, color='#555555', va='top')
axA.set_xlim(0, 365); axA.set_ylim(0.85, 1.0); axA.set_xticks([0, 90, 180, 270, 365]); axA.set_xlabel('Days since randomization')
axA.set_ylabel('Alive and free of first\nBARC 2/3/5 bleeding'); axA.set_title('A  Composite event-free survival', loc='left', fontsize=9.5)
axA.legend(frameon=False, loc='lower left', fontsize=8)
for s_ in ('top', 'right'): axA.spines[s_].set_visible(False); axB.spines[s_].set_visible(False)
axR.text(-0.045, 0.95, 'Number at risk', fontweight='bold', fontsize=8, ha='right', transform=axR.transAxes)
for i, (w, col, lab) in enumerate([(1, B3, '3-month'), (0, A12, '12-month')]):
    s = d[d.W == w]; axR.text(-0.045, 0.5 - 0.42 * i, lab, color=col, fontsize=8, ha='right', transform=axR.transAxes)
    for tq in [0, 90, 180, 270, 365]:
        n = int(((s.t_raw >= tq) if tq > 0 else (s.t_raw >= 0)).sum())
        axR.text(tq / 365, 0.5 - 0.42 * i, str(n), color=col, fontsize=8, ha='center', transform=axR.transAxes)
cz = d[d.event_raw == 0]; bins = np.arange(300, 460, 15)
for w, col, lab in [(1, B3, '3-month'), (0, A12, '12-month')]:
    axB.hist(cz[cz.W == w].t_raw, bins=bins, histtype='step', color=col, lw=1.3, label=lab)
axB.axvline(365, color='#666666', ls=':', lw=0.9); axB.set_xlim(300, 455)
axB.set_xlabel('End of composite follow-up\namong censored participants, days'); axB.set_ylabel('Censored participants')
axB.set_title('B  Visit timing and censoring', loc='left', fontsize=9.5); axB.legend(frameon=False, loc='upper right', fontsize=7.5)
fig.text(0.70, 0.03, '803 participants censored before\nday 365, all between day 306 and 364.\nReverse Kaplan-Meier median\nfollow-up 369 days (IQR 358 to 383)', fontsize=7, color='#333333')
fig.savefig('figures/out/Figure2.png'); plt.close(fig)

# ---------- Supplementary Figure S4 ----------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.5, 2.9), dpi=300, gridspec_kw={'width_ratios': [1, 1.15]})
vals = {}
for w in (0, 1):
    s = d[d.W == w]; n = len(s)
    vals[w] = [((s.blood == 1) & (s.blood_day <= 90)).sum(), ((s.blood == 1) & (s.blood_day > 90) & (s.blood_day <= 365)).sum(), n]
x = np.array([0, 1]); wdt = 0.34
for j, (lab, col) in enumerate([('day 0 to 90', '#9ecae1'), ('day 91 to 365', '#3182bd')]):
    hs = [100 * vals[w][j] / vals[w][2] for w in (0, 1)]
    bars = a1.bar(x + (j - 0.5) * wdt, hs, wdt, color=col, label=lab)
    for r, w in zip(bars, (0, 1)): a1.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.15, str(vals[w][j]), ha='center', fontsize=7.5)
a1.set_xticks(x); a1.set_xticklabels(['12-month (A)', '3-month (B)']); a1.set_ylabel('BARC 2/3/5 bleeding (% of arm)'); a1.set_ylim(0, 9.5)
a1.legend(frameon=False, fontsize=7.5, loc='upper right'); a1.set_title('A  Bleeding before and after day 90', loc='left', fontsize=9.5)
lm = d[d.t_raw > 90]; ymin = 1
for w, col, ls, lab in [(1, B3, '-', '3-month'), (0, A12, '--', '12-month')]:
    s = lm[lm.W == w]; xx, yy = km(np.minimum(s.t_raw, 366) - 90, np.where(s.t_raw <= 365, s.event_raw, 0))
    xx = np.append(xx, 275); yy = np.append(yy, yy[-1]); a2.step(xx + 90, yy, where='post', color=col, ls=ls, lw=1.3, label=lab); ymin = min(ymin, yy.min())
a2.set_xlim(90, 365); a2.set_ylim(np.floor(ymin * 100) / 100 - 0.005, 1.001); a2.set_xlabel('Days since randomization')
a2.set_ylabel('Conditional event-free survival\nfrom day 90'); a2.legend(frameon=False, fontsize=7.5, loc='lower left')
a2.set_title(f"B  Landmark view from day 90 ({int(((lm.event_raw == 1) & (lm.t_raw <= 365)).sum())} late events)", loc='left', fontsize=9.5)
for a in (a1, a2):
    for s_ in ('top', 'right'): a.spines[s_].set_visible(False)
fig.tight_layout(); fig.savefig('figures/out/FigureS4.png'); plt.close(fig)
print('ok')
