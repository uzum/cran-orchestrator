from odl_restconf.flow import Flow
from odl_restconf.api import ODLRestConfAPI
from odl_restconf.resource_mapper import ResourceMapper
import time

if __name__ == "__main__":
    rm = ResourceMapper()

    targetSwitch = rm.topo['switches'][0]
    decoyHost = targetSwitch.hosts[0]
    targetHost = targetSwitch.hosts[1]

    flow = rm.addUDPForwardingFlow(targetSwitch, decoyHost, targetHost, {
        'filter': {
            'destination-port': '3005'
        },
        'target-port': '3000'
    })
    time.sleep(120)
    rm.removeFlow(flow)
