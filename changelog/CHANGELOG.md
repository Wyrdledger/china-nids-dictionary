# Changelog

## 2026-06-03

- 重新评估并补齐全部 83 条记录的 `disease_name_en`，以 `disease_name_zh` 为基准维护专业医学/流行病学英文名称。
- 新增 `pathogen_type` 病原学分类字段，将新型冠状病毒感染、猴痘、基孔肯雅热、发热伴血小板减少综合征标记为 `病毒性疾病`，并将基孔肯雅热、发热伴血小板减少综合征归入 `动物源性及虫媒传染病`。
- 按新口径更新 `transmission_type`，新增 `动物源性及虫媒传染病`、`经血与性传播传染病` 和 `其他` 分类。
- 调整字段顺序，将记录类型、父子关系、名称、分类管理和传播类型按使用逻辑排列。
- 将 `痢疾` 的对外报告正式名称调整为 `细菌性和阿米巴痢疾`。
- 将所有 `乙类按甲类措施管理` 调整为 `甲类管理`；当前涉及 `传染性非典型肺炎` 和 `肺炭疽`，两者网络直报时限均为 2 小时。
- 将 HIV 记录类型从 `alias` 调整为 `subtype`，并将行顺序调整为法定传染病在上、子类/分型在下、`合计` 汇总项最后。
- 删除 `is_current`、`effective_start_date`、`effective_end_date`、`source_id` 和 `source_note` 字段，当前字典接口停在 `transmission_type`。
- 统一中文疾病名称字段，移除 `official_name_zh` 和 `report_name_zh`，将对外报告正式名称收敛到 `disease_name_zh`。
- 将 `raw_match_name_zh` 更名为 `cisdcp_disease_name`，明确用于精确匹配 CISDCP 疫情分析报表 `疾病病种` 列。
- 按报告展示口径调整 `痢疾`、`其他感染性腹泻病` 和一/二/三期梅毒名称，并新增中文括号校验。
- 扩展当前字典为 83 条统一记录，保留 42 条独立法定传染病并新增子项、别名和汇总项。
- 新增 `record_type`、`is_notifiable_disease`、`parent_disease_id`、`cisdcp_disease_name` 和 `transmission_type` 字段。
- 更新 CSV/JSON 数据、字段 schema、R/Python 读取示例和测试。
- 初始化 `china-nids-dictionary` 轻量数据字典项目。
- 建立当前 42 种中国法定传染病 NIDs 字典基线。
- 添加 CSV/JSON 数据文件、字段 schema、R/Python 读取示例和测试。
- 添加来源说明，引用 2025 年《中华人民共和国传染病防治法》和 2026 年第 3 号国家卫生健康委公告。
