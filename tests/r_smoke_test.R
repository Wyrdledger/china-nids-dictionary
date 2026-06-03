source("R/read_nids_dictionary.R", encoding = "UTF-8")

df <- read_nids_dictionary("data/nids_current.csv")
stopifnot(nrow(df) == 42)
stopifnot(sum(df$legal_class == "甲类") == 2)
stopifnot(sum(df$legal_class == "乙类") == 29)
stopifnot(sum(df$legal_class == "丙类") == 11)
stopifnot(is.integer(df$report_time_limit_hours))
stopifnot(is.logical(df$is_current))
