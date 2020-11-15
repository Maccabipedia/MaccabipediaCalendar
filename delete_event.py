# Script to delete events from google calendar
import googleapiclient
from cal_setup import get_calendar_service


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
