from datetime import datetime

from parse_games import parse_games
from upload_event import upload_event
from update_event import update_event
from list_events import get_events_list
from delete_event import delete_event


# Check if game if already on the calendar by comparing the links to game page in the official site
def event_already_exist(event: dict, curr_events: list) -> str:
    """
    Checking if the parsed game is exists in the calendar.
    If it is, return the id of the existing event, else return empty str

    :param event: event to search
    :type event: dict
    :param curr_events: list of events to compare to
    :type curr_events: list
    :return: event id or empty str
    :rtype: str
    """

    if curr_events:
        for curr_event in curr_events:
            if 'extendedProperties' in curr_event and 'extendedProperties' in event:
                if event['extendedProperties']['shared']['url'] == curr_event['extendedProperties']['shared']['url']:
                    if 'id' in curr_event:
                        return curr_event['id']
                    else:
                        return event['id']

    return ''


def main():
    calender_id = 'uvtou62l55g03ql7jq9qr7hjt0@group.calendar.google.com'

    season_12_13 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=2#content'
    season_13_14 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=74#content'
    season_14_15 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=75#content'
    season_15_16 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=76#content'
    season_16_17 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=77#content'
    season_17_18 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=78#content'
    season_18_19 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=79#content'
    season_19_20 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=80#content'
    season_20_21 = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season=81#content'
    upcoming_games = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%9c%d7%95%d7%97-%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d/'

    # TODO: Delete all events. add all the seasons again with links to game page in maccabipedia

    seasons = [season_12_13, season_13_14, season_14_15, season_15_16, season_16_17, season_17_18, season_18_19,
               season_19_20, season_20_21]

    time = datetime.utcnow().isoformat() + 'Z'
    curr_events = get_events_list(calender_id, time)
    # url - the URL to scrape from
    url = upcoming_games
    new_events = parse_games(url, False)
    # updating & adding upcoming games
    for event in new_events:
        event_id = event_already_exist(event, curr_events)
        if event_id != '':
            # TODO: Add comparison to avoid updating unchanged events (purpose: reduce syncing)
            update_event(event, event_id, calender_id)
        else:
            upload_event(event, calender_id)

    # deleting canceled/delayed/irrelevant events
    if curr_events:
        for event in curr_events:
            event_id = event_already_exist(event, new_events)
            if event_id == '':
                delete_event(event['id'], calender_id)

    # updating last game result
    url = seasons[len(seasons) - 1]
    last_game_update = parse_games(url, True)[0]
    last_event = get_events_list(calender_id, last_game_update['start']['dateTime'] + '+02:00', 1)[0]
    if 'extendedProperties' in last_game_update and 'extendedProperties' in last_event:
        if last_game_update['extendedProperties']['shared']['url'] == last_event['extendedProperties']['shared']['url']:
            if last_event['extendedProperties']['shared']['result'] == '':
                update_event(last_game_update, last_event['id'], calender_id)


if __name__ == '__main__':
    main()
