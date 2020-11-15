from cal_setup import get_calendar_service


def update_event(new_event: dict, event_id: str, calendar_id: str) -> None:
    service = get_calendar_service()

    event_result = service.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body={
            "summary": new_event['summary'],
            "location": new_event['location'],
            "description": new_event['description'],
            "source": new_event['source'],
            "extendedProperties": new_event['extendedProperties'],
            "start": new_event['start'],
            "end": new_event['end'],
        },
    ).execute()

    print("Updated event:")
    print("- id: ", event_result['id'])
    print("- summary: ", event_result['summary'])
    print("- starts at: ", event_result['start']['dateTime'])
    print("- ends at: ", event_result['end']['dateTime'])
