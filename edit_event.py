import logging
import googleapiclient
from typing import Dict
from cal_setup import get_calendar_service

_logger = logging.getLogger(__name__)


def upload_event(event: Dict, calendar_id: str) -> None:
    service = get_calendar_service()

    event_result = service.events().insert(calendarId=calendar_id, body=event).execute()

    _logger.info("Created event:")
    _logger.info(f"- id: {event_result['id']}")
    _logger.info(f"- summary: {event_result['summary']}")
    _logger.info(f"- starts at: {event_result['start']['dateTime']}")
    _logger.info(f"- ends at: {event_result['end']['dateTime']}")


def update_event(new_event: Dict, event_id: str, calendar_id: str) -> None:
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

    _logger.info("Updated event:")
    _logger.info(f"- id: {event_result['id']}")
    _logger.info(f"- summary: {event_result['summary']}")
    _logger.info(f"- starts at: {event_result['start']['dateTime']}")
    _logger.info(f"- ends at: {event_result['end']['dateTime']}")


def delete_event(event_id: str, calendar_id: str) -> None:
    """
    Deleting event from calendar

    :param event_id: id of the event to delete
    :param calendar_id: id of the calendar
    """
    service = get_calendar_service()
    try:
        _logger.info(f'Deleting event with ID: {event_id}')

        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()

        _logger.info("Event deleted")
    except googleapiclient.errors.HttpError:
        _logger.exception("Failed to delete event due to:")
