from typing import Any

from pydantic import BaseModel


class EventDate(BaseModel):
    dateTime: str
    timeZone: str


class CalendarEvent(BaseModel):
    id: str = ""
    summary: str
    location: str
    description: str
    start: EventDate
    end: EventDate
    source: dict[str, str]
    extendedProperties: dict[str, Any]
