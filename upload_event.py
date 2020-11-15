from datetime import datetime, timedelta
from cal_setup import get_calendar_service


def upload_event(event: dict, calendar_id: str) -> None:
    service = get_calendar_service()

    event_result = service.events().insert(calendarId=calendar_id, body=event).execute()

    print("Created event:")
    print("- id: ", event_result['id'])
    print("- summary: ", event_result['summary'])
    print("- starts at: ", event_result['start']['dateTime'])
    print("- ends at: ", event_result['end']['dateTime'])
