# Changelog

## 2026-06-03

- 统一中文疾病名称字段，移除 `official_name_zh` 和 `report_name_zh`，将对外报告正式名称收敛到 `disease_name_zh`。
- 将 `raw_match_name_zh` 更名为 `cisdcp_disease_name`，明确用于精确匹配 CISDCP 疫情分析报表 `疾病病种` 列。
- 按报告展示口径调整 `痢疾`、`其他感染性腹泻病` 和一/二/三期梅毒名称，并新增中文括号校验。
- 参考 `Infection_Weekly/config/dictionary.csv` 扩展当前字典为 83 条统一记录，保留 42 条独立法定传染病并新增子项、别名和汇总项。
- 新增 `record_type`、`is_notifiable_disease`、`parent_disease_id`、`cisdcp_disease_name` 和 `transmission_type` 字段。
- 更新 CSV/JSON 数据、字段 schema、R/Python 读取示例和测试，支持旧周报字典映射迁移校验。
- 初始化 `china-nids-dictionary` 轻量数据字典项目。
- 建立当前 42 种中国法定传染病 NIDs 字典基线。
- 添加 CSV/JSON 数据文件、字段 schema、R/Python 读取示例和测试。
- 添加来源说明，引用 2025 年《中华人民共和国传染病防治法》和 2026 年第 3 号国家卫生健康委公告。
