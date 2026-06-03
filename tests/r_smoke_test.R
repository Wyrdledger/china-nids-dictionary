source("R/read_nids_dictionary.R", encoding = "UTF-8")

df <- read_nids_dictionary("data/nids_current.csv")
expected_columns <- c(
  "disease_id",
  "record_type",
  "is_notifiable_disease",
  "parent_disease_id",
  "disease_name_zh",
  "cisdcp_disease_name",
  "disease_name_en",
  "legal_class",
  "management_class",
  "report_time_limit_hours",
  "transmission_type"
)
stopifnot(identical(colnames(df), expected_columns))
stopifnot("cisdcp_disease_name" %in% colnames(df))
stopifnot(!"raw_match_name_zh" %in% colnames(df))
stopifnot(!"official_name_zh" %in% colnames(df))
stopifnot(!"report_name_zh" %in% colnames(df))
stopifnot(!"is_current" %in% colnames(df))
stopifnot(!"effective_start_date" %in% colnames(df))
stopifnot(!"effective_end_date" %in% colnames(df))
stopifnot(!"source_id" %in% colnames(df))
stopifnot(!"source_note" %in% colnames(df))
stopifnot(nrow(df) == 83)
notifiable <- df[df$is_notifiable_disease, ]
stopifnot(nrow(notifiable) == 42)
stopifnot(all(df$record_type[1:42] == "notifiable_disease"))
stopifnot(all(df$record_type[43:(nrow(df) - 1)] == "subtype"))
stopifnot(sum(notifiable$legal_class == "甲类") == 2)
stopifnot(sum(notifiable$legal_class == "乙类") == 29)
stopifnot(sum(notifiable$legal_class == "丙类") == 11)
stopifnot(is.integer(df$report_time_limit_hours))
stopifnot(is.logical(df$is_notifiable_disease))
stopifnot(sum(df$record_type == "aggregate") == 1)
stopifnot(is.na(df$report_time_limit_hours[df$record_type == "aggregate"]))
stopifnot(tail(df$disease_name_zh, 1) == "合计")
stopifnot(df$record_type[df$cisdcp_disease_name == "HIV"] == "subtype")
stopifnot(df$disease_name_zh[df$cisdcp_disease_name == "痢疾"] == "细菌性和阿米巴痢疾")
class_a_managed <- df[df$legal_class == "乙类" & df$management_class == "甲类管理", ]
stopifnot(setequal(class_a_managed$disease_id, c("NID-B-002", "NID-B-013-S001")))
stopifnot(all(class_a_managed$report_time_limit_hours == 2))
expected_transmission_types <- c(
  "呼吸道传染病",
  "肠道传染病",
  "动物源性及虫媒传染病",
  "经血与性传播传染病",
  "其他"
)
stopifnot(all(expected_transmission_types %in% df$transmission_type))
stopifnot(df$transmission_type[df$disease_name_zh == "H5N1"] == "动物源性及虫媒传染病")
stopifnot(df$transmission_type[df$disease_name_zh == "H7N9"] == "动物源性及虫媒传染病")
stopifnot(df$transmission_type[df$disease_name_zh == "乙肝"] == "经血与性传播传染病")
stopifnot(df$transmission_type[df$disease_name_zh == "新生儿破伤风"] == "其他")
