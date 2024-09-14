from googleapiclient.discovery import build
import re
from datetime import datetime, date
from G_calendar_auth import get_credentials

creds = get_credentials()
service = build('calendar', 'v3', credentials=creds)

def parse_input(user_input):
    # Regular expressions for date, time, and email
    date_pattern = r'\b\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,?\s+\d{4})?\b'
    time_pattern = r'\b\d{1,2}[:\.]\d{2}\s*(?:am|pm)?\b|\b\d{1,2}\s*(?:am|pm)\b'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Extract date, time, and email
    date_match = re.search(date_pattern, user_input, re.IGNORECASE)
    time_match = re.search(time_pattern, user_input, re.IGNORECASE)
    email_matches = re.findall(email_pattern, user_input)
    
    date_str = date_match.group() if date_match else None
    time_str = time_match.group() if time_match else None
    emails = email_matches if email_matches else []

    # Remove date, time, and emails from input to get description
    description = user_input
    if date_str:
        description = description.replace(date_str, '')
    if time_str:
        description = description.replace(time_str, '')
    for email in emails:
        description = description.replace(email, '')
    
    description = description.strip()

    # Ensure proper formatting of the date string
    if date_str:
        date_str = date_str.replace(',', '').strip()  # Remove comma and extra spaces

    return date_str, time_str, description, emails

def format_datetime(date_str, time_str):
    current_year = datetime.now().year

    if date_str and time_str:
        # Try different date formats
        date_formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d', '%B %d %Y', '%B %d', '%b %d']
        for date_format in date_formats:
            try:
                if '%Y' not in date_format:
                    # For formats without year, add the current year
                    date = datetime.strptime(f"{date_str} {current_year}", f"{date_format} %Y").date()
                else:
                    date = datetime.strptime(date_str, date_format).date()
                break
            except ValueError:
                continue
        else:
            # If none of the date formats match, assume it's in the format 'mmdd'
            try:
                date = datetime.strptime(f"{date_str} {current_year}", "%m%d %Y").date()
            except ValueError:
                raise ValueError("Invalid date format")

        # Try different time formats
        time_formats = ['%I:%M %p', '%H:%M', '%I%p']
        for time_format in time_formats:
            try:
                time = datetime.strptime(time_str, time_format).time()
                break
            except ValueError:
                continue
        else:
            raise ValueError("Invalid time format")

        event_datetime = datetime.combine(date, time)

        # If the resulting date is in the past, assume it's for next year
        if event_datetime < datetime.now():
            event_datetime = event_datetime.replace(year=current_year + 1)

        return event_datetime.isoformat()
    else:
        return None

def addEvent(event_details):
    user_input = input("Enter event details (description, date, time, and attendee/s in any order): ")
    date_str, time_str, description, attendees = parse_input(user_input)

    event_datetime = format_datetime(date_str, time_str)

    if not event_datetime:
        print("Error: Unable to parse date and time. Please include both in your input.")
        return

    if not description:
        print("Error: No description provided. Please include a description for the event.")
        return

    # Format the event_datetime for output
    formatted_event_datetime = datetime.fromisoformat(event_datetime).strftime("%B %d, %Y, %I:%M %p")

    default_timezone = 'Asia/Manila'

    event = {
        'summary': description,
        'start': {
            'dateTime': event_datetime,
            'timeZone': default_timezone,
        },
        'end': {
            'dateTime': event_datetime,
            'timeZone': default_timezone,
        },
    }

    if attendees:
        event['attendees'] = [{'email': attendee} for attendee in attendees]

    created_event = service.events().insert(calendarId='primary', body=event).execute()

    # Print the event details and attendees
    print('Event created:')
    print('  Date and Time:', formatted_event_datetime)
    print('  Description:', created_event['summary'])
    if 'attendees' in created_event:
        print('  Attendees:')
        for attendee in created_event['attendees']:
            print('    -', attendee['email'])
    else:
        print('  No attendees')

if __name__ == '__main__':
    addEvent()