import json, os, pandas as pd, numpy as np
W = 'work/'; F = 'work/'; os.makedirs(F, exist_ok=True)
P = json.load(open(W + 'primary.json')); N = json.load(open(W + 'net.json'))
sens = {f[:-5]: json.load(open(W + 'sens/' + f)) for f in os.listdir(W + 'sens') if f.endswith('.json')}
bs = pd.read_csv(W + 'boot_summary.csv') if os.path.exists(W + 'boot_summary.csv') else None
km = P['km']['full']; kd, kse = km[2], km[3]
rows = [dict(label='Uniform 12-month, Kaplan-Meier difference', est=-kd, lo=-kd - 1.96 * kse, hi=-kd + 1.96 * kse, pct3=0.0, n12=2290, method='analytic Kaplan-Meier'),
        dict(label='Uniform 12-month, doubly robust score', est=P['policy']['csf'][4], lo=P['fixed_boot'][0][0], hi=P['fixed_boot'][1][0], pct3=0.0, n12=2290, method='fixed-prediction bootstrap')]
if bs is not None:
    rows.append(dict(label='Uniform 12-month, clustered bootstrap', est=bs.all12_minus_all3.mean(), lo=bs.all12_minus_all3.quantile(.025), hi=bs.all12_minus_all3.quantile(.975), pct3=0.0, n12=2290, method='clustered full-pipeline bootstrap'))
rows += [dict(label='Causal survival forest rule, original estimate', est=0.0, lo=np.nan, hi=np.nan, pct3=100.0, n12=0, method='zero by construction'),
         dict(label='Restricted comparator rule', est=0.0, lo=np.nan, hi=np.nan, pct3=100.0, n12=0, method='zero by construction'),
         dict(label='Interaction comparator rule', est=0.0, lo=np.nan, hi=np.nan, pct3=100.0, n12=0, method='zero by construction'),
         dict(label='Constrained comparator rule', est=0.0, lo=np.nan, hi=np.nan, pct3=100.0, n12=0, method='zero by construction'),
         dict(label='Minimally penalized interaction rule', est=N['pwf'][0], lo=N['pwf'][1], hi=N['pwf'][2], pct3=100 * P['policy']['pwf'][3], n12=int(P['policy']['pwf'][2]), method='doubly robust score')]
if bs is not None:
    rows.append(dict(label='Causal survival forest rule, clustered bootstrap', est=bs.learned_minus_all3.mean(), lo=bs.learned_minus_all3.quantile(.025), hi=bs.learned_minus_all3.quantile(.975),
                     pct3=100 * bs.frac3.mean(), n12=np.nan, method='clustered full-pipeline bootstrap'))
pd.DataFrame(rows).to_csv(F + 'fig4_rows.csv', index=False)

lab = [('h360', 'Horizon day 360', 'forest'), ('h270', 'Horizon day 270', 'forest'), ('h180', 'Horizon day 180', 'forest'),
       ('nosite', 'Discovery without site codes', 'forest'), ('mns20', 'Minimum node size 20', 'forest'), ('mns80', 'Minimum node size 80', 'forest'),
       ('seed2', 'Fold seed 20260908', 'forest'), ('seed3', 'Fold seed 20260909', 'forest'), ('age80', 'Exclude 4 participants aged over 80', 'forest'),
       ('site01', 'Released site code 01 only', 'forest'), ('discrepant', 'Exclude the record with discrepant follow-up', 'forest'),
       ('wins', 'Scores winsorized at 1st and 99th percentiles', 'forest'), ('landmark90', 'Day 90 to 365 landmark', 'forest'),
       ('landmark85', 'Day 85 landmark with course to date', 'forest'), ('nace', 'Net adverse clinical events', 'forest'),
       ('isch', 'Ischemic composite', 'forest'), ('reverse', 'Reverse transport, other codes to code 01', 'comparator'),
       ('train01', 'Train on code 01, evaluate other codes', 'forest'), ('smoke3', 'Three-level smoking encoding', 'forest'), ('grf261', 'Repeat under grf 2.6.1', 'forest')]
r6 = []
for k, l, m in lab:
    if k in sens:
        s = sens[k]; r6.append(dict(key=k, label=l, n=s['n'], mean=s['mean_score'], lo=s['lo'], hi=s['hi'], contrast=s['learned_minus_all3'],
                                    clo=s.get('lm_lo', np.nan), chi=s.get('lm_hi', np.nan), n12=s['n12'], model=m))
pd.DataFrame(r6).to_csv(F + 'fig6_rows.csv', index=False)
print(len(rows), len(r6))
