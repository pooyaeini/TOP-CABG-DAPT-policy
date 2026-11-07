#!/bin/bash
cd "$(dirname "$0")/.."; export GRF_THREADS=1
Rscript analysis/run_sens.R nace isch landmark85 h180 h270 landmark90 wins discrepant mns20 mns80 h360 nosite seed2 seed3 age80 site01 smoke3 train01 reverse >> work/sens.log 2>&1
GRF_LIB=new Rscript -e 'source("analysis/pipe.R"); d <- load_pat(); r <- crossfit(d, "t_raw", "event_raw"); dd <- as.numeric(r$tau >= 0); write_json(list(grf = as.character(packageVersion("grf")), n = nrow(d), mean_score = mean(r$gamma), lo = mean(r$gamma) - 1.96*sd(r$gamma)/sqrt(nrow(d)), hi = mean(r$gamma) + 1.96*sd(r$gamma)/sqrt(nrow(d)), learned_minus_all3 = mean((dd-1)*r$gamma), n12 = sum(dd==0), frac3 = mean(dd), tau_min = min(r$tau), tau_max = max(r$tau)), "work/sens/grf261.json", auto_unbox = TRUE, digits = 8)' >> work/sens.log 2>&1
echo SENSDONE >> work/sens.log
