import logging
import re

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings.
    Injecting from environment variables or .env file, by that order.
    Set default value if key isn't exist in environment variables or .env file
    """

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    # Google Credentials
    GOOGLE_CREDENTIALS: str = "missing_json"

    # Calendars settings
    FOOTBALL_CALENDAR_ID: str = "MISSING_FOOTBALL_CALENDAR_ID"
    BASKETBALL_CALENDAR_ID: str = "MISSING_BASKETBALL_CALENDAR_ID"
    VOLLEYBALL_CALENDAR_ID: str = "MISSING_VOLLEYBALL_CALENDAR_ID"
    HANDBALL_CALENDAR_ID: str = "MISSING_HANDBALL_CALENDAR_ID"

    @property
    def calendars(self) -> dict[str, str]:
        """
        Dynamically collects all calendar IDs from environment variables.
        Looks for variables ending with _CALENDAR_ID and extracts the calendar sport type.
        """
        result = {}
        for key, value in self.__dict__.items():
            # Match keys that end with _CALENDAR_ID
            match = re.match(r"^(.+)_CALENDAR_ID$", key)
            if match:
                calendar_sport_type = match.group(1).lower()
                result[calendar_sport_type] = value
        return result

    NUMBER_OF_EVENTS_TO_FETCH: int = 3000

    DELETE_ALL_MATCHES: bool = False
    ADD_HISTORY_MATCHES: bool = True

    # Calendar to update
    CALENDAR_TO_UPDATE: str = "football"

    # Logging Settings
    DEBUG_MODE: bool = False
    if DEBUG_MODE:
        PYTHON_LOG_LEVEL: int = logging.DEBUG
    else:
        PYTHON_LOG_LEVEL: int = logging.INFO
    PYTHON_LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(process)d | %(name)s | %(filename)s:%(lineno)d | %(message)s"


settings = Settings()
