from api import ODLRestConfAPI
from flow import Flow
from topology import Topology
from mapping import Mapping

class Mapping():
    def __init__(self, rrhId, bbuList):
        self.rrhId = rrhId
        self.bbuList = bbuList
        self.flows = []
        self.groups = []

class ResourceMapper():
    def __init__(self):
        self.api = ODLRestConfAPI()

        self.topology = Topology()
        self.topology.discover(self.api.topology())
        self.topology.print()

        self.mappings = []

    def setControllerNodeSwitch(self, switchId):
        self.topology.setControllerNodeSwitch(switchId)

    def addMapping(self, rrhId, bbuList):
        mapping = Mapping(rrhId, bbuList)
        targetSwitches = self.topology.getTargetNodes(bbuList)
        if (len(targetSwitches) == 1):
            flow = self.addForwardingFlow()
            mapping.flows.append(flow)
        else:
            group = self.addReplicationGroup()
            flow = self.addForwardingFlow()
            mapping.groups.append(group)
            mapping.flows.append(flow)

        for switch in targetSwitches:
            if (len(switch['hosts']) == 1):
                flow = self.addForwardingFlow()
                mapping.flows.append(flow)
            else:
                group = self.addReplicationGroup()
                flow = self.addForwardingFlow()
                mapping.groups.append(group)
                mapping.flows.append(flow)
        self.mappings.append(mapping)

    def onBBUMigration(self, bbuId):
        self.topology.discover(self.api.topology())
        for mapping in self.mappings:
            if bbuId in mapping.bbuList:
                for flow in mapping.flows:
                    self.removeFlow(flow)
                for group in mapping.groups:
                    self.removeGroup(group)
                self.addMapping(mapping.rrhId, mapping.bbuList)

    def addUDPForwardingFlow(self, switch, decoy, target, options={}):
        if ('filter' not in options):
            raise LookupError('filter is required for forwarding flows')

        print('Forwarding UDP packets:')
        print('\tintended for: ' + decoy.ip + ':' + options['filter']['destination-port'])
        print('\tsending to: ' + target.ip + ':' + options['target-port'])
        flow = Flow({
            'switch': switch.id,
            'priority': options.get('priority', '65535'),
            'hard-timeout': options.get('hard-timeout', '0'),
            'idle-timeout': options.get('idle-timeout', '0'),
            'table_id': options.get('table_id', '0'),
            'filters': {
                'ethernet': '2048',
                'ip': {
                    'protocol': options.get('protocol', 'udp'),
                    'destination': decoy.ip + '/32'
                },
                'udp': options['filter']
            },
            'instructions': [{
                'ip-destination': target.ip + '/32'
            }, {
                'mac-destination': target.mac
            }, {
                'udp-dst-port': options['target-port']
            }, {
                'output': 'NORMAL'
            }]
        })
        self.api.addFlow(flow)
        self.flows.append(flow)
        return flow

    def addRedirectFlow(self, switch, fromHost, toHost, options={}):
        print('Redirecting target packets from ' + fromHost.mac + ' to ' + toHost.mac)
        flow = Flow({
            'switch': switch.id,
            'priority': options.get('priority', '65535'),
            'hard-timeout': options.get('hard-timeout', '0'),
            'idle-timeout': options.get('idle-timeout', '0'),
            'table_id': options.get('table_id', '0'),
            'filters': {
                'ethernet': '2048',
                'ip': {
                    'protocol': options.get('protocol', 'udp'),
                    'destination': fromHost.ip + '/32'
                }
            },
            'instructions': [{
                'ip-destination': toHost.ip + '/32'
            }, {
                'mac-destination': toHost.mac
            }, {
                'output': 'NORMAL'
            }]
        })
        self.api.addFlow(flow)
        self.flows.append(flow)
        return flow

    def removeFlow(self, flow):
        self.api.removeFlow(flow)

    def removeGroup(self, group):
        self.api.removeGroup(group)
