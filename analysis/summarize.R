source("analysis/pipe.R")
## bootstrap replicate summaries
fs <- list.files("work/boot", full.names = TRUE)
if (length(fs)) { S <- do.call(rbind, lapply(fs, function(f) { x <- readRDS(f); c(b = x$b, x$summary) })); write.csv(S, "work/boot_summary.csv", row.names = FALSE) }
## simulation replicate summaries
fs <- list.files("work/sim", full.names = TRUE)
if (length(fs)) { S <- do.call(rbind, lapply(fs, function(f) { x <- readRDS(f); data.frame(scenario = sub("_.*", "", basename(f)), rep = as.integer(sub(".*_(\\d+)\\.rds", "\\1", basename(f))), t(x)) }))
  write.csv(S, "work/sim_summary.csv", row.names = FALSE) }
## TOC curves, fold-averaged
P <- read.csv("work/primary_patients.csv")
toc <- function(pr) { L <- lapply(0:4, function(k) { i <- P$fold == k; r <- rank_average_treatment_effect.fit(P$gamma[i], pr[i], target = "AUTOC", R = 200)
  data.frame(fold = k, q = r$TOC$q, est = r$TOC$estimate, se = r$TOC$std.err) }); do.call(rbind, L) }
if (!file.exists("work/toc.csv")) write.csv(rbind(cbind(priority = "forest", toc(P$tau)), cbind(priority = "comparator", toc(P$tau_pw))), "work/toc.csv", row.names = FALSE)
cat("ok\n")
