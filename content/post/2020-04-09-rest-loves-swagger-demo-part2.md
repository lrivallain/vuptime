---
author: lrivallain
author_name: Ludovic Rivallain
categories:
- Automation
date: "2020-04-09T00:00:00Z"
tags:
- rest
- swagger
- devops
- codegen
- api
- vcenter
- vcloud
- vmware
thumbnail: /images/rest-loves-swagger/APIEverywhereMeme.png
title: REST ❤ Swagger, 2 minutes to create an API SDK ⏱ – Codegen Demo – Part 2
aliases: 
- /2020/04/09/rest-loves-swagger-demo-part2/
toc: true
---

After a [short introduction of Swagger Codegen and the context of the demo made for a French vMUG Webinar](/2020/04/01/rest-loves-swagger-demo/), we will see how to apply this to VMware products like vCenter and vCloud Director.

As this post is following the steps made in the [part 1](/2020/04/01/rest-loves-swagger-demo/), I strongly encourage you to start with the previous post.

## Pre-requisites

Same as previous post + we will rely on some environment variables to set some local settings:

```bash
echo "Exporting vCenter env..."
export VMWARE_VCENTER_HOSTNAME="vcsa.vupti.me"
export VMWARE_VCENTER_USERNAME="demo@vsphere.local"
export VMWARE_VCENTER_PASSWORD='************'

echo "Exporting vCD env..."
export VMWARE_VCD_HOSTNAME="vcd.vupti.me"
export VMWARE_VCD_USERNAME="demo@orgdemo"
export VMWARE_VCD_PASSWORD="************"
```

## vCenter SDK with Codegen

```bash
# Get the API swagger description
curl -sk https://$VMWARE_VCENTER_HOSTNAME/apiexplorer/json/vcenter.json  \
  > codegen/in/vcenter.json

# Create a config file for our future python module
echo '{
  "packageName":"vc_client",
  "projectName":"vc-client",
  "packageVersion":"6.7.0"
}' > codegen/in/config_vc_client.json

# Generate the SDK
docker run --rm -v ${PWD}/codegen:/local \
  swaggerapi/swagger-codegen-cli generate \
    -i /local/in/vcenter.json \
    -o /local/out/python-vc \
    -c /local/in/config_vc_client.json \
    -l python

# Install new python mdule with PIP
pip install codegen/out/python-vc
```

So in the above section, we created a new API SDK for a subset of vCenter REST APIs (and we do not rely on the [`pyvmomi`](http://vmware.github.io/pyvmomi/) project).

We can now use it:

### Prepare a client object

```python
import vc_client
from vc_client.rest import ApiException
from utils import *
import os
logger = logging.getLogger("DEMO_VCENTER")

# Configure API
configuration = vc_client.Configuration()
configuration.verify_ssl = False
configuration.host = f"https://{os.environ.get('VMWARE_VCENTER_HOSTNAME')}/rest"

# credentials
_username = os.environ.get('VMWARE_VCENTER_USERNAME')
_password = os.environ.get('VMWARE_VCENTER_PASSWORD')
auth_str = basic_auth_str(_username, _password)

# Create a client
client = vc_client.ApiClient(configuration)
```

So we import our new `vc_client` module, we setup the target hostname and the authentication settings.

### Get a new session

New goal: getting a session to use a *cookie-based* authentication instead of providing username/password for each request:

```python
# Get a new session
try:
    logger.debug("Starting a new session")
    s = client.call_api(
        '/com/vmware/cis/session',
        "POST",
        header_params={
            "Authorization": auth_str,
        })
except ApiException as e:
    print("Exception when creating session: %s\n" % e)
    exit(-1)
logger.info("New session is created")

# Set the cookie according to the previous request result
logger.debug("Setting new session authorization token in cookies")
client.cookie = s[2].get('Set-Cookie')
logger.info(f"Client cookies updated: {client.cookie}")
```

As you see, we rely on our module code by using the `client.call_api` instruction and the cookie update: `client.cookie = s[2].get('Set-Cookie')`.

**Output**:

```
DEMO_VCENTER 	Starting a new session
DEMO_VCENTER 	New session is created
DEMO_VCENTER 	Setting new session authorization token in cookies
DEMO_VCENTER 	Client cookies updated: vmware-api-session-id=5cebc...;Path=/rest;Secure;HttpOnly
```

### Get some content

We will use our new session to get some data from the vCenter API.

Listing VMs:

```python
# List VM
logger.debug("Listing VMs...")
instance = vc_client.VM_Api(client)
for vm in instance.list().value:
    logger.info(
        f"{vm.name}: {vm.power_state} / vCPU: {vm.cpu_count} / Mem: {vm.memory_size_mi_b} Mb"
    )
    keep_last = vm
```

**Output**:

```
DEMO_VCENTER 	Listing VMs...
DEMO_VCENTER 	LRI_RancherMaster: POWERED_ON / vCPU: 4 / Mem: 8192 Mb
DEMO_VCENTER 	LRI_vRO: POWERED_ON / vCPU: 2 / Mem: 6144 Mb
DEMO_VCENTER 	LRI_vcd: POWERED_ON / vCPU: 2 / Mem: 12288 Mb
DEMO_VCENTER 	LRI_rabbitmq: POWERED_ON / vCPU: 2 / Mem: 3072 Mb
DEMO_VCENTER 	ESXi7-01: POWERED_ON / vCPU: 2 / Mem: 4096 Mb
DEMO_VCENTER 	vcsa7: POWERED_ON / vCPU: 2 / Mem: 12288 Mb
DEMO_VCENTER 	ESXi7-02: POWERED_ON / vCPU: 2 / Mem: 4096 Mb
DEMO_VCENTER 	ESXi7-03: POWERED_ON / vCPU: 2 / Mem: 4096 Mb
DEMO_VCENTER 	LRI_ubuntu01: POWERED_ON / vCPU: 2 / Mem: 1024 Mb
DEMO_VCENTER 	LRI_photon01: POWERED_ON / vCPU: 1 / Mem: 2048 Mb
DEMO_VCENTER 	DCScope: POWERED_ON / vCPU: 2 / Mem: 8192 Mb
DEMO_VCENTER 	FaH_1.0.0_01: POWERED_ON / vCPU: 8 / Mem: 8192 Mb
```

As you can see, we kept the last VM from the list to get more details:

```python
# Get more details for last VM
logger.debug("Getting details about last VM...")
vm_detailled = instance.get(keep_last.vm).value
logger.info("Data:\n" +
            json.dumps(vm_detailled.to_dict(), indent=2, default=str))

# Get its network
logger.debug("Getting a specifc detail about a VM:")
nic = vm_detailled.nics[0].value
logger.info(f"{keep_last.name} MAC address: {nic.mac_address}")
```

**Output** (only the VM details content):

```json
{
  "memory": {
    "hot_add_limit_mi_b": null,
    "hot_add_enabled": false,
    "hot_add_increment_size_mi_b": null,
    "size_mi_b": 8192
  },
  "hardware": {
    "upgrade_status": "NONE",
    "upgrade_version": null,
    "version": "VMX_13",
    "upgrade_error": null,
    "upgrade_policy": "NEVER"
  },
  "disks": [
    {
      "value": {
        "label": "Hard disk 1",
        "scsi": {
          "unit": 0,
          "bus": 0
        },
        "capacity": 4294967296,
        "type": "SCSI",
        "sata": null,
        "ide": null,
        "backing": {
          "type": "VMDK_FILE",
          "vmdk_file": "[vsanDatastore] d40d765e-a8c1-6d10-0d40-a0369fbcc808/FaH_1.0.0_01.vmdk"
        }
      },
      "key": "2000"
    }
  ],
  "cdroms": [
    {
      "value": {
        "label": "CD/DVD drive 1",
        "backing": {
          "type": "CLIENT_DEVICE",
          "device_access_type": "PASSTHRU",
          "iso_file": null,
          "host_device": null,
          "auto_detect": null
        },
        "state": "NOT_CONNECTED",
        "type": "IDE",
        "sata": null,
        "allow_guest_control": true,
        "ide": {
          "primary": true,
          "master": true
        },
        "start_connected": false
      },
      "key": "3000"
    }
  ],
  "boot_devices": [
    {
      "type": "CDROM",
      "nic": null,
      "disks": null
    }
  ],
  "nics": [
    {
      "value": {
        "wake_on_lan_enabled": false,
        "state": "CONNECTED",
        "label": "Network adapter 1",
        "backing": {
          "network": "dvportgroup-100",
          "distributed_port": "69",
          "distributed_switch_uuid": "50 2f 42 20 b1 c3 a5 2a-0d 95 b6 0c ab 7e b5 da",
          "network_name": null,
          "opaque_network_id": null,
          "type": "DISTRIBUTED_PORTGROUP",
          "opaque_network_type": null,
          "connection_cookie": 1884582175,
          "host_device": null
        },
        "start_connected": true,
        "pci_slot_number": 160,
        "type": "VMXNET3",
        "upt_compatibility_enabled": true,
        "allow_guest_control": true,
        "mac_type": "ASSIGNED",
        "mac_address": "00:50:56:af:db:98"
      },
      "key": "4000"
    }
  ],
  "parallel_ports": [],
  "guest_os": "VMWARE_PHOTON_64",
  "name": "FaH_1.0.0_01",
  "power_state": "POWERED_ON",
  "sata_adapters": [],
  "cpu": {
    "count": 8,
    "hot_add_enabled": false,
    "hot_remove_enabled": false,
    "cores_per_socket": 1
  },
  "serial_ports": [],
  "floppies": [],
  "scsi_adapters": [
    {
      "value": {
        "pci_slot_number": 16,
        "type": "LSILOGIC",
        "label": "SCSI controller 0",
        "scsi": {
          "unit": 7,
          "bus": 0
        },
        "sharing": "NONE"
      },
      "key": "1000"
    }
  ],
  "boot": {
    "retry_delay": 10000,
    "enter_setup_mode": false,
    "delay": 0,
    "type": "BIOS",
    "network_protocol": null,
    "efi_legacy_boot": null,
    "retry": false
  }
}
```

## vCloud Director SDK with Codegen

Last example, using vCloud Director.

```bash
# Get the API swagger description
curl -sk https://$VMWARE_VCD_HOSTNAME/api-explorer/tenant/orgdemo/cloudapi.json \
  > codegen/in/cloudapi.json

# Create a config file for our future python module
echo '{
  "packageName":"vcd_client",
  "projectName":"vcd-client",
  "packageVersion":"9.7.1"
}' > codegen/in/config_vcd_client.json

# Generate the SDK
docker run --rm -v ${PWD}/codegen:/local \
  swaggerapi/swagger-codegen-cli generate \
    -i /local/in/cloudapi.json \
    -o /local/out/python-vcd \
    -c /local/in/config_vcd_client.json \
    -l python

# Install new python mdule with PIP
pip install codegen/out/python-vcd
```

### Prepare a client object

We import our new `vcd_client` module, we setup the target hostname, the authentication settings.

```python
import vcd_client
from vcd_client.rest import ApiException
from utils import *
import os
logger = logging.getLogger("DEMO_VCD")

# Configure API
configuration = vcd_client.Configuration()
configuration.verify_ssl = False
configuration.host = f"https://{os.environ.get('VMWARE_VCD_HOSTNAME')}/cloudapi"

# credentials
_username = os.environ.get('VMWARE_VCD_USERNAME')
_password = os.environ.get('VMWARE_VCD_PASSWORD')
auth_str = basic_auth_str(_username, _password)

# Create a client
client = vcd_client.ApiClient(configuration)
```

### Get a new session

```python
# Get a new session
try:
    logger.debug("Starting a new session")
    s = vcd_client.SessionsApi(client)
    s_headers = s.login_with_http_info(authorization=auth_str)[2]
except ApiException as e:
    print("Exception when creating session: %s\n" % e)
    exit(-1)
logger.info("New session is created")

# Update client with access token
logger.debug("Setting new session authorization token in headers")
configuration.api_key_prefix['Authorization'] = 'Bearer'
configuration.api_key['Authorization'] = s_headers.get(
    "X-VMWARE-VCLOUD-ACCESS-TOKEN"
)
client = vcd_client.ApiClient(configuration)
logger.info(f"Client credentials updated to use access token: {s_headers.get('X-VMWARE-VCLOUD-ACCESS-TOKEN')}")
```

**Output**:

```
DEMO_VCD 	Starting a new session
DEMO_VCD 	New session is created
DEMO_VCD 	Setting new session authorization token in headers
DEMO_VCD 	Client credentials updated to use access token: eyJhbGciOiJSUzI1NiJ9...
```

### Get some content

We will use our session and list our rights in the current organization:

```python
# List rights of the current user
logger.debug("Getting rights of the current user")
rapi = vcd_client.RightsApi(client)
page, page_size = 1, 25
try:
    for right in rapi.query_rights(page, page_size).values:
        logger.info(" - ".join([right.name, right.id, right.right_type]))
except ApiException as e:
    logger.error("Exception when calling RightsApi->query_rights: %s\n" % e)
```

**Output** (only fist part):

```
DEMO_VCD 	Getting rights of the current user
DEMO_VCD 	Organization vDC Gateway: Configure DNS - urn:vcloud:right:d85b0e92-b9e8-31af-9b19-23cd00cae7e7 - MODIFY
DEMO_VCD 	Organization vDC Gateway: View DNS - urn:vcloud:right:c6563392-f6b3-3dd6-9720-b304e6319672 - VIEW
DEMO_VCD 	Token: Manage - urn:vcloud:right:23e7a571-4928-3c49-891f-f835474a9dc3 - MODIFY
DEMO_VCD 	Token: Manage All - urn:vcloud:right:67878e89-9d94-302f-92fd-997313c68ee1 - MODIFY
DEMO_VCD 	API Explorer: View - urn:vcloud:right:9ff43a6c-2c50-3b53-b00f-6f020b6bb5a0 - VIEW
```

## Conclusion

As you see, it is very easy to generate a new API client SDK from a VMware product. Authentication could require some customization but the most limiting thing will be linked to the limited available actions through the REST API on some products.

Anyway, for the available and documented REST API parts, you can now deliver/provide a lot of SDK, even without knowing the bases of the used language.