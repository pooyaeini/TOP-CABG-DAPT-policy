"""Summaries of the bootstrap and simulation replicates reported in the manuscript and Supplementary Tables S9 and S10.

Run from the repository root after analysis/summarize.R. Reads work/boot_summary.csv and work/sim_summary.csv.
Writes work/bootstrap_table.json and work/simulation_table.csv.
A simulation replicate counts as detecting personalization when its estimated gain exceeds the
95th percentile of the gains estimated in scenario B0, which has no heterogeneity.
"""
import json
import numpy as np
import pandas as pd

W = 'work/'
BS = pd.read_csv(W + 'boot_summary.csv')
SIM = pd.read_csv(W + 'sim_summary.csv')


def boot_stats(b):
    x = b.learned_minus_all3
    return dict(replicates=len(b), learned_minus_all3_mean=x.mean(), learned_minus_all3_median=x.median(),
                learned_minus_all3_lo=x.quantile(.025), learned_minus_all3_hi=x.quantile(.975), learned_minus_all3_sd=x.std(),
                replicates_value_zero=int((x == 0).sum()), replicates_value_positive=int((x > 0).sum()),
                replicates_all_three_months=int((b.frac3 == 1).sum()), mean_fraction_three_months=b.frac3.mean(),
                min_fraction_three_months=b.frac3.min(),
                all12_minus_all3_mean=b.all12_minus_all3.mean(), all12_minus_all3_lo=b.all12_minus_all3.quantile(.025),
                all12_minus_all3_hi=b.all12_minus_all3.quantile(.975), mean_score=b.mean_score.mean(),
                autoc_lo=b.autoc.quantile(.025), autoc_hi=b.autoc.quantile(.975), autoc_sd=b.autoc.std(), qini_sd=b.qini.std(),
                slope_lo=b.slope.quantile(.025), slope_hi=b.slope.quantile(.975), median_seconds=b.secs.median())


def sim_stats(s):
    q95 = s[s.scenario == 'B0'].v_hat.quantile(.95)
    rows = []
    for sc, g in s.groupby('scenario'):
        R = len(g); pw = (g.v_hat > q95).mean()
        rows.append(dict(scenario=sc, replicates=R, median_events365=g.events365.median(),
                         true_ate=g.true_ate.mean(), est_ate=g.est_ate.mean(), bias_ate=(g.est_ate - g.true_ate).mean(),
                         empirical_se_ate=g.est_ate.std(), mcse_bias_ate=g.est_ate.std() / np.sqrt(R), coverage_ate=g.ate_cover.mean(),
                         oracle_gain=g.oracle_gain.mean(), best_constant_gain=g.best_const_gain.mean(),
                         oracle_minus_best_constant=(g.oracle_gain - g.best_const_gain).mean(),
                         value_estimated=g.v_hat.mean(), value_true=g.v_true.mean(), bias_value=(g.v_hat - g.v_true).mean(),
                         empirical_se_value=g.v_hat.std(), mcse_bias_value=(g.v_hat - g.v_true).std() / np.sqrt(R),
                         coverage_value=g.v_cover.mean(), detection_threshold=q95, power=pw, mcse_power=np.sqrt(pw * (1 - pw) / R),
                         mean_n12=g.n12.mean(), true_fraction12=g.frac12_true.mean(), mean_correlation=g.cor.mean(),
                         sd_correlation=g.cor.std(), agreement_with_oracle=g.agree_oracle.mean(),
                         autoc_estimated=g.autoc.mean(), autoc_true=g.autoc_true.mean(), coverage_autoc=g.autoc_cover.mean()))
    return pd.DataFrame(rows)


json.dump(boot_stats(BS), open(W + 'bootstrap_table.json', 'w'), indent=1, default=float)
sim_stats(SIM).to_csv(W + 'simulation_table.csv', index=False)
print('wrote work/bootstrap_table.json and work/simulation_table.csv')
