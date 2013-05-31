#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime, timedelta
import pprint
import graphalytics_auth

from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError

import gflags

FLAGS = gflags.FLAGS

def request(**kwargs):
    service = graphalytics_auth.initialize_service(*kwargs.get('config'))

    try:
        accountId = get_account_id(service)
        if accountId:
            webPropertyId = get_webproperty_id(service,
                                               accountId,
                                               **kwargs.get('webProperty'))
            if webPropertyId:
                profileId = get_profile_id(service,
                                           accountId,
                                           webPropertyId,
                                           **kwargs.get('profile'))
                if profileId:
                    kwargs.get('query').update({'profileId': profileId})
                    results = get_results(service,
                                          **request_params(**kwargs.get('query')))
                    #pprint.pprint(results_to_graphite(results))
    except TypeError, error:
        print 'There was an error in constructing your query: %s' % error
    except HttpError, error:
        print 'API error: %s : %s' % (
                error.resp.status, error._get_reason())
    except AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, '
               'please re-run the application to reauth')
    return results_to_graphite(results)

def get_account_id(service, **kwargs):
    """If no kwargs specified or only one account item exists, return first
    account's ID."""
    accounts = service.management().accounts().list().execute()
    if len(accounts.get('items')) == 1 or len(kwargs) == 0:
        return accounts.get('items')[0].get('id')
    if accounts.get('items'):
        for acctItem in accounts.get('items'):
            for key in kwargs.keys():
                if acctItem.get(key) == kwargs.get(key):
                    return acctItem.get('id')
    return None

def get_webproperty_id(service, accountId, **kwargs):
    webproperties = service.management().webproperties().list(
            accountId=accountId).execute()
    if webproperties.get('items'):
        for wpItem in webproperties.get('items'):
            for key in kwargs.keys():
                if wpItem.get(key) == kwargs.get(key):
                    return wpItem.get('id')
    return None

def get_profile_id(service, accountId, webPropertyId, **kwargs):
    profiles = service.management().profiles().list(
            accountId=accountId,
            webPropertyId=webPropertyId
            ).execute()
    if profiles.get('items'):
        for profileItem in profiles.get('items'):
            for key in kwargs.keys():
                if profileItem.get(key) == kwargs[key]:
                    return profileItem.get('id')
    return None

def get_results(service, **kwargs):
    return service.data().ga().get(**kwargs).execute()

def request_params(**kwargs):
    return {
            'ids': 'ga:' + kwargs.get('profileId'),
            'start_date': sec_to_date(kwargs.get('start_date')),
            'end_date': sec_to_date(kwargs.get('end_date')),
            'metrics': ','.join(kwargs.get('metrics')),
            'dimensions': ','.join(kwargs.get('dimensions')),
            'max_results': '10000'
            }

def sec_to_date(seconds):
    """Convert epoch seconds to datestring of form: YYYY-MM-DD."""
    return datetime.fromtimestamp(int(seconds)).strftime(format('%Y-%m-%d'))

def results_to_graphite(results):
    """Convert rows from Core Reporting API to a format consistent with
    Graphite JSON objects."""
    formattedData = []
    query = results.get('query')
    headers = results.get('columnHeaders')
    dimensions = query.get('dimensions').split(',')
    rows = results.get('rows')
    dateIndex = get_date_index(dimensions, rows)
    step = dateIndex[1] - dateIndex[0]
    start = dateIndex[0]
    end = dateIndex[-1] + step
    for metric in query.get('metrics'):
        for i in xrange(len(headers)):
            if metric == headers[i].get('name'):
                rowIndex = i
                break
        formattedData.append({
                'name': metric,
                'values': map(lambda x: float(x[rowIndex]), rows),
                'step': step,
                'start': start,
                'end': end
                })
    return formattedData

#def results_to_graphite(results):
#    """Convert rows from Core Reporting API to a format consistent with
#    Graphite JSON objects."""
#    formattedData = []
#    query = results.get('query')
#    headers = results.get('columnHeaders')
#    dimensions = query.get('dimensions').split(',')
#    rows = results.get('rows')
#    dateIndex = get_date_index(dimensions, rows)
#    for metric in query.get('metrics'):
#        for i in xrange(len(headers)):
#            if metric == headers[i].get('name'):
#                rowIndex = i
#                break
#        formattedData.append({
#                'target': metric,
#                'datapoints': zip(dateIndex,
#                                  map(lambda x: float(x[rowIndex]), rows))
#                })
#    return formattedData


def get_date_index(dimensions, rows):
    dateIndex = []
    if 'ga:date' in dimensions:
        formatStr = '%Y%m%d'
        if 'ga:hour' in dimensions:
            formatStr += '%H'
            return map(lambda row: int(datetime.strptime(row[0] + row[1],
                    format(formatStr)).strftime('%s')), rows)
        else:
            return map(lambda row: int(datetime.strptime(row[0],
                    format(formatStr)).strftime('%s')), rows)


if __name__ == '__main__':
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    params = {
            'webProperty': { 'name': 'http://idealist.org' },
            'profile': { 'name': 'i3: English w/o filter' },
            'query': {
                'start_date': yesterday.strftime('%s'),
                'end_date': now.strftime('%s'),
                'metrics': ['ga:visits'],
                'dimensions': ['ga:date', 'ga:hour']
                },
            'config': ['analytics.dat', 'client_secrets.json']
            }
    request(**params)
