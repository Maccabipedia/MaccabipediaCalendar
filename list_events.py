import datetime
from datetime import datetime
from cal_setup import get_calendar_service
from delete_event import delete_event


def get_list_events(calendar_id, time_min, num_of_events):
    service = get_calendar_service()
    # Call the Calendar API
    print(f'Getting List of {num_of_events} events:\n')
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=time_min,
        maxResults=num_of_events, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    for event in events:
        # delete_event(calendar_id, event['id'])
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['id'], event['summary'], event['description'])


if __name__ == '__main__':
    cal_id = 'uvtou62l55g03ql7jq9qr7hjt0@group.calendar.google.com'
    time = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time, time = now
    # time = datetime(2012, 1, 1, 0, 0).isoformat() + 'Z'
    get_list_events(cal_id, time, 10)
