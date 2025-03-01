import os
import sys
from datetime import datetime, timezone
from typing import Any

import requests
from dotenv import load_dotenv

from calendar_operations import (
    Event,
    delete_event,
    fetch_games_from_calendar,
    update_event,
    upload_event,
)
from config.logging import setup_logging
from google_calendar_api import initialize_global_google_service_account_from_memory_json
from maccabi_tlv_site import fetch_games_from_maccabi_tlv_site

logger = setup_logging(__name__)

SEASON_LINK_UNFORMATTED = "https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season={season_number}#content"
UPCOMING_GAMES_LINK = "https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%9c%d7%95%d7%97-%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d/"


def delete_all_events(calendar_id: str) -> None:
    logger.info("--- Deleting All Events: ---")
    events = fetch_games_from_calendar(calendar_id, "2011-10-10T10:10:10.644170Z")
    for event in events:
        logger.info(f"Deleting event {event['summary']}")
        delete_event(event["id"], calendar_id)


def search_event_in_calendar(event: dict[str, Any], events_list: list[Event]) -> dict[str, Any]:
    """
    Checking if the parsed game is exists in the calendar by comparing links to game page in the official site.
    If it is, return the existing event, else return empty

    :param event: event to search
    :param events_list: list of events to compare to
    :return: event or empty object
    """

    if events_list:
        for temp_event in events_list:
            if "extendedProperties" in temp_event and "extendedProperties" in event:
                if (
                    event["extendedProperties"]["shared"]["url"]
                    == temp_event["extendedProperties"]["shared"]["url"]
                ):
                    if "id" in temp_event:
                        return temp_event
                    else:
                        return event

    return {}


def sync_future_games_to_calendar(
    events_list: list[Event], curr_events_list: list[Event], calendar_id: str
) -> None:
    logger.info("--- Adding & Updating Events: ---")

    for event in events_list:
        curr_event = search_event_in_calendar(event, curr_events_list)
        if curr_event != {}:
            if (
                event["summary"] != curr_event["summary"]
                or event["description"] != curr_event["description"]
                or event["start"] != curr_event["start"]
                or event["location"] != curr_event["location"]
            ):
                update_event(event, curr_event["id"], calendar_id)
        else:
            upload_event(event, calendar_id)


def delete_unnecessary_events(
    events_list: list[Event], future_calendars_events: list[Event], calendar_id: str
) -> None:
    """
    Deleting canceled/delayed/irrelevant events.
    Event which is in the calendar but not in the events list will be deleted
    """
    logger.info("--- Deleting Events: ---")

    for event in future_calendars_events:
        exist_event = search_event_in_calendar(event, events_list)

        if exist_event == {}:
            logger.info(f"Deleting event {event['summary']}")
            delete_event(event["id"], calendar_id)


def update_last_game(url: str, calendar_id: str) -> None:
    """
    Updating the last game result & adding link to game page at maccabipedia
    """

    logger.info("--- Updating Last Game: ---")
    last_game = fetch_games_from_maccabi_tlv_site(url, to_update_last_game=True)[0]
    last_event = fetch_games_from_calendar(
        calendar_id, last_game["start"]["dateTime"] + "+02:00", 1
    )[0]

    if "extendedProperties" in last_game and "extendedProperties" in last_event:
        if (
            last_game["extendedProperties"]["shared"]["url"]
            == last_event["extendedProperties"]["shared"]["url"]
        ):
            if last_event["extendedProperties"]["shared"]["result"] == "":
                update_event(last_game, last_event["id"], calendar_id)


def add_history_games(seasons: list[str], calendar_id: str) -> None:
    """
    Loop over all past seasons URLs and adding the games to the calendar
    """

    for season in seasons:
        events = fetch_games_from_maccabi_tlv_site(season, to_update_last_game=False)
        for event in events:
            upload_event(event, calendar_id)


def build_maccabi_tlv_site_seasons_links() -> list[str]:
    seasons_links = []

    logger.info("Building season links")

    current_season_number = 74  # 2013/14
    while (
        "המשחק האחרון"
        in requests.get(SEASON_LINK_UNFORMATTED.format(season_number=current_season_number)).text
    ):
        seasons_links.append(SEASON_LINK_UNFORMATTED.format(season_number=current_season_number))
        logger.info(
            f"Added new season: {current_season_number - 62}/{str(current_season_number - 61)[-2:]}"
        )

        current_season_number += 1

    logger.info(f"Finished to build season links, total seasons: {len(seasons_links)}")
    return seasons_links


def main(google_credentials: str, calendar_id: str) -> None:
    # current datetime - to update and add upcoming games only
    current_time = datetime.utcnow().isoformat() + "Z"
    logger.info(current_time)

    # current datetime - to update and add upcoming games only
    current_time2 = datetime.now(timezone.utc).isoformat() + "Z"
    logger.info(current_time2)

    initialize_global_google_service_account_from_memory_json(google_credentials)
    seasons = build_maccabi_tlv_site_seasons_links()

    future_calendars_events = fetch_games_from_calendar(
        calendar_id, fetch_after_this_time=current_time
    )
    upcoming_games_from_maccabi_tlv_site = fetch_games_from_maccabi_tlv_site(
        UPCOMING_GAMES_LINK, to_update_last_game=False
    )
    sync_future_games_to_calendar(
        upcoming_games_from_maccabi_tlv_site, future_calendars_events, calendar_id
    )
    delete_unnecessary_events(
        upcoming_games_from_maccabi_tlv_site, future_calendars_events, calendar_id
    )
    update_last_game(seasons[len(seasons) - 1], calendar_id)

    # Uncomment this in case you need to old games
    # add_history_games(seasons, calendar_id)


def entry_point() -> None:
    # noinspection PyBroadException
    try:
        logger.info("----- Starting -----")
        load_dotenv()

        google_credentials = os.environ["GOOGLE_CREDENTIALS"]
        calendar_id = os.environ["CALENDAR_ID"]

        main(google_credentials, calendar_id)
        logger.info("----- Done -----")
    except Exception:
        logger.exception("Unhandled exception (exiting the program): ")
        sys.exit(1)


if __name__ == "__main__":
    entry_point()
