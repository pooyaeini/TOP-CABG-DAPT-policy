import pandas as pd, numpy as np, sys, json
R='data/raw/'
b=pd.read_csv(R+'baseline.csv'); e=pd.read_csv(R+'event_main.csv',dtype={'site':str})
d=b.merge(e[['pid','site']+[c for c in e.columns if c not in ('pid','COL_INV','site')]],on='pid')
d['W']=(d.COL_INV=='B').astype(int)
T=np.minimum(d.blood_day,d.death_day)
d['t_raw']=T; d['event_raw']=(((d.blood==1)&(d.blood_day==T))|((d.death==1)&(d.death_day==T))).astype(int)
d.loc[d.Seq_SVG==99,'Seq_SVG']=np.nan
# folds (reproduces Supplementary Table S4 exactly)
def make_folds(seed):
    f=pd.Series(-1,index=d.index); rng=np.random.default_rng(seed)
    for key in sorted(d.groupby(['site','COL_INV']).groups.keys()):
        idx=d[(d.site==key[0])&(d.COL_INV==key[1])].sort_values('pid').index.values
        p=rng.permutation(idx); f[p]=np.arange(len(p))%5
    return f
d['fold']=make_folds(20260907)
d['fold_s2']=make_folds(20260908); d['fold_s3']=make_folds(20260909)
d.to_csv('work/patients.csv',index=False)
print(d.shape, d.event_raw.sum(), ((d.event_raw==1)&(d.t_raw<=365)).sum())
