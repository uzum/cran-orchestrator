# #!/usr/bin/env python
import json
import requests
import pprint

LG_API = 'http://127.0.0.1:5001/load-generator'
RM_API = 'http://127.0.0.1:5002/resource-mapper'
OC_API = 'http://127.0.0.1:5003/openstack-client'

def requestGet(url):
    r = requests.get(url)
    if (r.status_code != 200):
        raise ValueError('Unexpected status code: ' + r.status_code)
    return r.json()

def requestPost(url, payload=None):
    r = requests.post(url, data=payload)
    if (r.status_code != 200):
        raise ValueError('Unexpected status code: ' + r.status_code)
    return r.json()

# read configuration file
with open('configuration.json') as f:
    configuration = json.load(f)

# create load in waiting state
for rrh in configuration['rrhs']:
    rrhObject = requestPost(LG_API + '/rrh/create?rate=' + str(rrh['rate']))
    if (rrhObject['id'] is not None):
        requestPost(LG_API + '/rrh/' + str(rrhObject['id']) + '/add-connection?amount=' + str(rrh['connections']))
    requestPost(LG_API + '/rrh/' + str(rrhObject['id']) + '/start')
    print('RRH#' + str(rrhObject['id']) + ' started sending its load')
