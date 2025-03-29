from typing import Any

from pydantic import BaseModel, field_validator


class EventDate(BaseModel):
    dateTime: str
    timeZone: str = "Asia/Jerusalem"  # Default timezone


class CalendarEvent(BaseModel):
    id: str = ""
    summary: str
    location: str | None = None
    description: str
    start: EventDate
    end: EventDate
    source: dict[str, str]
    extendedProperties: dict[str, Any]

    @field_validator("start", "end")
    def ensure_timezone(cls, v):
        if isinstance(v, dict) and "dateTime" in v and "timeZone" not in v:
            v["timeZone"] = "Asia/Jerusalem"  # Asia/Jerusalem timezone
        return v
