# China NIDs Dictionary

中国法定传染病 NIDs 字典，面向后续传染病统计、数据质控和分析项目维护。项目只保存公开规则字典，不保存个案数据、患者信息或任何敏感数据。

## 当前基线

首版当前字典包含 42 种法定传染病：

- 甲类：2 种
- 乙类：29 种
- 丙类：11 种

本仓库从 2025 年新版《中华人民共和国传染病防治法》和 2026 年第 3 号国家卫生健康委公告建立当前目录基线。`data/nids_history.csv` 不是完整历史回溯表；它是从首版开始用于持续维护历史口径的主表。

## 文件结构

```text
data/
  nids_current.csv      当前有效字典
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
- 每条记录必须保留来源字段和生效日期。
- 中文文件统一使用 UTF-8。

## 校验

```powershell
python -m unittest discover -s tests
Rscript tests/r_smoke_test.R
```
