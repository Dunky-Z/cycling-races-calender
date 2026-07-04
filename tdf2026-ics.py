#!/usr/bin/env python3
"""Generate 2026 Tour de France ICS with race and Guanqi Shijie broadcast info."""

from datetime import datetime, timedelta
from ics import Calendar, Event
import uuid

STAGES = [
    {
        "num": 1,
        "date": "2026-07-04",
        "route": "Barcelona - Barcelona",
        "route_cn": "巴塞罗那 - 巴塞罗那",
        "type": "团队计时赛(TTT)",
        "distance": 19.6,
        "elevation": 220,
        "cest_start": (17, 5),
        "cest_finish": (19, 16),
        "broadcast_cn": ("23:00", "1:15"),
        "commentators": "李陶、萧深",
        "brief": "巴塞罗那傍晚发车的团队计时赛，末段含蒙特惠奇爬坡与奥林匹克馆上坡冲刺，获胜者穿上黄衫。",
    },
    {
        "num": 2,
        "date": "2026-07-05",
        "route": "Tarragona - Barcelona",
        "route_cn": "塔拉戈纳 - 巴塞罗那",
        "type": "丘陵",
        "distance": 168.5,
        "elevation": 2049,
        "cest_start": (13, 45),
        "cest_finish": (17, 26),
        "broadcast_cn": ("19:40", "23:55"),
        "commentators": "李陶、萧深",
        "brief": "沿海转内陆，终点巴塞罗那绕圈含蒙特惠奇(1.6km@9.3%)上坡冲刺，波加查或在此发动进攻。",
    },
    {
        "num": 3,
        "date": "2026-07-06",
        "route": "Granollers - Les Angles",
        "route_cn": "格拉诺列尔斯 - 莱桑格",
        "type": "山地",
        "distance": 195.9,
        "elevation": 3940,
        "cest_start": (12, 10),
        "cest_finish": (16, 54),
        "broadcast_cn": ("18:05", "23:25"),
        "commentators": "李陶、陈子昊",
        "brief": "首段真正山地赛，深入比利牛斯，一级爬坡距终点70km，适合远程进攻或突围争单站。",
    },
    {
        "num": 4,
        "date": "2026-07-07",
        "route": "Carcassonne - Foix",
        "route_cn": "卡尔卡松 - 福瓦",
        "type": "丘陵",
        "distance": 181.9,
        "elevation": 2784,
        "cest_start": (13, 10),
        "cest_finish": (17, 23),
        "broadcast_cn": ("19:05", "0:00"),
        "commentators": "李陶、陈子昊",
        "brief": "四个爬坡集中在赛段中段，最后35km起伏不大，突围车手有望争胜。",
    },
    {
        "num": 5,
        "date": "2026-07-08",
        "route": "Lannemezan - Pau",
        "route_cn": "拉内默藏 - 波城",
        "type": "平路",
        "distance": 158.3,
        "elevation": 1395,
        "cest_start": (14, 5),
        "cest_finish": (17, 37),
        "broadcast_cn": ("20:00", "0:10"),
        "commentators": "李陶、陈子昊",
        "brief": "今年首个平路冲刺赛段，冲刺积分最高70分，波城是环法到访次数最多的非巴黎城市。",
    },
    {
        "num": 6,
        "date": "2026-07-09",
        "route": "Pau - Gavarnie-Gèdre",
        "route_cn": "波城 - 加瓦尔尼-热德尔",
        "type": "山地",
        "distance": 186.2,
        "elevation": 4149,
        "cest_start": (12, 25),
        "cest_finish": (17, 29),
        "broadcast_cn": ("18:20", "0:00"),
        "commentators": "李陶、计成",
        "brief": "比利牛斯收官战，阿斯潘+图尔马莱组合，山顶终点加瓦尔尼，第一周最关键赛段之一。",
    },
    {
        "num": 7,
        "date": "2026-07-10",
        "route": "Hagetmau - Bordeaux",
        "route_cn": "阿热莫 - 波尔多",
        "type": "平路",
        "distance": 175.1,
        "elevation": 701,
        "cest_start": (13, 15),
        "cest_finish": (17, 13),
        "broadcast_cn": ("19:10", "23:45"),
        "commentators": "李陶、陈子昊",
        "brief": "较平坦的平路赛段，冲刺积分70分，终点拱门后有三个直角弯考验冲刺火车。",
    },
    {
        "num": 8,
        "date": "2026-07-11",
        "route": "Périgueux - Bergerac",
        "route_cn": "佩里格 - 贝尔热拉克",
        "type": "平路",
        "distance": 180.4,
        "elevation": 1353,
        "cest_start": (13, 15),
        "cest_finish": (17, 20),
        "broadcast_cn": ("19:10", "23:50"),
        "commentators": "李陶、陈子昊",
        "brief": "周末冲刺机会，终点设置复杂含急弯与转盘，对冲刺车队卡位要求很高。",
    },
    {
        "num": 9,
        "date": "2026-07-12",
        "route": "Malemort - Ussel",
        "route_cn": "马勒莫尔 - 于塞尔",
        "type": "丘陵",
        "distance": 185.5,
        "elevation": 3244,
        "cest_start": (13, 35),
        "cest_finish": (17, 47),
        "broadcast_cn": ("19:30", "0:15"),
        "commentators": "李陶、陈子昊",
        "brief": "起伏不断的突围日，开局即爬坡，乡村窄路适合兔子，之后迎来第一个休息日。",
    },
    {
        "num": None,
        "date": "2026-07-13",
        "rest": True,
    },
    {
        "num": 10,
        "date": "2026-07-14",
        "route": "Aurillac - Le Lioran",
        "route_cn": "欧里亚克 - 勒里奥兰",
        "type": "山地",
        "distance": 166.6,
        "elevation": 3791,
        "cest_start": (13, 10),
        "cest_finish": (17, 12),
        "broadcast_cn": ("19:05", "23:45"),
        "commentators": "李陶、陈子昊",
        "brief": "法国国庆日山地赛，后半程连续爬坡佩罗尔与佩尔蒂，2024年波加查与温格高在此激战。",
    },
    {
        "num": 11,
        "date": "2026-07-15",
        "route": "Vichy - Nevers",
        "route_cn": "维希 - 讷韦尔",
        "type": "平路",
        "distance": 161.3,
        "elevation": 1107,
        "cest_start": (13, 50),
        "cest_finish": (17, 31),
        "broadcast_cn": ("19:45", "0:00"),
        "commentators": "萧深、计成",
        "brief": "理论平路冲刺日，侧风强时可能变成陷阱赛段，冲刺积分70分。",
    },
    {
        "num": 12,
        "date": "2026-07-16",
        "route": "Magny-Cours - Chalon-sur-Saône",
        "route_cn": "马尼库尔赛道 - 索恩河畔沙隆",
        "type": "平路",
        "distance": 179.1,
        "elevation": 1412,
        "cest_start": (13, 30),
        "cest_finish": (17, 29),
        "broadcast_cn": ("19:25", "0:00"),
        "commentators": "李陶、计成",
        "brief": "从F1马尼库尔赛道发车，纯冲刺车手在艰难赛段到来前的最后机会，冲刺积分70分。",
    },
    {
        "num": 13,
        "date": "2026-07-17",
        "route": "Dole - Belfort",
        "route_cn": "多勒 - 贝尔福",
        "type": "丘陵",
        "distance": 205.8,
        "elevation": 2309,
        "cest_start": (13, 0),
        "cest_finish": (17, 46),
        "broadcast_cn": ("18:55", "0:15"),
        "commentators": "李陶、计成",
        "brief": "全年最长赛段205.8km，途经环法首座大山阿尔萨斯气球山，突围争胜日。",
    },
    {
        "num": 14,
        "date": "2026-07-18",
        "route": "Mulhouse - Le Markstein",
        "route_cn": "米卢斯 - 勒马克斯坦",
        "type": "山地",
        "distance": 155.3,
        "elevation": 3941,
        "cest_start": (13, 10),
        "cest_finish": (17, 24),
        "broadcast_cn": ("19:05", "23:55"),
        "commentators": "李陶、计成、云苏华",
        "brief": "孚日山区大战，全新哈格山口路线狭窄陡峭，坡顶距终点仅6km。",
    },
    {
        "num": 15,
        "date": "2026-07-19",
        "route": "Champagnole - Plateau de Solaison",
        "route_cn": "尚帕尼奥勒 - 索莱松高原",
        "type": "山地",
        "distance": 183.9,
        "elevation": 4098,
        "cest_start": (13, 20),
        "cest_finish": (17, 18),
        "broadcast_cn": ("19:15", "23:50"),
        "commentators": "李陶、云苏华",
        "brief": "首个HC级山顶终点，索莱松高原11.3km@9%，萨莱夫山前置爬坡同样凶险。",
    },
    {
        "num": None,
        "date": "2026-07-20",
        "rest": True,
    },
    {
        "num": 16,
        "date": "2026-07-21",
        "route": "Évian-les-Bains - Thonon-les-Bains",
        "route_cn": "埃维昂莱班 - 托农莱班",
        "type": "个人计时赛(ITT)",
        "distance": 26.1,
        "elevation": 470,
        "cest_start": (13, 0),
        "cest_finish": (17, 50),
        "broadcast_cn": ("18:55", "0:25"),
        "commentators": "李陶、计成",
        "brief": "沿日内瓦湖26.1km计时赛，含缓坡、技术性下坡与急弯，GC格局关键转折点。",
    },
    {
        "num": 17,
        "date": "2026-07-17",
        "route": "Chambéry - Voiron",
        "route_cn": "尚贝里 - 瓦龙",
        "type": "平路",
        "distance": 174.7,
        "elevation": 2362,
        "cest_start": (13, 20),
        "cest_finish": (17, 18),
        "broadcast_cn": ("19:15", "23:50"),
        "commentators": "李陶、云苏华",
        "brief": "名义平路实则2200m爬升，开局四个爬坡，高山决战前的喘息之机。",
    },
    {
        "num": 18,
        "date": "2026-07-23",
        "route": "Voiron - Orcières-Merlette",
        "route_cn": "瓦龙 - 奥尔西耶尔-梅莱特",
        "type": "山地",
        "distance": 185.2,
        "elevation": 3944,
        "cest_start": (12, 35),
        "cest_finish": (17, 12),
        "broadcast_cn": ("18:30", "23:45"),
        "commentators": "李陶、云苏华",
        "brief": "阿尔卑斯三连战首战，山顶终点奥尔西耶尔7km@6.5%，GC或保守、突围有机会。",
    },
    {
        "num": 19,
        "date": "2026-07-24",
        "route": "Gap - Alpe d'Huez",
        "route_cn": "加普 - 阿尔普迪埃",
        "type": "山地",
        "distance": 127.9,
        "elevation": 3572,
        "cest_start": (14, 0),
        "cest_finish": (17, 24),
        "broadcast_cn": ("19:55", "23:55"),
        "commentators": "李陶、云苏华",
        "brief": "环法史上首次连续两天阿尔普迪埃，128km迷你高山赛，HC级山顶终点。",
    },
    {
        "num": 20,
        "date": "2026-07-25",
        "route": "Le Bourg-d'Oisans - Alpe d'Huez",
        "route_cn": "勒布尔杜瓦桑 - 阿尔普迪埃",
        "type": "山地",
        "distance": 170.9,
        "elevation": 5624,
        "cest_start": (11, 20),
        "cest_finish": (16, 11),
        "broadcast_cn": ("17:15", "22:45"),
        "commentators": "李陶、萧深",
        "brief": "皇后赛段，5600m+爬升，铁十字+加利比耶+萨雷讷，GC终极决战。",
    },
    {
        "num": 21,
        "date": "2026-07-26",
        "route": "Thoiry - Paris",
        "route_cn": "图瓦里 - 巴黎香榭丽舍大街",
        "type": "平路",
        "distance": 133.0,
        "elevation": 1295,
        "cest_start": (16, 15),
        "cest_finish": (19, 30),
        "broadcast_cn": ("22:10", "2:00"),
        "commentators": "李陶、萧深、云苏华",
        "brief": "传统巴黎收官，三次蒙马特高地绕圈后香街冲刺，为第113届环法画上句号。",
    },
]

# Fix typo in stage 17 date
for s in STAGES:
    if s.get("num") == 17:
        s["date"] = "2026-07-22"


def fmt_time(h, m):
    return f"{h:02d}:{m:02d}"


def build_description(stage):
    route = stage["route_cn"]
    stype = stage["type"]
    dist = stage["distance"]
    cest_s = fmt_time(*stage["cest_start"])
    cest_f = fmt_time(*stage["cest_finish"])
    cn_s, cn_f = stage["broadcast_cn"]
    comm = stage["commentators"]
    brief = stage["brief"]
    return (
        f"{route} | {stype}({dist}KM) | "
        f"当地开赛：{cest_s}(CEST) | 预计完赛：{cest_f}(CEST) | "
        f"观骑世界直播：{cn_s}-{cn_f}(北京时间) | 解说：{comm} | {brief}"
    )


def main():
    calendar = Calendar()
    calendar.creator = "cycling-ics TDF2026 generator"
    now = datetime.utcnow()
    events = []

    for stage in STAGES:
        event = Event()
        event.begin = datetime.strptime(stage["date"], "%Y-%m-%d")
        event.make_all_day()
        event.dtstamp = now
        event.uid = str(uuid.uuid4())

        if stage.get("rest"):
            event.name = "环法自行车赛 Tour de France (2.UWT) - 休息日 Rest Day"
            event.description = "休息日 | 无赛段 | 观骑世界无直播"
        else:
            if stage["type"] == "团队计时赛(TTT)":
                suffix = f"Stage {stage['num']} (TTT)"
            elif stage["type"] == "个人计时赛(ITT)":
                suffix = f"Stage {stage['num']} (ITT)"
            else:
                suffix = f"Stage {stage['num']}"
            event.name = f"环法自行车赛 Tour de France (2.UWT) - {suffix}"
            event.description = build_description(stage)

        events.append(event)

    events.sort(key=lambda e: e.begin)
    for event in events:
        calendar.events.add(event)

    output = "TDF2026.ics"
    with open(output, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    print(f"Created {output} with {len(calendar.events)} events")


if __name__ == "__main__":
    main()
