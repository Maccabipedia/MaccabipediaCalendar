import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def get_month(x):
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


def get_stadium(x):
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


def get_competition(x):
    return {
        'ליגת הבורסה לניירות ערך': 'ליגת העל',
        'ליגת Winner': 'ליגת העל',
        "ליגת ג׳פניקה": 'ליגת העל',
    }.get(x, x)


def convert_date(date_str, time):
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


def get_result(div):
    maccabi_score_span = div.find("span", {"class": "ss maccabi h"})
    rival_score_span = div.find("span", {"class": "ss h"})
    if not maccabi_score_span or not rival_score_span:
        return ''

    maccabi_score = maccabi_score_span.text
    rival_score = rival_score_span.text

    if maccabi_score > rival_score:
        return f"\nניצחון {maccabi_score} - {rival_score}"
    elif maccabi_score == rival_score:
        return f"\nתיקו {maccabi_score} - {rival_score}"
    else:
        return f"\nהפסד {maccabi_score} - {rival_score}"


def handle_game(game):
    location_info = game.find("div", {"class": "location"})
    time_stadium = location_info.find("div").text.split(' ')

    location = get_stadium(time_stadium[1])

    date = location_info.find("span").text
    date = convert_date(date, time_stadium[0])
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
        'description': fixture + result + '\n<a href="https://maccabipedia.co.il">Maccabipedia</a>',
        'start': {
            'dateTime': start_date,
            'timeZone': time_zone,
        },
        'end': {
            'dateTime': end_date,
            'timeZone': time_zone,
        },
    }

    print(event)

    return event


def get_games(url):
    # url = the URL to web scrape from

    # Connect to the URL
    response = requests.get(url)

    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    events = []
    games = soup.findAll("div", {"class": "fixtures-holder"})
    for game in games:
        if game.find(text='מועד לא סופי') is None:
            event = handle_game(game)
            events.append(event)

    return events


if __name__ == '__main__':
    upcoming_games = 'https://www.maccabi-tlv.co.il/%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d-%d7%95%d7%aa%d7%95%d7%a6%d7%90%d7%95%d7%aa/%d7%94%d7%a7%d7%91%d7%95%d7%a6%d7%94-%d7%94%d7%91%d7%95%d7%92%d7%a8%d7%aa/%d7%9c%d7%95%d7%97-%d7%9e%d7%a9%d7%97%d7%a7%d7%99%d7%9d/'
    get_games(upcoming_games)
