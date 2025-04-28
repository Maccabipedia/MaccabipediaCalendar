# MaccabipediaCalendar - Copilot Instructions

## Purpose
This document provides guidance for GitHub Copilot to generate code that follows our team's standards and practices. These instructions help ensure that AI-generated code aligns with our project architecture, coding conventions, and quality expectations.

## Project Overview
The MaccabipediaCalendar project is a Python application that scrapes match schedules and results for Maccabi Tel Aviv sports teams from official websites, then synchronizes this data with Google Calendar. The application provides automated calendar updates for different sports including football, basketball, volleyball, and handball.

## Development Guidelines

### Backend Guidelines
You are a senior fullstack Python, engineer with extensive experience with beautifulSoup library and a preference for clean programming and design patterns.
Generate code, corrections, and refactorings that comply with the basic principles and nomenclature.

### Code Style, Standards, Best Practices
- Use type annotations for all function parameters and return values
- Use logging instead of print statements
- Keep functions focused on single responsibility
- Prefer to use Pydantic models
- Follow the established patterns for error handling
- Update tests when adding new functionality
- Document new functions and methods with docstrings
- Limit line length to 100 characters (as configured in ruff)
- Follow the linting rules specified in pyproject.toml including F, E, W, PL, RUF, I, PIE
- Try to always declare the type of each variable and function (parameters and return value).
- Use the most updated dependencies unless stated otherwise.

### Simplicity Guidelines
- **Prefer simplicity over complexity** - Write code that is easy to understand at first glance.
- **Avoid over-engineering** - Don't add layers of abstraction unless there's a clear benefit.
- **Do not over-generalize** - Create specific solutions for specific problems unless generalization is explicitly required.
- **Minimize indirection** - Each level of indirection adds cognitive load; keep it to a minimum.
- **Avoid premature optimization** - Focus on writing clear, correct code first. Optimize only when necessary and based on measurements.

### Core Architecture
- **Scrapers**: Modules that extract match data from various sports websites
- **Google Calendar API**: Integration to create, update, and delete calendar events
- **Event Management**: Logic to synchronize website data with calendar events

### Key Files and Components
- **`app/scrapers/`**: Contains scrapers for different sports
- **`app/google_calendar/`**: Google Calendar API integration
- **`app/models/`**: Data models for events and matches
- **`app/config/`**: Configuration and settings

### Adding a New Sport Scraper
1. Create a new file in `app/scrapers/` (e.g., `basketball_scraper.py`)
2. Implement the scraper class that extends `BaseScraper`
3. Implement required methods: `build_seasons_links()`, `fetch_matches_from_site()`, `handle_match()`
4. Update the main entry point to use the new scraper

### Calendar Events Structure
Event data should follow this structure:
```python
event = {
    "summary": "Team vs Opponent - Home/Away",
    "location": "Stadium Name",
    "description": "Competition details, result, etc.",
    "start": {"dateTime": start_date, "timeZone": time_zone},
    "end": {"dateTime": end_date, "timeZone": time_zone},
    "source": {"url": "original_source_url", "title": "Page Title"},
    "extendedProperties": {"shared": {"url": "match_page_url", "result": "score"}}
}
```

### Environment Variables
The following environment variables are required:

- `GOOGLE_CREDENTIALS`: JSON string with Google API service account credentials
- `FOOTBALL_CALENDAR_ID`, `BASKETBALL_CALENDAR_ID`, etc.: Calendar IDs for different sports
- `CALENDAR_TO_UPDATE`: Which sport calendar to update (default: "football")

```.env
FOOTBALL_CALENDAR_ID="id1@group.calendar.google.com"
BASKETBALL_CALENDAR_ID="id2@group.calendar.google.com"
VOLLEYBALL_CALENDAR_ID="id3@group.calendar.google.com"
HANDBALL_CALENDAR_ID="id4@group.calendar.google.com"

GOOGLE_CREDENTIALS='YOUR_JSON_STRING'
```

Remember to adapt these general guidelines to the specific context of each task and the established patterns in the codebase.