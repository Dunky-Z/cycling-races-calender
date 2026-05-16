# UCI 自行车世界巡回赛日历生成器

这是一个自动生成 UCI 世界巡回赛赛程日历的工具。它可以抓取 ProCyclingStats 网站的赛事信息，并生成可导入到各类日历应用的 ICS 文件。

## 功能特点

- 自动抓取 UCI 世界巡回赛赛事信息
- 支持生成双语（中英文）或纯英文赛事名称
- 多日赛事会显示每个赛段
- 生成标准 ICS 格式日历文件

## 订阅方式

### 双语版本（中英文）

```txt
https://cdn.jsdelivr.net/gh/Dunky-Z/cycling-races-calender/cycling_races_bilingual.ics
```
![](https://picbed-1311007548.cos.ap-shanghai.myqcloud.com/markdown_picbed/img//2025/03/18/4a562d1f43c5a26a085adbe2b62b9cca.png)

### 英文版本

```txt
https://cdn.jsdelivr.net/gh/Dunky-Z/cycling-races-calender/cycling_races.ics
```

![](https://picbed-1311007548.cos.ap-shanghai.myqcloud.com/markdown_picbed/img//2025/03/18/2117ecc36be5c31f681f68487d05f35a.png)


## 使用方法

### 安装依赖

```bash
pip install requests beautifulsoup4 ics httpx fake-useragent
```

### 运行程序

生成当前赛季双语版本（默认）：
```bash
python cycling-races-ics.py
```

指定赛季年度（例如 2025）：
```bash
python cycling-races-ics.py --year 2025
```

生成纯英文版本：
```bash
python cycling-races-ics.py --lang en
```

同时指定年度与语言：
```bash
python cycling-races-ics.py --year 2025 --lang en
```

导出该年度全部赛事（含已结束）：
```bash
python cycling-races-ics.py --year 2025 --all-races
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--year` | UCI 世界巡回赛赛季年度 | 当前年份 |
| `--lang` | 赛事名称语言：`bilingual`（中英文）或 `en`（仅英文） | `bilingual` |
| `--all-races` | 包含已结束赛事；默认仅导出尚未结束的赛事 | 否 |

### 输出文件

输出文件名包含赛季年度，例如：

- 双语版本：`cycling_races_bilingual_2025.ics`
- 英文版本：`cycling_races_en_2025.ics`

## 日历导入方法

生成的 ICS 文件可以导入到以下应用：

- Google Calendar
- Apple Calendar
- Microsoft Outlook
- 其他支持 ICS 格式的日历应用

## 赛事翻译维护

赛事的中英文对照存储在 `race_names.json` 文件中，本人只是骑行爱好者，对赛事名并不熟悉，如果翻译有误，欢迎提交PR修改。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 免责声明

本项目仅供学习交流使用，赛事数据来源于 ProCyclingStats 网站。请遵守相关网站的使用条款。
