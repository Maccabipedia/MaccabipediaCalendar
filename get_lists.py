import logging
from datetime import datetime
from typing import List, Optional

from cal_setup import get_calendar_service
from my_typing import Event

_logger = logging.getLogger(__name__)


_DEFAULT_NUMBER_OF_EVENTS_TO_FETCH = 2500


def get_calendars_list() -> List[str]:
    """
    Returns list of calendars

    :return: A list of calendars
    """

    service = get_calendar_service()
    # Call the Calendar API
    _logger.info('Getting list of calendars...')
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])

    if not calendars:
        _logger.info('No calendars found')

    _logger.info(f'{len(calendars)} calendars found:\n')
    for calendar in calendars:
        summary = calendar['summary']
        desc = calendar['description'] if calendar.get('description') else 'null'
        cal_id = calendar['id']
        primary = '- Primary \n' if calendar.get('primary') else ''
        _logger.info(f'Calendar: \n- Summary: {summary}\n- Desc:{desc}\n- ID: {cal_id}\n{primary}')

    return calendars


def fetch_games_from_calendar(calendar_id: str, fetch_after_this_time: str,
                              num_of_events: Optional[int] = _DEFAULT_NUMBER_OF_EVENTS_TO_FETCH) -> List[Event]:
    """
    Returns list of events of specific calendar

    :param calendar_id: the calendar to extract events from
    :param fetch_after_this_time: from which date to start extract
    :param num_of_events: amount of events to extract. optional
    :return: A list of events
    """

    service = get_calendar_service()
    # Call the Calendar API
    _logger.info(f'Getting List of existing events:')
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=fetch_after_this_time,
        singleEvents=True,
        maxResults=num_of_events,
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        _logger.info('No upcoming events found')
    else:
        _logger.info(f'Found {len(events)} events:')
        # for event in events:
        # delete_event(event['id'], calendar_id)  # Deleting all events

    return events


if __name__ == '__main__':
    # get_calendars_list()
    maccabi_calendar_id = 'uvtou62l55g03ql7jq9qr7hjt0@group.calendar.google.com'  # id of maccabi games calendar
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    time = datetime(2011, 1, 1, 0, 0).isoformat() + 'Z'  # 'Z' indicates UTC time
    fetch_games_from_calendar(maccabi_calendar_id, time)
