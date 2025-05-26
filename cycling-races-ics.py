import requests
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

# Add argument parser for language option
parser = argparse.ArgumentParser(description='Generate cycling race calendar')
parser.add_argument('--lang', choices=['en', 'bilingual'], default='bilingual',
                   help='Language for race names (en: English only, bilingual: English + Chinese)')
args = parser.parse_args()

# Load race name translations
try:
    with open('race_names.json', 'r', encoding='utf-8') as f:
        race_translations = json.load(f)
except FileNotFoundError:
    print("Warning: race_names.json not found. Using English names only.")
    race_translations = {}

def get_race_name(english_name, uci_class, bilingual=True):
    """Generate race name based on language preference"""
    base_name = english_name.strip()
    chinese_name = race_translations.get(base_name, '')
    
    if bilingual and chinese_name:
        return f"{chinese_name} {base_name} ({uci_class})"
    else:
        return f"{base_name} ({uci_class})"

def normalize_race_name_for_url(race_name):
    """Convert race name to URL format (lowercase with hyphens)"""
    # Remove common words and special characters
    race_name = race_name.lower()
    
    # Handle specific cases before general processing
    if "giro d'italia" in race_name:
        race_name = race_name.replace("giro d'italia", "giro-d-italia")
    
    # Replace special characters and spaces with hyphens
    race_name = re.sub(r'[^\w\s-]', '', race_name)
    race_name = re.sub(r'\s+', '-', race_name)
    race_name = re.sub(r'-+', '-', race_name)
    race_name = race_name.strip('-')
    
    # Handle some common name mappings
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
        'critérium-du-dauphiné': 'dauphine'
    }
    
    return name_mappings.get(race_name, race_name)

def fetch_stage_details(race_name, year, headers):
    """Fetch detailed stage information for multi-day races"""
    race_url_name = normalize_race_name_for_url(race_name)
    detail_url = f"https://www.procyclingstats.com/race/{race_url_name}/{year}"
    
    print(f"Fetching stage details from: {detail_url}")
    
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(detail_url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch stage details (status {response.status_code}): {detail_url}")
                return None
                
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the stages table
        stages_section = soup.select_one('div.mt20 h3:-soup-contains("Stages")')
        if not stages_section:
            print(f"No stages section found for {race_name}")
            return None
            
        stages_table = stages_section.find_next('table')
        if not stages_table:
            print(f"No stages table found for {race_name}")
            return None
            
        stages = []
        tbody = stages_table.select_one('tbody')
        if not tbody:
            print(f"No table body found for {race_name}")
            return None
            
        for row in tbody.select('tr'):
            cells = row.select('td')
            if len(cells) < 4:
                continue
                
            date_text = cells[0].text.strip()
            day_text = cells[1].text.strip()
            stage_text = cells[3].text.strip()
            
            # Skip summary rows or invalid dates
            if not date_text or '/' not in date_text:
                continue
                
            try:
                # Parse date (format: DD/MM)
                day, month = date_text.split('/')
                stage_date = datetime(year, int(month), int(day))
                
                # Check if it's a rest day
                is_rest_day = stage_text.lower() == 'restday' or not day_text
                
                stages.append({
                    'date': stage_date,
                    'stage_text': stage_text,
                    'is_rest_day': is_rest_day,
                    'day': day_text
                })
                
            except (ValueError, IndexError) as e:
                print(f"Error parsing date {date_text}: {e}")
                continue
                
        print(f"Found {len(stages)} stages for {race_name}")
        return stages
        
    except Exception as e:
        print(f"Error fetching stage details for {race_name}: {e}")
        return None

def is_race_finished(end_date):
    """Check if a race has already finished"""
    return end_date < datetime.now().date()

# Step 1: Fetch the main calendar webpage
url = "https://www.procyclingstats.com/races.php?year=2025&circuit=1&class=&filter=Filter&p=uci&s=year-calendar"
headers = {"User-Agent": UserAgent().random}

print("Fetching main calendar page...")
with httpx.Client(follow_redirects=True) as client:
    response = client.get(url, headers=headers, timeout=10)

soup = BeautifulSoup(response.content, 'html.parser')
print("Fetched main webpage")

# Step 2: Parse the HTML to extract race information
races = []
table_div = soup.select_one('div.mt10')
if table_div:
    for row in table_div.select('table tbody tr'):
        try:
            # Get date range from first column (e.g. "21.01 - 26.01" or "02.02")
            date_range = row.select_one('td.cu500').text.strip()
            
            # Get race name and format it according to language preference
            race_cell = row.select_one('td:nth-child(3)')
            english_name = race_cell.select_one('a').text.strip()
            uci_class = row.select_one('td:nth-child(5)').text.strip()
            
            # Parse start and end dates
            if ' - ' in date_range:
                start_date_str, end_date_str = date_range.split(' - ')
                start_date = datetime.strptime(start_date_str, '%d.%m').replace(year=2025)
                end_date = datetime.strptime(end_date_str, '%d.%m').replace(year=2025)
                # Handle year transition
                if end_date < start_date:
                    end_date = end_date.replace(year=2026)
            else:
                start_date = datetime.strptime(date_range, '%d.%m').replace(year=2025)
                end_date = start_date
            
            # Skip races that have already finished
            if is_race_finished(end_date.date()):
                print(f"Skipping finished race: {english_name}")
                continue
                
            race_name = get_race_name(
                english_name, 
                uci_class, 
                bilingual=(args.lang == 'bilingual')
            )
            
            races.append({
                'name': race_name,
                'english_name': english_name,
                'start_date': start_date,
                'end_date': end_date,
                'location': '',
                'uci_class': uci_class
            })
            
        except (AttributeError, ValueError) as e:
            print(f"Skipping race due to error: {e}")
            continue

print(f"\nFound {len(races)} upcoming races")

# Step 3: Create an ICS calendar
calendar = Calendar()
calendar.creator = 'ics.py - http://git.io/lLljaA'

now = datetime.utcnow()

for i, race in enumerate(races):
    print(f"\nProcessing race {i+1}/{len(races)}: {race['english_name']}")
    
    # Check if it's a multi-day race
    is_multi_day = race['start_date'] != race['end_date']
    
    if is_multi_day:
        print(f"Multi-day race detected, fetching stage details...")
        # Fetch detailed stage information
        stages = fetch_stage_details(race['english_name'], race['start_date'].year, headers)
        
        if stages:
            # Create events based on actual stage information
            for stage in stages:
                event = Event()
                
                if stage['is_rest_day']:
                    event.name = f"{race['name']} - 休息日 Rest Day"
                else:
                    # Extract stage info from stage_text
                    if 'Stage' in stage['stage_text'] and '|' in stage['stage_text']:
                        stage_info = stage['stage_text'].split('|', 1)[0].strip()
                        route_info = stage['stage_text'].split('|', 1)[1].strip() if '|' in stage['stage_text'] else ''
                        event.name = f"{race['name']} - {stage_info}"
                        if route_info:
                            event.description = route_info
                    else:
                        event.name = f"{race['name']} - {stage['stage_text']}"
                
                event.begin = stage['date']
                event.make_all_day()
                event.location = race['location']
                event.dtstamp = now
                event.uid = str(uuid.uuid4())
                
                calendar.events.add(event)
        else:
            # Fallback to simple day-by-day events if stage details unavailable
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
        
        # Add a small delay to avoid overwhelming the server
        time.sleep(0.5)
    else:
        # Single day race
        event = Event()
        event.name = race['name']
        event.begin = race['start_date']
        event.make_all_day()
        event.location = race['location']
        event.dtstamp = now
        event.uid = str(uuid.uuid4())
        
        calendar.events.add(event)

print("\nCreated calendar")

# Modify the output filename based on language
output_filename = 'cycling_races_bilingual.ics' if args.lang == 'bilingual' else 'cycling_races_en.ics'

# Step 4: Save the calendar to an ICS file
with open(output_filename, 'w', encoding='utf-8') as f:
    f.writelines(calendar)

print(f"ICS calendar file created: {output_filename}")
print(f"Total events created: {len(calendar.events)}")
