# 2026-06-03-02 参考旧周报字典扩展 NIDs 字典

## 目标

将 `Infection_Weekly/config/dictionary.csv` 中历史人工整理的疾病名称映射、子项/分型、别名、汇总项和传播类型迁移到本项目，形成可长期维护的统一字典。

## 实施口径

- 保留 42 个法定病种的既有 `disease_id`。
- 新增 `record_type`、`is_notifiable_disease`、`parent_disease_id`、`cisdcp_disease_name` 和 `transmission_type`。
- `disease_name_zh` 表示对外报告使用的正式中文名称。
- `cisdcp_disease_name` 精确对应 CISDCP 疫情分析报表中的 `疾病病种` 列。
- 字段迁移：`official_name_zh` 和 `report_name_zh` 已合并为 `disease_name_zh`；`raw_match_name_zh` 已更名为 `cisdcp_disease_name`。
- 旧周报 `tier=N` 记录进入主表，标记为 `subtype`、`alias` 或 `aggregate`。
- 法定病种名称、分类和管理方式仍以法律公告来源为准；旧周报字典仅作为业务映射来源。
- 本轮不改 `Infection_Weekly`，不生成 GBK 兼容导出文件。

## 验证

- Python unittest 校验 83 条当前记录、42 条法定病种、父子关系、JSON 镜像和旧周报 83 条映射迁移。
- R smoke test 校验新增字段读取、布尔类型和聚合项空时限。
