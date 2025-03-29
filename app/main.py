import sys
from datetime import datetime, timezone

from config.logging import setup_logging
from config.settings import get_settings
from google_calendar.google_calendar_api import GoogleCalendarService
from scrapers.football_scraper import football_scraper

logger = setup_logging(__name__)
settings = get_settings()


def update_football_calendar(calendar_service: GoogleCalendarService):
    """
    Update the calendar with upcoming matches from the Maccabi TLV site.
    """
    # Current DateTime - Update and add upcoming matches only
    current_time = datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z"
    logger.info(f"Current time: {current_time}")


    ft_scraper = football_scraper()

    # Build seasons links from the website
    seasons_links = ft_scraper.build_seasons_links()

    # Get future matches from calendar
    future_match_events = calendar_service.list_events(fetch_after_this_time=str(current_time))
    logger.info(f"Future match events: {future_match_events}")

    # Fetch matches from Maccabi TLV Site
    upcoming_matches = ft_scraper.fetch_matches_from_site()
    logger.info(f"Upcoming matches: {upcoming_matches}")

    logger.info("Syncing future matches to calendar")
    calendar_service.sync_future_events_to_calendar(upcoming_matches, future_match_events)

    logger.info("Deleting unnecessary events")
    calendar_service.delete_unnecessary_events(upcoming_matches, future_match_events)

    logger.info("Updating last match")
    last_season_link = seasons_links[-1]
    last_match = ft_scraper.fetch_matches_from_site(last_season_link, to_update_last_match=True)[0]
    last_match_event = calendar_service.list_events(last_match.start.dateTime + "+02:00", 1)[0]
    if (
        last_match_event.extendedProperties["shared"]["url"]
        == last_match.extendedProperties["shared"]["url"]
    ):
        if last_match_event.extendedProperties["shared"]["result"] == "":
            calendar_service.update_event(last_match, last_match_event.id)

    # Add history matches
    if settings.ADD_HISTORY_MATCHES:
        logger.info("Adding history matches")
        for season in seasons_links:
            logger.info(f"Adding history matches from season: {season}")
            events = ft_scraper.fetch_matches_from_site(season, to_update_last_match=False)
            calendar_service.sync_future_events_to_calendar(events, [])
            logger.info(f"Added {len(events)} events from season: {season}")
    else:
        logger.info("Skipping history matches")


def entry_point() -> None:
    try:
        logger.info("------------------------------")
        logger.info("---------- Starting ----------")
        logger.info("------------------------------")
        logger.info("")

        logger.info(f"Updating {settings.CALENDAR_TO_UPDATE} calendar")
        calendar_to_update = settings.calendars[settings.CALENDAR_TO_UPDATE]
        logger.debug(f"Calendar ID: {calendar_to_update}")
        calendar_service = GoogleCalendarService(calendar_to_update)

        if settings.DELETE_ALL_MATCHES:
            logger.info("Deleting all matches from calendar")
            calendar_service.delete_all_events()
            logger.info("All matches deleted")

        if settings.CALENDAR_TO_UPDATE == "football":
            update_football_calendar(calendar_service)
        else:
            raise Exception("Unsupported calendar type. Please check the settings.")

        logger.info("")
        logger.info("------------------------------")
        logger.info("------------ Done ------------")
        logger.info("------------------------------")
    except Exception:
        logger.exception("Unhandled exception (exiting the program): ")
        sys.exit(1)


if __name__ == "__main__":
    entry_point()
