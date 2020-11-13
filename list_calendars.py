from cal_setup import get_calendar_service


def main():
    service = get_calendar_service()
    # Call the Calendar API
    print('Getting list of calendars')
    calendars_result = service.calendarList().list().execute()

    calendars = calendars_result.get('items', [])

    if not calendars:
        print('No calendars found.')
    for calendar in calendars:
        summary = calendar['summary']
        desc = calendar['description'] if calendar.get('description') else 'null'
        cal_id = calendar['id']
        primary = "- Primary \n" if calendar.get('primary') else ""
        print("Calendar: \n- Summary: %s\n- Desc: %s\n- ID: %s\n%s" % (summary, desc, cal_id, primary))


if __name__ == '__main__':
    main()
