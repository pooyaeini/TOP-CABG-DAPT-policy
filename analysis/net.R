source("analysis/pipe.R"); d <- load_pat(); P <- read.csv("work/primary_patients.csv"); I <- readRDS("work/sens/isch.rds")
out <- list()
for (k in c(1, 2, 5)) { nb <- P$tau + k * I$tau; g <- P$gamma + k * I$gamma; dd <- as.numeric(nb >= 0); v <- (dd - 1) * g
  out[[paste0("k", k)]] <- c(n12 = sum(dd == 0), value = mean(v), lo = mean(v) - 1.96 * sd(v) / sqrt(nrow(d)), hi = mean(v) + 1.96 * sd(v) / sqrt(nrow(d)), mean_net = mean(g)) }
v <- (as.numeric(P$tau_pwf >= 0) - 1) * P$gamma; out$pwf <- c(value = mean(v), lo = mean(v) - 1.96 * sd(v) / sqrt(nrow(d)), hi = mean(v) + 1.96 * sd(v) / sqrt(nrow(d)))
out$cor_bleed_isch <- cor(P$tau, I$tau)
write_json(out, "work/net.json", auto_unbox = TRUE, digits = 6); print(out)
