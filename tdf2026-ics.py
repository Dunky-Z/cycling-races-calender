#!/usr/bin/env python3
"""Generate 2026 Tour de France ICS compatible with TDF2025.ics format."""

# 直播时间来源：观骑世界 / 中国体育 2026环法官方直播日程表
STAGES = [
    {
        "presentation": True,
        "date": "2026-07-03",
        "route_cn": "巴塞罗那",
        "broadcast_cn": ("00:30", "02:00"),
        "commentators": "李陶",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607030001",
    },
    {
        "num": 1,
        "date": "2026-07-04",
        "route_cn": "巴塞罗那 - 巴塞罗那",
        "type": "团队计时",
        "distance": 20,
        "broadcast_cn": ("22:55", "1:45"),
        "commentators": "李陶、计成",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607040001",
    },
    {
        "num": 2,
        "date": "2026-07-05",
        "route_cn": "塔拉戈纳 - 巴塞罗那",
        "type": "丘陵",
        "distance": 169,
        "broadcast_cn": ("19:35", "0:10"),
        "commentators": "李陶、计成",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607050002",
    },
    {
        "num": 3,
        "date": "2026-07-06",
        "route_cn": "格拉诺列尔斯 - 莱桑格",
        "type": "山地",
        "distance": 196,
        "broadcast_cn": ("18:00", "23:40"),
        "commentators": "李陶、计成、萧深",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607060003",
    },
    {
        "num": 4,
        "date": "2026-07-07",
        "route_cn": "卡尔卡松 - 福瓦",
        "type": "丘陵",
        "distance": 182,
        "broadcast_cn": ("19:00", "0:05"),
        "commentators": "李陶、计成",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607070004",
    },
    {
        "num": 5,
        "date": "2026-07-08",
        "route_cn": "拉内默藏 - 波城",
        "type": "平路",
        "distance": 158,
        "broadcast_cn": ("19:55", "0:15"),
        "commentators": "李陶、计成",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607080005",
    },
    {
        "num": 6,
        "date": "2026-07-06",
        "route_cn": "波城 - 加瓦尔尼-热德尔",
        "type": "山地",
        "distance": 186,
        "broadcast_cn": ("18:15", "0:05"),
        "commentators": "李陶、计成、陈子昊",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607090006",
    },
    {
        "num": 7,
        "date": "2026-07-10",
        "route_cn": "阿热莫 - 波尔多",
        "type": "平路",
        "distance": 175,
        "broadcast_cn": ("19:05", "23:55"),
        "commentators": "李陶、陈子昊",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607100007",
    },
    {
        "num": 8,
        "date": "2026-07-11",
        "route_cn": "佩里格 - 贝尔热拉克",
        "type": "平路",
        "distance": 180,
        "broadcast_cn": ("19:00", "0:00"),
        "commentators": "李陶、陈子昊",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607110008",
    },
    {
        "num": 9,
        "date": "2026-07-12",
        "route_cn": "马勒莫尔 - 于塞尔",
        "type": "丘陵",
        "distance": 186,
        "broadcast_cn": ("19:20", "0:30"),
        "commentators": "李陶、陈子昊",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607120009",
    },
    {"num": None, "date": "2026-07-13", "rest": True, "uid": "a1b2c3d4-e5f6-4789-a012-202607130000"},
    {
        "num": 10,
        "date": "2026-07-14",
        "route_cn": "欧里亚克 - 勒里奥兰",
        "type": "山地",
        "distance": 167,
        "broadcast_cn": ("19:00", "0:00"),
        "commentators": "云苏华、陈子昊",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607140010",
    },
    {
        "num": 11,
        "date": "2026-07-15",
        "route_cn": "维希 - 讷韦尔",
        "type": "平路",
        "distance": 161,
        "broadcast_cn": ("19:40", "0:10"),
        "commentators": "李陶、云苏华",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607150011",
    },
    {
        "num": 12,
        "date": "2026-07-16",
        "route_cn": "马尼库尔赛道 - 索恩河畔沙隆",
        "type": "平路",
        "distance": 179,
        "broadcast_cn": ("19:20", "0:15"),
        "commentators": "李陶、云苏华",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607160012",
    },
    {
        "num": 13,
        "date": "2026-07-17",
        "route_cn": "多勒 - 贝尔福",
        "type": "丘陵",
        "distance": 206,
        "broadcast_cn": ("18:50", "0:30"),
        "commentators": "李陶、云苏华",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607170013",
    },
    {
        "num": 14,
        "date": "2026-07-18",
        "route_cn": "米卢斯 - 勒马克斯坦",
        "type": "山地",
        "distance": 155,
        "broadcast_cn": ("19:00", "0:05"),
        "commentators": "李陶、云苏华",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607180014",
    },
    {
        "num": 15,
        "date": "2026-07-19",
        "route_cn": "尚帕尼奥勒 - 索莱松高原",
        "type": "山地",
        "distance": 184,
        "broadcast_cn": ("19:00", "0:25"),
        "commentators": "李陶、云苏华",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607190015",
    },
    {"num": None, "date": "2026-07-20", "rest": True, "uid": "a1b2c3d4-e5f6-4789-a012-202607200000"},
    {
        "num": 16,
        "date": "2026-07-21",
        "route_cn": "埃维昂莱班 - 托农莱班",
        "type": "个人计时",
        "distance": 26,
        "broadcast_cn": ("18:50", "0:20"),
        "commentators": "云苏华、萧深",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607210016",
    },
    {
        "num": 17,
        "date": "2026-07-22",
        "route_cn": "尚贝里 - 瓦龙",
        "type": "平路",
        "distance": 175,
        "broadcast_cn": ("19:10", "0:00"),
        "commentators": "李陶、萧深",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607220017",
    },
    {
        "num": 18,
        "date": "2026-07-23",
        "route_cn": "瓦龙 - 奥尔西耶尔-梅莱特",
        "type": "山地",
        "distance": 185,
        "broadcast_cn": ("18:20", "0:00"),
        "commentators": "李陶、萧深",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607230018",
    },
    {
        "num": 19,
        "date": "2026-07-24",
        "route_cn": "加普 - 阿尔普迪埃",
        "type": "山地",
        "distance": 128,
        "broadcast_cn": ("19:50", "0:15"),
        "commentators": "李陶、萧深",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607240019",
    },
    {
        "num": 20,
        "date": "2026-07-25",
        "route_cn": "勒布尔杜瓦桑 - 阿尔普迪埃",
        "type": "山地",
        "distance": 171,
        "broadcast_cn": ("17:10", "23:00"),
        "commentators": "李陶、萧深",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607250020",
    },
    {
        "num": 21,
        "date": "2026-07-26",
        "route_cn": "图瓦里 - 巴黎香榭丽舍大街",
        "type": "平路",
        "distance": 130,
        "broadcast_cn": ("22:05", "2:25"),
        "commentators": "李陶、萧深",
        "uid": "a1b2c3d4-e5f6-4789-a012-202607260021",
    },
]

# Fix stage 6 date typo
for s in STAGES:
    if s.get("num") == 6:
        s["date"] = "2026-07-09"


def to_ics_date(date_str):
    return date_str.replace("-", "")


def build_description(stage):
    if stage.get("rest"):
        return "休息日 | 无赛段 | 无解说"
    cn_s, cn_f = stage["broadcast_cn"]
    comm = stage["commentators"]
    time_range = f"{cn_s}-{cn_f}"
    if stage.get("presentation"):
        return f"{stage['route_cn']} | 车队亮相 | 解说员：{comm} | 解说时间：{time_range}"
    route = stage["route_cn"]
    stype = stage["type"]
    dist = stage["distance"]
    return f"{route} | {stype}({dist}KM) | 解说员：{comm} | 解说时间：{time_range}"


def build_summary(stage):
    if stage.get("presentation"):
        return "环法自行车赛 Tour de France (2.UWT) - 车队亮相"
    if stage.get("rest"):
        return "环法自行车赛 Tour de France (2.UWT) - 休息日 Rest Day"
    num = stage["num"]
    if stage["type"] == "团队计时":
        return f"环法自行车赛 Tour de France (2.UWT) - Stage {num} (TTT)"
    if stage["type"] == "个人计时":
        return f"环法自行车赛 Tour de France (2.UWT) - Stage {num} (ITT)"
    return f"环法自行车赛 Tour de France (2.UWT) - Stage {num}"


def format_event(stage):
    lines = [
        "BEGIN:VEVENT",
        f"DTSTART;VALUE=DATE:{to_ics_date(stage['date'])}",
        f"DESCRIPTION:{build_description(stage)}",
        f"SUMMARY:{build_summary(stage)}",
        f"UID:{stage['uid']}",
        "END:VEVENT",
    ]
    return lines


def main():
    sorted_stages = sorted(STAGES, key=lambda s: s["date"])
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:ics.py - http://git.io/lLljaA",
    ]
    for stage in sorted_stages:
        lines.extend(format_event(stage))
    lines.append("END:VCALENDAR")

    output = "TDF2026.ics"
    content = "\r\n".join(lines) + "\r\n"
    with open(output, "w", encoding="utf-8", newline="") as f:
        f.write(content)

    max_line = max(len(line) for line in lines)
    print(f"Created {output} with {len(sorted_stages)} events (max line {max_line} chars)")


if __name__ == "__main__":
    main()
