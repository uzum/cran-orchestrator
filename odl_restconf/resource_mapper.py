from .api import ODLRestConfAPI
from .flow import Flow

class Switch():
    def __init__(self, id):
        self.id = id
        self.hosts = []

    def addHost(self, host):
        self.hosts.append(host)

class Host():
    def __init__(self, parameters):
        self.id = parameters['id']
        self.mac = parameters['mac']
        self.ip = parameters['ip']

class ResourceMapper():
    def __init__(self):
        self.api = ODLRestConfAPI()
        self.topo = self.discoverTopology()
        self.flows = []
        self.printTopology()

    def printTopology(self):
        print('Switches:')
        for switch in self.topo['switches']:
            print('\t' + switch.id)
            print('\tConnected hosts:')
            for host in switch.hosts:
                print('\t\t' + host.ip + "/" + host.mac)
        print('Hosts:')
        for host in self.topo['hosts']:
            print('\t' + host.ip + "/" + host.mac)

    def discoverTopology(self):
        switches = []
        hosts = []

        response = self.api.topology()
        topology = response.json()['network-topology']['topology'][0]
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
                switches.append(switch)

        return { 'switches': switches, 'hosts': hosts }

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
        if flow in self.flows:
            self.api.removeFlow(flow)
            self.flows.remove(flow)
