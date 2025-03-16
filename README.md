# UCI 自行车世界巡回赛日历生成器

这是一个自动生成 UCI 世界巡回赛赛程日历的工具。它可以抓取 ProCyclingStats 网站的赛事信息，并生成可导入到各类日历应用的 ICS 文件。

## 功能特点

- 自动抓取 UCI 世界巡回赛赛事信息
- 支持生成双语（中英文）或纯英文赛事名称
- 多日赛事会显示每个赛段
- 生成标准 ICS 格式日历文件

## 使用方法

### 安装依赖

```bash
pip install requests beautifulsoup4 ics httpx fake-useragent
```

### 运行程序

生成双语版本（默认）：
```bash
python cycling-ics.py
```

生成纯英文版本：
```bash
python cycling-ics.py --lang en
```

### 输出文件

- 双语版本：`cycling_races_bilingual.ics`
- 英文版本：`cycling_races_en.ics`

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
