# UCI 自行车世界巡回赛 ICS 日历

UCI 世界巡回赛赛程 ICS 日历存储库。数据通过 [ProCyclingStats MCP Server](https://github.com/lewis-mcgillion/procyclingstats-mcp-server) 获取，定期更新后发布，用户可通过 jsDelivr CDN 订阅。

## 日历订阅

### 双语版本（中英文，当前赛季）

```txt
https://cdn.jsdelivr.net/gh/Dunky-Z/cycling-races-calender/cycling_races_bilingual.ics
```

### 按赛季年度

```txt
https://cdn.jsdelivr.net/gh/Dunky-Z/cycling-races-calender/cycling_races_bilingual_2026.ics
```

### 2026 环法（含中国直播时间与解说员信息）

```txt
https://cdn.jsdelivr.net/gh/Dunky-Z/cycling-races-calender/TDF2026.ics
```

订阅方法：在 Google Calendar、Apple Calendar、Outlook 等应用中选择「通过 URL 添加日历」或「订阅日历」，粘贴上述链接即可。

## 项目结构

```
cycling-ics/
├── cycling_races_bilingual.ics          # 当前赛季别名
├── cycling_races_bilingual_2026.ics     # 2026 世巡赛双语日历
├── TDF2026.ics                          # 2026 环法独立日历
├── data/
│   ├── race_names.json                  # 赛事中英文对照
│   ├── tdf2026_enrichment.json          # 环法中国直播/解说增强数据
│   └── wt_calendar_2026.json            # MCP 抓取的原始赛事数据
├── scripts/
│   ├── fetch_wt_calendar.py             # 从 PCS 抓取赛事数据
│   ├── build_calendar.py                # 构建世巡赛 ICS
│   └── generate_tdf.py                  # 生成环法 ICS
└── docs/
    └── generate-calendar.md             # 详细生成指南
```

## 部署 PCS MCP

本项目使用 [procyclingstats-mcp-server](https://github.com/lewis-mcgillion/procyclingstats-mcp-server) 获取赛事数据。在 Cursor 中配置 MCP 后，可直接在 Agent 对话中调用 PCS 工具。

### 1. 创建配置文件

将以下内容保存为项目根目录下的 `.cursor/mcp.json`（也可参考 `.cursor/mcp.json.example`）：

```json
{
  "mcpServers": {
    "procyclingstats": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/lewis-mcgillion/procyclingstats-mcp-server.git",
        "procyclingstats-mcp"
      ]
    }
  }
}
```

### 2. 重启 Cursor

保存配置后重启 Cursor，在 **Settings > Tools & MCP** 中确认 `procyclingstats` 显示绿色已连接。

### 3. 可用 MCP 工具

| 工具 | 用途 |
|------|------|
| `discover_races` | 按年份和级别发现赛事列表 |
| `get_race_overview` | 获取赛事元数据和赛段列表 |
| `get_stage_results` | 获取赛段路线和结果详情 |
| `search_pcs` | 搜索车手、赛事、车队 |

## 生成 ICS 日历

### 安装依赖

```bash
pip install -r requirements.txt
pip install git+https://github.com/lewis-mcgillion/procyclingstats-mcp-server.git
```

### 快速流程

```bash
# 1. 抓取指定年份世巡赛数据（写入 data/wt_calendar_{year}.json）
python scripts/fetch_wt_calendar.py --year 2026

# 2. 构建双语 ICS 日历
python scripts/build_calendar.py --year 2026

# 3. 单独生成环法日历（全天事件，含中国直播信息）
python scripts/generate_tdf.py --all-day -o TDF2026.ics
```

详细步骤与 Agent 提示词模板见 [docs/generate-calendar.md](docs/generate-calendar.md)。

### 环法增强数据

2026 环法赛段包含观骑世界/中国体育直播时间与解说员信息，数据维护在 `data/tdf2026_enrichment.json`。更新直播日程后修改此文件，重新运行 `build_calendar.py` 即可同步到总日历。

## 赛事翻译维护

赛事中英文对照存储在 [data/race_names.json](data/race_names.json)。PCS 返回的赛事名称可能与历史版本略有差异，可在 `scripts/build_calendar.py` 的 `NAME_ALIASES` 中添加别名映射。翻译有误欢迎提交 PR。

## 许可证

MIT License

## 免责声明

本项目仅供学习交流使用，赛事数据来源于 [ProCyclingStats](https://www.procyclingstats.com)。请遵守相关网站的使用条款。
