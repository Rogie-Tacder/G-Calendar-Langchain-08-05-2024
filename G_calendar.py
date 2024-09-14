from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle
from dotenv import load_dotenv
import re

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def initialize():
    global service
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

def get_events(max_results=2):
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events
def parse_relative_date(date_str):
    today = datetime.now().date()
    date_str = date_str.lower()
    
    if 'today' in date_str:
        return today
    elif 'tomorrow' in date_str:
        return today + timedelta(days=1)
    elif 'day after tomorrow' in date_str:
        return today + timedelta(days=2)
    elif 'next' in date_str:
        days = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
        for day, offset in days.items():
            if day in date_str:
                days_ahead = offset - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return today + timedelta(days=days_ahead)
    return None
def parse_relative_time(time_str):
    now = datetime.now()
    time_str = time_str.lower()
    
    if 'morning' in time_str:
        return now.replace(hour=9, minute=0, second=0, microsecond=0)
    elif 'afternoon' in time_str:
        return now.replace(hour=14, minute=0, second=0, microsecond=0)
    elif 'evening' in time_str:
        return now.replace(hour=18, minute=0, second=0, microsecond=0)
    elif 'night' in time_str or 'tonight' in time_str:
        return now.replace(hour=20, minute=0, second=0, microsecond=0)
    return None
def parse_event_details(event_details):
    # Extract summary (everything up to the first date-like string or time expression)
    summary_match = re.search(r'^(.*?)(?=\b(?:today|tomorrow|tonight|next|day after tomorrow|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|morning|afternoon|evening|night))', event_details, re.IGNORECASE | re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else "Untitled Event"

    # Try to parse relative date
    relative_date = parse_relative_date(event_details)
    if relative_date:
        date_obj = relative_date
    else:
        # Extract date
        date_match = re.search(r'\b(\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?)\b', event_details)
        if date_match:
            date_str = date_match.group(1)
            # Try different date formats
            for fmt in ('%m-%d-%Y', '%m/%d/%Y', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%y', '%m/%d/%y', '%d-%m-%y', '%d/%m/%y'):
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    # If the year is parsed as 24, assume it's 2024
                    if parsed_date.year < 100:
                        parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                    date_obj = parsed_date.date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Unable to parse date: {date_str}")
        else:
            date_obj = datetime.now().date()

    # Try to parse relative time
    relative_time = parse_relative_time(event_details)
    if relative_time:
        time_obj = relative_time.time()
    else:
        # Extract time
        time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b', event_details, re.IGNORECASE)
        if time_match:
            time_str = time_match.group(1)
            if 'am' in time_str.lower() or 'pm' in time_str.lower():
                # Handle cases like "3pm"
                if ':' not in time_str:
                    time_str = time_str.replace('am', ' am').replace('pm', ' pm')
                time_obj = datetime.strptime(time_str, '%I:%M %p' if ':' in time_str else '%I %p').time()
            else:
                time_obj = datetime.strptime(time_str, '%H:%M' if ':' in time_str else '%H').time()
        else:
            time_obj = datetime.strptime('9:00 AM', '%I:%M %p').time()  # Default to 9:00 AM if no time specified

    # Combine date and time
    start_time = datetime.combine(date_obj, time_obj)
    end_time = start_time + timedelta(hours=1)  # Default duration: 1 hour

    return summary, start_time, end_time

from datetime import datetime, timedelta

def add_event(title, date, time, attendees=None):
    # Convert date to ISO format (assuming input is YYYY-MM-DD)
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    date_iso = date_obj.strftime("%Y-%m-%d")
    
    # Convert time to 24-hour format (assuming input is HH:MM for simplicity)
    time_obj = datetime.strptime(time, "%H:%M")
    time_24 = time_obj.strftime("%H:%M:%S")
    
    start_time = f"{date_iso}T{time_24}"
    end_time = (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat()
    
    event = {
        'summary': title,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Manila',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Manila',
        },
    }
    
    if attendees:
        event['attendees'] = [{'email': attendee.strip()} for attendee in attendees.split(',')]
    
    # This is where you would add the event to the calendar. This example assumes you have
    # a `service` object already set up for interacting with the Google Calendar API.
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event['id']


def delete_event(event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()

def list_calendars():
    calendar_list = service.calendarList().list().execute().get('items', [])
    return [calendar['summary'] for calendar in calendar_list]

def create_calendar(name):
    new_calendar = {
        'summary': name,
        'timeZone': 'Asia/Manila'
    }
    created_calendar = service.calendars().insert(body=new_calendar).execute()
    return created_calendar['id']

if __name__ == '__main__':
    initialize()
    print("Calendars:", list_calendars())
    # print("Adding event...")
    # event_id = add_event("Test Event", "2024-08-14", "17:30")  # Provide date and time
    # print(f"Added event with ID: {event_id}")
    # print(get_events)
    # print("Events:", get_events())
    # print(f"Deleting event {event_id}...")
    # # delete_event(event_id)
    # print("Events after deletion:", get_events())
