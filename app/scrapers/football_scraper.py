import json
import re
from datetime import datetime, timedelta

import bs4
import httpx
from bs4 import BeautifulSoup
from config.logging import setup_logging
from models.schemas import CalendarEvent, EventDate

logger = setup_logging(__name__)


class football_scraper:
    """
    Scraper for Maccabi Tel Aviv football matches
    """

    def __init__(self):
        self.season_link_unformatted: str = "https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/?season={season_number}#content"
        self.upcoming_matches_url: str = "https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%9c%d7%95%d7%97-%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d/"
        self.seasons_links: list[str] = []

    def build_seasons_links(self):
        # Build seasons links from the website

        logger.info("Building season links")

        season_num = 75  # 2013/14
        while (
            "המשחק האחרון"
            in httpx.get(self.season_link_unformatted.format(season_number=season_num)).text
        ):
            self.seasons_links.append(self.season_link_unformatted.format(season_number=season_num))
            logger.info(f"Added season: {season_num - 62}/{str(season_num - 61)[-2:]}")

            season_num += 1

        logger.info(f"Finished to build season links, total seasons: {len(self.seasons_links)}")
        return self.seasons_links

    def fetch_matches_from_site(
        self, url_to_fetch: str | None = None, to_update_last_match: bool | None = False
    ) -> list[CalendarEvent]:
        """
        Gets matches from the official site, parse them and return as list of events

        :param url_to_fetch: Optional. The URL to web scrap from. Default is upcoming matches URL
        :param to_update_last_match: Optional. A flag to indicate if to get only the last played match or all events

        :return: a list of events representing the matches
        """
        if not url_to_fetch:
            url_to_fetch = self.upcoming_matches_url
        # Connect to the URL
        response = httpx.get(url_to_fetch)
        response.raise_for_status()

        # Parse HTML and save to BeautifulSoup object
        soup = BeautifulSoup(response.text, "html.parser")

        events: list[CalendarEvent] = []

        if not to_update_last_match:
            unparsed_matches = soup.find_all("div", {"class": "fixtures-holder"})
            logger.info(f'List of {len(unparsed_matches)} parsed matches:"')

            for match_data in unparsed_matches:
                # Ignoring matches without final schedule or U19 league
                if (
                    isinstance(match_data, bs4.element.Tag)
                    and match_data.find(text="מועד לא סופי") is None
                    and match_data.find(text="לנוער") is None
                ):
                    event = self.handle_match(match_data)
                    if "לנוער" in event.description:
                        logger.debug(f"Ignoring U19 match: {event}")
                        continue
                    events.append(event)
                else:
                    logger.debug("\n=============================================================")
                    logger.debug(f"Ignoring match without final date or a U19 match: {match_data}")
                    logger.debug("\n=============================================================")
        else:
            # Getting last match result
            match_data = soup.find("div", {"class": "fixtures-holder"})
            if isinstance(match_data, bs4.element.Tag):
                event = self.handle_match(match_data)
                events.append(event)
            else:
                logger.warning("Unable to find last match data or data is not a valid Tag")

        return events

    def handle_match(self, match: bs4.element.Tag) -> CalendarEvent:
        """
        Parsing single match to event

        :param match: html string - BeautifulSoup

        :return: dict
        """
        # TODO: Finish this function

        match_link = match.find("a", href=True)
        if (
            not match_link
            or not isinstance(match_link, bs4.element.Tag)
            or not match_link.get("href")
        ):
            logger.error("No match link found in the match data")
            raise ValueError("Missing match URL")

        official_match_page = str(match_link.get("href"))
        # Connect to the URL
        response = httpx.get(official_match_page)
        response.raise_for_status()

        # Parse HTML and save to BeautifulSoup object
        soup = BeautifulSoup(response.text, "html.parser")

        # Get match details
        tv_div = soup.find("div", {"class": "tv"})
        img_src = ""
        if tv_div and isinstance(tv_div, bs4.element.Tag):
            img_element = tv_div.find("img")
            if img_element and isinstance(img_element, bs4.element.Tag):
                src_attr = img_element.get("src")
                img_src = str(src_attr) if src_attr is not None else ""
        channel = self.get_channel(img_src)

        location_info = match.find("div", {"class": "location"})
        if not location_info or not isinstance(location_info, bs4.element.Tag):
            logger.warning("No location information found in the match data")
            raise ValueError("Missing location information")

        div_element = location_info.find("div")
        if not div_element or not isinstance(div_element, bs4.element.Tag):
            logger.error("No time/stadium information found in the location data")
            raise ValueError("Missing time/stadium information")

        time_stadium = div_element.text.split(" ")
        location = self.get_stadium(time_stadium[1] if len(time_stadium) > 1 else "")

        span_element = location_info.find("span")
        if not span_element or not isinstance(span_element, bs4.element.Tag):
            logger.error("No date information found in the location data")
            raise ValueError("Missing date information")

        match_date_str = span_element.text
        match_date = self.format_datetime(match_date_str, time_stadium[0])
        start_date = (match_date).isoformat()
        end_date = (match_date + timedelta(hours=2)).isoformat()

        if match.find("div", {"class": "Home"}) is not None:
            home_away = " - בית"
        else:
            home_away = " - חוץ"

        league_title_div = match.find("div", {"class": "league-title"})
        fixture = self.get_competition(league_title_div.text if league_title_div else "")
        round_div = match.find("div", {"class": "round"})
        if round_div is not None:
            fixture = fixture + ", " + round_div.text

        result_div = match.find("div", {"class": "holder split"})
        result = self.get_result(result_div if isinstance(result_div, bs4.element.Tag) else None)

        # Get link to match page at Maccabipedia
        response = httpx.get(
            f"https://www.maccabipedia.co.il/index.php?title=Special:CargoExport&format=json&tables=Football_Games&fields=_pageName&where=Football_Games.Date='{match_date.date()}'"
        )
        page_name = json.loads(response.text)
        if page_name and "_pageName" in page_name[0]:
            page_name = page_name[0]["_pageName"]
            page_name = re.sub(
                r"\s+", "_", page_name
            )  # Replacing spaces/whitespace with underscore
            match_page_link = f'\n<a href="https://maccabipedia.co.il/{page_name}">עמוד המשחק</a>'
        else:
            page_name = ""
            match_page_link = '\n<a href="https://maccabipedia.co.il">מכביפדיה</a>'

        opponent_div = match.find("div", {"class": "holder notmaccabi nn"})
        opponent_name = opponent_div.text if opponent_div else "יריבה לא ידועה"
        event = CalendarEvent(
            summary="⚽ " + opponent_name + home_away,
            location=location,
            description=fixture + result + channel + match_page_link,
            start=EventDate(dateTime=start_date),
            end=EventDate(dateTime=end_date),
            source={"url": f"https://www.maccabipedia.co.il/{page_name}", "title": "עמוד המשחק"},
            extendedProperties={"shared": {"url": official_match_page, "result": result}},
        )
        logger.info(event)
        return event

    def get_channel(self, x: str) -> str:
        return {
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2015/11/1949-300x62.png": "\nספורט1",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_202307161102372351947d86ebda6f4ca21f9a1b925c63-300x81.png": "\nספורט1",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_202307161101594c354ace1560ac3c93356ce1816e2a21-300x78.png": "\nספורט2",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_20230716110202545b088a9368be6285a53e59da64259d-300x78.png": "\nספורט3",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_202307161101541f9bda37ca4f08fc779a8421e22a973a-300x77.png": "\nספורט4",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2015/11/sport-chanel.png": "\nערוץ הספורט",
        }.get(x, "")

    def get_month(self, x: str) -> int:
        return {
            "ינו": 1,
            "פבר": 2,
            "מרץ": 3,
            "אפר": 4,
            "מאי": 5,
            "יונ": 6,
            "יול": 7,
            "אוג": 8,
            "ספט": 9,
            "אוק": 10,
            "נוב": 11,
            "דצמ": 12,
        }.get(x, 0)

    def get_stadium(self, x: str) -> str:
        return {
            "בלומפילד": "אצטדיון בלומפילד",
            "נתניה": "אצטדיון עירוני נתניה",
            "אצטדיון נתניה": "אצטדיון עירוני נתניה",
            "טדי": "אצטדיון טדי",
            'הי"א': 'איצטדיון עירוני הי"א',
            "היא באשדוד": 'איצטדיון עירוני הי"א',
            "אשדוד": 'איצטדיון עירוני הי"א',
            "סמי עופר": "אצטדיון סמי עופר",
            "טרנר": "אצטדיון טרנר",
            "טוטו טרנר": "אצטדיון טרנר",
            "קריית שמונה": "אצטדיון כדורגל קרית שמונה",
            "המושבה": "אצטדיון המושבה",
            "שלמה ביטוח": "אצטדיון המושבה",
            "דוחא": "אצטדיון דוחה",
            "גרין": "אצטדיון גרין",
            "רמת גן": "אצטדיון רמת גן",
            "טוטו עכו": "אצטדיון טוטו עכו",
            "טוטו - עכו": "אצטדיון טוטו עכו",
            "עכו": "אצטדיון טוטו עכו",
            "אצטדיון עכו": "אצטדיון טוטו עכו",
            "סלה": "אצטדיון סלה",
            "איצטדיון פרטיזן": "איצטדיון פרטיזן",
            "יוהאן קרויף ארינה": "יוהאן קרויף ארינה",
        }.get(x, "")

    def get_competition(self, x: str) -> str:
        return {
            "ליגת הבורסה לניירות ערך": "ליגת העל",
            "ליגת Winner": "ליגת העל",
            "ליגת WINNER": "ליגת העל",
            "ליגת one zero הבנק הדיגיטלי": "ליגת העל",
            "ליגת ג׳פניקה": "ליגת העל",
        }.get(x, x)

    def format_datetime(self, date_str: bs4.element.Tag, time: str) -> datetime:
        """
        Formatting date & time correctly

        :param date_str: string of html, contains date
        :param time: contains time (format: XX:XX)
        :return: string with the result if there is data, else returns empty string
        """

        if not date_str or not isinstance(date_str, str):
            raise ValueError("Invalid date string")

        arr = date_str.split(" ")
        year = int(arr[2])
        month = self.get_month(arr[1])
        day = int(arr[0])
        if time == "":
            hour = 20
            minutes = 0
        else:
            time_parts = time.split(":")
            hour = int(time_parts[0])
            minutes = int(time_parts[1])

        return datetime(year, month, day, hour, minutes)

    def get_result(self, div: bs4.element.Tag | None):
        """
        Parsing div to get the match's result

        :param div: BeautifulSoup Tag containing match result information
        :return: string with the result if there is data, else returns empty string
        """
        if not div:
            return ""

        maccabi_score = div.find("span", {"class": "ss maccabi h"})
        rival_score = div.find("span", {"class": "ss h"})
        if not maccabi_score or not rival_score:
            return ""

        maccabi_score = maccabi_score.text
        rival_score = rival_score.text

        if maccabi_score > rival_score:
            return f"\nניצחון {maccabi_score} - {rival_score}"
        elif maccabi_score == rival_score:
            return f"\nתיקו {maccabi_score} - {rival_score}"
        else:
            return f"\nהפסד {maccabi_score} - {rival_score}"
