source("analysis/pipe.R")
d <- load_pat(); P <- read.csv("work/primary_patients.csv"); R <- readRDS("work/primary.rds")
res <- list()
## event reconciliation
res$recon <- list(bleed = sum(d$blood), deaths = sum(d$death), same_day = sum(d$blood == 1 & d$death == 1 & d$blood_day == d$death_day),
  death_after_bleed = sum(d$blood == 1 & d$death == 1 & d$death_day > d$blood_day), death_first = sum(d$death == 1 & (d$blood == 0 | d$death_day < d$blood_day)),
  composite365 = sum(d$event_raw == 1 & d$t_raw <= 365), discrepant = sum(d$death == 1 & d$blood_day > d$death_day))
res$counts <- list(nace = tapply(d$e_nace == 1 & d$t_nace <= 365, d$W, sum), isch = tapply(d$e_isch == 1 & d$t_isch <= 365, d$W, sum),
                   comp = tapply(d$event_raw == 1 & d$t_raw <= 365, d$W, sum))
## censoring diagnostics
cens <- d$event_raw == 0 & d$t_raw < 365
res$cens <- list(n = sum(cens), by_arm = tapply(cens, d$W, sum), window_305_365 = sum(cens & d$t_raw >= 305), before_305 = sum(cens & d$t_raw < 305),
                 before_180 = sum(cens & d$t_raw < 180), q_cens_time = quantile(d$t_raw[cens], c(.05, .25, .5, .75)))
E <- encode(d, d)$tr; E <- E[, apply(E, 2, sd) > 0]
cd <- data.frame(time = pmin(d$t_raw, 365), cev = as.numeric(cens), W = d$W)
f0 <- coxph(Surv(time, cev) ~ W, data = cd); s0 <- summary(f0)
X23 <- d[, c("AGE", "men", "BMI", "Diabetes", "HTN", "Lipid", "PAD", "Cere", "ACS_2w", "MI", "PCI", "PRE_EGFR", "LVEF", "Onpump", "No_touch", "A_GRAFT", "V_GRAFT")]
X23$smoke <- factor(d$smoke_status); X23$CCS <- factor(d$CCS); X23$NYHA <- factor(d$NYHA); X23$site <- factor(d$site)
X23$LDLC <- ifelse(is.na(d$LDLC), median(d$LDLC, na.rm = TRUE), d$LDLC); X23$SYNTAX <- ifelse(is.na(d$SYNTAX), median(d$SYNTAX, na.rm = TRUE), d$SYNTAX)
X23$Seq <- ifelse(is.na(d$Seq_SVG), 0, d$Seq_SVG)
cd2 <- cbind(cd, X23)
f1 <- coxph(Surv(time, cev) ~ ., data = cd2); s1 <- summary(f1)
f1ns <- coxph(Surv(time, cev) ~ . - site, data = cd2)
fnull <- coxph(Surv(time, cev) ~ W, data = cd2)
lr_all <- 2 * (f1$loglik[2] - fnull$loglik[2]); df_all <- length(coef(f1)) - 1
lr_ns <- 2 * (f1ns$loglik[2] - fnull$loglik[2]); df_ns <- length(coef(f1ns)) - 1
co <- s1$coefficients; sig <- rownames(co)[co[, 5] < 0.05]
res$cens_cox <- list(hr_arm = unname(s0$conf.int[1, c(1, 3, 4)]), p_arm = unname(s0$coefficients[1, 5]),
                     hr_arm_adj = unname(s1$conf.int["W", c(1, 3, 4)]),
                     global_p_predictors = pchisq(lr_all, df_all, lower.tail = FALSE), df = df_all,
                     global_p_no_site = pchisq(lr_ns, df_ns, lower.tail = FALSE), df_ns = df_ns, significant = sig,
                     hr_sig = co[sig, 2, drop = FALSE])
## reverse Kaplan-Meier censoring survival at selected days, by arm
rk <- survfit(Surv(pmin(d$t_raw, 400), as.numeric(d$event_raw == 0)) ~ d$W)
res$G <- summary(rk, times = c(90, 180, 270, 300, 330, 350, 365))[c("time", "surv", "strata")]
## period decomposition of the RMST difference (Kaplan-Meier)
kmS <- function(w, t) { f <- survfit(Surv(d$t_raw[d$W == w], d$event_raw[d$W == w]) ~ 1); summary(f, times = t, extend = TRUE)$surv }
decomp <- function(L) {
  a3 <- km_rmst(d$t_raw[d$W == 1], d$event_raw[d$W == 1], L)[[1]]; a12 <- km_rmst(d$t_raw[d$W == 0], d$event_raw[d$W == 0], L)[[1]]
  S3 <- kmS(1, L); S12 <- kmS(0, L)
  # conditional RMST from L to 365 among those event-free at L
  sub <- d$t_raw > L
  c3 <- km_rmst(d$t_raw[sub & d$W == 1] - L, d$event_raw[sub & d$W == 1], 365 - L)[[1]]; c12 <- km_rmst(d$t_raw[sub & d$W == 0] - L, d$event_raw[sub & d$W == 0], 365 - L)[[1]]
  total <- km_rmst(d$t_raw[d$W == 1], d$event_raw[d$W == 1], 365)[[1]] - km_rmst(d$t_raw[d$W == 0], d$event_raw[d$W == 0], 365)[[1]]
  list(L = L, early_area = a3 - a12, S3 = S3, S12 = S12, carry = (S3 - S12) * c12, late_conditional = S3 * (c3 - c12), cond_diff = c3 - c12, total = total)
}
res$decomp <- list(d90 = decomp(90), d85 = decomp(85))
early_cox <- coxph(Surv(pmin(d$t_raw, 90), as.numeric(d$event_raw == 1 & d$t_raw <= 90)) ~ d$W); late_cox <- coxph(Surv(d$t_raw[d$t_raw > 90] - 90, as.numeric(d$event_raw[d$t_raw > 90] == 1 & d$t_raw[d$t_raw > 90] <= 365)) ~ d$W[d$t_raw > 90])
res$period_hr <- list(early = unname(summary(early_cox)$conf.int[c(1, 3, 4)]), early_p = unname(summary(early_cox)$coefficients[5]),
                      late = unname(summary(late_cox)$conf.int[c(1, 3, 4)]))
## prognostic accuracy of the restricted comparator, IPCW Brier with training-fold reverse Kaplan-Meier
brier <- function(tq) {
  num <- den <- 0; out <- c()
  pS <- rep(NA, nrow(d)); km_ref <- rep(NA, nrow(d)); idxint <- c(30, 60, 90, 180, 270, 365)
  bm <- bk <- c()
  for (k in 0:4) {
    te <- which(d$fold == k); tr <- which(d$fold != k)
    G <- survfit(Surv(d$t_raw[tr], 1 - d$event_raw[tr]) ~ 1); Gf <- stepfun(G$time, c(1, G$surv))
    Kf <- survfit(Surv(d$t_raw[tr], d$event_raw[tr]) ~ 1); Kref <- summary(Kf, times = tq, extend = TRUE)$surv
    j <- match(tq, idxint)
    # predicted survival at tq under the assigned arm, interpolated at interval ends
    S <- ifelse(d$W[te] == 1, R$pw$surv1[te, j], R$pw$surv0[te, j])
    tt <- d$t_raw[te]; ee <- d$event_raw[te]
    Gm <- Gf(pmax(tt - 1e-8, 0)); Gt <- Gf(tq)
    w <- ifelse(tt <= tq & ee == 1, 1 / Gm, ifelse(tt > tq, 1 / Gt, 0))
    yv <- as.numeric(tt > tq)
    bm <- c(bm, w * (yv - S)^2); bk <- c(bk, w * (yv - Kref)^2)
  }
  c(model = mean(bm), km = mean(bk), ipa = 1 - mean(bm) / mean(bk))
}
res$brier <- lapply(c(d90 = 90, d180 = 180, d270 = 270, d365 = 365), brier)
## Uno concordance at day 365 using predicted risk 1 - S(365) under the assigned arm
risk <- 1 - ifelse(d$W == 1, R$pw$surv1[, 6], R$pw$surv0[, 6])
uno <- function() { num <- den <- 0
  for (k in 0:4) { te <- which(d$fold == k); tr <- which(d$fold != k)
    G <- survfit(Surv(d$t_raw[tr], 1 - d$event_raw[tr]) ~ 1); Gf <- stepfun(G$time, c(1, G$surv))
    tt <- d$t_raw[te]; ee <- d$event_raw[te]; rr <- risk[te]
    for (i in which(ee == 1 & tt < 365)) { j <- tt > tt[i]; w <- 1 / Gf(tt[i] - 1e-8)^2
      num <- num + w * sum(j * ((rr[i] > rr) + 0.5 * (rr[i] == rr))); den <- den + w * sum(j) } }
  num / den }
res$uno365 <- uno()
## graft occlusion: heterogeneity of the effect of the shorter regimen (causal forest, cross-fitted)
so <- read.csv("data/raw/svg_occ_main.csv", colClasses = c(site = "character"))
anyo <- tapply(so$occluded_status, so$pid, max); gi <- d$pid %in% names(anyo); dg <- d[gi, ]; dg$occ <- as.numeric(anyo[dg$pid])
tg <- gg <- rep(NA, nrow(dg))
for (k in 0:4) { te <- which(dg$fold == k); tr <- which(dg$fold != k); E <- encode(dg[tr, ], dg[te, ])
  f <- causal_forest(E$tr, dg$occ[tr], dg$W[tr], W.hat = 0.5, num.trees = 4000, min.node.size = 5, seed = SEED + k, num.threads = NT)
  tg[te] <- predict(f, E$te)$predictions
  e <- causal_forest(E$te, dg$occ[te], dg$W[te], W.hat = 0.5, num.trees = 4000, seed = SEED + 100 + k, num.threads = NT)
  gg[te] <- get_scores(e) }
res$graft_cf <- list(n = nrow(dg), ate = mean(gg), ate_se = sd(gg) / sqrt(nrow(dg)), range = range(tg), n_harm = sum(tg > 0),
                     calib = calib(tg, gg), autoc = rate_fw(-tg, -gg, dg$fold, "AUTOC"))
write.csv(data.frame(pid = dg$pid, tau_graft = tg, gamma_graft = gg), "work/graft_cf.csv", row.names = FALSE)
write_json(res, "work/misc.json", auto_unbox = TRUE, digits = 8, pretty = TRUE)
cat("misc done\n")
