import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import httpx
from fake_useragent import UserAgent
import uuid
import json
import argparse

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

# Step 1: Fetch the webpage

url = "https://www.procyclingstats.com/races.php?year=2025&circuit=1&class=&filter=Filter&p=uci&s=year-calendar"
headers = {"User-Agent": UserAgent().random}

with httpx.Client(follow_redirects=True) as client:
    response = client.get(url, headers=headers, timeout=10)

soup = BeautifulSoup(response.content, 'html.parser')

print("Fetched webpage")

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
            
            race_name = get_race_name(
                english_name, 
                uci_class, 
                bilingual=(args.lang == 'bilingual')
            )
            
            # Parse start and end dates
            if ' - ' in date_range:
                start_date_str, end_date_str = date_range.split(' - ')
                start_date = datetime.strptime(start_date_str, '%d.%m').replace(year=2025)
                end_date = datetime.strptime(end_date_str, '%d.%m').replace(year=2025)
                # Handle year transition (e.g., if race starts in December and ends in January)
                if end_date < start_date:
                    end_date = end_date.replace(year=2026)
            else:
                start_date = datetime.strptime(date_range, '%d.%m').replace(year=2025)
                end_date = start_date
            
            races.append({
                'name': race_name,
                'start_date': start_date,
                'end_date': end_date,
                'location': ''
            })
            
        except (AttributeError, ValueError) as e:
            print(f"Skipping race due to error: {e}")
            continue

print("\nFetched Race Information:")
print("-" * 50)
for race in races:
    if race['start_date'] == race['end_date']:
        print(f"Date: {race['start_date'].strftime('%Y-%m-%d')}")
    else:
        print(f"Date: {race['start_date'].strftime('%Y-%m-%d')} to {race['end_date'].strftime('%Y-%m-%d')}")
    print(f"Name: {race['name']}")
    print("-" * 50)

# Step 3: Create an ICS calendar
calendar = Calendar()
calendar.creator = 'ics.py - http://git.io/lLljaA'  # Use creator property instead of add()

from datetime import datetime, timedelta

# Get current timestamp for DTSTAMP
now = datetime.utcnow()

for race in races:
    current_date = race['start_date']
    # Create an event for each day of the race
    while current_date <= race['end_date']:
        event = Event()
        # For multi-day races, include the stage number
        if race['start_date'] != race['end_date']:
            stage_num = (current_date - race['start_date']).days + 1
            event.name = f"{race['name']} - Stage {stage_num}"
        else:
            event.name = race['name']
            
        event.begin = current_date
        event.make_all_day()  # Make it an all-day event
        event.location = race['location']
        
        # Add required DTSTAMP
        event.dtstamp = now
        
        # Add unique identifier
        event.uid = str(uuid.uuid4())
        
        calendar.events.add(event)
        current_date += timedelta(days=1)

print("Created calendar")

# Modify the output filename based on language
output_filename = 'cycling_races_bilingual.ics' if args.lang == 'bilingual' else 'cycling_races_en.ics'

# Step 4: Save the calendar to an ICS file
with open(output_filename, 'w', encoding='utf-8') as f:
    f.writelines(calendar)

print(f"ICS calendar file created: {output_filename}")
