#!/usr/bin/env python3
"""Generate Tour de France ICS with rich descriptions and optional China broadcast times."""

import argparse
import json
from datetime import datetime
from pathlib import Path

import arrow
from ics import Calendar, Event

ROOT = Path(__file__).resolve().parent.parent
TZ = "Asia/Shanghai"
PRODID = "cycling-ics TDF generator"


def load_events(data_path):
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def parse_hm(time_str):
    hour, minute = time_str.split(":")
    return int(hour), int(minute)


def broadcast_range(date_str, start_str, end_str):
    year, month, day = (int(x) for x in date_str.split("-"))
    start_h, start_m = parse_hm(start_str)
    end_h, end_m = parse_hm(end_str)
    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m

    begin = arrow.get(year, month, day, start_h, start_m, tzinfo=TZ)
    if end_minutes <= start_minutes:
        end = arrow.get(year, month, day, end_h, end_m, tzinfo=TZ).shift(days=1)
    else:
        end = arrow.get(year, month, day, end_h, end_m, tzinfo=TZ)
    return begin.datetime, end.datetime


def make_event(item, timed=True):
    event = Event()
    event.name = item["summary"]
    event.description = item["description"]
    event.uid = item["uid"]

    year, month, day = (int(x) for x in item["date"].split("-"))
    if item.get("rest") or not timed:
        event.begin = datetime(year, month, day)
        event.make_all_day()
        return event

    start_str, end_str = item["broadcast_cn"]
    event.begin, event.end = broadcast_range(item["date"], start_str, end_str)
    return event


def main():
    parser = argparse.ArgumentParser(description="Generate Tour de France ICS")
    parser.add_argument(
        "--data",
        default=str(ROOT / "data" / "tdf2026_enrichment.json"),
        help="Path to TDF enrichment JSON",
    )
    parser.add_argument(
        "--all-day",
        action="store_true",
        default=True,
        help="Generate all-day events (default). Use --timed for broadcast windows.",
    )
    parser.add_argument(
        "--timed",
        action="store_true",
        help="Generate timed events using broadcast_cn in data file",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "TDF2026.ics"),
        help="Output ICS file path",
    )
    args = parser.parse_args()

    events = load_events(args.data)
    calendar = Calendar()
    calendar.creator = PRODID

    timed = args.timed and not args.all_day
    for item in events:
        calendar.events.add(make_event(item, timed=timed))

    output = Path(args.output)
    with open(output, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    mode = "timed (Asia/Shanghai broadcast)" if timed else "all-day"
    print(f"Created {output} with {len(events)} events ({mode})")


if __name__ == "__main__":
    main()
