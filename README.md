# TOP-CABG causal policy analysis

Analysis code, dated analysis plan and aggregate results for the manuscript

> Personalized versus uniform dual antiplatelet therapy de-escalation after coronary artery bypass grafting, a causal policy learning analysis of bleeding-free survival in the TOP-CABG trial

The study is a secondary analysis of the public TOP-CABG data release. It asks whether a rule that assigns three or twelve months of dual antiplatelet therapy from randomization-time characteristics improves restricted mean time free of BARC type 2, 3 or 5 bleeding or death through day 365, compared with uniform three-month therapy.

## Repository contents

| Folder | Contents |
|---|---|
| `plan/` | The dated analysis plan referred to in the manuscript |
| `analysis/` | Data preparation, causal survival forests, comparators, policy evaluation, sensitivity analyses, bootstrap and simulation |
| `figures/` | Scripts that draw every main and supplementary figure |
| `results/` | Aggregate results behind every table and figure |
| `data/raw/` | Location for the six released CSV files (not redistributed here) |

## Dated analysis plan

`plan/TOP-CABG_analysis_plan_2026-09-07.md` is deposited without modification (SHA-256 `31b2b2e1f94b478da18a0dc840f5d84fc277b202a1c8ebbbf6f472aef44607ae`). The document states that it was prepared on 7 September 2026, after descriptive inspection of the public release and before any model results were generated. It was written as an executable specification for the analysis code. It was not registered prospectively. Analyses described as prespecified in the manuscript are those in this plan. Deviations from it, and analyses added during peer review, are listed in Supplementary Table S12.

## Data

The input is the TOP-CABG release in the Dryad repository, doi:[10.5061/dryad.jsxksn0qs](https://doi.org/10.5061/dryad.jsxksn0qs), released under CC0. Download the release and place the six CSV files in `data/raw/`. The files used for the reported analysis had these SHA-256 checksums.

| File | SHA-256 |
|---|---|
| `baseline.csv` | `320a0b0b178473c42fab0f1111cb78261c591631fd33a41eb601c73aca819196` |
| `event_main.csv` | `4ac9d84d0eab0e22344f8c700d130b09e5075c5978b0ea784fa6fb0e44a2b009` |
| `graft_main.csv` | `722f5dc15d8498d58610a72346e2cd189d934a5bd940aaf87f3553ff38f03ebc` |
| `svg_occ_main.csv` | `9d515c430803779d6f5678e69d5210b424b3c40f6c4801ddd7ebf06720be1585` |
| `svg_pa_main.csv` | `812d7d626d42d4b43aaf330e9d997b50869b1fcfd040cf335c3362609a895c38` |
| `at_occ_main.csv` | `6775eed0c65e91a505c9ec584d118730d4acf3a3575850c11e85484fcaf6300a` |

Participant-level model outputs (predicted effects, evaluation scores, bootstrap and simulation replicate files) are not included. They are regenerated in `work/` by the scripts below.

## Software

| Component | Version |
|---|---|
| R | 4.3.3 with grf 2.4.0, survival 3.5.8, glmnet 4.1.8, jsonlite 1.8.8 |
| R, version sensitivity analysis | grf 2.6.1 |
| Python | 3.13 with pandas 3.0.5, numpy 2.5.3, scikit-learn 1.9.1, XGBoost 3.4.1, statsmodels 0.15.0, matplotlib 3.11.2 |

Every reported analysis uses grf 2.4.0. If it is installed in a separate R library, set `GRF240_LIB` to that library path. The version sensitivity analysis sets `GRF_LIB=new` and uses grf 2.6.1 from the default library. `GRF_THREADS` sets the number of threads per forest.

## Order of execution

Run every command from the repository root. Outputs are written to `work/`.

```bash
mkdir -p work
python3 analysis/build.py              # analysis file, composite endpoint, outer folds (site by arm strata, seed 20260907)
Rscript analysis/verify_desc.R         # baseline description and reproduction of the published counts
python3 analysis/aalen_johansen.py     # cumulative incidence of bleeding and death, bleeding first on the same day
Rscript analysis/run_primary.R         # causal survival forest, comparators, evaluation scores, policy values,
                                       # calibration, rank-weighted average treatment effects, Kaplan-Meier contrasts
Rscript analysis/run_misc.R            # event reconciliation, censoring diagnostics, decomposition, graft causal forest
Rscript analysis/net.R                 # weighted net benefit rules
Rscript analysis/ibs.R                 # integrated Brier score
python3 analysis/graft_models.py       # baseline graft-risk models
bash analysis/run_sens.sh              # sensitivity, secondary endpoint and landmark analyses, grf 2.6.1 repeat
bash analysis/run_boot.sh 1 500        # participant-clustered full-pipeline bootstrap, 500 replicates
bash analysis/run_sims.sh              # semi-synthetic simulations
Rscript analysis/summarize.R           # replicate summaries and targeting operator characteristic curves
python3 analysis/summarize_tables.py   # bootstrap and simulation summaries (Supplementary Tables S9 and S10)
python3 analysis/make_fig_inputs.py    # rows for Figures 4 and 6
python3 figures/make_all.py            # all figures, written to figures/out/
```

The bootstrap and simulation scripts save one file per replicate and skip replicates already present, so they can be run in batches and resumed. Each bootstrap replicate took about 30 seconds on one core. The favorable simulation scenario (A7) took about 4 minutes per replicate.

## Results and figures

`results/` holds the aggregate outputs of the steps above, copied from `work/`.

| File | Content |
|---|---|
| `primary.json` | Primary analysis, policy values, calibration, rank-weighted average treatment effects, Kaplan-Meier contrasts, censoring support |
| `misc.json` | Event reconciliation, censoring diagnostics, decomposition of the restricted mean difference, graft causal forest |
| `net.json`, `ibs.json`, `graft_models.json`, `aj.json` | Weighted net benefit rules, prognostic accuracy, graft-risk models, competing-risk incidence |
| `sens/*.json` | One file per sensitivity, secondary endpoint or landmark analysis |
| `boot_summary.csv`, `bootstrap_table.json` | One row per bootstrap replicate and the summary reported in the manuscript |
| `sim_summary.csv`, `simulation_table.csv` | One row per simulation replicate and the summary by scenario |
| `toc.csv`, `fig4_rows.csv`, `fig6_rows.csv` | Inputs for Supplementary Figure S5 and Figures 4 and 6 |

| Figure | Script |
|---|---|
| Figure 1, Figure 2, Supplementary Figure S4 | `figures/fig_data_only.py` |
| Figure 3 | `figures/fig3.py` |
| Figure 4 | `figures/fig4.py` |
| Figure 5 | `figures/fig5.py` |
| Figure 6 | `figures/fig6.py` |
| Supplementary Figures S1, S2, S3 | `figures/figS1.py`, `figures/figS2.py`, `figures/figS3.py` |
| Supplementary Figures S5 to S11 | `figures/figS5.py` to `figures/figS11.py` |

Figures 3 and 6 and Supplementary Figures S6 to S8 need the participant-level outputs in `work/`. The other figures can be drawn from `results/` alone by setting `TOPCABG_WORK=results` and `TOPCABG_FIGS=results`, except those based directly on the released files, which need `analysis/build.py` first.

## Citation

If you use this code, please cite the manuscript (under review), the trial report and the data release.

Yuan X, Li J, Lei L, et al. Efficacy of dual antiplatelet therapy for three months versus 12 months after coronary artery bypass grafting, multicentre, double blinded, randomised controlled trial. BMJ 2026;393:e088939. doi:[10.1136/bmj-2025-088939](https://doi.org/10.1136/bmj-2025-088939)

Yuan X, Li J, Lei L, et al. Data from three-month dual antiplatelet treatment versus twelve-month dual antiplatelet treatment after coronary artery bypass grafting. Dryad, 2026. doi:[10.5061/dryad.jsxksn0qs](https://doi.org/10.5061/dryad.jsxksn0qs)
