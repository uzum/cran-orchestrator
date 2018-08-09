#!/usr/bin/env python

import glanceclient.v2 as GlanceClient
import neutronclient.neutron.client as NeutronClient
import novaclient.client as NovaClient

from .credentials import Credentials
from ..config import *

# pylint: disable=broad-except

class Orchestrator(object):
    def __init__(self):
        self.credentials = Credentials()
        self.session = self.credentials.get_session()
        self.nova_client = NovaClient.Client(2, session=self.session)
        self.neutron_client = NeutronClient.Client('2.0', session=self.session)
        self.glance_client = GlanceClient.Client('3', session=self.session)

        self.DEFAULT_IMAGE = self.find_image(image_name=DEFAULT_IMAGE_NAME)
        self.DEFAULT_FLAVOR = self.find_flavor(flavor_name=DEFAULT_FLAVOR_NAME)
        self.DEFAULT_SEC_GROUP = self.find_sec_group(name=DEFAULT_SEC_GROUP_NAME)
        self.DEFAULT_NETWORK = self.find_network(label=DEFAULT_NETWORK_LABEL)

    # Find image (For now assume image is uploaded using CLI/Horizon
    def find_image(self, image_name):
        try:
            return next(self.glance_client.images.list(filters={'name': image_name}), None)
        except Exception as e:
            print(e)
        return None

    # Find network with label
    def find_network(self, label):
        try:
            networks = self.neutron_client.list_networks(label=label)
            if 'networks' in networks and networks['networks']:
                return networks['networks'][0]
            else:
                raise Exception
        except Exception as e:
            print(e)
        return None

    # Find flavor
    def find_flavor(self, flavor_name):
        try:
            return self.nova_client.flavors.find(name=flavor_name)
        except Exception as e:
            print(e)

    # Find security grouo
    def find_sec_group(self, name, project_id=None):
        security_groups = self.neutron_client.list_security_groups()
        if 'security_groups' in security_groups:
            for security_group in security_groups['security_groups']:
                if security_group['name'] == name:
                    if project_id:
                        if security_group['project_id'] == project_id:
                            return security_group
                    else:
                        return security_group
        return None

    def create_default_instance(self, name, availabilityZoneHostname):
        instance = self.nova_client.servers.create(name=name,
                                                   image=self.DEFAULT_IMAGE,
                                                   flavor=self.DEFAULT_FLAVOR,
                                                   availability_zone="nova:" + availabilityZoneHostname)
        return instance

    def create_instance(self, vm_name, image, flavor, key_name,
                        nic, sec_group, avail_zone=None, user_data=None,
                        config_drive=None, files=None):

        if sec_group:
            security_groups = [sec_group['id']]
        else:
            security_groups = None

        # Allow both single nic or multiple nics
        if not isinstance(nic, list):
            nic["net-id"] = nic["id"]
            nic = [nic]

        # Also attach the created security group for the test
        instance = self.nova_client.servers.create(name=vm_name,
                                                   image=image,
                                                   flavor=flavor,
                                                   key_name=key_name,
                                                   nics=nic,
                                                   availability_zone=avail_zone,
                                                   userdata=user_data,
                                                   config_drive=config_drive,
                                                   files=files,
                                                   security_groups=security_groups)
        return instance

    def find_instance(self, name):
        for server in self.nova_client.servers.list():
            if server.name == name:
                return server
        return None

    def list_hypervisors(self):
        return self.nova_client.hypervisors.list()

    def list_instances(self, func=lambda _: True):
        return list(filter(func, self.nova_client.servers.list()))

    def delete_instance(self, instance):
        # if instance name is given
        if isinstance(instance, str):
            instance = self.find_instance(name=instance)
            if instance:
                instance.delete()
        else:
            return instance.delete()
        return None

    def live_migrate_instance(self, instance, host=None):
        try:
            # if instance name is given
            if isinstance(instance, str):
                instance = self.find_instance(name=instance)
            return instance.live_migrate(host=host)
        except Exception as e:
            print(e)
        return instance.live_migrate(host=host)

    def get_instance_diagnostics(self, instance):
        if isinstance(instance, str):
            instance = self.find_instance(name=instance)
            if instance:
                return instance.diagnostics()
            return None
        return instance.diagnostics()
