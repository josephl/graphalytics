#!/usr/bin/python

import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

CLIENT_SECRETS = 'client_secrets.json'

MISSING_CLIENT_SECRETS_MESSAGE = '%s is missing' % CLIENT_SECRETS

FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
        scope='https://www.googleapis.com/auth/analytics.readonly',
        message=MISSING_CLIENT_SECRETS_MESSAGE)

# access token store
TOKEN_FILE_NAME = 'analytics.dat'

def prepare_credentials():
    # retrieve existing credentials
    storage = Storage(TOKEN_FILE_NAME)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(FLOW, storage)

    return credentials

def initialize_service():
    http = httplib2.Http()
    credentials = prepare_credentials()
    http = credentials.authorize(http)
    return build('analytics', 'v3', http=http)
