from dataclasses import dataclass, field
from pathlib import Path

from config.logging import setup_logging
from config.settings import get_settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from models.schemas import CalendarEvent

logger = setup_logging(__name__)
settings = get_settings()

# Path to the Google service account credentials
_CURRENT_FOLDER = Path(__file__).parent.absolute()
_DEFAULT_CREDENTIALS_FILE_PATH = _CURRENT_FOLDER / "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/calendar"]


@dataclass
class GoogleCalendarService:
    """Handles interactions with Google Calendar API for a specific calendar."""

    calendar_id: str
    service: object | None = field(default=None, init=False)

    def __post_init__(self):
        """Initialize Google Calendar API service."""
        try:
            self.init_credentials_json()
            creds = service_account.Credentials.from_service_account_file(
                _DEFAULT_CREDENTIALS_FILE_PATH, scopes=SCOPES
            )
            self.service = build("calendar", "v3", credentials=creds)
            logger.info(f"Authenticated with Google Calendar API for {self.calendar_id}.")
        except Exception as e:
            msg = f"Failed to authenticate with Google Calendar API for {self.calendar_id}: {e}"
            logger.error(msg)
            self.service = None
            raise e

    def init_credentials_json(self):
        """Write to credentials.json from environment variable."""
        creds = settings.GOOGLE_CREDENTIALS
        logger.info(f"Writing to credentials.json from memory, json size: {len(creds)}")
        _DEFAULT_CREDENTIALS_FILE_PATH.write_text(creds)

    def create_event(self, event: CalendarEvent) -> str | bool:
        """Create a Google Calendar event for a match."""

        try:
            created_event = (
                self.service.events()  # type: ignore
                .insert(calendarId=self.calendar_id, body=event.model_dump())
                .execute()
            )
            logger.info(f"Event created in {self.calendar_id}: {created_event.get('htmlLink')}")
            return created_event.get("id")
        except Exception as e:
            logger.error(f"Failed to create event in {self.calendar_id}: {e}")
            return False

    def delete_event(self, event_id: str) -> bool:
        """Delete an event by its ID."""
        if not self.service:
            logger.error(
                f"Google Calendar service not available for {self.calendar_id}. Skipping event deletion."
            )
            return False

        try:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()  # type: ignore
            logger.info(f"Event {event_id} deleted from {self.calendar_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete event {event_id} from {self.calendar_id}: {e}")
            raise e

    def delete_all_events(self) -> bool:
        """Delete all events in the calendar."""
        try:
            events = self.list_events(
                fetch_after_this_time="1970-01-01T00:00:00Z", max_events_to_fetch=9999
            )
            if not events:
                logger.info(f"No events found in {self.calendar_id} to delete.")
                return True

            logger.info(f"Deleting all events in {self.calendar_id}...")
            for event in events:
                if event.id:
                    self.delete_event(event.id)
                else:
                    logger.warning(f"Event {event} has no ID, skipping deletion.")

            logger.info(f"All events deleted from {self.calendar_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete all events in {self.calendar_id}: {e}")
            return False

    def update_event(self, new_event: CalendarEvent, event_id: str) -> bool:
        """Update an existing event in the calendar."""

        try:
            event_result = (
                self.service.events()  # type: ignore
                .update(
                    calendarId=self.calendar_id,
                    eventId=event_id,
                    body={
                        "summary": new_event.summary,
                        "location": new_event.location,
                        "description": new_event.description,
                        "source": new_event.source,
                        "extendedProperties": new_event.extendedProperties,
                        "start": new_event.start,
                        "end": new_event.end,
                    },
                )
                .execute()
            )

            logger.info(f"Event updated in {self.calendar_id}")
            logger.info("Updated event:")
            logger.info(f"- id: {event_result['id']}")
            logger.info(f"- summary: {event_result['summary']}")
            logger.info(f"- starts at: {event_result['start']['dateTime']}")
            logger.info(f"- ends at: {event_result['end']['dateTime']}")
            logger.info(f"- location: {event_result['location']}")
            logger.info(f"- description: {event_result['description']}")
            logger.info(f"- extendedProperties: {event_result['extendedProperties']}")
            return True

        except Exception as e:
            logger.error(f"Failed to update event {event_id} in {self.calendar_id}: {e}")
            return False

    def list_events(
        self,
        fetch_after_this_time: str,
        max_events_to_fetch: int = settings.NUMBER_OF_EVENTS_TO_FETCH,
    ) -> list[CalendarEvent]:
        """List upcoming events in the calendar."""

        logger.info(f"Getting all the events starting after time: {fetch_after_this_time}")
        calendar_events: list[CalendarEvent] = []
        try:
            events_result = (
                self.service.events()  # type: ignore
                .list(
                    calendarId=self.calendar_id,
                    timeMin=fetch_after_this_time,
                    singleEvents=True,
                    maxResults=max_events_to_fetch,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            if not events:
                logger.info(f"No upcoming events found in {self.calendar_id}.")
            else:
                logger.info(f"Found {len(events)} upcoming events")
                # Convert events to CalendarEvent objects
                calendar_events = [CalendarEvent(**event) for event in events]

            return calendar_events

        except Exception as e:
            logger.error(f"Failed to list events in {self.calendar_id}: {e}")
            raise e

    def search_event_in_calendar(
        self, event: CalendarEvent, events_list: list[CalendarEvent]
    ) -> CalendarEvent | None:
        """
        Checking if the parsed match is exists in the calendar by comparing links to game page in the official site.
        If it is, return the existing event, else return empty

        :param event: event to search
        :param events_list: list of events to compare to

        :return: event or empty object
        """
        if not events_list:
            return None

        for temp_event in events_list:
            if (
                event.extendedProperties["shared"]["url"]
                == temp_event.extendedProperties["shared"]["url"]
            ):
                if temp_event.id:
                    return temp_event
                else:
                    return event

        return None

    def sync_future_events_to_calendar(
        self, events_list: list[CalendarEvent], curr_events_list: list[CalendarEvent]
    ) -> bool:
        logger.info("--- Adding & Updating Events: ---")
        try:
            for event in events_list:
                curr_event = self.search_event_in_calendar(event, curr_events_list)
                if curr_event:
                    if (
                        event.summary != curr_event.summary
                        or event.description != curr_event.description
                        or event.start != curr_event.start
                        or event.location != curr_event.location
                    ):
                        self.update_event(event, curr_event.id)
                else:
                    self.create_event(event)
            return True
        except Exception as e:
            logger.error(f"Failed to sync future events to calendar: {e}")
            raise e

    def delete_unnecessary_events(
        self,
        events_list: list[CalendarEvent],
        future_calendars_events: list[CalendarEvent],
    ) -> bool:
        """
        Deleting canceled/delayed/irrelevant events.
        Event which is in the calendar but not in the events list will be deleted
        """

        logger.info("--- Deleting Events: ---")
        try:
            for event in future_calendars_events:
                exist_event = self.search_event_in_calendar(event, events_list)

                if not exist_event or exist_event == {}:
                    logger.info(f"Deleting event {event.summary}, id: {event.id}")
                    self.delete_event(event.id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete unnecessary events: {e}")
            return False
