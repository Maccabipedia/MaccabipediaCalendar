from cal_setup import get_calendar_service


def get_calendars_list() -> list:
    """Returns list of calendars

    :return: A list of calendars
    :rtype: list
    """
    service = get_calendar_service()
    # Call the Calendar API
    print('Getting list of calendars...')
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])

    if not calendars:
        print('No calendars found')

    print(f'{len(calendars)} calendars found:\n')
    for calendar in calendars:
        summary = calendar['summary']
        desc = calendar['description'] if calendar.get('description') else 'null'
        cal_id = calendar['id']
        primary = '- Primary \n' if calendar.get('primary') else ''
        print(f'Calendar: \n- Summary: {summary}\n- Desc:{desc}\n- ID: {cal_id}\n{primary}')

    return calendars


if __name__ == '__main__':
    get_calendars_list()
