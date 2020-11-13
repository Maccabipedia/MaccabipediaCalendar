from datetime import datetime, timedelta
from cal_setup import get_calendar_service


def main():
    # update the event to tomorrow 8 AM IST
    service = get_calendar_service()

    d = datetime.now().date()
    tomorrow = datetime(d.year, d.month, d.day, 8) + timedelta(days=1)
    start = tomorrow.isoformat()
    end = (tomorrow + timedelta(hours=3)).isoformat()

    event_result = service.events().update(
        calendarId='primary',
        eventId='<place your event ID here>',  # TODO: Put event id here
        body={
            "summary": 'Updated Game',
            "description": 'This is a tutorial example of automating google calendar with python, updated time.',
            "start": {"dateTime": start, "timeZone": 'Asia/Jerusalem'},
            "end": {"dateTime": end, "timeZone": 'Asia/Jerusalem'},
        },
    ).execute()

    print("updated event")
    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start']['dateTime'])
    print("ends at: ", event_result['end']['dateTime'])


if __name__ == '__main__':
    main()
