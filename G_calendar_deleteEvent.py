# G_calendar_deleteEvent.py

from googleapiclient.discovery import build
from G_calendar_auth import get_credentials
from datetime import datetime, timedelta

creds = get_credentials()
service = build('calendar', 'v3', credentials=creds)

def list_upcoming_events(num_events=10):
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=num_events, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []

    print('Upcoming events:')
    for i, event in enumerate(events, 1):
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
        formatted_time = start_time.strftime("%B %d, %Y, %I:%M %p")
        print(f"{i}. {formatted_time} - {event['summary']}")

    return events

def delete_event(event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    print('Event deleted.')

def deleteEvent():
    events = list_upcoming_events()
    
    if not events:
        return

    while True:
        try:
            choice = int(input("Enter the number of the event you want to delete (0 to cancel): "))
            if choice == 0:
                print("Operation cancelled.")
                return
            if 1 <= choice <= len(events):
                event_to_delete = events[choice - 1]
                confirm = input(f"Are you sure you want to delete '{event_to_delete['summary']}'? (y/n): ")
                if confirm.lower() == 'y':
                    delete_event(event_to_delete['id'])
                else:
                    print("Deletion cancelled.")
                break
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == '__main__':
    deleteEvent()