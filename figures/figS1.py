"""Supplementary Figure S1. Completeness of every candidate baseline predictor at the decision time.

Run from the repository root after analysis/build.py (sequential vein grafting code 99 is treated as missing there).
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('figures/out', exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})
d = pd.read_csv('work/patients.csv', dtype={'site': str})
FIELDS = [('AGE', 'Age'), ('men', 'Male sex'), ('smoke_status', 'Smoking status'), ('BMI', 'Body-mass index'),
          ('Diabetes', 'Diabetes mellitus'), ('HTN', 'Hypertension'), ('Lipid', 'Dyslipidemia'),
          ('PAD', 'Peripheral artery disease'), ('Cere', 'Prior cerebrovascular disease'),
          ('ACS_2w', 'Acute coronary syndrome within 2 weeks'), ('MI', 'Prior myocardial infarction'),
          ('PCI', 'Prior percutaneous coronary intervention'), ('CCS', 'CCS angina class'), ('NYHA', 'NYHA class'),
          ('PRE_EGFR', 'Estimated glomerular filtration rate'), ('LDLC', 'LDL cholesterol'),
          ('LVEF', 'Left ventricular ejection fraction'), ('SYNTAX', 'SYNTAX score'), ('Onpump', 'On-pump surgery'),
          ('No_touch', 'No-touch vein harvesting'), ('Seq_SVG', 'Sequential vein grafting'),
          ('A_GRAFT', 'Number of arterial grafts'), ('V_GRAFT', 'Number of venous grafts')]
n = len(d); miss = [int(d[f].isna().sum()) for f, _ in FIELDS]
fig, ax = plt.subplots(figsize=(6.5, 5.2), dpi=600)
y = range(len(FIELDS))[::-1]
ax.barh(list(y), miss, color='0.4', height=0.65)
for yy, m in zip(y, miss):
    ax.text(m + 2, yy, f"{m} ({100 * m / n:.1f}%)" if m else 'complete', va='center', fontsize=7, color='0.15' if m else '0.5')
ax.set_yticks(list(y)); ax.set_yticklabels([lab for _, lab in FIELDS])
ax.set_xlim(0, 200); ax.set_xlabel(f'Participants with the field missing, of {n}')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig('figures/out/FigureS1.png')
print('Supplementary Figure S1', {f: m for (f, _), m in zip(FIELDS, miss) if m})
