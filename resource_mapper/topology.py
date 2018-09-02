import socket

class Switch():
    def __init__(self, id):
        self.id = id
        self.hosts = []
        self.isController = False

    def addHost(self, host):
        self.hosts.append(host)

    def getForwardingAddress(self):
        if not self.hosts:
            raise IndexError('switch #' + self.id + ' does not have any hosts at the moment')
        if self.isController:
            for host in self.hosts:
                if host.ip == BROADCAST_ADDRESS:
                    return host
            raise IndexError('switch #' + self.id + ' is controller but does not have a port for the broadcast address')
        return self.hosts[0]

    def toObject(self):
        return {
            'id': self.id,
            'hosts': [host.toObject() for host in self.hosts]
        }

class Host():
    def __init__(self, parameters):
        self.id = parameters['id']
        self.mac = parameters['mac']
        self.ip = parameters['ip']

    def toObject(self):
        return {
            'id': self.id,
            'mac': self.mac,
            'ip': self.ip
        }

class Topology():
    def __init__(self):
        self.controllerNodeSwitch = None
        self.computeNodeSwitches = []

    def objectify(self):
        topoObject = {}
        if (self.controllerNodeSwitch):
            topoObject['controllerNode'] = self.controllerNodeSwitch.toObject()
        topoObject['computeNodes'] = [switch.toObject() for switch in self.computeNodeSwitches]
        return topoObject

    def display(self):
        if (self.controllerNodeSwitch):
            print('Controller Node: ')
            print('\t' + self.controllerNodeSwitch.id)
            print('\tConnected hosts: ')
            for host in self.controllerNodeSwitch.hosts:
                print('\t\tHost#' + str(host.id) + ' | ' + host.ip + "/" + host.mac)
        print('Compute Nodes:')
        for switch in self.computeNodeSwitches:
            print('\t' + switch.id)
            print('\tConnected hosts:')
            for host in switch.hosts:
                print('\t\tHost#' + str(host.id) + ' | ' + host.ip + "/" + host.mac)

    def findHost(self, id):
        for switch in self.computeNodeSwitches:
            for host in switch.hosts:
                if host.id == id:
                    return host

    def discover(self, topology):
        self.computeNodeSwitches = []
        hosts = []
        for node in topology['node']:
            if (node['node-id'].startswith('host')):
                host = Host(node['host-tracker-service:addresses'][0])
                hosts.append(host)

        for node in topology['node']:
            if (node['node-id'].startswith('openflow')):
                switch = Switch(node['node-id'])
                for link in topology['link']:
                    if (link['source']['source-node'] == node['node-id']):
                        for host in hosts:
                            if host.mac == link['destination']['dest-node'][5:]:
                                switch.addHost(host)
                if (self.controllerNodeSwitch == None or self.controllerNodeSwitch.id != switch.id):
                    self.computeNodeSwitches.append(switch)

    def setControllerNodeSwitch(self, id):
        for switch in self.computeNodeSwitches:
            if switch.id == id:
                self.controllerNodeSwitch = switch
                self.controllerNodeSwitch.isController = True
        self.computeNodeSwitches = [switch for switch in self.computeNodeSwitches if switch.id != id]

    def getTargetNodes(self, hostIDs):
        targets = []
        for switch in self.computeNodeSwitches:
            hosts = []
            for host in switch.hosts:
                if (host.id in hostIDs):
                    hosts.append(host)
            if (hosts):
                targets.append({ 'switch' : switch, 'hosts': hosts })
        return targets

    def getHostIdByIP(self, ip):
        for switch in self.computeNodeSwitches:
            for host in switch.hosts:
                if (host.ip == ip):
                    return host.id
        for switch in self.controllerNodeSwitch:
            for host in switch.hosts:
                if (host.ip == ip):
                    return host.id
