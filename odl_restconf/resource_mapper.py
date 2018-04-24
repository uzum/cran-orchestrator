from .api import ODLRestConfAPI
from .flow import Flow
from .group import Group
from .config import *
from .topology import Topology

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
        # self.topology.discover(self.api.topology())
        # self.topology.display()

        self.mappings = []

    def setControllerNodeSwitch(self, switchId):
        self.topology.setControllerNodeSwitch(switchId)

    def getCurrentMapping(self):
        mappingList = []
        for mapping in self.mappings:
            mappingList.append({
                'rrh': mapping.rrhId,
                'bbus': mapping.bbuList
            })
        return mappingList

    def addMapping(self, rrhId, bbuList):
        mapping = Mapping(rrhId, bbuList)
        targetSwitches = self.topology.getTargetNodes(bbuList)
        if (len(targetSwitches) == 1):
            # add a forwarding flow to the controller switch ovs
            # that will forward the packet to the single target switch
            flow = self.addForwardingFlow(
                self.topology.controllerNodeSwitch,
                # filters
                {
                    'ethernet': '2048',
                    'ip': {
                        'protocol': 'udp',
                        'destination': self.topology.controllerNodeSwitch.getForwardingAddress().ip
                    },
                    'udp': {
                        'destination-port': str(rrhId + RRH_BASE_PORT)
                    }
                },
                # instructions
                [{
                    'ip-destination': targetSwitch[0].getForwardingAddress().ip
                }, {
                    'mac-destination': targetSwitch[0].getForwardingAddress().mac
                }],
                {}
            )
            mapping.flows.append(flow)
        else:
            # there are more than one target switches, the packet needs to be replicated
            # create a replication group in the controller node switch for each target
            # then add a forwarding flow with group-id action included
            buckets = []
            for targetSwitch in targetSwitches:
                buckets.append({
                    'instructions': [{
                        'ip-destination': targetSwitch.getForwardingAddress().ip
                    }, {
                        'mac-destination': targetSwitch.getForwardingAddress().mac
                    }]
                })
            group = self.addReplicationGroup(
                self.topology.controllerNodeSwitch,
                'all',
                buckets
            )
            flow = self.addForwardingFlow(
                self.topology.controllerNodeSwitch,
                # filters
                {
                    'ethernet': '2048',
                    'ip': {
                        'protocol': 'udp',
                        'destination': self.topology.controllerNodeSwitch.getForwardingAddress().ip
                    },
                    'udp': {
                        'destination-port': str(rrhId + RRH_BASE_PORT)
                    }
                },
                # instructions
                [{ 'group-id': str(group.id) }],
                {}
            )
            mapping.groups.append(group)
            mapping.flows.append(flow)

        for switch in targetSwitches:
            # there is only one target host (bbu) in this target switch
            # add a forwarding flow to this target switch ovs that will redirect the packets
            # and change the udp destination port to the original value
            if (len(switch['hosts']) == 1):
                servingHost = switch['hosts'][0]
                flow = self.addForwardingFlow(
                    switch,
                    # filters
                    {
                        'ethernet': '2048',
                        'ip': {
                            'protocol': 'udp',
                            'destination': switch.getForwardingAddress().ip
                        },
                        'udp': {
                            'destination-port': str(rrhId + RRH_BASE_PORT)
                        }
                    },
                    # instructions
                    [{
                        'ip-destination': servingHost.ip
                    }, {
                        'mac-destination': servingHost.mac
                    }, {
                        'udp-dst-port': str(BBU_LISTEN_PORT)
                    }],
                    {}
                )
                mapping.flows.append(flow)
            else:
                # there are more than one target hosts (bbus) in this target switch
                # create a replication group in the switch that will change the dst ip&mac
                # accordingly for each serving host, and change the udp dst port to default
                # then create a forwarding flow refering to the new group's id
                buckets = []
                for host in switch['hosts']:
                    buckets.append({
                        'instructions': [{
                            'ip-destination': host.ip
                        }, {
                            'mac-destination': host.mac
                        }, {
                            'udp-dst-port': str(BBU_LISTEN_PORT)
                        }]
                    })
                group = self.addReplicationGroup(
                    switch,
                    'all',
                    buckets
                )
                flow = self.addForwardingFlow(
                    switch,
                    # filters
                    {
                        'ethernet': '2048',
                        'ip': {
                            'protocol': 'udp',
                            'destination': switch.getForwardingAddress().ip
                        },
                        'udp': {
                            'destination-port': str(rrhId + RRH_BASE_PORT)
                        }
                    },
                    #instructions
                    [{ 'group-id': str(group.id) }],
                    {}
                )
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

    def addForwardingFlow(self, switch, filters, instructions, options):
        print('Creating a forwarding flow in ' + switch.id)
        print('\tIntended for ' + filters['ip']['destination'] + ', forwarding to ' + instructions[0]['ip-destination'])
        instructions.append({ 'output': 'NORMAL' })
        flow = Flow({
            'switch': switch.id,
            'priority': options.get('priority', '65535'),
            'hard-timeout': options.get('hard-timeout', '0'),
            'idle-timeout': options.get('idle-timeout', '0'),
            'table_id': options.get('table_id', '0'),
            'filters': filters,
            'instructions': instructions
        })
        self.api.addFlow(flow)
        return flow

    def addReplicationGroup(self, switch, selectType, buckets):
        print('Creating a new group in ' + switch.id)
        buckets.append({ 'output': 'NORMAL' })
        group = Group({
            'switch': switch.id,
            'type': selectType,
            'buckets': buckets
        })
        self.api.addGroup(group)
        return group

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
