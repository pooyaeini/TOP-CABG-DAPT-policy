## Core pipeline for the revised TOP-CABG policy analysis (re-executed in full for the revision)
## grf 2.4.0 is used for every reported analysis. Set GRF240_LIB to the R library that holds it;
## GRF_LIB=new uses the default library (grf 2.6.1) for the version sensitivity analysis.
if (Sys.getenv("GRF_LIB") != "new" && nzchar(Sys.getenv("GRF240_LIB"))) .libPaths(c(Sys.getenv("GRF240_LIB"), .libPaths()))
suppressPackageStartupMessages({library(grf); library(survival); library(glmnet); library(jsonlite)})
source("analysis/enc.R")
SEED <- 20260907
NT <- as.integer(Sys.getenv("GRF_THREADS", "2"))
TREES <- as.integer(Sys.getenv("GRF_TREES", "4000"))

load_pat <- function() {
  d <- read.csv("work/patients.csv", colClasses = c(site = "character", pid = "character"))
  # secondary endpoints, same conservative construction
  Tn <- pmin(d$blood_day, d$death_day, d$mi_day, d$stroke_day, d$revas_cor_day)
  d$t_nace <- Tn
  d$e_nace <- as.integer((d$blood == 1 & d$blood_day == Tn) | (d$death == 1 & d$death_day == Tn) |
                         (d$mi == 1 & d$mi_day == Tn) | (d$stroke == 1 & d$stroke_day == Tn) | (d$revas_cor == 1 & d$revas_cor_day == Tn))
  Ti <- pmin(d$death_day, d$mi_day, d$stroke_day, d$revas_cor_day)
  d$t_isch <- Ti
  d$e_isch <- as.integer((d$death == 1 & d$death_day == Ti) | (d$mi == 1 & d$mi_day == Ti) |
                         (d$stroke == 1 & d$stroke_day == Ti) | (d$revas_cor == 1 & d$revas_cor_day == Ti))
  # death-first tie rule for the primary composite (labels only; time unchanged)
  d
}

csf <- function(X, Y, W, D, horizon, mns, seed, clusters = NULL, trees = TREES) {
  a <- list(X = X, Y = Y, W = W, D = D, W.hat = 0.5, target = "RMST", horizon = horizon,
            num.trees = trees, min.node.size = mns, mtry = max(1L, floor(sqrt(ncol(X)))),
            sample.fraction = 0.5, honesty = TRUE, honesty.fraction = 0.5, alpha = 0.05,
            seed = seed, num.threads = NT)
  if (!is.null(clusters)) a$clusters <- clusters
  suppressWarnings(do.call(causal_survival_forest, a))
}

## censoring survival at each subject's truncated time, same specification as the grf nuisance forest
chat_own <- function(X, Y, W, D, horizon, seed, clusters = NULL, trees = TREES) {
  D2 <- D; Y2 <- Y; D2[Y2 >= horizon] <- 1; Y2[Y2 >= horizon] <- horizon
  a <- list(X = cbind(X, W), Y = Y2, D = 1 - D2, num.trees = max(50, min(trees / 4, 500)),
            sample.fraction = 0.5, mtry = max(1L, floor(sqrt(ncol(X)))), min.node.size = 15, honesty = TRUE,
            honesty.fraction = 0.5, alpha = 0.05, prediction.type = "Nelson-Aalen", seed = seed, num.threads = NT)
  if (!is.null(clusters)) a$clusters <- clusters
  sf <- do.call(survival_forest, a)
  grid <- sort(unique(Y2)); P <- predict(sf, failure.times = grid)$predictions
  P[cbind(seq_along(Y2), match(Y2, grid))]
}

## generic cross-fitted run.  d: data frame; ycol/dcol: time and event columns; folds: vector
crossfit <- function(d, ycol, dcol, horizon = 365, folds = d$fold, site = TRUE, smoke3 = FALSE,
                     mns_disc = 40, mns_eval = 10, seed = SEED, clusters = NULL, extraX = NULL,
                     want_chat = FALSE, want_oob = TRUE, trees = TREES, train_idx_fun = NULL) {
  n <- nrow(d); tau <- gam <- chat <- rep(NA_real_, n); cut1 <- cut2 <- rep(NA_real_, n)
  for (k in sort(unique(folds))) {
    te <- which(folds == k); tr <- which(folds != k)
    E <- encode(d[tr, ], d[te, ], site = site, smoke3 = smoke3)
    Xtr <- E$tr; Xte <- E$te
    if (!is.null(extraX)) { Xtr <- cbind(Xtr, extraX[tr, , drop = FALSE]); Xte <- cbind(Xte, extraX[te, , drop = FALSE]) }
    cl_tr <- if (is.null(clusters)) NULL else clusters[tr]; cl_te <- if (is.null(clusters)) NULL else clusters[te]
    f <- csf(Xtr, d[[ycol]][tr], d$W[tr], d[[dcol]][tr], horizon, mns_disc, seed + k, cl_tr, trees)
    tau[te] <- predict(f, Xte)$predictions
    if (want_oob) { q <- quantile(predict(f)$predictions, c(1 / 3, 2 / 3)); cut1[te] <- q[1]; cut2[te] <- q[2] }
    # evaluation forest: same covariate set, evaluation fold only
    Ee <- encode(d[tr, ], d[te, ], site = TRUE, smoke3 = smoke3)$te
    if (!is.null(extraX)) Ee <- cbind(Ee, extraX[te, , drop = FALSE])
    e <- csf(Ee, d[[ycol]][te], d$W[te], d[[dcol]][te], horizon, mns_eval, seed + 100 + k, cl_te, trees)
    gam[te] <- get_scores(e)
    if (want_chat) chat[te] <- chat_own(Ee, d[[ycol]][te], d$W[te], d[[dcol]][te], horizon, seed + 200 + k, cl_te, trees)
  }
  list(tau = tau, gamma = gam, chat = chat, cut1 = cut1, cut2 = cut2, folds = folds)
}

pol <- function(tau, gam) {
  dd <- as.numeric(tau >= 0)
  c(mean_score = mean(gam), learned_minus_all3 = mean((dd - 1) * gam), n12 = sum(dd == 0), frac3 = mean(dd),
    all12_minus_all3 = -mean(gam))
}

rate_fw <- function(tau, gam, folds, target = "AUTOC", R = 200) {
  est <- se <- nk <- c()
  for (k in sort(unique(folds))) {
    i <- which(folds == k)
    r <- rank_average_treatment_effect.fit(gam[i], tau[i], target = target, R = R)
    est <- c(est, r$estimate); se <- c(se, r$std.err); nk <- c(nk, length(i))
  }
  w <- nk / sum(nk)
  list(estimate = sum(w * est), se = sqrt(sum(w^2 * se^2)), fold_est = est, fold_se = se)
}

calib <- function(tau, gam) {
  tc <- tau - mean(tau); fit <- lm(gam ~ tc); X <- model.matrix(fit); e <- residuals(fit)
  B <- solve(crossprod(X)); V <- B %*% crossprod(X * e) %*% B * nrow(X) / (nrow(X) - 2)
  b <- coef(fit); s <- sqrt(diag(V))
  list(intercept = unname(b[1]), int_lo = unname(b[1] - 1.96 * s[1]), int_hi = unname(b[1] + 1.96 * s[1]),
       slope = unname(b[2]), slope_lo = unname(b[2] - 1.96 * s[2]), slope_hi = unname(b[2] + 1.96 * s[2]))
}

groups <- function(tau, gam, cut1, cut2) {
  g <- ifelse(tau <= cut1, 1, ifelse(tau <= cut2, 2, 3))
  out <- lapply(1:3, function(j) { i <- g == j; m <- mean(gam[i]); s <- sd(gam[i]) / sqrt(sum(i))
    c(group = j, n = sum(i), mean = m, lo = m - 1.96 * s, hi = m + 1.96 * s, mean_tau = mean(tau[i])) })
  do.call(rbind, out)
}

## ---------------- piecewise-exponential comparators ----------------
pw_split <- function(time, event, brk) {
  rows <- list(); n <- length(time)
  for (j in seq_len(length(brk) - 1)) {
    a <- brk[j]; b <- brk[j + 1]
    expo <- pmin(time, b) - a
    keep <- expo > 0
    ev <- as.numeric(event == 1 & time > a & time <= b)
    rows[[j]] <- data.frame(id = which(keep), int = j, expo = expo[keep], ev = ev[keep])
  }
  do.call(rbind, rows)
}

pw_design <- function(S, Xs, W, brk, change, inter = FALSE, early_term = TRUE, inter_cols = NULL) {
  nI <- length(brk) - 1
  I <- sapply(1:nI, function(j) as.numeric(S$int == j)); colnames(I) <- paste0("int", 1:nI)
  late <- as.numeric(brk[S$int] >= change)
  Wr <- W[S$id]
  M <- cbind(I, W_late = Wr * late)
  pf <- c(rep(0, nI), 0)
  if (early_term) { M <- cbind(M, W_early = Wr * (1 - late)); pf <- c(pf, 0) }
  Xr <- Xs[S$id, , drop = FALSE]
  M <- cbind(M, Xr); pf <- c(pf, rep(1, ncol(Xr)))
  if (inter) {
    cols <- if (is.null(inter_cols)) colnames(Xs) else inter_cols
    XI <- Xr[, cols, drop = FALSE] * (Wr * late); colnames(XI) <- paste0("WxL_", cols)
    M <- cbind(M, XI); pf <- c(pf, rep(1, ncol(XI)))
  }
  list(M = M, pf = pf)
}

pw_fit_predict <- function(dtr, dte, ycol, dcol, horizon = 365, brk = c(0, 30, 60, 90, 180, 270, 365), change = 90,
                           inter = FALSE, early_term = TRUE, inter_vars = NULL, seed = SEED, site = TRUE, fixed_lambda = NULL) {
  E <- encode(dtr, dte, site = site)
  Xtr <- E$tr; Xte <- E$te
  keep <- apply(Xtr, 2, sd) > 0; Xtr <- Xtr[, keep, drop = FALSE]; Xte <- Xte[, keep, drop = FALSE]
  mu <- colMeans(Xtr); sdv <- apply(Xtr, 2, sd)
  Xtr <- sweep(sweep(Xtr, 2, mu), 2, sdv, "/"); Xte <- sweep(sweep(Xte, 2, mu), 2, sdv, "/")
  ttr <- pmin(dtr[[ycol]], horizon); etr <- as.numeric(dtr[[dcol]] == 1 & dtr[[ycol]] <= horizon)
  S <- pw_split(ttr, etr, brk)
  inter_cols <- if (is.null(inter_vars)) NULL else intersect(inter_vars, colnames(Xtr))
  DM <- pw_design(S, Xtr, dtr$W, brk, change, inter, early_term, inter_cols)
  set.seed(seed)
  pfold <- sample(rep(1:3, length.out = nrow(dtr)))
  lam <- if (is.null(fixed_lambda)) 10^seq(2, -4, length.out = 20) else fixed_lambda
  full <- glmnet(DM$M, S$ev, family = "poisson", offset = log(S$expo), alpha = 0, penalty.factor = DM$pf,
                 intercept = FALSE, lambda = if (length(lam) > 1) lam else c(lam * 10, lam), standardize = FALSE)
  devp <- matrix(NA, nrow(dtr), length(lam))
  for (v in if (length(lam) > 1) 1:3 else integer(0)) {
    rin <- pfold[S$id] != v; rout <- !rin
    g <- glmnet(DM$M[rin, ], S$ev[rin], family = "poisson", offset = log(S$expo[rin]), alpha = 0, penalty.factor = DM$pf,
                intercept = FALSE, lambda = lam, standardize = FALSE)
    mu <- predict(g, DM$M[rout, ], newoffset = log(S$expo[rout]), type = "response")
    y <- S$ev[rout]
    dv <- 2 * (ifelse(y > 0, y * log(y / mu), 0) - (y - mu))
    agg <- rowsum(dv, S$id[rout])
    devp[as.integer(rownames(agg)), ] <- agg
  }
  if (length(lam) > 1) {
    err <- colMeans(devp); se <- apply(devp, 2, sd) / sqrt(nrow(devp))
    jmin <- which.min(err); j1 <- min(which(err <= err[jmin] + se[jmin]))
    cv <- list(lambda.1se = lam[j1], lambda.min = lam[jmin])
  } else cv <- list(lambda.1se = lam, lambda.min = lam)
  cf <- as.numeric(coef(full, s = cv$lambda.1se, exact = FALSE))[-1]; names(cf) <- colnames(DM$M)
  rmst_for <- function(Xs, w) {
    nI <- length(brk) - 1; n <- nrow(Xs); lp <- as.numeric(Xs %*% cf[colnames(Xs)])
    S0 <- rep(1, n); r <- rep(0, n); surv <- matrix(NA, n, nI)
    for (j in 1:nI) {
      late <- brk[j] >= change
      eta <- cf[paste0("int", j)] + lp + (if (late) cf["W_late"] * w else if (early_term) cf["W_early"] * w else 0)
      if (inter && late) { ic <- grep("^WxL_", names(cf), value = TRUE); eta <- eta + w * as.numeric(Xs[, sub("^WxL_", "", ic), drop = FALSE] %*% cf[ic]) }
      h <- exp(eta); l <- brk[j + 1] - brk[j]
      r <- r + S0 * (1 - exp(-h * l)) / h; S0 <- S0 * exp(-h * l); surv[, j] <- S0
    }
    list(rmst = r, surv = surv)
  }
  p1 <- rmst_for(Xte, 1); p0 <- rmst_for(Xte, 0)
  list(tau = p1$rmst - p0$rmst, surv1 = p1$surv, surv0 = p0$surv, coef = cf, lambda = cv$lambda.1se,
       hr_late = exp(cf["W_late"]), hr_early = if (early_term) exp(cf["W_early"]) else NA)
}

pw_crossfit <- function(d, ycol = "t_raw", dcol = "event_raw", folds = d$fold, ...) {
  tau <- rep(NA, nrow(d)); s1 <- s0 <- matrix(NA, nrow(d), 6); info <- list()
  for (k in sort(unique(folds))) {
    te <- which(folds == k); tr <- which(folds != k)
    p <- pw_fit_predict(d[tr, ], d[te, ], ycol, dcol, seed = SEED + k, ...)
    tau[te] <- p$tau; s1[te, ] <- p$surv1; s0[te, ] <- p$surv0
    info[[as.character(k)]] <- list(lambda = p$lambda, hr_late = unname(p$hr_late), hr_early = unname(p$hr_early))
  }
  list(tau = tau, surv1 = s1, surv0 = s0, info = info)
}

## Kaplan-Meier RMST and its variance
km_rmst <- function(time, status, tau, lower = 0) {
  fit <- survfit(Surv(time, status) ~ 1)
  tt <- fit$time; ss <- fit$surv; ev <- fit$n.event; nr <- fit$n.risk
  grid <- c(0, tt[tt < tau], tau); sv <- c(1, ss[tt < tau])
  seg <- diff(grid) * sv
  # restrict to [lower, tau]
  st <- grid[-length(grid)]; en <- grid[-1]
  segl <- pmax(0, pmin(en, tau) - pmax(st, lower)) * sv
  rm <- sum(segl)
  v <- 0; et <- tt[tt < tau]
  for (j in seq_along(et)) {
    if (ev[j] > 0 && nr[j] > ev[j]) {
      A <- sum(segl[st >= et[j]])
      v <- v + A^2 * ev[j] / (nr[j] * (nr[j] - ev[j]))
    }
  }
  c(rmst = rm, se = sqrt(v))
}
