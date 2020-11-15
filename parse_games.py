import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def get_channel(x: str) -> str:
    return {
        'https://static.maccabi-tlv.co.il/wp-content/uploads/2015/11/1949-300x62.png': '\nספורט1',
        'https://static.maccabi-tlv.co.il/wp-content/uploads/2015/11/sport-chanel.png': '\nערוץ הספורט'
    }.get(x, '')


def get_month(x: str) -> int:
    return {
        'ינו': 1,
        'פבר': 2,
        'מרץ': 3,
        'אפר': 4,
        'מאי': 5,
        'יונ': 6,
        'יול': 7,
        'אוג': 8,
        'ספט': 9,
        'אוק': 10,
        'נוב': 11,
        'דצמ': 12,
    }.get(x)


def get_stadium(x: str) -> int:
    return {
        'בלומפילד': 'אצטדיון בלומפילד',
        'נתניה': 'אצטדיון עירוני נתניה',
        'אצטדיון נתניה': 'אצטדיון עירוני נתניה',
        'טדי': 'אצטדיון טדי',
        'הי"א': 'איצטדיון עירוני הי"א',
        'היא באשדוד': 'איצטדיון עירוני הי"א',
        'אשדוד': 'איצטדיון עירוני הי"א',
        'סמי עופר': 'אצטדיון סמי עופר',
        'טרנר': 'אצטדיון טוטו טרנר',
        'קריית שמונה': 'אצטדיון כדורגל קרית שמונה',
        'המושבה': 'אצטדיון המושבה',
        'דוחא': 'אצטדיון דוחה',
        'רמת גן': 'אצטדיון רמת גן',
        'טוטו עכו': 'אצטדיון טוטו עכו',
        'טוטו - עכו': 'אצטדיון טוטו עכו',
        'עכו': 'אצטדיון טוטו עכו',
        'סלה': 'אצטדיון סלה',
    }.get(x, '')


def get_competition(x: str) -> str:
    return {
        'ליגת הבורסה לניירות ערך': 'ליגת העל',
        'ליגת Winner': 'ליגת העל',
        "ליגת ג׳פניקה": 'ליגת העל',
    }.get(x, x)


def format_datetime(date_str: str, time: str) -> datetime:
    """formatting date & time correctly

        :param date_str: string of html, contains date
        :type date_str: class 'bs4.element.Tag'
        :param time: contains time (format: XX:XX)
        :type time: str
        :return: string with the result if there is data, else returns empty string
        :rtype: datetime
    """

    arr = date_str.split(' ')
    year = int(arr[2])
    month = get_month(arr[1])
    day = int(arr[0])
    if time == '':
        hour = 20
        minutes = 0
    else:
        time = time.split(':')
        hour = int(time[0])
        minutes = int(time[1])

    return datetime(year, month, day, hour, minutes)


def get_result(div: BeautifulSoup):
    """parsing div to get the game's result

    :param div: string of html
    :type div: class 'bs4.element.Tag'
    :return: string with the result if there is data, else returns empty string
    :rtype: str
    """
    maccabi_score = div.find("span", {"class": "ss maccabi h"})
    rival_score = div.find("span", {"class": "ss h"})
    if not maccabi_score or not rival_score:
        return ''

    maccabi_score = maccabi_score.text
    rival_score = rival_score.text

    if maccabi_score > rival_score:
        return f"\nניצחון {maccabi_score} - {rival_score}"
    elif maccabi_score == rival_score:
        return f"\nתיקו {maccabi_score} - {rival_score}"
    else:
        return f"\nהפסד {maccabi_score} - {rival_score}"


def handle_game(game: BeautifulSoup) -> dict:
    """Parsing single game to event

    :param game: html string - BeautifulSoup
    :type game: BeautifulSoup
    :return: event
    :rtype: dict
    """

    page_link = game.find('a', href=True)['href']
    # Connect to the URL
    response = requests.get(page_link)

    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    img_src = soup.find("div", {"class": "tv"})
    if img_src.contents:
        img_src = img_src.find('img')['src']
    else:
        img_src = ''
    channel = get_channel(img_src)

    location_info = game.find("div", {"class": "location"})
    time_stadium = location_info.find("div").text.split(' ')

    location = get_stadium(time_stadium[1])

    date = location_info.find("span").text
    date = format_datetime(date, time_stadium[0])
    start_date = date.isoformat()
    end_date = (date + timedelta(hours=2)).isoformat()
    time_zone = 'Asia/Jerusalem'

    if game.find("div", {"class": "Home"}) is not None:
        home_away = ' - בית'
    else:
        home_away = ' - חוץ'

    fixture = get_competition(game.find("div", {"class": "league-title"}).text)
    if game.find("div", {"class": "round"}) is not None:
        fixture = fixture + ', ' + game.find("div", {"class": "round"}).text

    result = get_result(game.find("div", {"class": "holder split"}))

    event = {
        'summary': game.find("div", {"class": "holder notmaccabi nn"}).text + home_away,
        'location': location,
        'description': fixture + result + channel + '\n<a href="https://maccabipedia.co.il">מכביפדיה</a>',
        'start': {
            'dateTime': start_date,
            'timeZone': time_zone,
        },
        'end': {
            'dateTime': end_date,
            'timeZone': time_zone,
        },
        "source": {
            "url": 'https://www.maccabipedia.co.il/',  # TODO: Add link to game page in maccabipedia
            "title": 'עמוד המשחק'
        },
        "extendedProperties": {
            "shared": {
                "url": page_link,
                "result": result
            }
        },
    }
    print(event)
    return event


def parse_games(url: str, to_update_last_game: bool = False) -> list:
    """Gets games from the official site, parse them and return as list of events

    :param url: The URL to web scrap from
    :type url: str
    :param to_update_last_game: Optional. A flag to indicate if to get only the last played game or all events
    :type to_update_last_game: bool, optional
    :return: a list of events representing the games
    :rtype: list
    """

    # Connect to the URL
    response = requests.get(url)

    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    events = []

    if not to_update_last_game:
        games = soup.findAll("div", {"class": "fixtures-holder"})
        print(f"List of {len(games)} parsed games:")
        for game in games:
            # Ignoring games without final schedule or U19 league
            if game.find(text='מועד לא סופי') is None or game.find(text='נוער') is None:
                event = handle_game(game)
                events.append(event)
    else:
        # Getting last game result
        game = soup.find("div", {"class": "fixtures-holder"})
        event = handle_game(game)
        events.append(event)

    return events


if __name__ == '__main__':
    upcoming_games = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7' \
                     '%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7' \
                     '%9c%d7%95%d7%97-%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d/ '
    parse_games(upcoming_games, False)
