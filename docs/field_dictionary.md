# 字段说明

| 字段 | 含义 |
| --- | --- |
| `disease_id` | 本仓库维护的稳定病种 ID，格式为 `NID-A-001`、`NID-B-001`、`NID-C-001`。 |
| `disease_name_zh` | 记录名称。法定病种为法定中文名，子项/别名/汇总项为对应记录名。 |
| `disease_name_en` | 英文参考名称，仅用于辅助识别；子项、别名和汇总项可为空。 |
| `legal_class` | 法定分类：`甲类`、`乙类`、`丙类`；汇总项为空。 |
| `management_class` | 管理方式，例如 `乙类管理`、`乙类按甲类措施管理`；汇总项为空。 |
| `report_time_limit_hours` | 网络直报时限，单位为小时；当前取值为 `2`、`24` 或空值。 |
| `record_type` | 记录类型：`notifiable_disease` 法定病种、`subtype` 子项/分型、`alias` 别名、`aggregate` 汇总项。 |
| `is_notifiable_disease` | 是否为独立法定传染病。当前 42 个法定病种为 `true`，旧周报子项/别名/汇总项为 `false`。 |
| `parent_disease_id` | 子项或别名对应的父级法定病种 ID；法定病种和汇总项为空。 |
| `official_name_zh` | 权威或标准中文名。法定病种优先使用法律/公告全称。 |
| `report_name_zh` | 报告展示名，保留旧周报常用短名或展示口径。 |
| `raw_match_name_zh` | 原始数据匹配名，用于对接既有周报输入表中的病种名称。 |
| `transmission_type` | 业务传播类型，来自旧周报字典；当前取值为 `呼吸道传染病`、`肠道传染病` 或空值。 |
| `is_current` | 是否为当前有效记录。 |
| `effective_start_date` | 本记录在本仓库口径中的生效日期，ISO 日期格式。 |
| `effective_end_date` | 本记录失效日期；当前有效记录为空。 |
| `source_id` | 来源标识，对应 `docs/sources.md`。 |
| `source_note` | 来源或口径备注。 |

## 维护约定

- `nids_history.csv` 是维护主表。
- `nids_current.csv` 应等于 `nids_history.csv` 中 `is_current == true` 的记录。
- 统计法定病种数量时，应筛选 `is_notifiable_disease == true`，不要把子项、别名或汇总项计入 42 种法定传染病。
- 子项和别名必须维护 `parent_disease_id`，以便回溯到父级法定病种。
- 对于部分病种存在特殊管理措施的情况，优先在 `management_class` 和 `source_note` 中保留机器可读分类与人工解释。
- `report_name_zh` 和 `raw_match_name_zh` 服务分析/周报匹配，不替代法定名称来源。
- 首版只建立当前目录基线，不声明覆盖 1989 年以来全部历史调整。
