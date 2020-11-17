import googleapiclient
from cal_setup import get_calendar_service


def upload_event(event: dict, calendar_id: str) -> None:
    service = get_calendar_service()

    event_result = service.events().insert(calendarId=calendar_id, body=event).execute()

    print("Created event:")
    print("- id: ", event_result['id'])
    print("- summary: ", event_result['summary'])
    print("- starts at: ", event_result['start']['dateTime'])
    print("- ends at: ", event_result['end']['dateTime'])


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


def delete_event(event_id: str, calendar_id: str) -> None:
    """Deleting event from calendar

    :param event_id: id of the event to delete
    :type event_id: str
    :param calendar_id: id of the calendar
    :type calendar_id: str
    """

    service = get_calendar_service()
    try:
        print(f'Deleting event with ID: {event_id}')
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()
    except googleapiclient.errors.HttpError:
        print("Failed to delete event")

    print("Event deleted")


