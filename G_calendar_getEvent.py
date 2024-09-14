from googleapiclient.discovery import build
from datetime import datetime
from G_calendar_auth import get_credentials

creds = get_credentials() #this function calls the credentials authentication from G_calendar_auth.py
service = build('calendar', 'v3', credentials=creds) # this function initializes the calendar service

def getEvent():
    """Shows basic usage of the Google Calendar API.
    Lists the next 10 events on the user's calendar.
    """
# Call the Calendar API
now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
print('Getting Events...')
events_result = service.events().list(calendarId='primary', timeMin=now,
                                      maxResults=10, singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

if not events:
    print('No upcoming events found.')
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    event_time_str = start.split(' ')[0]  # Get only the datetime part
    event_time = datetime.fromisoformat(event_time_str)
    formatted_time = event_time.strftime("%B %d, %Y, %I:%M %p")
    
    # Check if start contains a space and has at least two parts
    start_parts = start.split(' ')
    if len(start_parts) > 1:
        event_summary = start_parts[1]  # Get the event summary
    else:
        event_summary = event.get('summary', "No title available")  # Use event title if no summary

    print(f"{formatted_time} - {event_summary}")

if __name__ == '__main__':
   getEvent()