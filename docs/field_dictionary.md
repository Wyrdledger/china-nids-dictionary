# 字段说明

| 字段 | 含义 |
| --- | --- |
| `disease_id` | 本仓库维护的稳定病种 ID，格式为 `NID-A-001`、`NID-B-001`、`NID-C-001`。 |
| `disease_name_zh` | 中文病种名称。 |
| `disease_name_en` | 英文参考名称，仅用于辅助识别。 |
| `legal_class` | 法定分类：`甲类`、`乙类`、`丙类`。 |
| `management_class` | 管理方式，例如 `乙类管理`、`乙类按甲类措施管理`。 |
| `report_time_limit_hours` | 网络直报时限，单位为小时；当前取值为 `2` 或 `24`。 |
| `is_current` | 是否为当前有效记录。 |
| `effective_start_date` | 本记录在本仓库口径中的生效日期，ISO 日期格式。 |
| `effective_end_date` | 本记录失效日期；当前有效记录为空。 |
| `source_id` | 来源标识，对应 `docs/sources.md`。 |
| `source_note` | 来源或口径备注。 |

## 维护约定

- `nids_history.csv` 是维护主表。
- `nids_current.csv` 应等于 `nids_history.csv` 中 `is_current == true` 的记录。
- 对于部分病种存在特殊管理措施的情况，优先在 `management_class` 和 `source_note` 中保留机器可读分类与人工解释。
- 首版只建立当前目录基线，不声明覆盖 1989 年以来全部历史调整。
