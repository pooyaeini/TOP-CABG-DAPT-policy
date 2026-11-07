source("analysis/pipe.R"); d <- load_pat()
m <- function(v, w) sprintf("%.2f (%.2f)", mean(d[[v]][d$W == w], na.rm = TRUE), sd(d[[v]][d$W == w], na.rm = TRUE))
for (v in c("AGE", "BMI", "PRE_EGFR", "LDLC", "LVEF", "SYNTAX", "A_GRAFT", "V_GRAFT")) cat(v, m(v, 0), m(v, 1), "\n")
for (v in c("men", "Diabetes", "HTN", "Lipid", "PAD", "Cere", "ACS_2w", "MI", "PCI", "Onpump", "No_touch", "Seq_SVG")) cat(v, sum(d[[v]][d$W == 0] == 1, na.rm = TRUE), sum(d[[v]][d$W == 1] == 1, na.rm = TRUE), " ")
cat("\n")
# reverse KM median follow-up and IQR
rk <- survfit(Surv(d$t_raw, 1 - d$event_raw) ~ 1); print(quantile(rk, c(.25, .5, .75))$quantile)
# Aalen-Johansen bleeding with death competing, day 365
st <- ifelse(d$event_raw == 0, 0, ifelse(d$blood == 1 & d$blood_day == d$t_raw, 1, 2))
for (w in 0:1) { f <- survfit(Surv(d$t_raw[d$W == w], factor(st[d$W == w], 0:2)) ~ 1); s <- summary(f, times = 365); cat("AJ arm", w, round(100 * s$pstate[, 2:3], 2), "\n") }
# graft: segment OR with cluster-robust SE
so <- read.csv("data/raw/svg_occ_main.csv", colClasses = c(site = "character")); so$W <- as.numeric(so$COL_INV == "B")
g <- glm(occluded_status ~ W, family = binomial, data = so); X <- model.matrix(g); e <- residuals(g, "response")
B <- solve(crossprod(X * sqrt(g$weights))); U <- rowsum(X * e, so$pid); V <- B %*% crossprod(U) %*% B
cat("OR", round(exp(coef(g)[2]), 2), round(exp(coef(g)[2] + c(-1.96, 1.96) * sqrt(V[2, 2])), 2), "\n")
