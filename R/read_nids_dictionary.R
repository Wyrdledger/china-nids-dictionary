# Lightweight reader for the China NIDs dictionary.
# Uses base R only, so it can be sourced from downstream analysis projects.

default_nids_current_csv <- paste0(
  "https://raw.githubusercontent.com/",
  "Wyrdledger/china-nids-dictionary/main/data/nids_current.csv"
)

read_nids_dictionary <- function(path_or_url = default_nids_current_csv) {
  df <- utils::read.csv(
    path_or_url,
    fileEncoding = "UTF-8-BOM",
    stringsAsFactors = FALSE,
    check.names = FALSE
  )

  df$report_time_limit_hours <- as.integer(df$report_time_limit_hours)
  df$is_current <- tolower(df$is_current) == "true"
  df$effective_end_date[df$effective_end_date == ""] <- NA_character_
  df
}
