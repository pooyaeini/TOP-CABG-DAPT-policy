## Participant-clustered full-pipeline bootstrap. Usage: Rscript analysis/boot.R <from> <to>
source("analysis/pipe.R")
args <- as.integer(commandArgs(TRUE)); from <- args[1]; to <- args[2]
d0 <- load_pat(); dir.create("work/boot", showWarnings = FALSE)
strata <- paste(d0$site, d0$COL_INV)
for (b in from:to) {
  out <- sprintf("work/boot/rep_%03d.rds", b)
  if (file.exists(out)) next
  t0 <- Sys.time()
  set.seed(SEED + b)
  idx <- unlist(lapply(split(seq_len(nrow(d0)), strata), function(s) s[sample.int(length(s), replace = TRUE)]))
  db <- d0[idx, ]; rownames(db) <- NULL
  # outer folds assigned to original participants within site-by-arm strata, so copies share a fold
  up <- unique(db[, c("pid", "site", "COL_INV")]); up$fold <- -1L
  rng_perm <- function(v) v[sample.int(length(v))]
  for (key in sort(unique(paste(up$site, up$COL_INV)))) {
    ii <- which(paste(up$site, up$COL_INV) == key); ii <- ii[order(up$pid[ii])]; p <- rng_perm(ii)
    up$fold[p] <- (seq_along(p) - 1) %% 5
  }
  db$fold <- up$fold[match(db$pid, up$pid)]
  cl <- match(db$pid, unique(db$pid))
  cf <- crossfit(db, "t_raw", "event_raw", folds = db$fold, clusters = cl, want_oob = FALSE)
  pp <- pol(cf$tau, cf$gamma)
  cb <- tryCatch(calib(cf$tau, cf$gamma), error = function(e) list(slope = NA))
  au <- tryCatch(rate_fw(cf$tau, cf$gamma, db$fold, "AUTOC", R = 2)$estimate, error = function(e) NA)
  qi <- tryCatch(rate_fw(cf$tau, cf$gamma, db$fold, "QINI", R = 2)$estimate, error = function(e) NA)
  saveRDS(list(b = b, summary = c(pp, slope = cb$slope, autoc = au, qini = qi,
                                  secs = as.numeric(Sys.time() - t0, units = "secs")),
               pid = db$pid, fold = db$fold, tau = cf$tau, gamma = cf$gamma), out)
}
