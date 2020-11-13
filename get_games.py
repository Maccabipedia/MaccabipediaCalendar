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


def handle_game(game):
    location_info = game.find("div", {"class": "location"})
    date = location_info.find("span").text
    time_stadium = location_info.find("div").text
    time_stadium = time_stadium.split(' ')
    date = convert_date(date, time_stadium[0])
    start = date.isoformat()
    end = (date + timedelta(hours=2)).isoformat()
    location = get_stadium(time_stadium[1])
    time_zone = 'Asia/Jerusalem'
    if game.find("div", {"class": "Home"}) is not None:
        home_away = ' - בית'
    else:
        home_away = ' - חוץ'

    fixture = game.find("div", {"class": "league-title"}).text + ', ' + game.find("div", {"class": "round"}).text

    event = {
        'summary': game.find("div", {"class": "holder notmaccabi nn"}).text + home_away,
        'location': location,
        'description': fixture,
        'start': {
            'dateTime': start,
            'timeZone': time_zone,
        },
        'end': {
            'dateTime': end,
            'timeZone': time_zone,
        },
    }

    print(event)

    return event


def get_games():
    # Set the URL you want to web scrape from
    url = \
        'https://www.maccabi-tlv.co.il/%D7%9E%D7%A9%D7%97%D7%A7%D7%99%D7%9D-%D7%95%D7%AA%D7%95%D7%A6%D7%90%D7%95%D7%AA/'

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
    get_games()
