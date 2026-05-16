from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import httpx
from fake_useragent import UserAgent
import uuid
import json
import argparse
import re
import time

parser = argparse.ArgumentParser(description='Generate cycling race calendar')
parser.add_argument('--year', type=int, default=datetime.now().year,
                   help='Season year for the UCI calendar (default: current year)')
parser.add_argument('--lang', choices=['en', 'bilingual'], default='bilingual',
                   help='Language for race names (en: English only, bilingual: English + Chinese)')
parser.add_argument('--all-races', action='store_true',
                   help='Include finished races (default: only upcoming races)')
args = parser.parse_args()
year = args.year

# Load race name translations
try:
    with open('race_names.json', 'r', encoding='utf-8') as f:
        race_translations = json.load(f)
except FileNotFoundError:
    print("Warning: race_names.json not found. Using English names only.")
    race_translations = {}

PCS_BASE = 'https://www.procyclingstats.com'


def get_http_headers():
    return {
        'User-Agent': UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }


def calendar_url(season_year):
    return (
        f'{PCS_BASE}/races.php'
        f'?p=uci&s=year-calendar&year={season_year}&circuit=1&class=&filter=Filter'
    )


def get_race_name(english_name, uci_class, bilingual=True):
    """Generate race name based on language preference"""
    base_name = english_name.strip()
    chinese_name = race_translations.get(base_name, '')

    if bilingual and chinese_name:
        return f"{chinese_name} {base_name} ({uci_class})"
    return f"{base_name} ({uci_class})"


def normalize_race_name_for_url(race_name):
    """Convert race name to URL format (lowercase with hyphens)"""
    race_name = race_name.lower()

    if "giro d'italia" in race_name:
        race_name = race_name.replace("giro d'italia", "giro-d-italia")

    race_name = re.sub(r'[^\w\s-]', '', race_name)
    race_name = re.sub(r'\s+', '-', race_name)
    race_name = re.sub(r'-+', '-', race_name)
    race_name = race_name.strip('-')

    name_mappings = {
        'giro-d-italia': 'giro-d-italia',
        'tour-de-france': 'tour-de-france',
        'vuelta-a-españa': 'vuelta-a-espana',
        'la-vuelta-ciclista-a-españa': 'vuelta-a-espana',
        'milano-sanremo': 'milano-sanremo',
        'ronde-van-vlaanderen': 'ronde-van-vlaanderen',
        'tour-des-flandres': 'ronde-van-vlaanderen',
        'paris-roubaix': 'paris-roubaix',
        'liège-bastogne-liège': 'liege-bastogne-liege',
        'il-lombardia': 'il-lombardia',
        'strade-bianche': 'strade-bianche',
        'tirreno-adriatico': 'tirreno-adriatico',
        'paris-nice': 'paris-nice',
        'volta-a-catalunya': 'volta-a-catalunya',
        'volta-ciclista-a-catalunya': 'volta-a-catalunya',
        'criterium-du-dauphine': 'dauphine',
        'critérium-du-dauphiné': 'dauphine',
        'tour-auvergne-rhone-alpes': 'tour-auvergne-rhone-alpes',
    }

    return name_mappings.get(race_name, race_name)


def extract_race_slug(href):
    """Extract race slug from PCS href, e.g. race/giro-d-italia/2026/gc"""
    if not href:
        return None
    match = re.search(r'race/([^/]+)/\d+', href)
    return match.group(1) if match else None


def find_calendar_table(soup):
    """Locate the UCI year calendar results table."""
    for table in soup.select('table.basic'):
        headers = [th.get_text(strip=True) for th in table.select('thead th')]
        if 'Race' in headers and 'Date' in headers:
            return table

    table_div = soup.select_one('div.mt10')
    if table_div:
        return table_div.select_one('table')

    return soup.select_one('table.basic')


def parse_date_range(date_range, season_year):
    """Parse DD.MM or DD.MM - DD.MM into start/end datetimes."""
    if ' - ' in date_range:
        start_date_str, end_date_str = date_range.split(' - ', 1)
        start_date = datetime.strptime(start_date_str, '%d.%m').replace(year=season_year)
        end_date = datetime.strptime(end_date_str, '%d.%m').replace(year=season_year)
        if end_date < start_date:
            end_date = end_date.replace(year=season_year + 1)
    else:
        start_date = datetime.strptime(date_range, '%d.%m').replace(year=season_year)
        end_date = start_date
    return start_date, end_date


def parse_calendar_races(soup, season_year, upcoming_only=True):
    """Parse race rows from the calendar page HTML."""
    table = find_calendar_table(soup)
    if not table:
        return []

    races = []
    for row in table.select('tbody tr'):
        try:
            date_cell = row.select_one('td.cu500')
            if not date_cell:
                continue

            date_range = date_cell.get_text(strip=True)
            if not date_range or '.' not in date_range:
                continue

            race_cell = row.select_one('td:nth-child(3)')
            race_link = race_cell.select_one('a') if race_cell else None
            if not race_link:
                continue

            english_name = race_link.get_text(strip=True)
            uci_cell = row.select_one('td:nth-child(5)')
            uci_class = uci_cell.get_text(strip=True) if uci_cell else ''

            start_date, end_date = parse_date_range(date_range, season_year)

            if upcoming_only and end_date.date() < datetime.now().date():
                print(f"Skipping finished race: {english_name}")
                continue

            race_slug = extract_race_slug(race_link.get('href', ''))
            if not race_slug:
                race_slug = normalize_race_name_for_url(english_name)

            races.append({
                'name': get_race_name(
                    english_name,
                    uci_class,
                    bilingual=(args.lang == 'bilingual'),
                ),
                'english_name': english_name,
                'race_slug': race_slug,
                'start_date': start_date,
                'end_date': end_date,
                'location': '',
                'uci_class': uci_class,
            })
        except (AttributeError, ValueError) as e:
            print(f"Skipping race due to error: {e}")
            continue

    return races


def find_stages_table(soup):
    """Find the stages table on a race detail page."""
    for h3 in soup.select('h3'):
        if h3.get_text(strip=True) == 'Stages':
            container = h3.find_parent('div') or h3
            stages_table = container.find('table', class_='basic')
            if stages_table:
                return stages_table
            return h3.find_next('table')

    return soup.select_one('div.mt20 h3 + .table-cont table') or soup.select_one('div.mt20 table.basic')


def fetch_stage_details(race_slug, season_year, headers):
    """Fetch detailed stage information for multi-day races."""
    detail_url = f"{PCS_BASE}/race/{race_slug}/{season_year}"
    print(f"Fetching stage details from: {detail_url}")

    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(detail_url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch stage details (status {response.status_code}): {detail_url}")
                return None

        soup = BeautifulSoup(response.content, 'html.parser')
        stages_table = find_stages_table(soup)
        if not stages_table:
            print(f"No stages table found for {race_slug}")
            return None

        tbody = stages_table.select_one('tbody')
        if not tbody:
            print(f"No table body found for {race_slug}")
            return None

        stages = []
        for row in tbody.select('tr'):
            if 'sum' in row.get('class', []):
                continue

            cells = row.select('td')
            if len(cells) < 4:
                continue

            date_text = cells[0].get_text(strip=True)
            day_text = cells[1].get_text(strip=True)
            stage_cell = cells[3]
            stage_link = stage_cell.select_one('a')
            stage_text = stage_link.get_text(strip=True) if stage_link else stage_cell.get_text(strip=True)

            if not date_text or '/' not in date_text:
                continue

            try:
                day, month = date_text.split('/')
                stage_date = datetime(season_year, int(month), int(day))

                is_rest_day = stage_text.lower() == 'restday' or (
                    not day_text and not stage_link
                )

                stages.append({
                    'date': stage_date,
                    'stage_text': stage_text,
                    'is_rest_day': is_rest_day,
                    'day': day_text,
                })
            except (ValueError, IndexError) as e:
                print(f"Error parsing date {date_text}: {e}")
                continue

        # Fix year for stages that fall in the next calendar year (e.g. Giro ending in June)
        if stages:
            for i, stage in enumerate(stages):
                if i > 0 and stage['date'] < stages[i - 1]['date']:
                    stage['date'] = stage['date'].replace(year=stage['date'].year + 1)

        print(f"Found {len(stages)} stages for {race_slug}")
        return stages

    except Exception as e:
        print(f"Error fetching stage details for {race_slug}: {e}")
        return None


def fetch_calendar_page(season_year, headers):
    url = calendar_url(season_year)
    print(f"Fetching {season_year} UCI calendar from: {url}")
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        hint = ' (site may be blocking automated requests)' if response.status_code == 403 else ''
        raise RuntimeError(f"Failed to fetch calendar (HTTP {response.status_code}){hint}: {url}")
    return response


headers = get_http_headers()
response = fetch_calendar_page(year, headers)
soup = BeautifulSoup(response.content, 'html.parser')
print("Fetched main webpage")

races = parse_calendar_races(soup, year, upcoming_only=not args.all_races)
if not races:
    print("Warning: no races parsed. The page structure may have changed or the request was blocked.")

print(f"\nFound {len(races)} races to export")

calendar = Calendar()
calendar.creator = 'ics.py - http://git.io/lLljaA'
now = datetime.utcnow()

for i, race in enumerate(races):
    print(f"\nProcessing race {i+1}/{len(races)}: {race['english_name']}")

    is_multi_day = race['start_date'] != race['end_date']

    if is_multi_day:
        print("Multi-day race detected, fetching stage details...")
        stages = fetch_stage_details(race['race_slug'], year, headers)

        if stages:
            for stage in stages:
                event = Event()

                if stage['is_rest_day']:
                    event.name = f"{race['name']} - 休息日 Rest Day"
                elif 'Stage' in stage['stage_text'] and '|' in stage['stage_text']:
                    stage_info, route_info = stage['stage_text'].split('|', 1)
                    event.name = f"{race['name']} - {stage_info.strip()}"
                    event.description = route_info.strip()
                else:
                    event.name = f"{race['name']} - {stage['stage_text']}"

                event.begin = stage['date']
                event.make_all_day()
                event.location = race['location']
                event.dtstamp = now
                event.uid = str(uuid.uuid4())
                calendar.events.add(event)
        else:
            print(f"Using fallback method for {race['english_name']}")
            current_date = race['start_date']
            while current_date <= race['end_date']:
                event = Event()
                stage_num = (current_date - race['start_date']).days + 1
                event.name = f"{race['name']} - Stage {stage_num}"
                event.begin = current_date
                event.make_all_day()
                event.location = race['location']
                event.dtstamp = now
                event.uid = str(uuid.uuid4())
                calendar.events.add(event)
                current_date += timedelta(days=1)

        time.sleep(0.5)
    else:
        event = Event()
        event.name = race['name']
        event.begin = race['start_date']
        event.make_all_day()
        event.location = race['location']
        event.dtstamp = now
        event.uid = str(uuid.uuid4())
        calendar.events.add(event)

print("\nCreated calendar")

lang_suffix = 'bilingual' if args.lang == 'bilingual' else 'en'
output_filename = f'cycling_races_{lang_suffix}_{year}.ics'

with open(output_filename, 'w', encoding='utf-8') as f:
    f.writelines(calendar)

print(f"ICS calendar file created: {output_filename}")
print(f"Total events created: {len(calendar.events)}")
