"""Aalen-Johansen cumulative incidence of bleeding and of death without prior bleeding at day 365, by arm.

Run from the repository root after analysis/build.py. Bleeding takes precedence when both occur on the same day.
Writes work/aj.json (percentages; b = bleeding, d = death, 12 = twelve-month arm, 3 = three-month arm).
"""
import json
import numpy as np
import pandas as pd

d = pd.read_csv('work/patients.csv', dtype={'site': str})


def aalen_johansen(g, horizon=365):
    T = np.minimum(g.blood_day, g.death_day).values
    bl = ((g.blood == 1) & (g.blood_day == T)).values
    de = ((g.death == 1) & (g.death_day == T)).values & ~bl
    s, cb, cd = 1.0, 0.0, 0.0
    for t in np.unique(T[(bl | de) & (T <= horizon)]):
        n = (T >= t).sum(); db = (bl & (T == t)).sum(); dd = (de & (T == t)).sum()
        cb += s * db / n; cd += s * dd / n; s *= 1 - (db + dd) / n
    return 100 * cb, 100 * cd


b12, d12 = aalen_johansen(d[d.W == 0])
b3, d3 = aalen_johansen(d[d.W == 1])
res = {k: round(float(v), 6) for k, v in dict(b12=b12, d12=d12, b3=b3, d3=d3).items()}
json.dump(res, open('work/aj.json', 'w'))
print(res)
