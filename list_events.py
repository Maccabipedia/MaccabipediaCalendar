from datetime import datetime
from cal_setup import get_calendar_service
from delete_event import delete_event


def get_events_list(calendar_id: str, time_min: str, num_of_events: int = 2500) -> list:
    """Returns list of events of specific calendar

    :param calendar_id: the calendar to extract events from
    :type: str
    :param time_min: from which date to start extract
    :type: str
    :param num_of_events: amount of events to extract. optional
    :type: int
    :return: A list of events
    :rtype: list
    """

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
        print('No upcoming events found')
    else:
        print(f'Found {len(events)} events:')
        for event in events:
            # delete_event(event['id'], calendar_id)  # TODO: Delete line
            print(event)
    return events


if __name__ == '__main__':
    cal_id = 'uvtou62l55g03ql7jq9qr7hjt0@group.calendar.google.com'  # id of maccabi games calendar
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    time = datetime(2011, 1, 1, 0, 0).isoformat() + 'Z'  # 'Z' indicates UTC time
    get_events_list(cal_id, time)
