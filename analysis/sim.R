## Semi-synthetic simulation engine. Usage: Rscript analysis/sim.R <scenario> <from> <to>
source("analysis/pipe.R")
a <- commandArgs(TRUE); scn <- a[1]; from <- as.integer(a[2]); to <- as.integer(a[3])
d0 <- load_pat(); dir.create("work/sim", showWarnings = FALSE)
BRK <- c(0, 90, 180, 270, 365, Inf)
LAM0 <- c(85 / 98206, 24 / 93535, 23 / 91371, 22 / 89049, 22 / 89049)   # per day, twelve-month arm
M_BEN <- exp(-0.768)                                                     # observed late rate ratio, 0.46

index_score <- function(d) 0.03 * (d$AGE - 61.5) - 0.02 * (d$PRE_EGFR - 94) + 0.5 * d$MI + 0.5 * d$PAD + 0.3 * d$Diabetes

scen <- list(
  A1 = list(p = 0, m_resp = 1, m_non = 1, cens = "real"),
  A3 = list(p = 0.5, m_resp = 1 / M_BEN, m_non = M_BEN, cens = "real"),
  A4 = list(p = 0, m_resp = M_BEN, m_non = M_BEN, cens = "covariate"),
  A5 = list(p = 0, m_resp = M_BEN, m_non = M_BEN, cens = "poor"),
  A6 = list(p = 0.5, m_resp = 1 / M_BEN, m_non = M_BEN, cens = "none"),
  A7 = list(p = NA, m_resp = 1 / M_BEN^2, m_non = M_BEN, cens = "none", big = 3, age_rule = TRUE),
  B0 = list(p = 0, m_resp = M_BEN, m_non = M_BEN, cens = "real"),
  B1 = list(p = 0.05, m_resp = 1 / M_BEN, m_non = M_BEN, cens = "real"),
  B2 = list(p = 0.10, m_resp = 1 / M_BEN, m_non = M_BEN, cens = "real"),
  B3 = list(p = 0.20, m_resp = 1 / M_BEN, m_non = M_BEN, cens = "real"),
  B4 = list(p = 0.40, m_resp = 1 / M_BEN, m_non = M_BEN, cens = "real"),
  B5 = list(p = 0.20, m_resp = 1 / M_BEN^2, m_non = M_BEN, cens = "real"),
  B6 = list(p = 0.40, m_resp = 1 / M_BEN^2, m_non = M_BEN, cens = "real"))
S <- scen[[scn]]

## hazard for each participant under each regimen: identical before day 90, multiplier m after day 90 for 3 months
haz <- function(m, w) t(sapply(seq_along(m), function(i) LAM0 * c(1, rep(if (w[i] == 1) m[i] else 1, 4))))
rmst_pw <- function(H, horizon = 365) {
  r <- 0; S0 <- 1
  for (j in 1:4) { l <- min(BRK[j + 1], horizon) - BRK[j]; h <- H[, j]; r <- r + S0 * (1 - exp(-h * l)) / h; S0 <- S0 * exp(-h * l) }
  r
}
draw_T <- function(H) {
  n <- nrow(H); E <- rexp(n); out <- rep(Inf, n); cum <- rep(0, n)
  for (j in 1:5) { len <- BRK[j + 1] - BRK[j]; inc <- H[, j] * len
    hit <- is.infinite(out) & (cum + inc >= E)
    out[hit] <- BRK[j] + (E[hit] - cum[hit]) / H[hit, j]; cum <- cum + inc }
  out
}

for (r in from:to) {
  out <- sprintf("work/sim/%s_%03d.rds", scn, r)
  if (file.exists(out)) next
  t0 <- Sys.time(); set.seed(SEED * 10 + r + 1000 * match(scn, names(scen)))
  d <- d0
  if (!is.null(S$big)) {   # larger sample: resample covariate rows, new identifiers and folds
    d <- d0[sample.int(nrow(d0), S$big * nrow(d0), replace = TRUE), ]; d$pid <- sprintf("s%05d", seq_len(nrow(d)))
    d$W <- rbinom(nrow(d), 1, 0.5); d$COL_INV <- ifelse(d$W == 1, "B", "A"); d$fold <- -1L
    for (key in sort(unique(paste(d$site, d$COL_INV)))) { ii <- which(paste(d$site, d$COL_INV) == key); p <- ii[sample.int(length(ii))]; d$fold[p] <- (seq_along(p) - 1) %% 5 }
  }
  n <- nrow(d)
  resp <- rep(FALSE, n)
  if (isTRUE(S$age_rule)) resp <- d$AGE >= 65 else if (S$p > 0) { s <- index_score(d); resp[order(-s)[seq_len(round(S$p * n))]] <- TRUE }
  m <- ifelse(resp, S$m_resp, S$m_non)
  H1 <- haz(m, rep(1, n)); H0 <- haz(m, rep(0, n))
  tau_true <- rmst_pw(H1) - rmst_pw(H0)
  Tm <- draw_T(if (TRUE) { H <- H0; H[d$W == 1, ] <- H1[d$W == 1, ]; H } else NULL)
  # censoring times
  C <- ifelse(d$death == 0, d$death_day, NA)
  for (w in 0:1) { miss <- which(is.na(C) & d$W == w); pool <- C[!is.na(C) & d$W == w]; C[miss] <- sample(pool, length(miss), replace = TRUE) }
  if (S$cens == "covariate") { rate <- (-log(0.85) / 365) * exp(0.05 * (d$AGE - 61.5) + 0.5 * (d$Diabetes - 0.43)); C <- pmin(C, rexp(n, rate)) }
  if (S$cens == "poor") C <- pmin(C, rexp(n, -log(0.2) / 365))
  if (S$cens == "none") C <- rep(Inf, n)
  d$sim_t <- pmin(Tm, C, 800); d$sim_e <- as.integer(Tm <= pmin(C, 800))
  cf <- crossfit(d, "sim_t", "sim_e", folds = d$fold, want_oob = FALSE, trees = 2000)
  th <- cf$tau; g <- cf$gamma; dd <- as.numeric(th >= 0)
  v_hat <- mean((dd - 1) * g); se_v <- sd((dd - 1) * g) / sqrt(n); v_true <- mean((dd - 1) * tau_true)
  ate_hat <- mean(g); ate_se <- sd(g) / sqrt(n)
  ra <- tryCatch(rate_fw(th, g, d$fold, "AUTOC", R = 200), error = function(e) list(estimate = NA, se = NA))
  rt <- tryCatch(rate_fw(th, tau_true, d$fold, "AUTOC", R = 2)$estimate, error = function(e) NA)
  cb <- tryCatch(calib(th, g)$slope, error = function(e) NA)
  res <- c(n = n, events365 = sum(d$sim_e == 1 & d$sim_t <= 365), cens365 = sum(d$sim_e == 0 & d$sim_t < 365),
           true_ate = mean(tau_true), oracle_gain = mean(pmax(0, -tau_true)), best_const_gain = max(0, -mean(tau_true)),
           est_ate = ate_hat, ate_cover = abs(ate_hat - mean(tau_true)) <= 1.96 * ate_se,
           v_hat = v_hat, v_se = se_v, v_true = v_true, v_cover = abs(v_hat - v_true) <= 1.96 * se_v + 1e-12,
           n12 = sum(dd == 0), frac12_true = mean(tau_true < 0), agree_oracle = mean(dd == as.numeric(tau_true >= 0)),
           cor = if (sd(tau_true) > 0) cor(th, tau_true) else NA, slope = cb,
           autoc = ra$estimate, autoc_se = ra$se, autoc_true = rt,
           autoc_cover = if (is.na(ra$estimate)) NA else abs(ra$estimate - rt) <= 1.96 * ra$se,
           mean_tau_resp = if (any(resp)) mean(th[resp]) else NA, mean_tau_non = mean(th[!resp]),
           secs = as.numeric(Sys.time() - t0, units = "secs"))
  saveRDS(res, out)
}
