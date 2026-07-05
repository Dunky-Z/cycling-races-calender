#!/usr/bin/env python3
"""Build UCI WorldTour bilingual ICS calendar from MCP-exported JSON."""

import argparse
import json
import re
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from ics import Calendar, Event

ROOT = Path(__file__).resolve().parent.parent
PRODID = "cycling-ics MCP calendar builder"
TDF_SLUG = "race/tour-de-france"
DUPLICATE_SLUGS = {
    "race/la-fleche-wallonne",  # alias of la-fleche-wallone
    "race/dauphine",  # alias of tour-auvergne-rhone-alpes
}

# PCS name variants -> race_names.json keys
NAME_ALIASES = {
    "Omloop Het Nieuwsblad": "Omloop Nieuwsblad ME",
    "Omloop Nieuwsblad ME": "Omloop Nieuwsblad ME",
    "E3 Saxo Classic": "E3 Saxo Classic ME",
    "E3 Saxo Classic ME": "E3 Saxo Classic ME",
    "Gent-Wevelgem": "Gent-Wevelgem in Flanders Fields ME",
    "In Flanders Fields": "Gent-Wevelgem in Flanders Fields ME",
    "Dwars door Vlaanderen": "Dwars door Vlaanderen - A travers la Flandre ME",
    "Ronde van Vlaanderen": "Ronde van Vlaanderen ME",
    "Ronde Van Brugge - Tour of Bruges ME": "Classic Brugge-De Panne",
    "Volta a Catalunya": "Volta Ciclista a Catalunya",
    "La Vuelta a España": "La Vuelta Ciclista a España",
    "Vuelta a España": "La Vuelta Ciclista a España",
    "Cadel Evans Great Ocean Road Race": "Cadel Evans Great Ocean Road Race - Men",
    "Great Ocean Road Race": "Cadel Evans Great Ocean Road Race - Men",
    "Tour Down Under": "Santos Tour Down Under",
    "Santos Tour Down Under": "Santos Tour Down Under",
    "Critérium du Dauphiné": "Critérium du Dauphiné",
    "Dauphiné": "Critérium du Dauphiné",
    "Tour Auvergne - Rhône-Alpes": "Critérium du Dauphiné",
    "Donostia San Sebastián Classic": "Donostia San Sebastian Klasikoa",
    "Donostia San Sebastian Klasikoa": "Donostia San Sebastian Klasikoa",
    "San Sebastian Classic": "Donostia San Sebastian Klasikoa",
    "Cyclassics Hamburg": "ADAC Cyclassics",
    "Tour of Guangxi": "Gree-Tour of Guangxi",
    "Paris - Roubaix": "Paris-Roubaix",
    "Liège - Bastogne - Liège": "Liège-Bastogne-Liège",
    "Bretagne Classic - CIC": "Bretagne Classic - Ouest-France",
    "World Championships ME - Road Race": "World Championships ME - Road Race",
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def race_slug(race_url):
    parts = race_url.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return race_url


def resolve_chinese_name(english_name, translations):
    key = NAME_ALIASES.get(english_name, english_name)
    if key in translations:
        return translations[key]
    for trans_key, chinese in translations.items():
        if trans_key.lower() in english_name.lower() or english_name.lower() in trans_key.lower():
            return chinese
    return ""


def race_display_name(english_name, uci_tour, translations):
    key = NAME_ALIASES.get(english_name, english_name)
    display_en = key if key in translations else english_name
    chinese = translations.get(key, "")
    if chinese:
        return f"{chinese} {display_en} ({uci_tour})"
    return f"{display_en} ({uci_tour})"


def parse_stage_number(stage_url):
    match = re.search(r"stage-(\d+)", stage_url or "")
    return int(match.group(1)) if match else None


def stage_label(stage_info, stage_num):
    stage_type = (stage_info or {}).get("stage_type", "")
    base = f"Stage {stage_num}"
    if stage_type == "ITT":
        return f"{base} (ITT)"
    if stage_type == "TTT":
        return f"{base} (TTT)"
    return base


def stage_description(stage_info):
    if not stage_info:
        return ""
    departure = stage_info.get("departure")
    arrival = stage_info.get("arrival")
    if departure and arrival:
        return f"{departure} - {arrival}"
    stage_name = stage_info.get("stage_name", "")
    if stage_name:
        return stage_name.replace(" → ", " - ")
    return ""


def parse_date(date_str, year):
    if not date_str:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    month, day = date_str.split("-")
    return datetime(year, int(month), int(day)).date()


def make_all_day_event(name, date_obj, description="", uid=None):
    event = Event()
    event.name = name
    event.begin = datetime(date_obj.year, date_obj.month, date_obj.day)
    event.make_all_day()
    if description:
        event.description = description
    event.uid = uid or str(uuid.uuid4())
    return event


def tdf_events_from_enrichment(enrichment):
    events = []
    for item in enrichment:
        date_obj = datetime.strptime(item["date"], "%Y-%m-%d").date()
        events.append(
            make_all_day_event(
                item["summary"],
                date_obj,
                description=item.get("description", ""),
                uid=item.get("uid"),
            )
        )
    return events


def rest_day_events(race_name, prev_date, next_date):
    events = []
    current = prev_date + timedelta(days=1)
    while current < next_date:
        events.append(
            make_all_day_event(
                f"{race_name} - 休息日 Rest Day",
                current,
            )
        )
        current += timedelta(days=1)
    return events


def multi_day_events(race, translations):
    race_name = race_display_name(race["name"], race["uci_tour"], translations)
    year = race["year"]
    stages = race.get("stages", [])
    stage_details = {s["stage_url"]: s for s in race.get("stage_details", [])}

    dated_stages = []
    for stage in stages:
        date_obj = parse_date(stage.get("date"), year)
        if date_obj:
            dated_stages.append((date_obj, stage))

    dated_stages.sort(key=lambda x: x[0])
    events = []
    prev_date = None

    for date_obj, stage in dated_stages:
        if prev_date and (date_obj - prev_date).days > 1:
            events.extend(rest_day_events(race_name, prev_date, date_obj))

        stage_num = parse_stage_number(stage.get("stage_url"))
        detail = stage_details.get(stage.get("stage_url"), {})
        label = stage_label(detail, stage_num) if stage_num else "Stage"
        desc = stage_description(detail)

        events.append(
            make_all_day_event(
                f"{race_name} - {label}",
                date_obj,
                description=desc,
            )
        )
        prev_date = date_obj

    return events


def one_day_event(race, translations):
    race_name = race_display_name(race["name"], race["uci_tour"], translations)
    date_obj = datetime.strptime(race["startdate"], "%Y-%m-%d").date()
    detail = (race.get("stage_details") or [{}])[0]
    desc = stage_description(detail)
    return [make_all_day_event(race_name, date_obj, description=desc)]


def build_events(races, translations, tdf_enrichment):
    all_events = []

    for race in races:
        slug = race_slug(race.get("url", ""))
        if slug in DUPLICATE_SLUGS:
            continue

        if slug == TDF_SLUG:
            all_events.extend(tdf_events_from_enrichment(tdf_enrichment))
            continue

        if race.get("is_one_day_race"):
            all_events.extend(one_day_event(race, translations))
        else:
            all_events.extend(multi_day_events(race, translations))

    all_events.sort(key=lambda e: e.begin)
    return all_events


def main():
    parser = argparse.ArgumentParser(description="Build WorldTour bilingual ICS calendar")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument(
        "--input",
        help="Path to wt_calendar JSON (default: data/wt_calendar_{year}.json)",
    )
    parser.add_argument(
        "--tdf-data",
        default=str(ROOT / "data" / "tdf2026_enrichment.json"),
        help="Path to TDF enrichment JSON",
    )
    parser.add_argument(
        "--translations",
        default=str(ROOT / "data" / "race_names.json"),
        help="Path to race name translations",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT),
        help="Directory for output ICS files",
    )
    parser.add_argument(
        "--no-alias",
        action="store_true",
        help="Do not copy output to cycling_races_bilingual.ics",
    )
    args = parser.parse_args()

    input_path = Path(args.input or ROOT / "data" / f"wt_calendar_{args.year}.json")
    translations = load_json(args.translations)
    tdf_enrichment = load_json(args.tdf_data) if args.year == 2026 else []

    data = load_json(input_path)
    races = data.get("races", data) if isinstance(data, dict) else data

    calendar = Calendar()
    calendar.creator = PRODID

    for event in build_events(races, translations, tdf_enrichment):
        calendar.events.add(event)

    output_dir = Path(args.output_dir)
    year_file = output_dir / f"cycling_races_bilingual_{args.year}.ics"
    with open(year_file, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    if not args.no_alias:
        alias_file = output_dir / "cycling_races_bilingual.ics"
        shutil.copy2(year_file, alias_file)

    print(f"Created {year_file} with {len(calendar.events)} events")
    if not args.no_alias:
        print(f"Copied to {alias_file}")


if __name__ == "__main__":
    main()
