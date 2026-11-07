source("analysis/pipe.R"); d <- load_pat(); R <- readRDS("work/primary.rds")
tqs <- c(30, 60, 90, 180, 270, 365); bm <- bk <- c()
for (tq in tqs) { a <- b <- c()
  for (k in 0:4) { te <- which(d$fold == k); tr <- which(d$fold != k)
    G <- survfit(Surv(d$t_raw[tr], 1 - d$event_raw[tr]) ~ 1); Gf <- stepfun(G$time, c(1, G$surv))
    Kf <- survfit(Surv(d$t_raw[tr], d$event_raw[tr]) ~ 1); Kref <- summary(Kf, times = tq, extend = TRUE)$surv
    j <- match(tq, tqs); S <- ifelse(d$W[te] == 1, R$pw$surv1[te, j], R$pw$surv0[te, j]); tt <- d$t_raw[te]; ee <- d$event_raw[te]
    w <- ifelse(tt <= tq & ee == 1, 1 / Gf(pmax(tt - 1e-8, 0)), ifelse(tt > tq, 1 / Gf(tq), 0)); y <- as.numeric(tt > tq)
    a <- c(a, w * (y - S)^2); b <- c(b, w * (y - Kref)^2) }
  bm <- c(bm, mean(a)); bk <- c(bk, mean(b)) }
tt <- c(0, tqs); trap <- function(v) sum(diff(tt) * (c(0, v)[-1] + c(0, v)[-length(tt)]) / 2) / 365
cat(round(bm, 4), "\n", round(bk, 4), "\nIBS", round(trap(bm), 4), round(trap(bk), 4), "IPA", round(1 - trap(bm) / trap(bk), 4), "\n")
write_json(list(ibs = trap(bm), ibs_km = trap(bk)), "work/ibs.json", auto_unbox = TRUE, digits = 6)
