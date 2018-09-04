from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("--load-generator", action="store_true", dest="loadgenerator", help="start load generator")
    parser.add_option("--resource-mapper", action="store_true", dest="resourcemapper", help="start resource mapper")
    parser.add_option("--control-panel", action="store_true", dest="controlpanel", help="start control panel")
    parser.add_option("--log-collector", action="store_true", dest="logcollector", help="start monitor service server side")
    parser.add_option("--openstack-client", action="store_true", dest="openstackclient", help="start openstack client api")

    (options, args) = parser.parse_args()

    if (options.loadgenerator):
        from load_generator import LGServer
        print('load generator activated')
        lgServer = LGServer()
    if (options.resourcemapper):
        from resource_mapper import RMServer
        print('resource mapper activated')
        rmServer = RMServer()
    if (options.controlpanel):
        from control_panel import CPServer
        print('control panel activated')
        cpServer = CPServer()
    if (options.logcollector):
        from log_collector import LCServer
        print('log collector activated')
        lcServer = LCServer()
    if (options.openstackclient):
        from openstack_client import OCServer
        print('openstack client activated')
        ocServer = OCServer()
