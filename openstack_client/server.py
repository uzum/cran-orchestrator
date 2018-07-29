from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from .config import *
from .cloud_orchestrator.orchestrator import Orchestrator

openstack_client = Blueprint('openstack_client', __name__)

# returns a simplified representation of an hypervisor
def getHypervisorDetails(hypervisor):
    return {
        'id': hypervisor.id,
        'host_ip': hypervisor.host_ip,
        'hostname': hypervisor.hypervisor_hostname,
        'running_vms': hypervisor.running_vms,
        'state': hypervisor.state
    }

# returns a simplified representation of a network address
def getAddressDetails(address):
    return {
        'type': address['OS-EXT-IPS:type'],
        'addr': address['addr']
    }

# returns a simplifed representation of an instance
def getInstanceDetails(instance):
    return {
        'name': instance.name,
        'status': instance.status,
        'id': instance.id,
        'addresses': list(map(getAddressDetails, instance.addresses[DEFAULT_NETWORK_LABEL]))
    }

class OCServer():
    ref = None

    def __init__(self):
        OCServer.ref = Orchestrator()
        app = Flask('openstack-client')
        CORS(app)
        app.register_blueprint(openstack_client, url_prefix='/openstack-client')
        app.run(host='0.0.0.0', port=SERVICE_PORT)

    # returns the list of hypervisors registered to openstack
    @openstack_client.route("/hypervisor/all", methods=['GET'])
    def getHypervisors():
        return jsonify(list(map(getHypervisorDetails, OCServer.ref.list_hypervisors())))

    # returns the list of instances located in the given hostname (hypervisor|node)
    @openstack_client.route("/hypervisor/<hostname>/instances", methods=['GET'])
    def getInstancesInHypervisor(hostname):
        # test function to be used in filtering; checks the relevant hypervisor hostname value
        testFunction = lambda instance: getattr(instance, 'OS-EXT-SRV-ATTR:hypervisor_hostname') == hostname
        return jsonify(list(map(getInstanceDetails, OCServer.ref.list_instances(testFunction))))

    # creates a new instance with the given parameters
    @openstack_client.route("/instance", methods=['POST'])
    def createInstance():
        # TODO: other parameters could be provided in the request, do not always assume default
        return jsonify(getInstanceDetails(OCServer.ref.create_instance(
            vm_name=request.args.get("name"), # read the vm name from the query parameters
            image=OCServer.ref.DEFAULT_IMAGE,
            flavor=OCServer.ref.DEFAULT_FLAVOR,
            sec_group=OCServer.ref.DEFAULT_SEC_GROUP,
            nic=OCServer.ref.DEFAULT_NETWORK,
            key_name=None
        )))

    # live-migrates the given instance to the target hypervisor with the given hostname
    @openstack_client.route("/instance/<name>/migrate", methods=['POST'])
    def migrateInstance(name):
        return True
        # return jsonify(getInstanceDetails(OCServer.ref.live_migrate_instance(name, request.args.get("target"))))

    # deletes the given instance
    @openstack_client.route("/instance/<name>/delete", methods=['POST'])
    def deleteInstance(name):
        return True
        # return OCServer.ref.delete_instance(name)
