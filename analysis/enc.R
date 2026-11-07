CONT <- c("AGE","BMI","PRE_EGFR","LDLC","LVEF","A_GRAFT","V_GRAFT","SYNTAX")
BIN  <- c("men","Diabetes","HTN","Lipid","PAD","Cere","ACS_2w","MI","PCI","Onpump","No_touch","Seq_SVG")
encode <- function(tr, te, spec = "E1", site = TRUE, smoke3 = FALSE) {
  out <- function(d) {
    cols <- list()
    for (v in CONT) { m <- median(tr[[v]], na.rm = TRUE); x <- d[[v]]; cols[[paste0(v, "_miss")]] <- as.numeric(is.na(x)); x[is.na(x)] <- m; cols[[v]] <- x }
    bins <- BIN
    for (v in bins) { m <- median(tr[[v]], na.rm = TRUE); x <- d[[v]]; cols[[paste0(v, "_miss")]] <- as.numeric(is.na(x)); x[is.na(x)] <- m; cols[[v]] <- x }
    if (smoke3) { for (l in 1:3) cols[[paste0("smoke_", l)]] <- as.numeric(d$smoke_status == l); cols[["smoke_miss"]] <- as.numeric(is.na(d$smoke_status)) }
    else { cols[["smoke_never"]] <- as.numeric(d$smoke_status == 1); cols[["smoke_never_miss"]] <- as.numeric(is.na(d$smoke_status)) }
    for (v in c("CCS","NYHA")) { for (l in 1:4) cols[[paste0(v, "_", l)]] <- as.numeric(!is.na(d[[v]]) & d[[v]] == l); cols[[paste0(v, "_missing")]] <- as.numeric(is.na(d[[v]])) }
    if (site) { for (s in c("01","14","17","98","99")) cols[[paste0("site_", s)]] <- as.numeric(d$site == s); cols[["site_unknown"]] <- as.numeric(!(d$site %in% c("01","14","17","98","99"))) }
    as.matrix(as.data.frame(cols))
  }
  list(tr = out(tr), te = out(te))
}
