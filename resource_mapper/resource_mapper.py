from .api import ODLRestConfAPI
from .flow import Flow
from .group import Group
from .config import *
from .topology import Topology

class Mapping():
    nextMappingId = 0

    def __init__(self, rrhId, bbuList):
        self.id = Mapping.nextMappingId
        Mapping.nextMappingId = Mapping.nextMappingId + 1
        self.rrhId = rrhId
        self.bbuList = bbuList
        self.flows = []
        self.groups = []

    def objectify(self):
        return {
            'id': self.id,
            'rrh': self.rrhId,
            'bbus': self.bbuList
        }

class ResourceMapper():
    def __init__(self):
        self.api = ODLRestConfAPI()

        self.topology = Topology()
        self.topology.discover(self.api.topology())
        self.topology.display()

        self.mappings = []

    def getTopology(self):
        return self.topology

    def setControllerNodeSwitch(self, switchId):
        self.topology.setControllerNodeSwitch(switchId)
        self.topology.discover(self.api.topology())
        self.topology.display()

    def getCurrentMapping(self):
        return [mapping.objectify() for mapping in self.mappings]

    def addMapping(self, rrhId, bbuList):
        print("adding a new rrh-bbu mapping for rrh#" + str(rrhId))
        print("target bbus: " + (", ".join(str(id) for id in bbuList)))
        mapping = Mapping(rrhId, bbuList)
        targetNodes = self.topology.getTargetNodes(bbuList)
        if (not targetNodes):
            print("given set of bbus are not found in any switches!")
            return None

        if (len(targetNodes) == 1):
            # add a forwarding flow to the controller switch ovs
            # that will forward the packet to the single target switch
            flow = self.addForwardingFlow(
                self.topology.controllerNodeSwitch,
                # filters
                {
                    'ethernet': '2048',
                    'ip': {
                        'protocol': 'udp',
                        'destination': self.topology.controllerNodeSwitch.getForwardingAddress().ip + '/32'
                    },
                    'udp': {
                        'destination-port': str(rrhId + RRH_BASE_PORT)
                    }
                },
                # instructions
                [{
                    'ip-destination': targetNodes[0]['switch'].getForwardingAddress().ip + '/32'
                }, {
                    'mac-destination': targetNodes[0]['switch'].getForwardingAddress().mac
                }],
                {}
            )
            mapping.flows.append(flow)
        else:
            # there are more than one target switches, the packet needs to be replicated
            # create a replication group in the controller node switch for each target
            # then add a forwarding flow with group-id action included
            buckets = []
            for targetNode in targetNodes:
                buckets.append({
                    'instructions': [{
                        'ip-destination': targetNode['switch'].getForwardingAddress().ip + '/32'
                    }, {
                        'mac-destination': targetNode['switch'].getForwardingAddress().mac
                    }, {
                        'output': 'NORMAL'
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
                        'destination': self.topology.controllerNodeSwitch.getForwardingAddress().ip + '/32'
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

        for targetNode in targetNodes:
            # there is only one target host (bbu) in this target switch
            # add a forwarding flow to this target switch ovs that will redirect the packets
            # and change the udp destination port to the original value
            if (len(targetNode['hosts']) == 1):
                servingHost = targetNode['hosts'][0]
                flow = self.addForwardingFlow(
                    targetNode['switch'],
                    # filters
                    {
                        'ethernet': '2048',
                        'ip': {
                            'protocol': 'udp',
                            'destination': targetNode['switch'].getForwardingAddress().ip + '/32'
                        },
                        'udp': {
                            'destination-port': str(rrhId + RRH_BASE_PORT)
                        }
                    },
                    # instructions
                    [{
                        'ip-destination': servingHost.ip + '/32'
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
                for host in targetNode['hosts']:
                    buckets.append({
                        'instructions': [{
                            'ip-destination': host.ip + '/32'
                        }, {
                            'mac-destination': host.mac
                        }, {
                            'udp-dst-port': str(BBU_LISTEN_PORT)
                        }, {
                            'output': 'NORMAL'
                        }]
                    })
                group = self.addReplicationGroup(
                    targetNode['switch'],
                    'all',
                    buckets
                )
                flow = self.addForwardingFlow(
                    targetNode['switch'],
                    # filters
                    {
                        'ethernet': '2048',
                        'ip': {
                            'protocol': 'udp',
                            'destination': targetNode['switch'].getForwardingAddress().ip + '/32'
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
        return mapping

    def removeMapping(self, id):
        for mapping in self.mappings:
            if mapping.id == id:
                for flow in mapping.flows:
                    self.removeFlow(flow)
                for group in mapping.groups:
                    self.removeGroup(group)
        self.mappings = [mapping for mapping in self.mappings if mapping.id != id]

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
        print('\tIntended for ' + filters['ip']['destination'])
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
        group = Group({
            'switch': switch.id,
            'type': selectType,
            'buckets': buckets
        })
        self.api.addGroup(group)
        return group

    def removeFlow(self, flow):
        self.api.removeFlow(flow)

    def removeGroup(self, group):
        self.api.removeGroup(group)
