# China NIDs Dictionary

中国法定传染病 NIDs 字典，面向后续传染病统计、数据质控和分析项目维护。项目只保存公开规则字典和业务映射口径，不保存个案数据、患者信息或任何敏感数据。

## 当前基线

当前字典包含 83 条当前有效记录，其中 42 条为独立法定传染病：

- 甲类：2 种
- 乙类：29 种
- 丙类：11 种

其余记录为旧周报字典迁移而来的子项、分型、别名和汇总项。统计法定病种数量时，应筛选 `is_notifiable_disease == true`。

本仓库从 2025 年新版《中华人民共和国传染病防治法》和 2026 年第 3 号国家卫生健康委公告建立当前目录基线，并参考 `Infection_Weekly` 旧周报字典补充 CISDCP 原始报表匹配名和传播类型。`data/nids_history.csv` 不是完整历史回溯表；它是从首版开始用于持续维护历史口径的主表。

## 文件结构

```text
data/
  nids_current.csv      当前有效统一字典
  nids_current.json     当前有效字典 JSON 镜像
  nids_history.csv      带生效/失效日期的维护主表
schema/
  nids.schema.json      单行字典记录的字段 schema
R/
  read_nids_dictionary.R
python/
  nids_dictionary.py
docs/
  field_dictionary.md
  sources.md
tests/
  test_dictionary.py
  r_smoke_test.R
```

## Python 调用

```python
from python.nids_dictionary import read_nids_csv

rows = read_nids_csv("data/nids_current.csv")
notifiable_rows = [row for row in rows if row["is_notifiable_disease"]]
```

在线读取最新版：

```python
from python.nids_dictionary import read_nids_csv

rows = read_nids_csv()
```

正式分析建议固定版本：

```python
url = "https://raw.githubusercontent.com/Wyrdledger/china-nids-dictionary/v2026.04.01/data/nids_current.csv"
rows = read_nids_csv(url)
```

## R 调用

```r
source("R/read_nids_dictionary.R", encoding = "UTF-8")

nids <- read_nids_dictionary("data/nids_current.csv")
notifiable_nids <- nids[nids$is_notifiable_disease, ]
```

在线读取最新版：

```r
source("R/read_nids_dictionary.R", encoding = "UTF-8")

nids <- read_nids_dictionary()
```

正式分析建议固定版本：

```r
source("R/read_nids_dictionary.R", encoding = "UTF-8")

url <- "https://raw.githubusercontent.com/Wyrdledger/china-nids-dictionary/v2026.04.01/data/nids_current.csv"
nids <- read_nids_dictionary(url)
```

## 维护规则

- `main` 表示最新维护版，适合探索和日常使用。
- 正式分析使用 Git tag URL，例如 `v2026.04.01`。
- 目录调整时，先更新 `data/nids_history.csv`，再同步 `nids_current.csv` 和 `nids_current.json`。
- 行顺序固定为：法定传染病在上，子类/分型在下，`合计` 汇总项在最后一行。
- 只有 `record_type == "notifiable_disease"` 且 `is_notifiable_disease == true` 的记录计入法定传染病目录。
- 子项和分型必须维护 `parent_disease_id`。
- `record_type == "aggregate"` 的 `合计` 不是病种，只为与 CISDCP 疫情分析报表结构对应，固定放在最后一行。
- `disease_name_zh` 是对外报告使用的正式中文名称。
- `cisdcp_disease_name` 必须能精确匹配 CISDCP 导出的疫情分析报表 `疾病病种` 列。
- `transmission_type` 当前包含 `呼吸道传染病`、`肠道传染病`、`动物源性及虫媒传染病`、`经血与性传播传染病`、`其他` 和空值。
- `pathogen_type` 当前包含 `细菌性疾病`、`病毒性疾病`、`寄生虫病性疾病` 和空值；未明确列入病原学清单的记录保持空值。
- 当前 `传染性非典型肺炎` 和 `肺炭疽` 的 `management_class` 记为 `甲类管理`，网络直报时限均为 2 小时。
- 中文疾病名称字段统一使用中文全角括号 `（`、`）`，不得使用英文半角括号 `(`、`)`。
- 字段迁移：`official_name_zh` 和 `report_name_zh` 已合并为 `disease_name_zh`；`raw_match_name_zh` 已更名为 `cisdcp_disease_name`。
- 中文文件统一使用 UTF-8。

## 校验

```powershell
python -m unittest discover -s tests
Rscript tests/r_smoke_test.R
```
