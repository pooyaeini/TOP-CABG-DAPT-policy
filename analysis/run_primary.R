source("analysis/pipe.R")
d <- load_pat(); n <- nrow(d)
t0 <- Sys.time()
cf <- crossfit(d, "t_raw", "event_raw", want_chat = TRUE)
cat("csf done", round(as.numeric(Sys.time() - t0, units = "secs")), "\n")
pw  <- pw_crossfit(d)                                   # restricted comparator
pwi <- pw_crossfit(d, inter = TRUE)                     # all-covariate late interactions
pw3 <- pw_crossfit(d, inter = TRUE, inter_vars = c("AGE", "PRE_EGFR", "SYNTAX"))  # prespecified three
pwf <- pw_crossfit(d, inter = TRUE, fixed_lambda = 1e-4)          # minimally penalized interaction model
pwc <- pw_crossfit(d, brk = c(0, 30, 60, 85, 180, 270, 365), change = 85, early_term = FALSE)  # constrained
cat("comparators done", round(as.numeric(Sys.time() - t0, units = "secs")), "\n")
tau <- cf$tau; gam <- cf$gamma
res <- list()
res$policy <- list(csf = pol(tau, gam), pw = pol(pw$tau, gam), pwi = pol(pwi$tau, gam), pw3 = pol(pw3$tau, gam), pwc = pol(pwc$tau, gam), pwf = pol(pwf$tau, gam))
res$tau_range <- list(csf = range(tau), pw = range(pw$tau), pwi = range(pwi$tau), pw3 = range(pw3$tau), pwc = range(pwc$tau), pwf = range(pwf$tau))
res$n_negative <- list(csf = sum(tau < 0), pw = sum(pw$tau < 0), pwi = sum(pwi$tau < 0), pw3 = sum(pw3$tau < 0), pwc = sum(pwc$tau < 0), pwf = sum(pwf$tau < 0))
res$agree_csf_pw <- mean((tau >= 0) == (pw$tau >= 0))
res$cor_tau <- list(csf_pw = cor(tau, pw$tau), csf_pwi = cor(tau, pwi$tau))
res$calib <- calib(tau, gam)
res$calib_uncentered_intercept <- unname(coef(lm(gam ~ tau))[1])
res$groups <- groups(tau, gam, cf$cut1, cf$cut2)
res$autoc_csf <- rate_fw(tau, gam, d$fold, "AUTOC"); res$qini_csf <- rate_fw(tau, gam, d$fold, "QINI")
res$autoc_pw <- rate_fw(pw$tau, gam, d$fold, "AUTOC"); res$qini_pw <- rate_fw(pw$tau, gam, d$fold, "QINI")
res$autoc_pwi <- rate_fw(pwi$tau, gam, d$fold, "AUTOC"); res$autoc_pwf <- rate_fw(pwf$tau, gam, d$fold, "AUTOC")
res$calib_pw <- calib(pw$tau, gam); res$calib_pwf <- calib(pwf$tau, gam)
res$pw_info <- list(pw = pw$info, pwi = pwi$info, pwc = pwc$info)
# difference in AUTOC, forest minus comparator, same implementation
de <- ds <- nk <- c()
for (k in 0:4) { i <- which(d$fold == k)
  r <- rank_average_treatment_effect.fit(gam[i], cbind(tau[i], pw$tau[i]), target = "AUTOC", R = 200)
  de <- c(de, r$estimate[3]); ds <- c(ds, r$std.err[3]); nk <- c(nk, length(i)) }
w <- nk / sum(nk); res$autoc_diff <- list(estimate = sum(w * de), se = sqrt(sum(w^2 * ds^2)))
# score distribution and censoring support
res$score_sd <- sd(gam); res$score_gt365 <- sum(abs(gam) > 365)
res$chat <- list(q = quantile(cf$chat, c(0, .01, .05, .1, .25, .5)), lt10 = mean(cf$chat < 0.10), lt05 = mean(cf$chat < 0.05),
                 w_median = median(1 / cf$chat), w_p99 = unname(quantile(1 / cf$chat, .99)), w_max = max(1 / cf$chat),
                 ess = sum(1 / cf$chat)^2 / sum(1 / cf$chat^2))
# fixed-prediction bootstrap, 2000 replicates within site-by-arm strata
set.seed(SEED); strata <- paste(d$site, d$W); B <- 2000; dd <- as.numeric(tau >= 0)
bs <- t(replicate(B, { i <- unlist(lapply(split(seq_len(n), strata), function(s) s[sample.int(length(s), replace = TRUE)]))
  c(all12 = -mean(gam[i]), learned = mean((dd[i] - 1) * gam[i]), score = mean(gam[i])) }))
res$fixed_boot <- apply(bs, 2, quantile, c(.025, .975))
# conventional Kaplan-Meier RMST between randomized arms
km <- function(lo, hi) { a <- km_rmst(d$t_raw[d$W == 1], d$event_raw[d$W == 1], hi, lo); b <- km_rmst(d$t_raw[d$W == 0], d$event_raw[d$W == 0], hi, lo)
  c(rmst3 = a[[1]], rmst12 = b[[1]], diff = a[[1]] - b[[1]], se = sqrt(a[[2]]^2 + b[[2]]^2)) }
res$km <- list(full = km(0, 365), early90 = km(0, 90), late90 = km(90, 365), early85 = km(0, 85), late85 = km(85, 365), d360 = km(0, 360),
               h180 = km(0, 180), h270 = km(0, 270))
res$runtime_s <- as.numeric(Sys.time() - t0, units = "secs")
write_json(res, "work/primary.json", auto_unbox = TRUE, digits = 8, pretty = TRUE)
saveRDS(list(cf = cf, pw = pw, pwi = pwi, pw3 = pw3, pwc = pwc, pwf = pwf), "work/primary.rds")
write.csv(data.frame(pid = d$pid, fold = d$fold, W = d$W, tau = tau, gamma = gam, chat = cf$chat, tau_pw = pw$tau, tau_pwi = pwi$tau,
                     tau_pw3 = pw3$tau, tau_pwc = pwc$tau, tau_pwf = pwf$tau, cut1 = cf$cut1, cut2 = cf$cut2), "work/primary_patients.csv", row.names = FALSE)
cat("done", res$runtime_s, "\n")
