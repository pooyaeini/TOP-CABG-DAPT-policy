import pandas as pd, numpy as np, json, itertools
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
from sklearn.model_selection import StratifiedKFold
import xgboost as xgb
import statsmodels.api as sm

d = pd.read_csv('work/patients.csv', dtype={'site': str, 'pid': str})
so = pd.read_csv('data/raw/svg_occ_main.csv', dtype={'site': str})
occ = so.groupby('pid').occluded_status.max()
g = d[d.pid.isin(occ.index)].copy(); g['occ'] = g.pid.map(occ).astype(int)
CONT = ["AGE", "BMI", "PRE_EGFR", "LDLC", "LVEF", "A_GRAFT", "V_GRAFT", "SYNTAX"]
BIN = ["men", "Diabetes", "HTN", "Lipid", "PAD", "Cere", "ACS_2w", "MI", "PCI", "Onpump", "No_touch", "Seq_SVG"]

def encode(tr, te):
    def out(x):
        c = {}
        for v in CONT + BIN:
            m = tr[v].median(); c[v + '_miss'] = x[v].isna().astype(float); c[v] = x[v].fillna(m)
        c['smoke_never'] = (x.smoke_status == 1).astype(float)
        for v in ['CCS', 'NYHA']:
            for l in range(1, 5): c[f'{v}_{l}'] = (x[v] == l).astype(float)
        for s in ['01', '14', '17', '98', '99']: c['site_' + s] = (x.site == s).astype(float)
        c['W'] = x.W.astype(float)
        return pd.DataFrame(c)
    A, B = out(tr), out(te); keep = A.columns[A.std() > 0]
    return A[keep].values, B[keep].values

def cal(y, p):
    lp = np.log(p / (1 - p)); m = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial()).fit()
    citl = sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Binomial(), offset=lp).fit().params[0]
    return m.params[1], citl

Cs = np.logspace(-4, 2, 13)
grid = [dict(max_depth=a, learning_rate=b, min_child_weight=c, subsample=s, colsample_bytree=s2, reg_lambda=l)
        for a, b, c, s, s2, l in [(2, .03, 5, .8, .8, 1), (2, .05, 5, .8, 1., 5), (2, .08, 5, .8, 1., 5), (2, .05, 15, .8, .8, 5),
                                  (3, .05, 5, 1., .8, 5), (3, .03, 15, 1., 1., 1), (2, .03, 15, 1., .8, 5), (3, .08, 5, .8, .8, 1),
                                  (3, .05, 15, .8, 1., 5), (2, .08, 15, 1., 1., 1), (3, .03, 5, .8, 1., 5), (2, .05, 5, 1., 1., 1)]]
pr = np.full(len(g), np.nan); px = np.full(len(g), np.nan); tune = []
for k in range(5):
    tr = g[g.fold != k]; te = g[g.fold == k]; Xtr, Xte = encode(tr, te); ytr = tr.occ.values
    mu, sd = Xtr.mean(0), Xtr.std(0); Ztr, Zte = (Xtr - mu) / sd, (Xte - mu) / sd
    inner = StratifiedKFold(3, shuffle=True, random_state=20260907 + k)
    ll = []
    for C in Cs:
        s = 0
        for a, b in inner.split(Ztr, ytr):
            m = LogisticRegression(C=C, max_iter=5000).fit(Ztr[a], ytr[a]); s += log_loss(ytr[b], m.predict_proba(Ztr[b])[:, 1], labels=[0, 1])
        ll.append(s)
    Cb = Cs[int(np.argmin(ll))]; m = LogisticRegression(C=Cb, max_iter=5000).fit(Ztr, ytr); pr[(g.fold == k).values] = m.predict_proba(Zte)[:, 1]
    best = None
    for j, p in enumerate(grid):
        s = 0; rounds = []
        for a, b in inner.split(Xtr, ytr):
            mdl = xgb.XGBClassifier(n_estimators=1000, early_stopping_rounds=30, eval_metric='logloss', random_state=20260907, n_jobs=1, **p)
            mdl.fit(Xtr[a], ytr[a], eval_set=[(Xtr[b], ytr[b])], verbose=False)
            s += log_loss(ytr[b], mdl.predict_proba(Xtr[b])[:, 1], labels=[0, 1]); rounds.append(mdl.best_iteration + 1)
        if best is None or s < best[0]: best = (s, p, int(np.mean(rounds)))
    mdl = xgb.XGBClassifier(n_estimators=best[2], eval_metric='logloss', random_state=20260907, n_jobs=1, **best[1]).fit(Xtr, ytr)
    px[(g.fold == k).values] = mdl.predict_proba(Xte)[:, 1]
    tune.append(dict(fold=k, n=len(te), occl=int(te.occ.sum()), C=float(Cb), rounds=best[2], **best[1]))
y = g.occ.values; res = {}
for nm, p in [('ridge', pr), ('xgb', px)]:
    sl, citl = cal(y, p)
    res[nm] = dict(auc=roc_auc_score(y, p), auprc=average_precision_score(y, p), brier=brier_score_loss(y, p), logloss=log_loss(y, p),
                   slope=sl, citl=citl, pmin=float(p.min()), pmax=float(p.max()))
res['prevalence'] = float(y.mean()); res['tuning'] = tune
json.dump(res, open('work/graft_models.json', 'w'), indent=1, default=float)
pd.DataFrame(dict(pid=g.pid, occ=y, p_ridge=pr, p_xgb=px)).to_csv('work/graft_pred.csv', index=False)
print({k: {a: round(b, 4) for a, b in v.items()} for k, v in res.items() if k in ('ridge', 'xgb')}, res['prevalence'])
