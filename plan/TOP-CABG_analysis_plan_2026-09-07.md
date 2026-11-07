# TOP-CABG: executable research and implementation plan

**Prepared:** 7 September 2026. **Target machine:** Linux, 64 GB RAM, 32 CPU cores, NVIDIA RTX 3060 with 12 GB VRAM. **Deliverable:** a reproducible research repository, validated analyses, and a publication package. This is a specification for a coding agent; model results have not yet been generated.

## 1. Instructions to the coding agent

Read this entire document before writing code. Implement and execute the project on the user's server, starting with environment inspection and public data acquisition. Continue through all feasible stages without repeatedly asking permission for routine installation into a project environment, local analysis, or figure generation. Use the defaults here unless a documented incompatibility requires an amendment. Never silently change the clinical question, endpoint, treatment coding, evaluation design, or inferential method to make code run.

Maintain `STATUS.md` with completed stages, active work, blockers, elapsed time, and the exact next command. Maintain `DECISIONS.md` for deviations and their scientific consequences. A failed optional analysis must not prevent completion of other valid analyses. A failed primary statistical validity check must prevent a positive primary claim, even if attractive figures can be produced.

Do not fabricate results, references, external validation, ethics approval, preregistration, or significance. Do not select a random seed, endpoint, model, subgroup, or threshold because it gives the most favorable result. Do not contact investigators, submit a manuscript, publicly upload patient-level predictions, or create accounts without the user's authorization. A research codebase and manuscript package are authorized; autonomous journal submission is not.

The project is **machine learning for a randomized treatment decision**, not a deep-learning demonstration. There are 2,290 patients and relatively few clinical events. No CT images, ECG waveforms, or longitudinal laboratory streams are supplied. Do not build a CNN, transformer, LLM agent, reinforcement-learning simulator, or synthetic-patient generator to create artificial novelty. Use the GPU only where a measured benchmark supports it. CPU-based statistical learning is the main workload.

## 2. Chosen question and honest novelty claim

**Working title:** *Does personalized dual antiplatelet therapy duration improve on uniform de-escalation after coronary artery bypass grafting? A cross-fitted survival and graft-outcome analysis of TOP-CABG.*

**Primary question:** Among patients represented in the released TOP-CABG modified intention-to-treat cohort, can a baseline treatment rule choosing three versus twelve months of DAPT improve the restricted mean time alive and free of a first clinically relevant bleeding event, compared with assigning everyone to three months?

**Secondary question:** How does any proposed rule relate to observed graft outcomes, and how sensitive is that assessment to missing imaging and the concentration of patients and bleeding events in one released site group?

The important comparison is with **uniform three-month treatment**, not merely uniform twelve-month treatment. Predicting bleeding accurately does not establish that individual treatment choices improve outcomes. An estimated difference in benefit magnitude does not necessarily mean anyone should receive the longer regimen.

The proposed contribution combines a decision-focused estimand, honest evaluation of a learned rule, a simple risk-based comparator, censoring-aware analysis, and a transparent graft-outcome audit. None of the algorithms is itself new. A finding that personalization does not demonstrably improve on uniform shorter treatment is a valid and potentially useful result.

### 2.1 What is already known

TOP-CABG randomized patients shortly after CABG to regimens that were identical for the initial three months. The main publication already examined treatment subgroups and a 90-day landmark analysis. Therefore, another age/sex/bleeding-score subgroup forest plot, or simply restricting analysis to bleeding after day 90, is not an adequate novelty claim. The trial report also identifies limitations in generalizability and missing graft assessment. Read the [primary trial](https://www.bmj.com/content/393/bmj-2025-088939) and [protocol](https://bmjopen.bmj.com/content/13/6/e070823) before implementation.

Causal forests have already been applied to CABG questions, including a secondary analysis of STICH. Do not describe this project as the first use of causal ML in cardiac surgery. See the [STICH analysis](https://pubmed.ncbi.nlm.nih.gov/37716652/).

Targeted public searches on 7 September 2026 did not identify an exact TOP-CABG secondary analysis matching this proposed question. That is a limited search result, not proof that no other researcher is working on it. The original investigators have already used this dataset. “Previously unused dataset” is an incorrect claim.

### 2.2 Required literature update before freezing the analysis

Create `docs/novelty_search.csv` with date, database, query, title, DOI/URL, eligibility, overlap, and reason for inclusion/exclusion. Search PubMed, Europe PMC, Crossref, and accessible preprint indexes. Use both `TOP-CABG` and `TOPCABG`, trial registration `NCT05380063`, data DOI `10.5061/dryad.jsxksn0qs`, and combinations of `heterogeneous treatment effect`, `causal forest`, `machine learning`, `personalized`, `policy learning`, `DAPT duration`, `bleeding`, and `graft occlusion`. Inspect original studies, not search snippets alone. Record search failures rather than claiming a database was searched successfully.

If an exact competing analysis exists, document it and continue the reproducibility and data-audit stages. Amend the paper's contribution toward independently evaluated policy benefit, missing-imaging sensitivity, or an honest negative result only if that distinction is real. Do not invent a new algorithm name to conceal overlap.

Save a dated `docs/SAP_v1.md` before fitting outcome-driven candidate models. This is a **secondary, post hoc study**, and the descriptive data inspection summarized below has already occurred. A timestamped analysis plan is not a prospective trial preregistration. The user may later register the secondary analysis, disclosing prior access.

## 3. Dataset access and independently verified facts

### 3.1 Public source

- Repository: [TOP-CABG on Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.jsxksn0qs).
- Dataset DOI: `10.5061/dryad.jsxksn0qs`.
- Public release inspected: **31 March 2026**.
- Repository displays a CC0 data license; preserve the displayed license and citation when downloading.
- Trial registry: [NCT05380063](https://clinicaltrials.gov/study/NCT05380063).

The complete archive was successfully downloaded through the public browser interface without registration during preparation of this plan. Direct scripted file requests returned HTTP 403 in the preparation environment. This does **not** mean the dataset requires an account. Dryad's authenticated API download route and the public browser download are different mechanisms. Use the ordinary public download interface; do not bypass access controls.

### 3.2 Acquisition procedure

Implement `scripts/download_data.py` with these behaviors:

1. Accept `--archive /path/to/downloaded.zip` and `--source-url URL`. Prefer an explicitly supplied local archive, then a valid cached archive.
2. Otherwise try the public dataset page with a browser downloader using Playwright in an isolated project environment. Resolve the visible **Download full dataset** button from the live page, use `expect_download`, allow up to 90 seconds, and save the resulting file. Do not hardcode a guessed API token or extract private session credentials.
3. Some browser configurations open another tab instead of emitting a download event. Check the configured download directory for a newly completed ZIP and validate it. Never treat an HTML error page named `.zip` as data.
4. Allow at most two public download attempts. If unsuccessful, write clear manual instructions: open the public page on the researcher's computer, select Download full dataset, transfer the ZIP using `scp`, and rerun with `--archive`. Continue environment setup and unit tests while the data transfer is pending. Do not fabricate substitute data.
5. Keep the original archive under `data/source/`, compute SHA-256, and extract only the expected filenames. Reject absolute paths, `..` traversal, symlinks, and unexpected executable files. Enforce a 25 MB uncompressed size ceiling for this release; a larger future release requires a documented manifest review.
6. Keep `data/raw/` immutable after extraction. Never overwrite source CSVs with cleaned versions.
7. Save access date, source URL, repository version, archive hash, file hashes, byte sizes, headers, and row counts in `data/source/manifest.json`.

The inspected archive was named `doi_10_5061_dryad_jsxksn0qs__v20260331.zip`, 884,375 bytes, with SHA-256:

```text
ec4e61a9cbc1f4edf55ad8ca4c751dd592d5f090122225a3b9937c3252bc7e75
```

ZIP packaging can change without CSV contents changing. Use individual file hashes as the stronger content check. A changed hash is a version discrepancy to investigate, not a reason to edit data until it matches.

### 3.3 Verified content manifest

These counts come from direct inspection of the downloaded CSV files, not from assuming that each row is a patient.

| File | Rows | Unique patients | Unit and purpose |
|---|---:|---:|---|
| `baseline.csv` | 2,290 | 2,290 | Baseline and surgery descriptors |
| `event_main.csv` | 2,290 | 2,290 | Clinical event flags and event/censoring times |
| `svg_occ_main.csv` | 5,125 | 2,070 | SVG segments; occlusion status |
| `svg_pa_main.csv` | 5,125 | 2,070 | SVG segments; patency status |
| `at_occ_main.csv` | 2,060 | 1,984 | Arterial graft segments |
| `graft_main.csv` | 7,185 | 2,070 | All-graft segment occlusion/stenosis audit |
| `README.md` | — | — | Dictionary, coding, data provenance |
| `Code_and_software.txt` | — | — | Original analysis code, largely SAS |

```text
baseline.csv          320a0b0b178473c42fab0f1111cb78261c591631fd33a41eb601c73aca819196
event_main.csv        4ac9d84d0eab0e22344f8c700d130b09e5075c5978b0ea784fa6fb0e44a2b009
svg_occ_main.csv      9d515c430803779d6f5678e69d5210b424b3c40f6c4801ddd7ebf06720be1585
svg_pa_main.csv       812d7d626d42d4b43aaf330e9d997b50869b1fcfd040cf335c3362609a895c38
at_occ_main.csv       6775eed0c65e91a505c9ec584d118730d4acf3a3575850c11e85484fcaf6300a
graft_main.csv        722f5dc15d8498d58610a72346e2cd189d934a5bd940aaf87f3553ff38f03ebc
Code_and_software.txt e9dc28529fa6fad9f30e04e8b85ac2257ed08a3268965dda905e4b3b55d227b7
README.md             67536cc9e0ee4a4cd306e8650f176ce272a0f4641c776d507e5064a5d51717af
```

### 3.4 Treatment and follow-up coding

Use the following mapping everywhere, including figures, scores, and tests:

```python
TREATMENT_MAP = {"A": 0, "B": 1}
# W=0: 12-month DAPT, n=1138
# W=1:  3-month DAPT, n=1152
# Positive RMST effect = advantage of shorter treatment.
```

Time zero is **randomization**, not surgery or hospital admission. Treatment assignment occurred on postoperative day 5. The primary population is the 2,290 released modified intention-to-treat participants; do not label it the complete 2,300-person randomized population or manufacture the ten unreleased records. Obtain exact exclusion explanations from the original flow diagram where accessible. Do not make per-protocol or as-treated claims without the requisite adherence data.

For a clinical endpoint, its paired `*_day` variable represents an event time when its event flag is one and a follow-up/censoring time when its flag is zero. The original survival code supports this interpretation. **An event flag of zero with follow-up ending before day 365 is not proof of being event-free at day 365.**

### 3.5 Mandatory audit findings to reproduce

| Check | Expected result in inspected release | Consequence |
|---|---|---|
| Bleeding flags | 244 total: 149 A, 95 B | Too few events for an unrestricted model zoo |
| Bleeding at day ≤90 | 147: 83 A, 64 B | Early period is shared-regimen diagnostic |
| Bleeding after day 90 | 97: 66 A, 31 B | Late HTE is particularly underpowered |
| All-cause deaths | 12: 7 A, 5 B | No complex mortality model |
| Other clinical events | 53 `mace`, 4 `mi`, 38 `stroke`, 9 `revas_cor`, 3 `death_cvd` | Descriptive/supporting analyses only |
| SVG occlusion | 563/5,125 segments; 407/2,070 patients with any occlusion | Patient and segment outcomes differ |
| SVG patient occlusion by arm | 207 A, 200 B | Use correct patient denominators |
| No SVG imaging record | 220 baseline patients | Missing outcome, not negative outcome |
| Nonpatent SVG segments | 799 | Nonpatent does not mean occluded |
| `event_main.svgf` | 408 flags | Not interchangeable with 407 imaged patients with occlusion |
| Missing predictors | `SYNTAX`:168; `LDLC`:22; `Seq_SVG=99`:25 | Impute inside training partitions |
| Age | Four records >80; observed range 28–86 | Flag eligibility discrepancy; retain in primary analysis |
| Nonbleeders with `blood_day<365` | 812 | Administrative visit timing/censoring matters |

The released `site` field has **five codes**, not thirteen usable hospital labels:

| Released site code | Patients | Bleeding flags |
|---|---:|---:|
| `01` | 1,809 | 225 |
| `14` | 122 | 9 |
| `17` | 100 | 1 |
| `98` | 142 | 5 |
| `99` | 117 | 4 |

Preserve these values as strings, including leading zeros. Codes may reflect de-identification or aggregation; do not infer their institutional identities. Approximately 79% of participants and 92% of recorded bleeding events are in code `01`. This may reflect case mix or ascertainment differences and does not establish which explanation is correct. It sharply limits claims of geographic transportability.

`graft_main.csv` has 7,185 rows, equal to 5,125 SVG plus 2,060 arterial segments. Its dictionary prose is inconsistent with its all-graft variable labels and original code. Treat it as an all-graft audit file after reproducing counts, document the inconsistency, and do not use it as if every row were an SVG.

No released segment identifier reliably links individual segments across graft files. **Never merge two raw segment files on `pid` alone.** That creates a many-to-many Cartesian product. Aggregate separately to patient level before joining. Identical segment rows can represent separate real segments; do not delete them as duplicates merely because their values match.

## 4. Clinical estimands and outcome construction

### 4.1 Primary endpoint

Use time to the first of **BARC 2/3/5 bleeding or all-cause death**. Estimate restricted mean time in the alive-and-first-bleeding-free state through day 365. This composite is a newly specified secondary-analysis endpoint, not the original trial's primary endpoint.

Including death avoids treating a death before bleeding as an advantageous bleed-free outcome. This does not assign equal clinical severity to death and a minor bleed, does not measure quality-adjusted survival, and does not count recovery time after a bleed. Name it precisely in every output: **restricted mean time alive and free of first BARC 2/3/5 bleeding**.

For patient `i`, construct from the two endpoint-specific observation processes:

```python
t_raw = min(blood_day, death_day)
event_raw = int(
    (blood == 1 and blood_day == t_raw)
    or (death == 1 and death_day == t_raw)
)
t365 = min(t_raw, 365.0)
event365 = int(event_raw == 1 and t_raw <= 365.0)
```

This is conservative when the components have unequal observation ends: after either component is no longer observed, composite event-free status is unknown. Keep raw times and status in the analytic dataset. For GRF, pass `t_raw`, `event_raw`, and `horizon=365`; let the documented implementation handle the horizon. **Never recode all people reaching day 365 as actual bleeding/death events.**

Expected audit: 253 observed composite first events through day 365, 154 A and 99 B, with 803 patients conservatively censored before day 365. Recompute these numbers. One nonbleeding death record has discrepant component follow-up ends; keep conservative censoring in the primary analysis, list the discrepancy privately, and test a documented alternative. Two bleeding/death ties should remain a single composite first event.

The planned potential-outcome estimand is:

\[
\tau(x)=E[\min(T^{1},365)-\min(T^{0},365)\mid X=x].
\]

`T^1` and `T^0` refer to the composite first-event time under shorter and longer assignment. `tau` is measured in days and is a conditional average, not an observable individual treatment effect. Identification additionally requires adequate censoring support and conditional independent censoring; randomization alone does not solve missing follow-up.

### 4.2 Primary policy and primary contrast

Learn a fixed rule on a training partition:

```python
d_x = 1 if predicted_tau_days >= 0 else 0
# Exact ties choose the shorter regimen.
```

The **single primary contrast** is the estimated policy value minus the value of uniform shorter treatment, in restricted mean event-free days per patient. Evaluate it only using held-out participants and censoring-robust scores. A positive result requires more than an internally attractive CATE histogram.

This rule optimizes the stated bleeding/death endpoint only. Graft safety is assessed separately. It must not be described as an established optimal overall antiplatelet recommendation. No deployment or patient treatment advice is part of this project.

### 4.3 Secondary endpoints and analyses

1. **Bleeding cumulative incidence** through day 365 with death before bleeding as a competing event. Use Aalen–Johansen estimates for descriptive arm comparisons. For ties, specify a deterministic rule and repeat with the alternative; do not double count.
2. **RMST through day 360**, specified now because annual visits may occur before day 365. Do not choose between 360 and 365 after inspecting significance.
3. **Day 0–90 analysis:** treatment groups received the same planned drugs in this interval. Analyze early composite and bleeding outcomes as a diagnostic for chance imbalance, overfitting, or ascertainment effects. It is not guaranteed to be exactly null in a finite sample and is not a formal proof of model validity.
4. **Day 90–365 landmark sensitivity:** include only patients alive, free of the composite event, and known to be observed at day 90; reset time by subtracting 90. Clearly label the selected survivor population and the approximately 101 late composite events seen in the full raw audit. Selection can compromise the original randomization; do not substitute this for the primary baseline-randomized analysis or claim a newly randomized day-90 trial. Use a simple model as default; complex late HTE is exploratory.
5. **Patient-level any SVG occlusion** among the 2,070 patients with released SVG assessment. Use `max(occluded_status)` within `pid`. Without imaging dates, call this the scheduled annual assessment, not a precisely observed day-365 outcome.
6. **Segment-level SVG occlusion** for reproduction/support: account for within-patient clustering, not 5,125 independent people.
7. **All-cause death, MACCE, MI, stroke, revascularization:** descriptive treatment contrasts with uncertainty. Do not train separate high-dimensional models for endpoints with only 3–53 events.

Do not apply the trial's segment-level 3.5-percentage-point noninferiority margin to patient-level occlusion, a learned policy, or a different composite. A nonsignificant harm comparison does not establish safety or noninferiority.

## 5. Server setup and resource use

### 5.1 Environment inspection before installation

Create the project in a user-writable directory, default `$HOME/projects/topcabg_policy`. Do not repurpose `HOME`, change GPU drivers, upgrade system packages globally, or terminate unrelated jobs. Inspect `uname -a`, `lscpu`, `free -h`, `df -h`, `nvidia-smi`, `python3 --version`, and `R --version`. Record results in `reports/environment/system.txt`, excluding credentials and unrelated environment variables.

Use an isolated environment. Preferred: existing micromamba/conda with Python 3.11 and a currently compatible R 4.x; otherwise Python `venv` plus the available R installation and a project-local R library. If R is unavailable and system installation is not permitted, use a user-space package manager. Do not replace causal-survival analysis with ordinary classification merely because Python-only code is easier.

Python dependencies: `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `pyarrow`, `pyyaml`, `psutil`, `joblib`, `pytest`, `requests`, and optional `playwright`, `xgboost`, `scikit-survival`. R dependencies: `grf`, `survival`, `glmnet`, `jsonlite`, `data.table`, `sandwich`, `geepack`, `renv`, and `testthat`. Add a package only when a documented analysis needs it. Use `survival` for competing-risk descriptive estimates if possible rather than a large redundant dependency stack.

Resolve compatible versions once, run the smoke suite, then commit exact versions in `requirements.lock.txt`, `renv.lock`, and `sessionInfo.txt`. Avoid asserting that an untested list of arbitrary versions is a validated environment. Provide `environment.yml` or equivalent bootstrap script plus restore commands.

### 5.2 Resource policy

| Workload | Default allocation | Rationale |
|---|---|---|
| Data audit and figures | 1–4 CPU threads | Source data are under 1 MB |
| Main outer-fold fits | 4 concurrent jobs × 6 threads | 24 threads total; leave system headroom |
| Small bootstrap refits | Start 8 jobs × 2 threads | Benchmark memory and overhead before increasing |
| Large single forest | Up to 24 threads | Use only when parallel folds are not active |
| GPU booster benchmark | One process, no simultaneous GPU fits | Avoid VRAM contention |
| RAM | 48 GB soft target; 54 GB stop-launch threshold | Leave memory for OS and other processes |
| GPU | 8 GB target working set; single job | 12 GB is capacity, not a utilization goal |

Set thread limits explicitly for each worker. Avoid `n_jobs=-1` in every nested estimator. In a many-process stage, cap BLAS/OpenMP threads and pass the chosen `num.threads` to GRF. Read the [scikit-learn parallelism guidance](https://scikit-learn.org/stable/computing/parallelism.html) when implementing the scheduler.

```bash
export OMP_NUM_THREADS=2
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MPLBACKEND=Agg
```

These are starting values for bootstrap workers, not universal settings for all stages. The scheduler may assign six GRF threads to a main-fold job while preventing nested BLAS oversubscription.

Every expensive stage must log wall time, peak resident memory, CPU allocation, seed, input hash, and package versions. Monitor available memory before launching jobs; wait or reduce future concurrency rather than killing other users' processes. Save completed fold and bootstrap outputs atomically so interrupted work resumes.

### 5.3 GPU and waiting-time rules

The primary GRF analysis runs on CPU. A small tabular dataset often trains faster on CPU once GPU setup and transfer overhead are included. Benchmark CPU versus CUDA on the **same training partition**, parameters, and seed for the optional XGBoost graft-risk comparator; choose the device using wall time and numerical validity, never held-out outcome performance.

For a compatible current XGBoost build, CUDA configuration is `tree_method="hist", device="cuda"`; verify the installed version's official [GPU documentation](https://xgboost.readthedocs.io/en/stable/gpu/) and driver requirements. Do not blindly install a wheel requiring a newer driver or use obsolete parameters. CPU fallback is a successful supported configuration.

Do not force deep learning to occupy VRAM. Do not spend hours tuning a neural network on 2,290 tabular cases. Use spare CPU capacity for prespecified uncertainty estimation and sensitivity analyses. Do not claim a runtime before measuring: benchmark one full fold and five refits, then write a conservative completion-time estimate to `reports/runtime_estimate.json`.

## 6. Repository structure and executable interface

Implement this structure. Files named below are deliverables, not placeholders to leave empty.

```text
topcabg_policy/
  plan.md
  README.md
  STATUS.md
  DECISIONS.md
  Makefile
  environment.yml
  requirements.lock.txt
  renv.lock
  config/analysis.yaml
  config/features.yaml
  data/source/manifest.json
  data/source/<original_archive>.zip
  data/raw/<eight_original_files>
  data/derived/patients.parquet
  data/derived/svg_patients.parquet
  data/derived/folds.csv
  data/derived/data_dictionary.csv
  docs/SAP_v1.md
  docs/novelty_search.csv
  docs/endpoint_decisions.md
  docs/deviations.md
  scripts/bootstrap.sh
  scripts/download_data.py
  scripts/run_pipeline.py
  scripts/run_survival.R
  src/topcabg/io.py
  src/topcabg/audit.py
  src/topcabg/endpoints.py
  src/topcabg/features.py
  src/topcabg/folds.py
  src/topcabg/resources.py
  src/topcabg/graft_models.py
  src/topcabg/metrics.py
  src/topcabg/figures.py
  src/topcabg/tables.py
  R/preprocess.R
  R/piecewise_survival.R
  R/causal_survival.R
  R/policy_evaluation.R
  R/competing_risks.R
  R/bootstrap.R
  tests/<meaningful_data_and_statistical_tests>
  models/<run_id>/<fold>/<model>.rds
  outputs/predictions/<run_id>.parquet
  outputs/scores/<run_id>.parquet
  outputs/bootstrap/<replicate_id>.json
  outputs/metrics/<analysis>.json
  reports/audit.json
  reports/audit.md
  reports/environment/
  reports/figures/main/
  reports/figures/supplement/
  reports/tables/main/
  reports/tables/supplement/
  reports/quality_report.md
  manuscript/manuscript.md
  manuscript/figure_legends.md
  manuscript/references.bib
  manuscript/TRIPOD_AI_mapping.csv
  manuscript/PATH_mapping.csv
  manuscript/PROBAST_AI_assessment.md
  logs/<stage>.jsonl
```

Use a Python driver invoking `Rscript` with a JSON configuration and explicit input/output paths. Prefer CSV/JSON at the R/Python boundary to avoid expensive R Arrow builds. Validate `pid` as a string and preserve row order through explicit joins. Do not install `rpy2` unless a concrete need arises.

Implement these commands and make their help text accurate:

```bash
bash scripts/bootstrap.sh
python scripts/run_pipeline.py --stage acquire --archive /path/to/archive.zip
python scripts/run_pipeline.py --stage audit
python scripts/run_pipeline.py --stage prepare
python scripts/run_pipeline.py --stage test
python scripts/run_pipeline.py --stage benchmark
python scripts/run_pipeline.py --stage fit --profile full --resume
python scripts/run_pipeline.py --stage evaluate --resume
python scripts/run_pipeline.py --stage bootstrap --profile full --resume
python scripts/run_pipeline.py --stage sensitivity --resume
python scripts/run_pipeline.py --stage report --resume
python scripts/run_pipeline.py --stage verify
```

Also support `--stage all`, `--profile smoke`, and `--dry-run`. The driver must discover dependency order, skip only outputs whose input/config/code hashes match, and never count a smoke result as a full result. Save the exact invoked commands in `reports/run_manifest.json`. Use `tmux` or an existing job manager for long execution; do not introduce a cluster framework for this machine.

### 6.1 Frozen configuration defaults

```yaml
study:
  name: topcabg_policy
  dataset_doi: 10.5061/dryad.jsxksn0qs
  release: '2026-03-31'
  population: released_modified_intention_to_treat
  primary_horizon_days: 365
  secondary_horizon_days: 360
  landmark_day: 90
  treatment_map: {A: 0, B: 1}
  treatment_probability: 0.5
  primary_endpoint: first_barc235_bleeding_or_all_cause_death
  primary_contrast: learned_policy_minus_uniform_shorter_rmst_days
resampling:
  seed: 20260907
  outer_folds: 5
  inner_folds: 3
  split_strata: [site, COL_INV]
  sensitivity_seeds: [20260908, 20260909]
  bootstrap_replicates: 500
  bootstrap_pilot_replicates: 5
  fixed_prediction_bootstrap_replicates: 2000
forest:
  trees_smoke: 200
  trees_full: 4000
  min_node_size_discovery: 40
  min_node_size_evaluation: 10
  honesty: true
  honesty_fraction: 0.5
  sample_fraction: 0.5
  alpha: 0.05
  tune_parameters: none
  primary_include_site: true
policy:
  threshold_days: 0.0
  tie_treatment: 1
  primary_model: causal_survival_forest
resources:
  total_training_threads: 24
  concurrent_main_jobs: 4
  threads_per_main_job: 6
  concurrent_bootstrap_jobs: 8
  threads_per_bootstrap_job: 2
  ram_soft_gb: 48
  ram_pause_launch_gb: 54
  concurrent_gpu_jobs: 1
  gpu_optional: true
```

`min_node_size` and other settings are conservative design choices, not claimed optimal values. Keep them fixed for the primary analysis. A prespecified node-size sensitivity at 20 and 80 belongs in the supplement; do not promote its most favorable result. Set `mtry=max(1,floor(sqrt(p)))` explicitly for reproducibility. Document parameter names against the installed GRF API.

## 7. Data preparation and leakage controls

### 7.1 Required functions and contracts

- `load_raw(path) -> dict[str, DataFrame]`: preserve identifiers; assert exact required columns; normalize blank missing values without silently modifying category codes.
- `audit_raw(raw) -> AuditReport`: sizes, IDs, arm consistency, sites, missingness, ranges, events, timing conflicts, file hashes, and relational cardinality.
- `build_patient_table(raw) -> DataFrame`: validated one-to-one baseline/event join, then validated one-to-one joins to already aggregated graft summaries.
- `build_primary_endpoint(df, horizon) -> DataFrame`: keep raw and horizon-specific status/time; execute the rules in section 4.
- `aggregate_svg(svg) -> DataFrame`: `pid`, segment count, occluded count, and any-occlusion indicator; preserve all valid segment rows.
- `make_folds(df, seed) -> DataFrame`: assign each original patient to exactly one outer fold within site-by-arm strata; deterministic sorting before shuffling.
- `fit_preprocessor(train, specification)`: learn imputation, scaling, and encodings on training participants only; serialize all learned values.
- `transform(preprocessor, data)`: preserve rows; reject new undocumented fields; encode unseen site/category levels safely without refitting.

### 7.2 Predictor specification

Primary clinical candidate fields, subject to dictionary verification:

```text
AGE, men, smoke_status, BMI, Diabetes, HTN, Lipid, PAD, Cere,
ACS_2w, MI, PCI, CCS, NYHA, PRE_EGFR, LDLC, LVEF,
Onpump, No_touch, Seq_SVG, A_GRAFT, V_GRAFT, SYNTAX
```

Include the five released site codes in the primary forest's feature matrix to allow outcome/censoring adjustment. Consequently the primary rule is conditional on these released groups and is not automatically portable to a new hospital. A required site-excluded discovery-model sensitivity is specified below; its independent evaluator should still include site. Do not pretend the standard GRF API has separate nuisance-only and effect-only covariate lists if it does not.

Surgery descriptors are permissible only because the intended decision time is after surgery at randomization. This is not a preoperative risk calculator. Exclude `pid` from all models. `COL_INV` becomes treatment `W`, never an ordinary baseline risk feature in a causal forest. Outcome flags, follow-up times, imaging availability, postrandomization events, derived event scores, and graft assessment labels must never enter the treatment-rule features.

Primary exclusions:

- `BB`, `RASI`, `Statin`: timing of medication ascertainment is insufficiently clear; exclude unless verified as known before randomization. A documented timing clarification can support a secondary feature set.
- `Ht_cat`, `Wt_cat`: BMI already represents body size; avoid unnecessary categorical expansion.
- `Cre`: use eGFR as the primary renal measure; the dictionary's “Creatine” label needs clarification before calling it creatinine.
- `Bypass`: overlaps with `Onpump` but is not identical; audit rather than assuming equivalence.
- `T_GRAFT`: audit whether it equals `A_GRAFT+V_GRAFT`; avoid including all three redundant counts.
- `sub_*` fields from SVG files: outcome-assessment subset and duplicated/categorized baseline information; audit mappings only.

Use `men` as a coded sex variable. Confirm its mapping against available subgroup coding and trial totals; if still unresolved, label “sex code 0/1” rather than inventing an interpretation. Keep smoking categorical. Use one-hot CCS/NYHA for the main penalized regression; forest ordinal coding is acceptable if documented consistently. Map `Seq_SVG=99` to missing before analysis.

For continuous predictors, use training-fold medians and missingness indicators. For categorical predictors, use an explicit missing category. Fit scaling using training means/SDs for regression only. No whole-dataset imputation, no outcome-informed imputation, no SMOTE, no balancing treatment groups by discarding patients, and no univariate outcome screening.

Retain the four ages above 80 in the primary analysis, because their presence may reflect a release/eligibility discrepancy rather than a correctable error. Run an exclusion sensitivity and record the impact. Do not winsorize variables to force trial eligibility criteria. A clearly impossible value should be flagged and handled under a written rule, with raw values preserved.

Do not reconstruct PRECISE-DAPT, ARC-HBR, or SAFINOUS under their original names unless every required variable, definition, and coding is available. Incomplete proxies are not validated scores.

### 7.3 Relational and timing checks

Assert that all graft IDs are present in baseline, arm labels agree across files, and site codes agree wherever observed. Report disagreement and block the affected merge; do not choose whichever value improves a model. Check binary flags, nonnegative times, events after death, simultaneous events, and component-specific follow-up. Produce endpoint-specific censoring histograms by treatment and site.

Document the difference between “no annual imaging record,” “follow-up before a fixed 365-day cutoff,” and “lost to follow-up.” The original study's high annual follow-up completion can coexist with visits before day 365. The plan's fixed-horizon censoring count must not be misreported as 803 or 812 participants lost to follow-up.

## 8. Reproduce the source study before developing models

Implement a compact reproduction report to verify coding:

1. Baseline counts, arm sizes, age/sex summaries, missing predictors, and the five released site groups.
2. Raw bleeding totals and the ≤90/>90 split.
3. Kaplan–Meier curves for the original bleeding endpoint, with an explicit note that censoring death differs from a competing-risk cumulative incidence interpretation.
4. SVG segment occlusion by arm: A 283/2,529 and B 280/2,596. Reproduce a patient-clustered marginal comparison with treatment and released site, using GEE where feasible.
5. Patient-level any SVG occlusion: A 207 patients, B 200 patients; compute corresponding imaged-patient denominators from data.
6. Compare available source-code estimators and published estimates. A robust Poisson approximation is not numerically identical to a converged log-binomial model; label changes. Published adjusted/KM rates need not equal crude proportions.

Do not require a paid SAS license. Reproduce transparent counts exactly and regression estimates as closely as the released data and supported methods permit. Explain discrepancies, including anonymized site aggregation, endpoint definition, follow-up horizon, and numerical estimator differences. A discrepancy report is preferable to hardcoding published results.

## 9. Modeling strategy

### 9.1 Outer evaluation design

Use five patient-level outer folds stratified by released site and randomized arm. Do not stratify the primary causal split on the observed outcome. Keep the fold map immutable. All preprocessing, parameter tuning, feature decisions, threshold decisions, and model selection occur without using a held-out fold's outcomes for that fold's treatment rule.

There is no additional tiny 20% final holdout. With this event count, repeated data partitioning wastes information. Five-fold cross-fitting uses each participant once for held-out evaluation while retaining approximately 80% for rule training. Report this as internal evaluation, not external validation.

Use three inner folds only where tuning is actually needed. Primary forest settings are fixed. Use the two additional specified seeds as robustness analyses; do not average selectively or pick a favorable split. Final all-data fitted models are for archiving and future validation, not for reporting training-set performance.

### 9.2 Comparator 0: constant treatment policies

Always evaluate both:

- `d_short(x)=1` for everyone.
- `d_long(x)=0` for everyone.

Their difference is an average treatment effect under the chosen endpoint. Improvement over the inferior constant policy alone does not demonstrate value from personalization. The primary reference is the shorter policy chosen before model fitting.

### 9.3 Comparator 1: simple risk-based survival model

Implement a penalized piecewise-exponential model with main predictor effects and separate treatment coefficients in the first 90 days and after day 90. This allows the protocol's delayed treatment divergence without requiring proportional hazards across the entire year. Do not include predictor-by-treatment interactions in this comparator.

Use intervals `(0,30], (30,60], (60,90], (90,180], (180,270], (270,365]`, with time zero as the origin. An event exactly at day 90 belongs to the early period. Flag any time-zero event for a documented handling rule rather than creating a zero-exposure Poisson row. Create a person-period row only for positive observed exposure. Use a Poisson likelihood with `log(exposure_days)` offset. Include interval-specific baseline intercepts, `W*I(early)` and `W*I(late)`, and baseline predictor main effects. Do not include an extra global intercept if the interval indicators already span the intercept. Keep interval and treatment terms unpenalized; penalize clinical/site coefficients with ridge regression.

Choose the ridge penalty by three-fold inner validation using per-patient summed held-out Poisson deviance; all rows from one patient must remain together. Use a fixed logarithmic grid of 20 penalties and the one-standard-error rule. Guard zero exposure and nonfinite rates explicitly.

For each held-out patient, predict interval hazards under `W=1` and `W=0`. Starting with `S(0)=1`, integrate piecewise exponential survival analytically:

\[
\mathrm{RMST}_a=\sum_j S_a(l_j)\frac{1-\exp(-\lambda_{aj}\Delta_j)}{\lambda_{aj}}.
\]

Use the limit `S_a(l_j)*Delta_j` near zero hazard and numerically stable `expm1`. The difference is the simple model's predicted absolute benefit. Even a common relative treatment effect can create differences in absolute benefit by baseline risk; do not interpret such variation as an interaction finding.

Optional prespecified interaction comparator: add only late-treatment interactions with age, eGFR, and SYNTAX, all penalized. This is exploratory and not a replacement for the primary forest. Do not select interactions using whole-data P values.

### 9.4 Primary model: honest causal survival forest

Use R `grf::causal_survival_forest`, targeting RMST with known randomization probability 0.5. Preserve right-censored outcomes. The package exposes the required target and horizon; use the [official API](https://grf-labs.github.io/grf/reference/causal_survival_forest.html) and [survival methods vignette](https://grf-labs.github.io/grf/articles/survival.html).

Implementation skeleton, after training-only preprocessing:

```r
fit <- grf::causal_survival_forest(
  X = X_train,
  Y = t_raw_train,
  W = W_train,
  D = event_raw_train,
  W.hat = rep(0.5, length(W_train)),
  target = "RMST", horizon = 365,
  num.trees = 4000,
  min.node.size = 40,
  mtry = max(1L, floor(sqrt(ncol(X_train)))),
  sample.fraction = 0.5,
  honesty = TRUE, honesty.fraction = 0.5,
  alpha = 0.05,
  tune.parameters = "none",
  num.threads = allocated_threads,
  seed = fold_seed
)
tau_test <- as.numeric(predict(fit, X_test)$predictions)
policy_test <- as.integer(tau_test >= 0)
```

Do not estimate treatment propensity from clinical predictors; treatment was randomized. The observed group sizes do not justify changing 0.5 to the empirical proportion. Do not cluster by the five site groups in a way that falsely turns five released codes into a large independent-hospital sample. Site is adjusted as a predictor; primary inferential scope is conditional on the represented groups.

Use all observed event times initially. Do not round times or reduce the time grid for speed unless a training-only benchmark demonstrates numerical agreement and the change is documented. Do not equate ordinary forest feature importance with causal mechanisms. Do not train a conventional binary causal forest on `blood` while ignoring `blood_day`.

### 9.5 Supporting graft prognostic models

Among assessed patients, fit two models for patient-level any SVG occlusion: ridge logistic regression and a restrained XGBoost classifier. Include treatment as a prediction covariate plus the same baseline feature set. This is a conditional prognostic task in the assessed subset, not automatically a causal treatment-effect analysis of all participants.

Use the same outer patient folds restricted to assessed patients. Fit preprocessing inside training folds. Inner selection minimizes log loss, with Brier score as a secondary check. Do not choose a model by test AUROC. XGBoost search: at most 12 prespecified configurations spanning depth 2–3, learning rate 0.03–0.08, minimum child weight 5–15, row/column subsampling 0.8–1.0, and L2 regularization. Early stopping uses only an inner validation partition. Fix the selected boosting rounds before fitting the full outer training partition.

No SMOTE or class balancing by default. Unweighted loss estimates natural risk. If class weights are explored, recalibration and their consequences must be handled inside training and labeled secondary. Use a maximum of two prognostic model families; an extra 15 algorithms adds little scientific value here.

Do not use SHAP values from this prognostic model to claim who benefits from a treatment. Prognostic risk and treatment-effect heterogeneity are different quantities.

## 10. Honest treatment-effect and policy evaluation

### 10.1 Separate rule discovery from evaluation scores

For each outer fold `k`:

1. Fit each discovery model on the other four folds and obtain treatment-effect predictions and policy assignments for fold `k` without reading its outcomes during rule fitting.
2. Freeze those predictions to disk with a hash before computing evaluation statistics.
3. Build an **evaluation forest using only fold `k`**, with the same clinical covariates plus released site, known propensity 0.5, and the same RMST endpoint. Apply the frozen outer-training preprocessor to its features; include stable predefined site categories. Use honest estimation, 4,000 trees, and evaluation minimum node size 10 because this partition is smaller. Its out-of-bag nuisance estimation is used to construct censoring-robust scores for its training participants.
4. Obtain the vector `Gamma_k <- grf::get_scores(eval_forest)`. Verify its length, ordering, finiteness, and estimand. Do not call a regression `predict` value an evaluation score. The [score API](https://grf-labs.github.io/grf/reference/get_scores.causal_survival_forest.html) is distinct from CATE prediction.
5. Evaluate all frozen policies on this same score vector. The held-out outcomes are permitted for evaluation and nuisance estimation, but never to choose the policy, its threshold, or the discovery model for those participants.
6. Concatenate held-out predictions and scores, retaining fold labels. The discovery/evaluation separation follows the train/evaluation strategy illustrated in the GRF causal-survival documentation. Cross-fold dependence and finite-sample nuisance estimation still require careful uncertainty analysis; do not treat this as five external validations.

The evaluation forest is a scoring instrument, not a second candidate selected for better policy results. Its out-of-bag scores are estimated quantities. With about 450 people and roughly 50 composite events per fold, scores can be noisy. Log censoring support, effective sample size diagnostics, and extreme scores. If scores are persistently invalid or unstable, retain descriptive and prognostic outputs and label the primary policy analysis inconclusive; do not silently replace the scores with uncensored binary labels.

### 10.2 Policy-value equations and signs

Let `Gamma_i` be the held-out evaluation score estimating the RMST treatment contrast, shorter minus longer. For a rule `d_i` that selects shorter treatment when one:

\[
\widehat\Delta_{d,\text{short}}=\frac{1}{n}\sum_i(d_i-1)\Gamma_i,
\qquad
\widehat\Delta_{d,\text{long}}=\frac{1}{n}\sum_i d_i\Gamma_i.
\]

Compare forest and simple-model policies using:

\[
\widehat\Delta_{\text{forest},\text{simple}}=
\frac{1}{n}\sum_i(d_i^{\text{forest}}-d_i^{\text{simple}})\Gamma_i.
\]

Report days per patient, 95% intervals, and the proportion assigned to each regimen. An always-shorter policy must have exactly zero incremental value versus itself. If the learned rule selects shorter treatment for everyone, report that personalization collapsed to the constant policy. Do not introduce another threshold after seeing that result. A degenerate zero interval when two evaluated rules are identical is an algebraic identity for those rules, not proof of clinical equivalence between the two randomized treatments.

The mean of `Gamma` estimates the average shorter-minus-longer RMST effect. Compare it with an independently computed marginal arm-level RMST difference as a reasonableness check, allowing sampling and covariate-adjustment differences. Do not hardcode agreement or a positive sign.

These equations estimate **contrasts**, not each policy's absolute RMST. Do not add them to an unrelated complete-case mean and call the result a causal absolute value. If absolute policy values are later needed, implement a documented arm-specific censoring-robust value estimator and validate it separately; contrasts suffice for this paper.

### 10.3 Heterogeneity diagnostics

Report, as secondary analyses:

- Distribution of out-of-fold predicted `tau` in days, its range, and the fraction crossing zero. This alone is not evidence of real heterogeneity.
- Treatment-effect calibration: regress held-out `Gamma` on centered held-out `tau`, report intercept/slope with appropriate uncertainty. A slope near zero is evidence that predicted differences are poorly supported; do not reinterpret it as successful personalization.
- Three prespecified predicted-benefit groups, using training-derived cutpoints for held-out patients. Report actual participants/events per group and estimates with intervals. Do not show ten thinly supported subgroups.
- AUTOC/RATE using independently obtained priorities and evaluation scores. Check the installed interface of [rank_average_treatment_effect.fit](https://grf-labs.github.io/grf/reference/rank_average_treatment_effect.fit.html). Calculate it separately within each outer evaluation fold, then summarize with patient-count weighting and full-pipeline resampling. Do not pass concatenated cross-fitted predictions to a routine that assumes one globally independent training/evaluation split and accept its default standard error. Use forest-vs-simple ranking as a secondary comparison. Preserve the higher-priority-means-more-shorter-benefit direction.
- Treatment-rule stability across the two additional split seeds: assignment agreement, distribution of policy contrasts, and which patients consistently cross zero. Do not report only the most favorable seed.

Do not calculate individual treatment-effect RMSE, individual benefit AUROC, or “percentage of correctly treated patients” from real trial data: individual counterfactual outcomes are unobserved. Such metrics are permissible only in clearly labeled simulations with known potential outcomes.

### 10.4 Censoring support and scoring diagnostics

Produce reverse-KM follow-up summaries and censoring distributions by randomized arm and released site. Estimate censoring survival support using training/evaluation nuisance procedures appropriate to each analysis. Display risk-set size and the fraction of observations with estimated censoring survival below 0.10 and 0.05 over the evaluation window. Save both these estimates and diagnostics, not just a final score vector.

Do not manually truncate GRF internal weights without understanding the implemented estimator. For separately implemented IPCW metrics, prespecify a 0.05 denominator floor only as a sensitivity, report how many weights are affected, and show untruncated estimates when numerically supported. Extreme scores are a warning to investigate support, not a license to remove unfavorable patients.

If day-365 support is inadequate, report the primary 365-day estimate as unstable or not estimable and present the already specified day-360 sensitivity. Do not relabel day 360 as the original primary endpoint. If only a subgroup lacks support, explicitly limit interpretation there.

## 11. Uncertainty, repeated fitting, and statistical limits

### 11.1 Primary uncertainty procedure

The principal uncertainty analysis is a **patient-resampling, full-pipeline bootstrap**, conditional on the released site groups and treatment-arm allocation counts. Target 500 successful replicates. Resample patients within released-site-by-arm strata; carry every linked record for a patient together. Preserve original-patient identity for leakage protection even when a patient is drawn more than once.

Within every replicate, rerun preprocessing, required inner tuning, discovery fitting, policy assignment, evaluation-score construction, and policy contrasts. Keep all bootstrap copies of an original patient in the same outer fold. Where GRF's out-of-bag nuisance estimation operates on bootstrap duplicates, pass original-patient identity as the sampling cluster so one copy cannot be in-bag while another copy supplies supposedly out-of-bag evaluation. This clustering is for repeated copies of **patients**, not a claim that five site codes support hospital-level cluster inference. Verify the installed package's cluster semantics in a simulation before trusting this implementation.

Start with five full replicates to measure runtime and RAM. Schedule independent replicates using the resource limits. Save one immutable result per replicate, including seed, estimates, assignment fractions, warnings, and all failure reasons. Resume only missing replicates. Do not replace failed replicates until their scientific cause is understood; report the failure rate and investigate if it exceeds 5%.

Report percentile intervals as **approximate full-pipeline bootstrap intervals**, along with the empirical bootstrap distribution. Hard treatment thresholds and cross-fitting can make inference nonregular, particularly when treatment effects cluster around zero. Simulation checks below assess implementation and behavior; they do not establish universal coverage. Do not advertise exact frequentist coverage merely because 500 replicates were run.

Use a fixed-prediction patient bootstrap with 2,000 replicates only as a faster supplementary diagnostic. It conditions on learned predictions and does not include training uncertainty; label it accordingly. Never silently substitute it for the planned full-pipeline uncertainty analysis. If the full procedure cannot be made statistically valid, present policy results as exploratory estimates without definitive superiority claims and explain the unresolved limitation.

If compute resources constrain completion, reduce parallelism before reducing statistical work. A smaller interim run may be labeled preliminary with its exact replicate count; the final package must either complete the specified run or clearly state which inferential results remain incomplete. Do not invent an ETA or declare bootstrap completion from progress logs alone.

### 11.2 Hypothesis hierarchy and interpretation

The single primary contrast is forest-policy RMST minus uniform-shorter RMST at day 365. Present its estimate and two-sided 95% interval. The null is no incremental benefit. All ranking, subgroup, graft-policy, alternative-horizon, alternative-seed, and interaction analyses are secondary/exploratory. If multiple secondary formal tests are emphasized, apply a stated family-wise or false-discovery adjustment and list the family; do not correct only unfavorable tests.

Do not count the number of significant subgroup effects as evidence of interaction. Do not declare safety because a confidence interval includes zero. Do not use the original trial's power calculation as this HTE study's power calculation. The relevant limits include 253 composite events, only 97 late bleeding events, missing imaging, and event concentration by site.

A defensible positive claim requires a robust advantage over the shorter constant policy, consistency against the simple comparator, acceptable censoring diagnostics, and honest discussion of graft uncertainty. Even then, it is internally evaluated secondary evidence requiring independent validation before clinical adoption. If these conditions fail, state that individualized duration was not supported by the available evidence.

### 11.3 Simulations required before expensive fitting

Implement a small, separately labeled simulation suite with approximately 2,290 people, randomized `W`, baseline features, delayed treatment differences, and adjustable censoring. Keep simulation files outside real-result directories. Scenarios:

1. No treatment effect and no treatment interaction.
2. A common beneficial effect of shorter treatment with baseline risk variation, but no subgroup where longer is better.
3. Genuine crossing treatment effects determined by a known baseline feature.
4. Censoring associated with baseline features/site but conditionally independent of event time.
5. Poor censoring support, which should trigger warnings rather than false precision.

For speed, use 200–500 trees for routine implementation checks and a limited set of full-setting simulations for uncertainty validation. Compare score signs and values with known simulation truth. Assess whether the policy recovers a useful rule in the crossing scenario and tends toward the appropriate constant policy in a strong constant-benefit scenario. Under the null, report how often the uncertainty procedure falsely declares benefit; do not tune to one favorable simulation draw. If calibration is poor, investigate estimator implementation and weaken inference rather than optimizing the real-data conclusion.

Include an uncensored simulation where score behavior can be compared with the familiar randomized-treatment AIPW contrast. This checks signs and index alignment. Do not use that uncensored formula as a substitute in the censored real data.

## 12. Graft assessment, missingness, and safety interpretation

### 12.1 Required descriptive audit

Create `R_image=1` for patients in `svg_occ_main.csv`; otherwise zero. Compare baseline characteristics, treatment, released site, and available clinical outcomes by imaging availability. Report imaging completeness by arm and site. Do not put `R_image` into the treatment-rule feature set: it is postrandomization information.

For the 2,070 assessed participants, estimate observed patient-level occlusion proportions by randomized arm, with intervals, and report the conditional prognostic performance of the two graft-risk models. Explicitly acknowledge selection into assessment. Do not assert that randomization necessarily remains unconfounded after conditioning on assessment.

### 12.2 Mandatory missing-outcome bounds

For each randomized arm, let `O_a` be observed occlusions, `M_a` missing imaging outcomes, and `N_a` all baseline participants. Compute the simple identification bounds:

\[
O_a/N_a \le P(\text{occlusion under the specified annual-assessment outcome})
\le (O_a+M_a)/N_a.
\]

These are crude missing-outcome bounds, not competing-risk estimands. A graft state after death is not automatically defined. Therefore show two clearly distinguished analyses: the assessed-patient outcome and an explicitly defined **death by day 365 or any occlusion at scheduled annual assessment** sensitivity outcome. The latter mixes a fixed death horizon with an annual imaging window because exact imaging dates are unavailable. Name that limitation.

For the death-or-occlusion sensitivity: classify a known death by day 365 as a bad outcome; otherwise use observed annual imaging when available. Patients without a death by day 365 are not necessarily known alive at day 365 if death follow-up ended earlier. Mark those with insufficient death follow-up and no already-established bad outcome as unresolved rather than assuming survival. A observed occlusion is a bad outcome regardless of later death ascertainment. Produce bounds by setting unresolved outcomes all good or all bad, including arm-differential scenarios.

Do not turn missing imaging into an occlusion solely because it is missing in the primary analysis. Do not infer death from missing imaging. The purpose is to show how much the safety conclusion depends on unobserved outcomes, not to create a favorable imputation.

### 12.3 Optional MAR policy safety analysis: only after core completion

If implemented, label it exploratory and assumption-dependent. Use a fully specified binary annual-assessment/death composite with an observation indicator `R`, as above. Within outer training folds estimate `rho_a(X)=P(R=1|A=a,X)` and `mu_a(X)=E[Y|R=1,A=a,X]` with restrained penalized models. Use the known treatment probability `e_a=0.5`.

For held-out records, a treatment-specific score is:

\[
\phi_{a,i}=\hat\mu_a(X_i)+
\frac{1(A_i=a)R_i}{e_a\hat\rho_a(X_i)}
\{Y_i-\hat\mu_a(X_i)\}.
\]

Set the residual term to zero when `R=0` without evaluating an undefined `Y`. The harmful-outcome contrast for policy `d` versus uniform shorter is `mean((d-1)*(phi_1-phi_0))`, using the already frozen bleeding/death policy. Here **negative means less harm**, unlike the favorable RMST sign. Test this difference explicitly.

This analysis requires missing-at-random/positivity assumptions and correct enough nuisance estimation; randomization does not identify unobserved imaging outcomes. Fit and evaluate everything inside the existing outer partitioning. Use untruncated weights where supported and prespecified 0.05/0.10 observation-probability floors as sensitivities. Show bounds and missing-not-at-random tipping scenarios alongside it. Do not create an “optimal net-benefit policy” by choosing a bleeding-versus-graft utility weight from the observed results.

This optional module must not delay or replace the core policy analysis. If missingness identification or event definition cannot be defended, omit MAR causal safety estimates, deliver the descriptive results and bounds, and state that graft safety of personalization remains unresolved.

## 13. Required sensitivity analyses

| Analysis | Exact change | Interpretation constraint |
|---|---|---|
| Horizon | RMST 360 instead of 365 | Prespecified timing robustness; keep primary label unchanged |
| Site-free discovery | Exclude site from discovery features; retain it for evaluator nuisance adjustment | Tests dependence of the learned rule on released groups |
| Dominant group | Train/evaluate within code `01` using patient folds | Restricted population; not external validation |
| Across-group stress test | Train on `01`, evaluate pooled other codes where support permits | Only 19 recorded bleeds outside `01`; expect imprecision |
| Reverse transport | Other codes training, `01` evaluation | Simple model only by default; 481-person training set is too sparse for ambitious HTE |
| Age discrepancy | Exclude four AGE>80 records | Release/eligibility sensitivity, not data correction |
| Forest complexity | Discovery minimum node sizes 20 and 80 | No selecting the best setting as primary |
| Fold seeds | Exactly 20260908 and 20260909 | Stability, not seed optimization |
| Timing | Early 0–90 and selected 90-day landmark | Diagnostic/exploratory; landmark selection caveat |
| Component mismatch | Documented alternative composite observation rule for the discrepant record | Show whether result changes; no silent recoding |
| Missing imaging | Bounds and differential missing-outcome scenarios | Safety uncertainty, not proof of noninferiority |

For across-group evaluation, fit preprocessing on the training group only. Encode an unseen site as unknown; the site-free discovery sensitivity is the appropriate portable rule. Do not refit the treatment rule on external evaluation outcomes. Evaluation nuisance estimation can use evaluation-group outcomes with the same honest/OOB safeguards, but resulting estimates remain unstable with few events. If support fails, output `not reliably estimable` and descriptive distributions; do not force a numeric table entry.

Never call this “13-center internal-external validation.” There are only five released codes. Do not use a conventional five-cluster sandwich estimator or a five-site bootstrap as if it supported precise hospital-population inference. Patient-level inference conditional on the represented site mixture is the primary target.

## 14. Predictive metrics, calibration, and explanation

### 14.1 Survival prognosis

The piecewise model supplies survival probabilities and can be assessed as a prognostic model. Report censoring-aware Brier scores at days 90, 180, 270, and 365 where support permits; integrated Brier score over a supported range; and Uno's C or time-dependent AUROC as secondary metrics. Use appropriate training-derived censoring distributions and explicit support checks. Follow [scikit-survival's evaluation documentation](https://scikit-survival.readthedocs.io/en/stable/user_guide/evaluating-survival-models.html), or a validated R equivalent.

GRF CATE predictions are not arm-specific survival probabilities. Do not compute a prognostic Brier score from `tau`. Do not take `1-KM` with competing deaths censored and label it a bleeding cumulative incidence.

### 14.2 Graft prognosis

Report held-out log loss, Brier score, AUROC, AUPRC with prevalence reference, calibration-in-the-large, and calibration slope. Produce a smooth calibration curve with uncertainty if stable; otherwise use three to five groups with denominators and intervals. Do not recalibrate on the same held-out labels used to report final performance. If calibration is fitted, fit it in the inner training procedure.

Compare models using paired patient-level resampling of held-out predictions, labeled as conditional prediction-performance uncertainty; a full refit sensitivity is stronger if affordable. Do not report only accuracy or optimal-cutpoint sensitivity/specificity. Any decision threshold must have a real clinical interpretation set in advance, which this protocol does not assume.

### 14.3 Explainability

Primary explanation outputs are the distribution of treatment-effect predictions, held-out treatment-effect calibration, and policy stability. A small depth-two surrogate tree may be fitted on training-fold CATE predictions for illustration, with held-out agreement reported; do not claim it inherits the full model's validated policy value unless independently evaluated as another frozen rule.

For prognostic models, show training-derived coefficients or permutation importance assessed without using the held-out set for subsequent feature selection. SHAP is optional, computed only after performance evaluation with explicit labeling as model attribution. Avoid causal language such as “raising eGFR reduces bleeding” based on these explanations.

## 15. Meaningful tests and automatic scientific gates

Write tests for errors that would invalidate the research, rather than tests that merely mirror each function's implementation.

### 15.1 Required unit and integration tests

1. **Treatment direction:** simulated shorter-beneficial data yield the expected score direction. Swapping A/B and reversing policy coding reverses the treatment contrast appropriately.
2. **Endpoint timing:** cases for bleed before death, death before bleed, equal event times, censoring before either event, censoring at day 365, event at day 365, and event after day 365. The horizon-reaching non-event is not an actual event.
3. **Unequal component follow-up:** a later component event after earlier unresolved follow-up is not automatically a known composite event under the conservative rule.
4. **Merge cardinality:** raw segment-to-segment `pid` joins raise an error; patient-level aggregates join one-to-one and maintain 2,290 baseline rows.
5. **No artificial deduplication:** identical segment rows remain separate observations until patient aggregation.
6. **Missing outcome handling:** absent SVG records remain unresolved; neither zero nor one is silently assigned.
7. **Fold leakage:** original `pid` never appears in both rule-training and evaluation partitions, including bootstrap duplicate copies.
8. **Preprocessing leakage:** changing held-out numeric values does not change training imputation/scaling or selected parameters.
9. **Policy outcome isolation:** changing held-out outcomes leaves the held-out policy unchanged while allowing evaluation scores to change.
10. **Score alignment:** permuting file rows then joining by `pid` produces identical matched outputs; accidental positional merging fails.
11. **Policy identities:** always-shorter gain versus itself is exactly zero; forest-minus-simple is zero when the rules agree everywhere.
12. **Survival integration:** constant-hazard RMST matches its analytic expression and respects `[0,horizon]`; probabilities are finite, bounded, and nonincreasing.
13. **Person-period boundaries:** exposure sums equal observed follow-up; events occur once; day-90 assignment matches the declared early/late rule.
14. **Graft bounds:** lower bounds do not exceed upper bounds; resolved bad outcomes remain bad under every missingness scenario.
15. **Resumability:** interrupting after a fold and resuming does not repeat valid completed folds or mix smoke/full artifacts.
16. **Determinism:** fixed seed/config/data reproduce predictions within documented numerical tolerance; GPU deviations are measured rather than hidden.
17. **Censoring simulation:** no-censoring and informative-by-X scenarios behave as expected; poor support triggers a warning.

### 15.2 Gate behavior

| Gate | Pass condition | If it fails |
|---|---|---|
| Source integrity | Readable expected files and reviewed version | Stop real-data analysis; continue environment/tests |
| Cohort integrity | Consistent IDs/arms and explained row counts | Block affected model inputs |
| Time/endpoint integrity | Tested construction and recorded discrepancies | Block primary survival claims |
| Evaluation independence | Frozen held-out policies and no patient leakage | Rebuild affected folds |
| Score validity | Finite, aligned, supported scores with simulation checks | Investigate; retain only defensible descriptive results |
| Uncertainty | Planned refits completed or clearly marked incomplete | Do not claim definitive superiority |
| Reporting consistency | Tables/figures trace to actual metric files | Regenerate; never hand-edit numbers |

A scientific review by a clinician/statistician remains advisable before manuscript submission, particularly for censoring assumptions and policy inference. The coding agent must make the analysis concrete and auditable before requesting that review, rather than stopping at an empty scaffold.

## 16. Figures for a journal submission package

Generate figures from saved analytic outputs only. Each figure must have a matching source-data CSV and an executable generation function. No AI-generated data graphics. No simulated values in real-result panels. No plotted raw patient identifiers.

Use a colorblind-safe palette, consistent treatment colors, clear units, legible fonts at final size, and neutral language. Suggested colors: shorter `#0072B2`, longer `#D55E00`, simple comparator `#009E73`, neutral `#666666`. Use line styles or shapes as well as color. Avoid rainbow palettes, 3-D plots, unnecessary dual axes, and significance stars without effect estimates.

Export vector PDF and SVG. Export TIFF at 600 dpi for line art or 300 dpi for mixed raster figures when a selected journal requires it. Default widths: 85 mm single-column and 180 mm double-column; final-size text approximately 8–10 points. Embed fonts where practical, use consistent decimal precision, and visually inspect every output for clipping and tiny labels. Journal-specific sizing can be applied after a target is chosen; do not claim every Q1 journal shares identical requirements.

### 16.1 Main figures

| Number/file stem | Required content | Required safeguards |
|---|---|---|
| F1 `cohort_and_analysis_flow` | Released cohort, endpoint construction, imaging subset, outer training/evaluation flow | Distinguish 2,300 randomized from 2,290 released; no fictitious exclusions |
| F2 `event_timing_and_followup` | Composite event-free curves by arm, risk table, day-90 marker, censoring/visit timing inset | Time from randomization; do not imply day-90 rerandomization |
| F3 `predicted_benefit_and_calibration` | Out-of-fold CATE distribution and three-group score calibration | Predicted benefit is not individual observed truth |
| F4 `policy_value_comparison` | Forest and simple rule contrasts versus uniform shorter, with 95% intervals and assignment proportions | Zero reference, correct favorable sign, exact inferential method |
| F5 `graft_outcomes_and_missingness` | Patient occlusion estimates, imaging completeness, missing-outcome bounds | Do not equate absence of significance with safety |
| F6 `robustness_and_site_dependence` | Prespecified sensitivity contrast estimates and site concentration summary | Mark unstable/not-estimable rows rather than hiding them |

If the learned rule is constant or calibration groups collapse, adapt F3 to show that fact; do not manufacture three distinct benefit groups. If primary inference fails, F4 should show exploratory point estimates with an explicit limitation or be omitted with explanation, not display invented narrow intervals.

### 16.2 Supplementary figures

Create: baseline missingness; endpoint-specific censoring distributions; bleeding cumulative incidence with competing death; early/late outcome diagnostics; treatment-effect ranking/TOC if supported; split-seed assignment stability; graft-model calibration and ROC/PR curves; missing-imaging tipping scenarios; runtime/memory benchmark; and simulation performance. Keep the supplement focused; omit unsupported panels with a recorded reason.

## 17. Tables and machine-readable results

Export every table as CSV and Markdown. Provide an HTML preview if helpful. Avoid relying on a manually edited spreadsheet as the source of truth. Include denominators, missingness, units, event definitions, horizon, effect direction, and confidence-interval method in footnotes.

### 17.1 Main tables

1. **T1 Cohort characteristics:** all released patients by treatment. Continuous summaries, categorical counts/percentages, missing counts, and standardized differences. No baseline significance-testing ritual in a randomized trial.
2. **T2 Outcomes and observation:** clinical events, early/late events, composite construction, follow-up/censoring, imaging availability, patient-level and segment-level graft outcomes with distinct denominators.
3. **T3 Primary policy results:** model/rule, fraction assigned shorter, contrast versus uniform shorter, contrast versus uniform longer, contrast versus simple rule where applicable, 95% interval, and uncertainty method. Constant policies must appear.
4. **T4 Heterogeneity and predictive performance:** clearly separate treatment-effect calibration/RATE from ordinary graft/survival prognosis. Do not put incomparable quantities under a single “accuracy” heading.
5. **T5 Robustness and limitations:** horizon/site/seed/node-size/age/missingness sensitivities, sample sizes, event counts, and exact departures from the primary specification.

### 17.2 Supplementary tables

Data dictionary and predictor availability at decision time; file-level audit; fold counts/events; original-trial reproduction discrepancies; complete model parameters; individual released-site counts; bootstrap failures and diagnostics; simulation results; missing-outcome scenarios; software/hardware versions; reporting-checklist mappings.

### 17.3 Required result schemas

`outputs/predictions/<run_id>.parquet` must include:

```text
pid, outer_fold, split_seed, model_id, model_train_hash,
W, site, t_raw, event_raw, horizon,
tau_hat_days, policy_short,
svg_observed, svg_any_occlusion,
graft_risk_hat_if_applicable
```

`outputs/scores/<run_id>.parquet` must include:

```text
pid, outer_fold, evaluator_id, evaluator_hash, horizon,
gamma_rmst_days, score_warning_flags
```

Metrics JSON records must include `estimand`, `population`, `unit`, `model`, `reference_policy`, `estimate`, `ci_low`, `ci_high`, `ci_method`, `n`, `events`, `seed`, `replicates_completed`, `warnings`, `data_hash`, and `config_hash`. Use JSON `null` plus a reason for unavailable values, never a misleading zero. Clinical record-level outputs remain local unless separately authorized for release.

## 18. Manuscript package and publication standard

Write a complete draft in `manuscript/manuscript.md` after verified results exist. Use a structured abstract; introduction focused on the actual treatment decision; methods specifying the secondary-analysis design, data release, decision time, estimand, leakage controls, censoring assumptions, missing imaging, and uncertainty; results linked to tables; discussion including null findings and limitations; and reproducibility/data statements.

Do not promise acceptance by a Q1 or “A-rank” journal. Quartiles depend on the index, category, and year, and “A-rank” is not a universal journal classification. At the end, prepare a short candidate-journal fit note based on current official scopes, article types, length limits, and verified ranking source if accessible. If ranking cannot be verified, mark it unverified. Do not choose a journal only because it accepts machine learning papers.

Use the [PATH statement](https://pubmed.ncbi.nlm.nih.gov/31711134/) to structure treatment-effect heterogeneity reporting. Use [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) for the predictive modeling components and transparent reporting; it is not a substitute for causal estimand justification. Use [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505) to identify risk-of-bias concerns, without presenting a self-assessment as an independent certification.

Required limitations include:

- Secondary analysis after the trial and after descriptive inspection of the public data.
- No verified claim that the dataset or analysis idea is unused by other researchers.
- Small effective event counts for HTE, especially after three months.
- Five released site groups and strong concentration in one group.
- Conditional censoring and missing-imaging assumptions.
- Composite endpoint interpretation and absence of severity-weighted utility.
- Regimens shared the early period; a baseline rule is not a validated dynamic day-90 strategy.
- Unavailable adherence detail, exact imaging dates, some established score components, and complete randomized population.
- Internal evaluation, no independent prospective or external validation, and uncertainty of hard-threshold policy inference.
- Applicability limited to the trial's represented population and ticagrelor-based regimens; no automatic extrapolation to all CABG patients or other drugs.

Ethics/data statement: accurately describe secondary analysis of released de-identified trial data and cite the repository/trial consent information. Do not claim a new institutional review exemption or approval number unless the researcher supplies an actual determination. Code availability should point to a prepared repository only after publication authorization; until then state that a reproducible package has been prepared.

## 19. Stage-by-stage execution order and completion criteria

| Stage | Work | Required evidence before marking complete |
|---|---|---|
| 0 | Read plan, inspect machine, initialize project and logs | Environment report, resource settings, dependency strategy |
| 1 | Download/cache source and save license/version | Valid archive, hashes, eight expected files |
| 2 | Audit and reproduce basic source results | Counts match or discrepancies explained; no bad joins |
| 3 | Finalize endpoints, features, novelty update, and dated SAP | Written definitions and transparent amendments |
| 4 | Implement preprocessing/folds/statistical modules | Contracts, leakage tests, endpoint tests pass |
| 5 | Run simulations and smoke profile | Score signs, policy identities, censoring behavior validated |
| 6 | Benchmark one main fold and five refits | Actual runtime/RAM report and concurrency choice |
| 7 | Run five outer-fold main models and evaluators | Frozen held-out predictions/scores for all eligible patients |
| 8 | Compute policy/prognostic metrics | Correct references, units, populations, support diagnostics |
| 9 | Run full-pipeline uncertainty | 500 successful replicates or explicit incomplete status |
| 10 | Run prespecified sensitivities and graft audit | Complete sensitivity inventory, including failed/unsupported analyses |
| 11 | Generate figures/tables and manuscript | All numbers trace to saved outputs; visuals inspected |
| 12 | Reproducibility and handoff audit | One-command rerun, locked environment, manifest, limitations |

Do not interleave exploratory result viewing with changes to the primary design. New scientific ideas go into `docs/future_work.md` or a dated exploratory amendment. Stage 3 may proceed with the existing plan if no exact competing study is found; no routine user confirmation is needed to choose defaults already specified here.

### 19.1 Runtime management

The dataset is small; downloads, audits, and basic models should be lightweight once the environment works. Repeated survival forests and uncertainty estimation dominate runtime. Do not provide an exact hours estimate until measuring the server. Use:

```text
estimated_remaining_time =
  sum(remaining_jobs_in_stage * median_measured_job_seconds /
      effective_concurrent_jobs) * 1.3
```

This is a planning estimate, not a guarantee. Account for memory bottlenecks and variable forest durations. Update it when enough jobs complete. A single slow dependency compile should not trigger installation of a huge alternative stack. Cache environments and model outputs, avoid plotting during worker training, and avoid saving thousands of redundant large objects. Keep main models and sufficient bootstrap summaries; delete only project-generated temporary intermediates once reproducibility is preserved.

### 19.2 Final handoff from the coding agent

Return a concise status message containing the project path, exact rerun command, primary scientific result with interval or an explicit inconclusive status, successful/failed gates, runtime, and links/paths to the manuscript and main figures/tables. Supply `reports/quality_report.md` with every caveat, not just a success badge.

The project is complete only when the core end-to-end workflow runs, scientific failures are honestly represented, and the publication package is traceable to actual data. A folder tree, unexecuted notebook, model training log without evaluation, or set of attractive figures without valid statistics is not completion.

## 20. Source index for implementation and manuscript citations

Verify bibliographic metadata from the source before generating BibTeX. Do not cite this plan as evidence for clinical efficacy. Data-audit counts in this plan must be recomputed from the archived release.

1. [TOP-CABG public data, Dryad, release 31 March 2026](https://datadryad.org/dataset/doi:10.5061/dryad.jsxksn0qs) — source data, dictionary, original code, license, version.
2. [TOP-CABG primary trial, BMJ](https://www.bmj.com/content/393/bmj-2025-088939) — trial design, source results, prior subgroup analyses, limitations.
3. [Primary trial full text in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13162091/) — alternative full-text access to item 2, not a separate study.
4. [TOP-CABG protocol, BMJ Open](https://bmjopen.bmj.com/content/13/6/e070823) — trial eligibility and planned methods.
5. [ClinicalTrials.gov NCT05380063](https://clinicaltrials.gov/study/NCT05380063) — registration and protocol history.
6. [STICH heterogeneous-treatment-effect analysis](https://pubmed.ncbi.nlm.nih.gov/37716652/) — prior causal ML in CABG; algorithmic novelty boundary.
7. [PATH statement](https://pubmed.ncbi.nlm.nih.gov/31711134/) — reporting and interpretation of treatment-effect heterogeneity.
8. [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) — prediction-model reporting.
9. [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505) — prediction-model risk-of-bias assessment.
10. [GRF causal survival forest API](https://grf-labs.github.io/grf/reference/causal_survival_forest.html) — model interface; cite the original methodological paper listed there in the manuscript.
11. [GRF survival vignette](https://grf-labs.github.io/grf/articles/survival.html) — censoring-aware estimation and assumptions.
12. [GRF causal-survival score API](https://grf-labs.github.io/grf/reference/get_scores.causal_survival_forest.html) — evaluation scores.
13. [GRF rank-weighted treatment-effect interface](https://grf-labs.github.io/grf/reference/rank_average_treatment_effect.fit.html) — independent score/priority evaluation.
14. [Survival prediction metrics](https://scikit-survival.readthedocs.io/en/stable/user_guide/evaluating-survival-models.html) — censoring-aware predictive evaluation.
15. [XGBoost GPU documentation](https://xgboost.readthedocs.io/en/stable/gpu/) — current CUDA interface and compatibility requirements.
16. [scikit-learn parallelism documentation](https://scikit-learn.org/stable/computing/parallelism.html) — CPU thread/process limits.
17. [Dryad API documentation](https://datadryad.org/api) — distinguish API authentication from public browser downloads.

## 21. Copy-and-paste launch instruction for the coding agent

> Implement and execute this entire `plan.md` in a user-writable project directory on my Linux server with 64 GB RAM, 32 CPU cores, and an RTX 3060 12 GB. Start by inspecting the environment and obtaining the public TOP-CABG release. Build the code, run meaningful statistical and leakage tests, benchmark resources, execute the prespecified models and honest evaluation, run uncertainty and sensitivity analyses, then generate the complete manuscript/figure/table package. Follow the treatment coding, endpoint, censoring, missing-imaging, and evaluation rules exactly. Use CPU parallelism intelligently and GPU only if a benchmark supports it. Keep STATUS.md and DECISIONS.md current and resume completed work. Do not fabricate findings, tune for significance, call internal evaluation external validation, or promise journal acceptance. If a scientific gate fails, investigate it, complete unaffected analyses, and clearly report the limitation. Return concrete executed results and a reproducible handoff, not just scaffolding.
