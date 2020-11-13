from get_games import get_games
from create_event import create_event


def main():
    calender_id = 'uvtou62l55g03ql7jq9qr7hjt0@group.calendar.google.com'
    events = get_games()
    for event in events:
        create_event(event, calender_id)


if __name__ == '__main__':
    main()
