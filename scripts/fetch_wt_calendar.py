#!/usr/bin/env python3
"""Fetch UCI WorldTour calendar data via PCS MCP client and save to JSON."""

import argparse
import json
import sys
import time
from pathlib import Path

from procyclingstats_mcp.pcs_client import (
    discover_races,
    get_race_overview,
    get_stage_results,
)

ROOT = Path(__file__).resolve().parent.parent
DUPLICATE_SLUGS = {"race/la-fleche-wallonne", "race/dauphine"}
TDF_SLUG = "race/tour-de-france"


def slim_stage_detail(detail):
    if detail.get("error"):
        return None
    return {
        "stage_url": detail.get("url"),
        "stage_name": detail.get("stage_name"),
        "date": detail.get("date"),
        "departure": detail.get("departure"),
        "arrival": detail.get("arrival"),
        "stage_type": detail.get("stage_type"),
        "distance": detail.get("distance"),
    }


def fetch_race(race_url, year):
    full_url = f"{race_url}/{year}"
    overview = get_race_overview(full_url)
    if overview.get("error"):
        print(f"  ERROR: {overview['error']}", file=sys.stderr)
        return None

    stage_details = []
    if overview.get("is_one_day_race"):
        result_url = f"{full_url}/result"
        detail = get_stage_results(result_url)
        slim = slim_stage_detail(detail)
        if slim:
            stage_details.append(slim)
    elif race_url != TDF_SLUG:
        for stage in overview.get("stages", []):
            stage_url = stage.get("stage_url")
            if not stage_url:
                continue
            detail = get_stage_results(stage_url)
            slim = slim_stage_detail(detail)
            if slim:
                stage_details.append(slim)
            time.sleep(0.1)

    overview["stage_details"] = stage_details
    return overview


def main():
    parser = argparse.ArgumentParser(description="Fetch WorldTour calendar via PCS MCP client")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument(
        "--tiers",
        nargs="+",
        default=["worldtour"],
        help="Race tiers to include",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON path (default: data/wt_calendar_{year}.json)",
    )
    args = parser.parse_args()

    output = Path(args.output or ROOT / "data" / f"wt_calendar_{args.year}.json")
    print(f"Discovering {args.year} races (tiers: {args.tiers})...")
    discovered = discover_races(args.year, tiers=args.tiers)
    race_urls = sorted(
        r["race_url"] for r in discovered if r["race_url"] not in DUPLICATE_SLUGS
    )
    print(f"Found {len(race_urls)} unique races")

    races = []
    for i, race_url in enumerate(race_urls, 1):
        print(f"[{i}/{len(race_urls)}] {race_url}")
        race = fetch_race(race_url, args.year)
        if race:
            races.append(race)

    payload = {"year": args.year, "tiers": args.tiers, "races": races}
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(races)} races to {output}")


if __name__ == "__main__":
    main()
