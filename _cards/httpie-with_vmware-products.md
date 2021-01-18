---
layout: card
title: HTTPie – quick memo on the usage with VMware products
tags: api httpie cli linux vmware
author: lrivallain
date: 2020-12-14
---

Here is a quick memo on the usage of [HTTPie](https://httpie.io) to connect to VMware products to explore or use the API.

## Install

(Ubuntu/Debian)

```bash
sudo apt  install -qy jq
sudo pip3 install -U httpie
```

## VMware vCenter

```bash
# login
http POST https://vcsa.vlab.lcl/rest/com/vmware/cis/session --verify=no --session=vcsa -a 'administrator@vsphere.local:VMware1!'

# list VMs
http https://vcsa65.vlab.lcl/rest/vcenter/vm --verify=no --session=vcsa
```

## VMware vCloud Director

```bash
# One liner login
export VCD_TOKEN=$(http POST https://vcd.vlab.lcl/api/sessions "Accept: application/*+json;version=32.0" --session=vcd --verify=no -a 'administrator@System:VMware1!' -h | grep X-VMWARE-VCLOUD-ACCESS-TOKEN | cut -d' ' -f2)

# List VMs
http "https://vcd.vlab.lcl/api/query?type=vm" \
    "Accept: application/*+json;version=32.0" \
    "Authorization: Bearer $VCD_TOKEN"

# Filtering
http "https://vcd.vlab.lcl/api/query?type=vm&filter=isVAppTemplate==false;name==mstr-rm7c" \
    "Accept: application/*+json;version=32.0" \
    "Authorization: Bearer $VCD_TOKEN"

# Change tenant context
http "https://vcd.vlab.lcl/api/query?type=vm&filter=isVAppTemplate==false;name==mstr-rm7c" \
    "Accept: application/*+json;version=32.0" \
    "X-VMWARE-VCLOUD-TENANT-CONTEXT: <org id>" \
    "Authorization: Bearer $VCD_TOKEN"
```

## NSX-V

NSX-V API requires basic-auth but does not provide a specific endpoint to create a session. Nevermind you can use the following command to create a HTTPie session, named `nsx`, and test it. 

Then other API call will not require the authentication credentials (just the mention of the session to use).

```bash
# login
http https://nsxmgr.vlab.lcl/api/2.0/services/usermgmt/user/admin --session=nsx -a 'admin:VMware1!'

# Show DFW config
http https://nsxmgr.vlab.lcl/api/4.0/firewall/globalroot-0/config "Accept: application/json" --session=nsx
```
