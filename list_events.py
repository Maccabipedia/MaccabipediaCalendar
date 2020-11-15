import datetime
from datetime import datetime
from cal_setup import get_calendar_service
from delete_event import delete_event


def get_list_events(calendar_id, time_min, num_of_events=2500):
    service = get_calendar_service()
    # Call the Calendar API
    print(f'Getting List of existing events:')
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        singleEvents=True,
        maxResults=num_of_events,
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    for event in events:
        delete_event(event['id'], calendar_id)
        # print(event)
    return events


if __name__ == '__main__':
    cal_id = 'uvtou62l55g03ql7jq9qr7hjt0@group.calendar.google.com'
    # time = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time, time = now
    time = datetime(2011, 1, 1, 0, 0).isoformat() + 'Z'
    get_list_events(cal_id, time)
