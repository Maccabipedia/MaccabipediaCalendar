import json
import re
from datetime import datetime, timedelta

import bs4
import requests
from bs4 import BeautifulSoup
from config.logging import setup_logging
from models.schemas import CalendarEvent, EventDate

logger = setup_logging(__name__)


class FootballScraper:
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

        current_season_number = 74  # 2013/14
        while (
            "המשחק האחרון"
            in requests.get(
                self.season_link_unformatted.format(season_number=current_season_number)
            ).text
        ):
            self.seasons_links.append(
                self.season_link_unformatted.format(season_number=current_season_number)
            )
            logger.info(
                f"Added new season: {current_season_number - 62}/{str(current_season_number - 61)[-2:]}"
            )

            current_season_number += 1

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
        response = requests.get(url_to_fetch)
        response.raise_for_status()

        # Parse HTML and save to BeautifulSoup object
        soup = BeautifulSoup(response.text, "html.parser")

        events: list[CalendarEvent] = []

        if not to_update_last_match:
            unparsed_matches = soup.find_all("div", {"class": "fixtures-holder"})
            logger.info(f'List of {len(unparsed_matches)} parsed matches:"')

            for match_data in unparsed_matches:
                # Ignoring matches without final schedule or U19 league
                if match_data.find(text="מועד לא סופי") is None and match_data.find(text="לנוער") is None:
                    event = self.handle_match(match_data)
                    events.append(event)
                else:
                    logger.debug(f"Ignoring match without final date or a U19 match: {match_data}")
        else:
            # Getting last match result
            match_data = soup.find("div", {"class": "fixtures-holder"})
            event = self.handle_match(match_data)
            events.append(event)

        return events

    def handle_match(self, match: bs4.element.Tag) -> CalendarEvent:
        """
        Parsing single match to event

        :param match: html string - BeautifulSoup

        :return: dict
        """
        # TODO: Finish this function

        official_match_page = match.find("a", href=True).get("href")
        # Connect to the URL
        response = requests.get(official_match_page)
        response.raise_for_status()

        # Parse HTML and save to BeautifulSoup object
        soup = BeautifulSoup(response.text, "html.parser")

        # Get match details
        img_src = soup.find("div", {"class": "tv"})
        if img_src and img_src.contents:
            img_src = img_src.find("img").get("src")
        else:
            img_src = ""
        channel = self.get_channel(img_src)

        location_info = match.find("div", {"class": "location"})
        time_stadium = location_info.find("div").text.split(" ")
        location = self.get_stadium(time_stadium[1])

        match_date_str = location_info.find("span").text
        match_date = self.format_datetime(match_date_str, time_stadium[0])
        start_date = match_date.isoformat()
        end_date = (match_date + timedelta(hours=2)).isoformat()
        time_zone = "Asia/Jerusalem"

        if match.find("div", {"class": "Home"}) is not None:
            home_away = " - בית"
        else:
            home_away = " - חוץ"

        fixture = self.get_competition(match.find("div", {"class": "league-title"}).text)
        if match.find("div", {"class": "round"}) is not None:
            fixture = fixture + ", " + match.find("div", {"class": "round"}).text

        result = self.get_result(match.find("div", {"class": "holder split"}))

        # Get link to match page at Maccabipedia
        response = requests.get(
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

        event = CalendarEvent(
            summary=match.find("div", {"class": "holder notmaccabi nn"}).text + home_away,
            location=location,
            description=fixture + result + channel + match_page_link,
            start=EventDate(dateTime=start_date, timeZone=time_zone),
            end=EventDate(dateTime=end_date, timeZone=time_zone),
            source={"url": f"https://www.maccabipedia.co.il/{page_name}", "title": "עמוד המשחק"},
            extendedProperties={"shared": {"url": official_match_page, "result": result}},
        )
        logger.info(event)
        return event

    def get_channel(self, x: str) -> str:
        return {
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2015/11/1949-300x62.png": "ספורט1\n",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_202307161102372351947d86ebda6f4ca21f9a1b925c63-300x81.png": "ספורט1\n",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_202307161101594c354ace1560ac3c93356ce1816e2a21-300x78.png": "ספורט2\n",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_20230716110202545b088a9368be6285a53e59da64259d-300x78.png": "ספורט3\n",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2023/07/MTA_202307161101541f9bda37ca4f08fc779a8421e22a973a-300x77.png": "ספורט4\n",
            "https://static.maccabi-tlv.co.il/wp-content/uploads/2015/11/sport-chanel.png": "ערוץ הספורט\n",
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
            "טרנר": "אצטדיון טוטו טרנר",
            "קריית שמונה": "אצטדיון כדורגל קרית שמונה",
            "המושבה": "אצטדיון המושבה",
            "דוחא": "אצטדיון דוחה",
            "רמת גן": "אצטדיון רמת גן",
            "טוטו עכו": "אצטדיון טוטו עכו",
            "טוטו - עכו": "אצטדיון טוטו עכו",
            "עכו": "אצטדיון טוטו עכו",
            "סלה": "אצטדיון סלה",
        }.get(x, "")

    def get_competition(self, x: str) -> str:
        return {
            "ליגת הבורסה לניירות ערך": "ליגת העל",
            "ליגת Winner": "ליגת העל",
            "ליגת ג׳פניקה": "ליגת העל",
        }.get(x, x)

    def format_datetime(self, date_str: bs4.element.Tag, time: str) -> datetime:
        """
        Formatting date & time correctly

        :param date_str: string of html, contains date
        :param time: contains time (format: XX:XX)
        :return: string with the result if there is data, else returns empty string
        """

        arr = date_str.split(" ")
        year = int(arr[2])
        month = self.get_month(arr[1])
        day = int(arr[0])
        if time == "":
            hour = 20
            minutes = 0
        else:
            time = time.split(":")
            hour = int(time[0])
            minutes = int(time[1])

        return datetime(year, month, day, hour, minutes)

    def get_result(self, div: BeautifulSoup):
        """
        Parsing div to get the match's result

        :param div: string of html
        :return: string with the result if there is data, else returns empty string
        """

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
