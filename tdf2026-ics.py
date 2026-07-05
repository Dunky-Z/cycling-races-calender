#!/usr/bin/env python3
"""Generate 2026 Tour de France ICS compatible with TDF2025.ics format."""

from datetime import datetime
from ics import Calendar, Event
import uuid

# 直播时间来源：观骑世界 / 中国体育 2026环法官方直播日程表
# route 使用英文地名，与 TDF2025.ics 的 DESCRIPTION 格式一致
STAGES = [
    {
        "presentation": True,
        "date": "2026-07-03",
        "route": "Barcelona",
        "broadcast_cn": ("00:30", "02:00"),
        "commentators": "李陶",
    },
    {
        "num": 1,
        "date": "2026-07-04",
        "route": "Barcelona - Barcelona",
        "type": "团队计时",
        "distance": 20,
        "broadcast_cn": ("22:55", "1:45"),
        "commentators": "李陶、计成",
    },
    {
        "num": 2,
        "date": "2026-07-05",
        "route": "Tarragona - Barcelona",
        "type": "丘陵",
        "distance": 169,
        "broadcast_cn": ("19:35", "0:10"),
        "commentators": "李陶、计成",
    },
    {
        "num": 3,
        "date": "2026-07-06",
        "route": "Granollers - Les Angles",
        "type": "山地",
        "distance": 196,
        "broadcast_cn": ("18:00", "23:40"),
        "commentators": "李陶、计成、萧深",
    },
    {
        "num": 4,
        "date": "2026-07-07",
        "route": "Carcassonne - Foix",
        "type": "丘陵",
        "distance": 182,
        "broadcast_cn": ("19:00", "0:05"),
        "commentators": "李陶、计成",
    },
    {
        "num": 5,
        "date": "2026-07-08",
        "route": "Lannemezan - Pau",
        "type": "平路",
        "distance": 158,
        "broadcast_cn": ("19:55", "0:15"),
        "commentators": "李陶、计成",
    },
    {
        "num": 6,
        "date": "2026-07-09",
        "route": "Pau - Gavarnie-Gèdre",
        "type": "山地",
        "distance": 186,
        "broadcast_cn": ("18:15", "0:05"),
        "commentators": "李陶、计成、陈子昊",
    },
    {
        "num": 7,
        "date": "2026-07-10",
        "route": "Hagetmau - Bordeaux",
        "type": "平路",
        "distance": 175,
        "broadcast_cn": ("19:05", "23:55"),
        "commentators": "李陶、陈子昊",
    },
    {
        "num": 8,
        "date": "2026-07-11",
        "route": "Périgueux - Bergerac",
        "type": "平路",
        "distance": 180,
        "broadcast_cn": ("19:00", "0:00"),
        "commentators": "李陶、陈子昊",
    },
    {
        "num": 9,
        "date": "2026-07-12",
        "route": "Malemort - Ussel",
        "type": "丘陵",
        "distance": 186,
        "broadcast_cn": ("19:20", "0:30"),
        "commentators": "李陶、陈子昊",
    },
    {"num": None, "date": "2026-07-13", "rest": True},
    {
        "num": 10,
        "date": "2026-07-14",
        "route": "Aurillac - Le Lioran",
        "type": "山地",
        "distance": 167,
        "broadcast_cn": ("19:00", "0:00"),
        "commentators": "云苏华、陈子昊",
    },
    {
        "num": 11,
        "date": "2026-07-15",
        "route": "Vichy - Nevers",
        "type": "平路",
        "distance": 161,
        "broadcast_cn": ("19:40", "0:10"),
        "commentators": "李陶、云苏华",
    },
    {
        "num": 12,
        "date": "2026-07-16",
        "route": "Magny-Cours - Chalon-sur-Saône",
        "type": "平路",
        "distance": 179,
        "broadcast_cn": ("19:20", "0:15"),
        "commentators": "李陶、云苏华",
    },
    {
        "num": 13,
        "date": "2026-07-17",
        "route": "Dole - Belfort",
        "type": "丘陵",
        "distance": 206,
        "broadcast_cn": ("18:50", "0:30"),
        "commentators": "李陶、云苏华",
    },
    {
        "num": 14,
        "date": "2026-07-18",
        "route": "Mulhouse - Le Markstein",
        "type": "山地",
        "distance": 155,
        "broadcast_cn": ("19:00", "0:05"),
        "commentators": "李陶、云苏华",
    },
    {
        "num": 15,
        "date": "2026-07-19",
        "route": "Champagnole - Plateau de Solaison",
        "type": "山地",
        "distance": 184,
        "broadcast_cn": ("19:00", "0:25"),
        "commentators": "李陶、云苏华",
    },
    {"num": None, "date": "2026-07-20", "rest": True},
    {
        "num": 16,
        "date": "2026-07-21",
        "route": "Evian-les-Bains - Thonon-les-Bains",
        "type": "个人计时",
        "distance": 26,
        "broadcast_cn": ("18:50", "0:20"),
        "commentators": "云苏华、萧深",
    },
    {
        "num": 17,
        "date": "2026-07-22",
        "route": "Chambery - Voiron",
        "type": "平路",
        "distance": 175,
        "broadcast_cn": ("19:10", "0:00"),
        "commentators": "李陶、萧深",
    },
    {
        "num": 18,
        "date": "2026-07-23",
        "route": "Voiron - Orcières-Merlette",
        "type": "山地",
        "distance": 185,
        "broadcast_cn": ("18:20", "0:00"),
        "commentators": "李陶、萧深",
    },
    {
        "num": 19,
        "date": "2026-07-24",
        "route": "Gap - Alpe d'Huez",
        "type": "山地",
        "distance": 128,
        "broadcast_cn": ("19:50", "0:15"),
        "commentators": "李陶、萧深",
    },
    {
        "num": 20,
        "date": "2026-07-25",
        "route": "Le Bourg d'Oisans - Alpe d'Huez",
        "type": "山地",
        "distance": 171,
        "broadcast_cn": ("17:10", "23:00"),
        "commentators": "李陶、萧深",
    },
    {
        "num": 21,
        "date": "2026-07-26",
        "route": "Thoiry - Paris Champs-Élysées",
        "type": "平路",
        "distance": 130,
        "broadcast_cn": ("22:05", "2:25"),
        "commentators": "李陶、萧深",
    },
]


def build_description(stage):
    if stage.get("rest"):
        return "休息日 | 无赛段 | 无解说"
    cn_s, cn_f = stage["broadcast_cn"]
    comm = stage["commentators"]
    time_range = f"{cn_s}-{cn_f}"
    if stage.get("presentation"):
        return f"{stage['route']} | 车队亮相 | 解说员：{comm} | 解说时间：{time_range}"
    route = stage["route"]
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


def make_event(stage):
    event = Event()
    event.name = build_summary(stage)
    event.description = build_description(stage)
    y, m, d = (int(x) for x in stage["date"].split("-"))
    event.begin = datetime(y, m, d)
    event.make_all_day()
    event.uid = str(uuid.uuid4())
    return event


def main():
    calendar = Calendar()
    calendar.creator = "ics.py - http://git.io/lLljaA"

    events = [make_event(stage) for stage in sorted(STAGES, key=lambda s: s["date"])]
    for event in events:
        calendar.events.add(event)

    output = "TDF2026.ics"
    with open(output, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    max_line = max(len(line.rstrip("\r\n")) for line in calendar)
    print(f"Created {output} with {len(events)} events (max line {max_line} chars)")


if __name__ == "__main__":
    main()
