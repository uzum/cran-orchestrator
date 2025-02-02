# #!/usr/bin/env python


import pytest

from cloud_orchestrator.cloud_orchestrator.orchestrator import Orchestrator

orchestrator = Orchestrator()


@pytest.mark.orchestrator
def test_find_image():
    assert orchestrator.find_image(
        image_name="cirros-0.3.5-x86_64-disk").name == "cirros-0.3.5-x86_64-disk"


@pytest.mark.orchestrator
def test_find_flavor():
    assert orchestrator.find_flavor(flavor_name="m1.tiny").get_keys() == {}


@pytest.mark.orchestrator
def test_find_network():
    network = orchestrator.find_network(label="private")
    assert network is not None
    assert network['name'] == "private"


@pytest.mark.orchestrator
def test_sec_group():
    assert orchestrator.find_sec_group(name="default")["name"] == "default"


@pytest.mark.orchestrator
def test_create_instance():
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
                                            sec_group=sec_group,
                                            key_name=None,
                                            nic=network)
    assert instance.name == "vm1"


@pytest.mark.orchestrator
def test_live_migrate():
    assert orchestrator.live_migrate_instance(instance="vm1", host="5G-2") is ()


@pytest.mark.orchestrator
def test_get_instance_diagnostics():
    assert orchestrator.get_instance_diagnostics(instance="vm1") is not None


@pytest.mark.orchestrator
def test_delete_instance():
    # Test the deletion with name
    assert orchestrator.delete_instance(instance="vm1") is not None
