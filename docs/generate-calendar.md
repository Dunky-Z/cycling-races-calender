# ICS 日历生成指南

本文档说明如何使用 PCS MCP 和项目脚本生成 UCI 世界巡回赛 ICS 日历。

## 前置条件

1. 已配置 PCS MCP（见 [README.md](../README.md)）
2. 已安装 Python 依赖：

```bash
pip install -r requirements.txt
pip install git+https://github.com/lewis-mcgillion/procyclingstats-mcp-server.git
```

## 方式一：脚本自动抓取（推荐）

`scripts/fetch_wt_calendar.py` 使用 PCS MCP 服务端同款客户端库，可批量抓取并保存 JSON。

```bash
# 抓取 2026 世巡赛全部赛事
python scripts/fetch_wt_calendar.py --year 2026

# 构建 ICS
python scripts/build_calendar.py --year 2026
```

输出文件：

- `cycling_races_bilingual_2026.ics` — 按年度命名
- `cycling_races_bilingual.ics` — 当前赛季别名（内容与上述相同）

## 方式二：Cursor Agent + MCP 工具

在 Cursor Agent 对话中，可使用以下提示词模板：

```
请使用 PCS MCP 为 {year} 年 UCI 世界巡回赛生成日历数据：

1. 调用 discover_races(year={year}, tiers=["worldtour"]) 获取赛事列表
2. 对每场赛事调用 get_race_overview(race_url="race/{slug}/{year}")
3. 对多日赛的每个赛段调用 get_stage_results(stage_url="...")
4. 将结果汇总写入 data/wt_calendar_{year}.json，格式如下：

{
  "year": {year},
  "tiers": ["worldtour"],
  "races": [
    {
      "url": "race/tour-de-france/{year}",
      "name": "Tour de France",
      "year": {year},
      "uci_tour": "2.UWT",
      "is_one_day_race": false,
      "startdate": "2026-07-04",
      "enddate": "2026-07-26",
      "stages": [...],
      "stage_details": [...]
    }
  ]
}

5. 运行 python scripts/build_calendar.py --year {year}
```

## 环法特殊处理

环法赛段在总日历中使用 `data/tdf2026_enrichment.json` 中的增强数据，而非 PCS 原始赛段。该文件包含：

- 7 月 3 日车队亮相（PCS 赛段列表不含此项）
- 休息日（7 月 13 日、7 月 20 日）
- 每场赛段的路线、类型、当地开赛/完赛时间
- 观骑世界/中国体育直播时间与解说员

更新环法直播信息后：

1. 编辑 `data/tdf2026_enrichment.json`
2. 运行 `python scripts/build_calendar.py --year 2026`
3. 运行 `python scripts/generate_tdf.py --all-day -o TDF2026.ics`

## 赛事名称翻译

PCS 返回的英文名称可能与 `data/race_names.json` 中的 key 不完全一致。在 `scripts/build_calendar.py` 的 `NAME_ALIASES` 字典中添加映射即可，例如：

```python
"Tour Auvergne - Rhône-Alpes": "Critérium du Dauphiné",
"In Flanders Fields": "Gent-Wevelgem in Flanders Fields ME",
```

## 已知限制

- PCS MCP 有请求频率限制，批量抓取需数分钟
- 部分赛前赛段的 `departure/arrival` 可能为空，DESCRIPTION 将为空
- `race/uec-road-european-championships` 目前 PCS 解析可能失败，需手动补充或跳过
- `discover_races` 可能返回重复 slug（如 `la-fleche-wallone` / `la-fleche-wallonne`），构建脚本会自动去重

## 验证

生成后检查：

```bash
# 统计事件数量
grep -c "^BEGIN:VEVENT" cycling_races_bilingual_2026.ics

# 确认环法含直播信息
grep "观骑世界" cycling_races_bilingual_2026.ics | head -3
```

2026 世巡赛日历预期约 170-180 条事件（含多日赛赛段和休息日）。
