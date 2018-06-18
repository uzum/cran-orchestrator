# #!/usr/bin/env python

from orchestrator import Orchestrator

# Before using make sure to source the openrc file. If you are using openrc file under test use
# source openrc <ADMIN-PASSWORD>
orchestrator = Orchestrator()
# Find Cirros Image
image = orchestrator.find_image(image_name="cirros-0.3.5-x86_64-disk")
# Find m1.tiny flavor
flavor = orchestrator.find_flavor(flavor_name="m1.tiny")
# Find private network
network = orchestrator.find_network(label="private")
# Find sec group with name default
sec_group = orchestrator.find_sec_group(name="default")
# Create an instance with the image/flavor/network above without any ssh key
instance = orchestrator.create_instance(vm_name="vm1", image=image, flavor=flavor,
                                        sec_group=sec_group, key_name=None, nic=network)
# Live Migrate instance
orchestrator.live_migrate_instance(instance="vm1", host="5G-2")
# Delete instance
orchestrator.delete_instance(instance="vm1")
