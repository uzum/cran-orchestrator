# #!/usr/bin/env python
import json
import requests
import pprint
import time

LG_API = 'http://127.0.0.1:5001/load-generator'
RM_API = 'http://127.0.0.1:5002/resource-mapper'
OC_API = 'http://127.0.0.1:5003/openstack-client'

rrhs = []
bbus = []

def requestGet(url):
    r = requests.get(url)
    if (r.status_code != 200):
        raise ValueError('Unexpected status code: ' + r.status_code)
    return r.json()

def requestPost(url, payload = None):
    r = requests.post(url, data = payload)
    if (r.status_code != 200):
        raise ValueError('Unexpected status code: ' + r.status_code)
    return r.json()

def pollBBUObject(bbu, retryCount = 0):
    if (retryCount > 10): return False

    builtInstances = requestGet(OC_API + '/hypervisor/' + bbu['zone'] + '/instances')
    for instance in builtInstances:
        if instance['name'] == bbu['name']:
            for address in instance['addresses']:
                if address['type'] == 'fixed' and address['addr'].startswith('10.0'):
                    bbus.append({
                        'name': bbu['name'],
                        'ip': address['addr']
                    })
                    return True

    print('BBU instance is not ready yet, retry number: ' + retryCount)
    time.sleep(10)
    return pollBBUObject(bbu, retryCount + 1)

def getBBUIP(name):
    for bbu in bbus:
        if (bbu['name'] == name):
            return bbu['ip']

# read configuration file
with open('configuration.json') as f:
    configuration = json.load(f)

# create load in waiting state
for rrh in configuration['rrhs']:
    rrhObject = requestPost(LG_API + '/rrh/create?rate=' + str(rrh['rate']))
    if (rrhObject['id'] is not None):
        requestPost(LG_API + '/rrh/' + str(rrhObject['id']) + '/add-connection?amount=' + str(rrh['connections']))
    rrhs.append({
        'id': rrhObject['id'],
        'bbus': rrh['bbus']
    })

# create openstack instances
for bbu in configuration['bbus']:
    requestPost(OC_API + '/instance?name=' + bbu['name'] + '&zone=' + bbu['zone'])
    # poll until BBU ip address could be obtained
    if (pollBBUObject(bbu)):
        print('BBU instance is being built and IP is obtained')
    else:
        print('Cannot obtain BBU instance IP before timeout')
        exit(1)

# create openflow mapping rules
for rrh in rrhs:
    bbuIps = [getBBUIP(bbuName) for bbuName in rrh['bbus']]
    mapping = requestPost(RM_IP + '/mapping?format=ip&rrh=' + str(rrh['id']) + '&bbus=' + (','.join(bbuIps)))
    print('mapping created for rrh#' + str(rrh['id']))
    print(json.dumps(mapping, indent = 2))

# start sending UDP load
print('all BBU instances are ready and mapping is complete, starting to send load')
time.sleep(5)
for rrhId in rrhs:
    requestPost(LG_API + '/rrh/' + str(rrhId) + '/start')
    print('RRH#' + str(rrhId) + ' started sending its load')
print('system is ready')
exit(0)
