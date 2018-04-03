from odl_restconf.flow import Flow
from odl_restconf.api import ODLRestConfAPI
from odl_restconf.resource_mapper import ResourceMapper
import time

if __name__ == "__main__":
    rm = ResourceMapper()
    targetSwitch = rm.topo['switches'][0]
    targetFromHost = targetSwitch.hosts[0]
    targetToHost = targetSwitch.hosts[1]

    flow = rm.addRedirectFlow(targetSwitch, targetFromHost, targetToHost)
    time.sleep(120)
    rm.removeFlow(flow)
