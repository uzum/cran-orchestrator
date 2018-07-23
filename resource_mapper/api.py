import requests
from .config import *

class OSClientAPI():
    def __init__(self):
        self.remote = OPENSTACK_CLIENT_IP
        self.port =  OPENSTACK_CLIENT_PORT
        self.pathPrefix = 'http://' + self.remote + ':' + self.port

    def requestGet(self, path):
        return requests.get(self.pathPrefix + path)

    def requestPost(self, path, data):
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        return requests.post(self.pathPrefix + path, data=data, headers=headers)

    def hypervisors(self):
        return self.requestGet('/openstack-client/hypervisor/all')

    def instances(self, hypervisor):
        return self.requestGet('/openstack-client/hypervisor/' + hypervisor['hostname'] + '/instances')

class ODLRestConfAPI():
    def __init__(self):
        self.remote = CONTROLLER_IP
        self.port = CONTROLLER_API_PORT
        self.pathPrefix = 'http://' + self.remote + ':' + self.port

    def requestGet(self, path):
        response = requests.get(self.pathPrefix + path, auth=(ODL_USERNAME, ODL_PASSWORD))
        # response.raise_for_status()
        return response

    def requestPost(self, path, data):
        headers = {
            'Content-Type': 'application/xml',
            'Cache-Control': 'no-cache'
        }
        response = requests.post(self.pathPrefix + path, data=data, headers=headers, auth=(ODL_USERNAME, ODL_PASSWORD))
        # response.raise_for_status()
        return response

    def topology(self):
        response = self.requestGet('/restconf/operational/network-topology:network-topology').json()['network-topology']['topology']
        for topo in response:
            if (topo['topology-id'] == 'flow:1'):
                return topo
        return None

    def addFlow(self, flow):
        return self.requestPost('/restconf/operations/sal-flow:add-flow', flow.xml())

    def removeFlow(self, flow):
        return self.requestPost('/restconf/operations/sal-flow:remove-flow', flow.xml())

    def listFlows(self):
        return None

    def addGroup(self, group):
        return self.requestPost('/restconf/operations/sal-group:add-group', group.xml())

    def removeGroup(self, group):
        return self.requestPost('/restconf/operations/sal-group:remove-group', group.xml())

    def listGroups(self):
        return None
