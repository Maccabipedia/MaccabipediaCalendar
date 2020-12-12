import pickle
import os.path

import googleapiclient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import client
from google.oauth2 import service_account
import googleapiclient.discovery

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

CREDENTIALS_FILE = 'credentials.json'
SERVICE_ACCOUNT_FILE = 'google-credentials.json'


def get_calendar_service() -> googleapiclient.discovery.Resource:
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time

    # if os.path.exists('token.pickle'):
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)
    # else:
    #     creds = None
    #
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #
    #     # Save the credentials for the next run
    #     with open('token.pickle', 'wb') as token:
    #         pickle.dump(creds, token)

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds, cache_discovery=False)

    return service


def list_service_accounts(project_id):
    """Lists all service accounts for the current project."""

    credentials = service_account.Credentials.from_service_account_file(
        filename=SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    service_accounts = service.projects().serviceAccounts().list(
        name='projects/' + project_id).execute()

    for account in service_accounts['accounts']:
        print('Name: ' + account['name'])
        print('Email: ' + account['email'])
        print(' ')
    return service_accounts


if __name__ == '__main__':
    list_service_accounts('maccabipedia-calendar')
    print(get_calendar_service())
