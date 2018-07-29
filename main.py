from optparse import OptionParser

from load_generator import LGServer
from resource_mapper import RMServer
from control_panel import CPServer
from openstack_client import OCServer
from log_collector import LCServer

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("--load-generator", action="store_true", dest="loadgenerator", help="start load generator")
    parser.add_option("--resource-mapper", action="store_true", dest="resourcemapper", help="start resource mapper")
    parser.add_option("--control-panel", action="store_true", dest="controlpanel", help="start control panel")
    parser.add_option("--log-collector", action="store_true", dest="logcollector", help="start monitor service server side")
    parser.add_option("--openstack-client", action="store_true", dest="openstackclient", help="start openstack client api")

    (options, args) = parser.parse_args()

    if (options.loadgenerator):
        print('load generator activated')
        lgServer = LGServer()
    if (options.resourcemapper):
        print('resource mapper activated')
        rmServer = RMServer()
    if (options.controlpanel):
        print('control panel activated')
        cpServer = CPServer()
    if (options.logcollector):
        print('log collector activated')
        lcServer = LCServer()
    if (options.openstackclient):
        print('openstack client activated')
        ocServer = OCServer()
