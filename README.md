# Maccabipedia Calendar
The MaccabipediaCalendar project is a Python application that scrapes match schedules and results for Maccabi Tel Aviv sports teams from official websites, then synchronizes this data with Google Calendar. The application provides automated calendar updates for different sports including football, basketball, volleyball, and handball.


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Twitter Follow][follow-shield]][follow-url]


## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [GitHub Actions Workflow](#github-actions-workflow)
* [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
* [Future Development Ideas](#future-development-ideas)
* [Contributing](#contributing)
* [Contact](#contact)


## About The Project

We wanted to have a calender for for Maccabi matches in Football, but without manual updating.
So we decided to scrap the data from the official site and automate the process as much as possible.
Later we added support for additional sports such as Basketball.

### Built With
* Python
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [googleapiclient](https://github.com/googleapis/google-api-python-client)
* [Pydantic](https://docs.pydantic.dev/latest/)


## Getting Started

1. Have a Google account with Google Developer Console

### Prerequisites

* Python >= 3.13

### Installation

1. Clone the repo

2. Create .env file, insert your calendar id and save it in repo directory:
```env
CALENDAR_ID = 'your_calendar_id'
GOOGLE_CREDENTIALS='your_service_account_json_info'
```

3. Create OAuth 2.0 Client Credentials for your user at [Google Developer Console](https://console.developers.google.com/)

4. Download the credentials & save them inside GOOGLE_CREDENTIALS (Remove any spaces or line breaks)

5. Install Python packages in virtual environment:
```bash
sudo apt install python-virtualenv # In case it's not installed
python3.13 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

6. run main.py


## GitHub Actions Workflow
The project uses GitHub Actions to automatically update the calendars:

- Schedule: Daily at 21:05 UTC
- Manually triggerable via workflow_dispatch
- Environment variables are stored as GitHub Secrets


## Common Issues and Troubleshooting
- Authentication Errors: Verify GOOGLE_CREDENTIALS is valid and formatted correctly
- Scraping Failures: Check if website structure has changed
- Missing Events: Verify that the event matching logic is working correctly


## Future Development Ideas
- Support for additional Maccabi sports teams
- Enhanced error reporting
- Mobile notifications for upcoming matches
- Historical data analysis and visualizations
- Scraping into external DB, extracting from DB into Calendar


## Contributing

Pull requests are welcome.

For major changes, please open an issue first to discuss what you would like to change.

Best to talk with us first!


<!-- LICENSE
## License

Distributed under the MIT License. See `LICENSE` for more information.
 -->


## Contact

Maccabipedia - [@maccabipedia](https://twitter.com/maccabipedia) - maccabipedia@gmail.com

[kosh-b](https://github.com/kosh-b)

[Shlomixg](https://github.com/Shlomixg)

Project Link: [https://github.com/Maccabipedia/MaccabipediaCalendar](https://github.com/Maccabipedia/MaccabipediaCalendar)


<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/Maccabipedia/MaccabipediaCalendar.svg?style=flat-square
[contributors-url]: https://github.com/Maccabipedia/MaccabipediaCalendar/graphs/contributors
[follow-shield]: https://img.shields.io/twitter/follow/maccabipedia?color=%23ffdd00&style=flat-square
[follow-url]: https://twitter.com/intent/follow?screen_name=maccabipedia
