#!/usr/bin/env python

import glanceclient.v2.client as GlanceClient
import neutronclient.neutron.client as NeutronClient
import novaclient.client as NovaClient

from credentials import Credentials


# This file contains some simple examples of openstack python api.
# Before running, make sure openrc file is sourced.

# Use wide exceptions for now

class Orchestrator(object):
    def __init__(self):
        self.credentials = Credentials()
        self.session = self.credentials.get_session()
        self.nova_client = NovaClient.Client(2, session=self.session)
        self.neutron_client = NeutronClient.Client('2.0', session=self.session)
        self.glance_client = GlanceClient.Client('2', session=self.session)

    # Find image (For now assume image is uploaded using CLI/Horizon
    def find_image(self, image_name):
        try:
            return next(self.glance_client.images.list(filters={'name': image_name}), None)
        except Exception as e:
            print(e)
        return None

    # Find network with label
    def find_network(self, label):
        return self.neutron_client.list_networks(label=label)

    # Find flavor
    def find_flavor(self, flavor_name):
        try:
            return self.nova_client.flavors.find(name=flavor_name)
        except Exception as e:
            print(e)

    def create_instance(self, vm_name, image, flavor, key_name,
                        nic, sec_group, avail_zone=None, user_data=None,
                        config_drive=None, files=None):

        if sec_group:
            security_groups = [sec_group['id']]
        else:
            security_groups = None

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


def main():
    orchestrator = Orchestrator()
    image = orchestrator.find_image(image_name="cirros")
    flavor = orchestrator.find_flavor(flavor_name="m1.tiny")
    network = orchestrator.find_network(label="private")
    instance = orchestrator.create_instance(vm_name="vm1", image=image, flavor=flavor, key_name=None, nic=network)


if __name__ == "__main__":
    main()
