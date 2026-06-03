# 字段说明

| 字段 | 含义 |
| --- | --- |
| `disease_id` | 本仓库维护的稳定病种 ID，格式为 `NID-A-001`、`NID-B-001`、`NID-C-001`。 |
| `record_type` | 记录类型：`notifiable_disease` 法定病种、`subtype` 子项/分型、`alias` 别名、`aggregate` 汇总项。 |
| `is_notifiable_disease` | 是否为独立法定传染病。当前 42 个法定病种为 `true`，旧周报子项/汇总项为 `false`。 |
| `parent_disease_id` | 子项对应的父级法定病种 ID；法定病种和汇总项为空。 |
| `disease_name_zh` | 对外报告使用的正式中文名称。法定病种参考法定传染病报告展示口径，子项/别名/汇总项为对应报告名称。 |
| `cisdcp_disease_name` | CISDCP 导出的疫情分析报表中 `疾病病种` 列的精确匹配名称。 |
| `disease_name_en` | 英文参考名称，仅用于辅助识别；子项、别名和汇总项可为空。 |
| `legal_class` | 法定分类：`甲类`、`乙类`、`丙类`；汇总项为空。 |
| `management_class` | 管理方式，例如 `甲类管理`、`乙类管理`、`丙类管理`；汇总项为空。 |
| `report_time_limit_hours` | 网络直报时限，单位为小时；当前取值为 `2`、`24` 或空值。 |
| `transmission_type` | 业务传播类型；当前取值为 `呼吸道传染病`、`肠道传染病`、`动物源性及虫媒传染病`、`经血与性传播传染病`、`其他` 或空值。 |
| `pathogen_type` | 病原学分类；当前取值为 `细菌性疾病`、`病毒性疾病`、`寄生虫病性疾病` 或空值。 |

## 维护约定

- `nids_history.csv` 是维护主表。
- `nids_current.csv` 当前应与 `nids_history.csv` 保持一致；后续如需恢复历史沿革，再另行设计版本字段。
- 行顺序固定为：法定传染病在上，子类/分型在下，`合计` 汇总项在最后一行。
- 统计法定病种数量时，应筛选 `is_notifiable_disease == true`，不要把子项、别名或汇总项计入 42 种法定传染病。
- `record_type == "aggregate"` 的 `合计` 不是病种，只为与 CISDCP 疫情分析报表结构对应，固定放在最后一行。
- 子项必须维护 `parent_disease_id`，以便回溯到父级法定病种。
- 对于部分病种存在特殊管理措施的情况，优先在 `management_class` 中保留机器可读分类。
- 当前 `传染性非典型肺炎` 和 `肺炭疽` 的 `management_class` 记为 `甲类管理`，网络直报时限均为 2 小时。
- `cisdcp_disease_name` 必须能精确匹配 CISDCP 疫情分析报表中的 `疾病病种`。
- 中文疾病名称字段统一使用中文全角括号 `（`、`）`，不得使用英文半角括号 `(`、`)`。
- 字段迁移：`official_name_zh` 和 `report_name_zh` 已合并为 `disease_name_zh`；`raw_match_name_zh` 已更名为 `cisdcp_disease_name`。
- 首版只建立当前目录基线，不声明覆盖 1989 年以来全部历史调整。
