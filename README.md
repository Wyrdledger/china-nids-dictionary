<div align="center">

# China NIDs Dictionary

**中国法定传染病 NIDs 统一字典**

面向传染病统计、CISDCP 报表匹配、数据质控和分析项目维护的轻量级 UTF-8 字典。

![CSV + JSON](https://img.shields.io/badge/data-CSV%20%2B%20JSON-2E7D32)
![Python + R](https://img.shields.io/badge/helpers-Python%20%2B%20R-276DC3)
![UTF-8](https://img.shields.io/badge/encoding-UTF--8-4B5563)
![CISDCP](https://img.shields.io/badge/CISDCP-compatible-0078D4)
![No case data](https://img.shields.io/badge/data-no%20case%20data-F59E0B)

[当前基线](#当前基线) · [快速使用](#快速使用) · [字段口径](#字段口径) · [维护规则](#维护规则) · [校验](#校验)

</div>

本仓库只保存公开规则字典、业务映射口径、schema、读取示例和维护记录；不保存个案数据、患者信息、原始报表或任何敏感数据。当前目录基线来自公开法规和公告，旧周报字典仅作为业务映射来源，不作为法定依据来源。

## 当前基线

当前字典包含 83 条当前有效记录，其中 42 条为独立法定传染病：

- 甲类：2 种
- 乙类：29 种
- 丙类：11 种

其余记录为从 `Infection_Weekly` 旧周报字典迁移而来的子项、分型和汇总项。统计法定病种数量时，只使用 `record_type == "notifiable_disease"` 且 `is_notifiable_disease == true` 的记录；不要把子项或 `合计` 计入 42 种法定传染病。

本仓库从 2025 年新版《中华人民共和国传染病防治法》和 2026 年第 3 号国家卫生健康委公告建立当前目录基线，并参考 `Infection_Weekly/config/dictionary.csv` 补充 CISDCP 原始报表匹配名、子项/分型、传播类型和病原学分类。`data/nids_history.csv` 当前是持续维护主表，不是覆盖 1989 年以来所有历史调整的完整回溯表。

## 快速使用

主要数据文件：

```text
data/nids_current.csv      当前有效统一字典
data/nids_current.json     当前有效字典 JSON 镜像
data/nids_history.csv      当前维护主表
schema/nids.schema.json    单行字典记录 schema
docs/field_dictionary.md   字段说明
docs/sources.md            来源与更新依据
```

Python：

```python
from python.nids_dictionary import read_nids_csv

rows = read_nids_csv("data/nids_current.csv")
notifiable_rows = [
    row for row in rows
    if row["record_type"] == "notifiable_disease" and row["is_notifiable_disease"]
]
```

R：

```r
source("R/read_nids_dictionary.R", encoding = "UTF-8")

nids <- read_nids_dictionary("data/nids_current.csv")
notifiable_nids <- nids[
  nids$record_type == "notifiable_disease" & nids$is_notifiable_disease,
]
```

在线读取最新版：

```python
from python.nids_dictionary import read_nids_csv

rows = read_nids_csv()
```

正式分析建议固定到 Git tag URL，避免 `main` 后续维护更新影响复现：

```python
url = "https://raw.githubusercontent.com/Wyrdledger/china-nids-dictionary/v2026.04.01/data/nids_current.csv"
rows = read_nids_csv(url)
```

## 字段口径

核心字段如下；完整说明见 `docs/field_dictionary.md`。

| 字段 | 用途 |
| --- | --- |
| `disease_id` | 本项目维护的稳定 ID。 |
| `record_type` | `notifiable_disease`、`subtype`、`alias` 或 `aggregate`。 |
| `is_notifiable_disease` | 是否计入独立法定传染病数量。 |
| `parent_disease_id` | 子项/分型对应的父级法定病种 ID。 |
| `disease_name_zh` | 对外报告使用的正式中文名称。 |
| `cisdcp_disease_name` | 必须精确匹配 CISDCP 疫情分析报表 `疾病病种` 列。 |
| `disease_name_en` | 以 `disease_name_zh` 为基准维护的专业英文名称。 |
| `legal_class` | 法定分类：甲类、乙类、丙类。 |
| `management_class` | 管理方式：甲类管理、乙类管理、丙类管理。 |
| `report_time_limit_hours` | 网络直报时限，单位为小时。 |
| `transmission_type` | 业务传播类型。 |
| `pathogen_type` | 病原学分类。 |

关键口径：

- `disease_name_zh` 是对外报告名称；`cisdcp_disease_name` 是原始报表匹配名称，两者可以不同。例如 `细菌性和阿米巴痢疾` 对应 CISDCP 中的 `痢疾`。
- `cisdcp_disease_name` 应与 CISDCP 导出的疫情分析报表 `疾病病种` 列完全一致，括号统一使用中文全角 `（`、`）`。
- `disease_name_en` 不做简单直译，应参考医学/流行病学文献、WHO/CDC/China CDC Weekly 等权威英文口径；当前所有 83 条记录均维护英文值。
- `record_type == "aggregate"` 的 `合计` 不是病种，只为对齐 CISDCP 疫情分析报表结构，固定放在最后一行。
- `HIV` 是 `艾滋病` 的 `subtype` 记录；肝炎、禽流感亚型、炭疽分型、痢疾分型、结核分型、梅毒分期和疟疾分型也以 `subtype` 维护。
- `传染性非典型肺炎` 和 `肺炭疽` 的 `management_class` 为 `甲类管理`，网络直报时限均为 2 小时；炭疽父级本身仍为 `乙类管理`、24 小时。
- `pathogen_type` 仅按已确认清单赋值；未明确列入的记录保持空值，不自动从父级继承。

## 维护规则

- `main` 表示最新维护版，适合探索和日常使用；正式分析使用 Git tag URL。
- 目录调整时，先更新 `data/nids_history.csv`，再同步 `data/nids_current.csv` 和 `data/nids_current.json`。
- CSV 与 JSON 字段集合应保持一致；JSON 中空字符串按读取契约转换为 `null`。
- 行顺序固定为：法定传染病在上，子类/分型在下，`合计` 汇总项在最后一行。
- 子项和分型必须维护 `parent_disease_id`，以便回溯到父级法定病种。
- 中文文件统一使用 UTF-8；本项目暂不导出兼容旧周报项目的 GBK `dictionary.csv`。
- 字段迁移关系：`official_name_zh` 和 `report_name_zh` 已合并为 `disease_name_zh`；`raw_match_name_zh` 已更名为 `cisdcp_disease_name`。
- 新增、删除、调整病种时，应同步更新 `docs/sources.md`、`docs/field_dictionary.md`、`changelog/CHANGELOG.md` 和测试。

## 校验

```powershell
python -m unittest discover -s tests
Rscript tests/r_smoke_test.R
git diff --check
```

测试会检查记录数、字段顺序、法定病种计数、父子关系、CISDCP 名称唯一性、中文括号、CSV/JSON 镜像一致性、关键分类口径，以及 Python/R 读取器的类型转换。
