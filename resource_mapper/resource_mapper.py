from .api import ODLRestConfAPI, OSClientAPI
from .flow import Flow
from .group import Group
from .config import *
from .topology import Topology
import os

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
            'bbus': self.bbuList,
            'flows': [flow.xml(pretty=True) for flow in self.flows],
            'groups': [group.xml(pretty=True) for group in self.groups]
        }

class ResourceMapper():
    def __init__(self):
        self.ODLAPI = ODLRestConfAPI()
        self.OSAPI = OSClientAPI()

        self.topology = Topology()
        self.topology.discover(self.ODLAPI.topology())
        self.discoverControllerNode()

        self.mappings = []

    def getTopology(self):
        return self.topology

    def updateTopology(self):
        self.topology.discover(self.ODLAPI.topology())
        return self.topology

    def discoverControllerNode(self):
        # retrieve all the hypervisors in the openstack
        hypervisors = self.OSAPI.hypervisors()
        for hv in hypervisors:
            # find the hypervisor with id=1 (controller node)
            if (hv['id'] == 1):
                # retrieve the instances located in controller node
                vms = self.OSAPI.instances(hv)
                # iterate over switch hosts and try to find overlapping ip addresses
                for switch in self.topology.computeNodeSwitches:
                    for host in switch.hosts:
                        for vm in vms:
                            for address in vm['addresses']:
                                if address['type'] == 'fixed' and address['addr'] == host.ip:
                                    self.setControllerNodeSwitch(switch.id)
                                    return
        print('Unable to discover controller node!')

    def setControllerNodeSwitch(self, switchId):
        self.topology.setControllerNodeSwitch(switchId)
        self.topology.discover(self.ODLAPI.topology())
        self.topology.display()

    def getCurrentMapping(self):
        return [mapping.objectify() for mapping in self.mappings]

    def addMapping(self, rrhId, bbuList):
        print("adding a new rrh-bbu mapping for rrh#" + str(rrhId))
        print("target bbus: " + (", ".join(str(id) for id in bbuList)))
        mapping = Mapping(rrhId, bbuList)
        self.addMappingRules(mapping)
        self.mappings.append(mapping)
        return mapping

    def addMappingRules(self, mapping):
        targetNodes = self.topology.getTargetNodes(mapping.bbuList)
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
                        'destination-port': str(mapping.rrhId + RRH_BASE_PORT)
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
                        'destination-port': str(mapping.rrhId + RRH_BASE_PORT)
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
                            'destination-port': str(mapping.rrhId + RRH_BASE_PORT)
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
                            'destination-port': str(mapping.rrhId + RRH_BASE_PORT)
                        }
                    },
                    #instructions
                    [{ 'group-id': str(group.id) }],
                    {}
                )
                mapping.groups.append(group)
                mapping.flows.append(flow)

    def removeMapping(self, id):
        for mapping in self.mappings:
            if mapping.id == id:
                for flow in mapping.flows:
                    self.removeFlow(flow)
                for group in mapping.groups:
                    self.removeGroup(group)
        self.mappings = [mapping for mapping in self.mappings if mapping.id != id]

    def updateMapping(self, mapping):
        for flow in mapping.flows:
            self.removeFlow(flow)
        for group in mapping.groups:
            self.removeGroup(group)
        mapping.flows = []
        mapping.groups = []
        self.addMappingRules(mapping)

    def onBBUMigration(self, address):
        previousId = self.topology.getHostIdByIP(address)
        if (os.system('ping -c 1 ' + address) != 0):
            print('new bbu is still unreachable')
            return False

        self.topology.discover(self.ODLAPI.topology())
        newId = self.topology.getHostIdByIP(address)

        if (newId == None):
            print('could not find the migrated instance address in ODL topology')
            return False

        if (newId == previousId):
            print('host id did not change for bbu at ' + address + ' after migration')
            return False

        for mapping in self.mappings:
            if previousId in mapping.bbuList:
                # update the bbu id in the mapping list and re-create openflow flows&groups
                mapping.bbuList = [newId if bbuId == previousId else bbuId for bbuId in mapping.bbuList]
                self.updateMapping(mapping)
        return True

    def onBBUCreation(self, address):
        if (os.system('ping -c 1 ' + address) != 0):
            print('new bbu is still unreachable')
            return False
        self.topology.discover(self.ODLAPI.topology())
        return True

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
        self.ODLAPI.addFlow(flow)
        return flow

    def addReplicationGroup(self, switch, selectType, buckets):
        print('Creating a new group in ' + switch.id)
        group = Group({
            'switch': switch.id,
            'type': selectType,
            'buckets': buckets
        })
        self.ODLAPI.addGroup(group)
        return group

    def removeFlow(self, flow):
        self.ODLAPI.removeFlow(flow)

    def removeGroup(self, group):
        self.ODLAPI.removeGroup(group)

    def getHostIdByIP(self, ip):
        return self.topology.getHostIdByIP(ip)
