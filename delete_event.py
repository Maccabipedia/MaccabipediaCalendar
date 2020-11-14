# Script to delete events from google calendar
import googleapiclient
from cal_setup import get_calendar_service


def delete_event(calendar_id, event_id):
    # Delete the event
    service = get_calendar_service()
    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()
    except googleapiclient.errors.HttpError:
        print("Failed to delete event")

    print("Event deleted")


# if __name__ == '__main__':
#     delete_event()
