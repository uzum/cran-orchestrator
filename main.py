from odl_restconf.flow import Flow
from odl_restconf.group import Group
from odl_restconf.api import ODLRestConfAPI
from odl_restconf.resource_mapper import ResourceMapper
import time

if __name__ == "__main__":
    g1 = Group({
        'switch': 'openflow:1',
        'type': 'all',
        'buckets': [{
            'instructions': [{
                'ip-destination': '10.0.0.5/32'
            }, {
                'mac-destination': '00:00:00:00:00:05'
            }, {
                'udp-dst-port': '3005'
            }, {
                'output': 'NORMAL'
            }]
        }, {
            'instructions': [{
                'ip-destination': '10.0.0.6/32'
            }, {
                'mac-destination': '00:00:00:00:00:06'
            }, {
                'udp-dst-port': '3006'
            }, {
                'output': 'NORMAL'
            }]
        }]
    })
    api = ODLRestConfAPI()
    api.addGroup(g1)
    time.sleep(60)
    api.removeGroup(g1)

    # rm = ResourceMapper()
    #
    # targetSwitch = rm.topo['switches'][0]
    # server = [h for h in targetSwitch.hosts if h.ip == '10.0.0.1'][0]
    # # host2 = [h for h in targetSwitch.hosts if h.ip == '10.0.0.2'][0]
    # # host3 = [h for h in targetSwitch.hosts if h.ip == '10.0.0.3'][0]
    #
    # # print(server.ip)
    # # print(host2.ip)
    # # print(host3.ip)
    #
    #
    # flow1 = rm.addUDPForwardingFlow(targetSwitch, server, server, {
    #     'filter': {
    #         'destination-port': '3002'
    #     },
    #     'target-port': '3000'
    # })
    # flow2 = rm.addUDPForwardingFlow(targetSwitch, server, server, {
    #     'filter': {
    #         'destination-port': '3003'
    #     },
    #     'target-port': '3000'
    # })
    # time.sleep(900)
    # rm.removeFlow(flow1)
    # rm.removeFlow(flow2)
