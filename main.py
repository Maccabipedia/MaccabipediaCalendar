import logging
from datetime import datetime
from typing import Dict, List

from edit_event import upload_event, update_event, delete_event
from get_lists import fetch_games_from_calendar
from parse_games import parse_games_from_url
from my_typing import Event

_logger = logging.getLogger(__name__)


def event_already_exist(event: Dict, events_list: List) -> Dict:
    """
    Checking if the parsed game is exists in the calendar by comparing links to game page in the official site.
    If it is, return the existing event, else return empty

    :param event: event to search
    :param events_list: list of events to compare to
    :return: event or empty object
    """
    if events_list:
        for temp_event in events_list:
            if 'extendedProperties' in temp_event and 'extendedProperties' in event:
                if event['extendedProperties']['shared']['url'] == temp_event['extendedProperties']['shared']['url']:
                    if 'id' in temp_event:
                        return temp_event
                    else:
                        return event

    return {}


def add_update_events(events_list: List[Event], curr_events_list: List[Event], calendar_id: str) -> None:
    """
    Updating & adding upcoming games

    :param events_list: list of the most updated events
    :param curr_events_list: list of the current events
    :param calendar_id: id of calendar to add games to
    """
    for event in events_list:
        curr_event = event_already_exist(event, curr_events_list)
        if curr_event != {}:
            if event['summary'] != curr_event['summary'] or event['description'] != curr_event['description'] \
                    or event['start'] != curr_event['start'] or event['location'] != curr_event['location']:
                update_event(event, curr_event['id'], calendar_id)
        else:
            upload_event(event, calendar_id)


def delete_unnecessary_events(events_list: List, curr_events_list: List, calendar_id: str) -> None:
    """
    Deleting canceled/delayed/irrelevant events.
    Event which is in the calendar but not in the events list will be deleted

    :param events_list: list of the most updated events
    :param curr_events_list: list of the current events
    :param calendar_id: id of calendar to delete from
    """
    if curr_events_list:
        for event in curr_events_list:
            exist_event = event_already_exist(event, events_list)
            if exist_event == {}:
                _logger.info(f"Deleting event {event['summary']}")
                delete_event(event['id'], calendar_id)


def update_last_game(url: str, calendar_id: str) -> None:
    """
    Updating the last game result & adding link to game page at maccabipedia

    :param url: URL of the season game results
    :param calendar_id: id of calendar to update
    """
    last_game = parse_games_from_url(url, True)[0]
    last_event = fetch_games_from_calendar(calendar_id, last_game['start']['dateTime'] + '+02:00', 1)[0]
    if 'extendedProperties' in last_game and 'extendedProperties' in last_event:
        if last_game['extendedProperties']['shared']['url'] == last_event['extendedProperties']['shared']['url']:
            if last_event['extendedProperties']['shared']['result'] == '':
                update_event(last_game, last_event['id'], calendar_id)


def add_history_games(seasons: List, calendar_id: str) -> None:
    """
    Loop over all past seasons URLs and adding the games to the calendar

    :param seasons: list of URLs to seasons list of games
    :param calendar_id: id of calendar to update
    """
    for season in seasons:
        events = parse_games_from_url(season, False)
        for event in events:
            upload_event(event, calendar_id)


def main(calendar_id):
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

    seasons = [season_12_13, season_13_14, season_14_15, season_15_16, season_16_17, season_17_18, season_18_19,
               season_19_20, season_20_21]

    # add_history_games(seasons, calendar_id)

    time = datetime.utcnow().isoformat() + 'Z'  # current datetime - to update and add upcoming games only
    upcoming_events = parse_games_from_url(upcoming_games, False)
    curr_events = fetch_games_from_calendar(calendar_id, time)

    add_update_events(upcoming_events, curr_events, calendar_id)
    delete_unnecessary_events(upcoming_events, curr_events, calendar_id)
    update_last_game(seasons[len(seasons) - 1], calendar_id)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    maccabipedia_games_calendar_id = 'uvtou62l55g03ql7jq9qr7hjt0@group.calendar.google.com'

    main(maccabipedia_games_calendar_id)
