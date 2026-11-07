## Sensitivity analyses, all re-executed. Usage: Rscript analysis/run_sens.R <name ...>
source("analysis/pipe.R")
d <- load_pat(); P <- read.csv("work/primary_patients.csv"); dir.create("work/sens", showWarnings = FALSE)
summ <- function(tau, gam, extra = list()) {
  dd <- as.numeric(tau >= 0); n <- length(gam); m <- mean(gam); s <- sd(gam) / sqrt(n)
  c(list(n = n, mean_score = m, lo = m - 1.96 * s, hi = m + 1.96 * s, learned_minus_all3 = mean((dd - 1) * gam),
         lm_lo = mean((dd - 1) * gam) - 1.96 * sd((dd - 1) * gam) / sqrt(n), lm_hi = mean((dd - 1) * gam) + 1.96 * sd((dd - 1) * gam) / sqrt(n),
         n12 = sum(dd == 0), frac3 = mean(dd), tau_min = min(tau), tau_max = max(tau)), extra)
}
early <- as.numeric((d$mi == 1 & d$mi_day <= 85) | (d$stroke == 1 & d$stroke_day <= 85) | (d$revas_cor == 1 & d$revas_cor_day <= 85))
RUN <- list(
  h360 = function() { r <- crossfit(d, "t_raw", "event_raw", horizon = 360); summ(r$tau, r$gamma) },
  h180 = function() { r <- crossfit(d, "t_raw", "event_raw", horizon = 180, want_chat = TRUE); summ(r$tau, r$gamma, list(chat_min = min(r$chat), autoc = rate_fw(r$tau, r$gamma, d$fold)$estimate)) },
  h270 = function() { r <- crossfit(d, "t_raw", "event_raw", horizon = 270, want_chat = TRUE); summ(r$tau, r$gamma, list(chat_min = min(r$chat), autoc = rate_fw(r$tau, r$gamma, d$fold)$estimate)) },
  nosite = function() { r <- crossfit(d, "t_raw", "event_raw", site = FALSE); summ(r$tau, r$gamma) },
  mns20 = function() { r <- crossfit(d, "t_raw", "event_raw", mns_disc = 20); summ(r$tau, r$gamma) },
  mns80 = function() { r <- crossfit(d, "t_raw", "event_raw", mns_disc = 80); summ(r$tau, r$gamma) },
  seed2 = function() { r <- crossfit(d, "t_raw", "event_raw", folds = d$fold_s2); write.csv(data.frame(tau = r$tau), "work/sens/seed2_tau.csv"); summ(r$tau, r$gamma, list(cor_primary = cor(r$tau, P$tau))) },
  seed3 = function() { r <- crossfit(d, "t_raw", "event_raw", folds = d$fold_s3); write.csv(data.frame(tau = r$tau), "work/sens/seed3_tau.csv"); summ(r$tau, r$gamma, list(cor_primary = cor(r$tau, P$tau))) },
  age80 = function() { i <- d$AGE <= 80; dd <- d[i, ]; r <- crossfit(dd, "t_raw", "event_raw", folds = dd$fold); summ(r$tau, r$gamma) },
  site01 = function() { dd <- d[d$site == "01", ]; r <- crossfit(dd, "t_raw", "event_raw", folds = dd$fold); summ(r$tau, r$gamma) },
  discrepant = function() { i <- !(d$death == 1 & d$blood_day > d$death_day); dd <- d[i, ]; r <- crossfit(dd, "t_raw", "event_raw", folds = dd$fold); summ(r$tau, r$gamma, list(excluded = sum(!i))) },
  smoke3 = function() { r <- crossfit(d, "t_raw", "event_raw", smoke3 = TRUE); write.csv(data.frame(tau = r$tau), "work/sens/smoke3_tau.csv"); summ(r$tau, r$gamma, list(cor_primary = cor(r$tau, P$tau), mean_abs_change = mean(abs(r$tau - P$tau)))) },
  landmark90 = function() { dd <- d[d$t_raw > 90, ]; dd$y <- dd$t_raw - 90; r <- crossfit(dd, "y", "event_raw", horizon = 275, folds = dd$fold); summ(r$tau, r$gamma, list(events = sum(dd$event_raw == 1 & dd$t_raw <= 365))) },
  landmark85 = function() { i <- d$t_raw > 85; dd <- d[i, ]; dd$y <- dd$t_raw - 85; ex <- cbind(early_isch = early[i])
    r <- crossfit(dd, "y", "event_raw", horizon = 280, folds = dd$fold, extraX = ex)
    summ(r$tau, r$gamma, list(events = sum(dd$event_raw == 1 & dd$t_raw <= 365), n_early_isch = sum(ex), calib_slope = calib(r$tau, r$gamma)$slope,
                              autoc = rate_fw(r$tau, r$gamma, dd$fold)$estimate, autoc_se = rate_fw(r$tau, r$gamma, dd$fold)$se)) },
  nace = function() { r <- crossfit(d, "t_nace", "e_nace"); saveRDS(r, "work/sens/nace.rds")
    summ(r$tau, r$gamma, list(events = sum(d$e_nace == 1 & d$t_nace <= 365), calib_slope = calib(r$tau, r$gamma)$slope, autoc = rate_fw(r$tau, r$gamma, d$fold)$estimate, autoc_se = rate_fw(r$tau, r$gamma, d$fold)$se)) },
  isch = function() { r <- crossfit(d, "t_isch", "e_isch"); saveRDS(r, "work/sens/isch.rds")
    summ(r$tau, r$gamma, list(events = sum(d$e_isch == 1 & d$t_isch <= 365), calib_slope = calib(r$tau, r$gamma)$slope, autoc = rate_fw(r$tau, r$gamma, d$fold)$estimate)) },
  wins = function() { g <- P$gamma; q <- quantile(g, c(.01, .99)); g <- pmin(pmax(g, q[1]), q[2]); summ(P$tau, g) },
  train01 = function() { tr <- d[d$site == "01", ]; te <- d[d$site != "01", ]; E <- encode(tr, te)
    f <- csf(E$tr, tr$t_raw, tr$W, tr$event_raw, 365, 40, SEED); tau <- predict(f, E$te)$predictions
    e <- csf(E$te, te$t_raw, te$W, te$event_raw, 365, 10, SEED + 100); summ(tau, get_scores(e), list(events = sum(te$event_raw == 1 & te$t_raw <= 365))) },
  reverse = function() { tr <- d[d$site != "01", ]; te <- d[d$site == "01", ]; p <- pw_fit_predict(tr, te, "t_raw", "event_raw")
    E <- encode(tr, te); e <- csf(E$te, te$t_raw, te$W, te$event_raw, 365, 10, SEED + 100); summ(p$tau, get_scores(e)) }
)
for (nm in commandArgs(TRUE)) {
  out <- paste0("work/sens/", nm, ".json"); if (file.exists(out)) next
  t0 <- Sys.time(); r <- RUN[[nm]](); r$secs <- as.numeric(Sys.time() - t0, units = "secs")
  write_json(r, out, auto_unbox = TRUE, digits = 8)
  cat(nm, "done", round(r$secs), "\n")
}
