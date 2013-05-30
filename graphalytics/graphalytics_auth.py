#!/usr/bin/python

import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

#CLIENT_SECRETS = 'client_secrets.json'
#
#
#FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
#        scope='https://www.googleapis.com/auth/analytics.readonly',
#        message=MISSING_CLIENT_SECRETS_MESSAGE)

MISSING_CLIENT_SECRETS_MESSAGE = 'client_secrets.json is missing'

# access token store
TOKEN_FILE_NAME = 'analytics.dat'

def prepare_credentials(token_file_name, client_secrets):
    # retrieve existing credentials

    storage = Storage(token_file_name)
    credentials = storage.get()

    flow = flow_from_clientsecrets(client_secrets,
            scope='https://www.googleapis.com/auth/analytics.readonly',
            message=MISSING_CLIENT_SECRETS_MESSAGE)

    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)

    return credentials

def initialize_service(token_file_name, client_secrets):
    http = httplib2.Http()
    credentials = prepare_credentials(token_file_name, client_secrets)
    http = credentials.authorize(http)
    return build('analytics', 'v3', http=http)
