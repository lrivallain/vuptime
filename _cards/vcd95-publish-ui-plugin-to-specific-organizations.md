---
layout: card
title: vCloud Director 9.5 – Publish UI Plugin to specific organizations
tags: vmware vcloud director extension plugin curl
author: lrivallain
date: 2019-08-05
---

Use these (with caution) commands to publish a vCloud Director's UI plugin to specific organisations of your deployment:

```bash
# Prepare settings
vcloud_host="vcd.vuptime.io" # specify your vcd host
vcloud_token="ff27f9fde1784b4289c58e7f848190c7" # specify an auth token for a system administrator account

# Get the plugin ID
curl -ks -H "x-vcloud-authorization: $vcloud_token" https://$vcloud_host/cloudapi/extensions/ui | python -m json.tool # get the appropriate ID
plugin_id="urn%3Avcloud%3AuiPlugin%3Ace095910-f925-4de3-ae98-8a6c868d62f5" # You can use an url encoder tool like https://www.urlencoder.org/

# Unpublish UI Plugin for ALL organizations
curl -ks -H "x-vcloud-authorization: $vcloud_token" -H "Accept: application/json" -X POST "https://$vcloud_host/cloudapi/extensions/ui/$plugin_id/tenants/unpublishAll"

# Get target org's URN ID+name:
curl -ks -H "x-vcloud-authorization: $vcloud_token" -H "Accept: application/*+xml;version=31.0" "https://$vcloud_host/api/query?type=organization&format=references&pageSize=128"

# Send the correct data for UI publication
curl -ks -H "x-vcloud-authorization: $vcloud_token" -H "Accept: application/json" -H "Content-Type: application/json" -X POST "https://$vcloud_host/cloudapi/extensions/ui/$plugin_id/tenants/publish" -d '[
  {
    "name": "Org1",
    "id": "urn:vcloud:org:82e52bcd-bcfa-4d7a-b0b8-25b0f246d5c3"
  },{
    "name": "Org2",
    "id": "urn:vcloud:org:8c4617d3-7705-48d3-a389-e9e3729dc9ee"
  }
]'

# Check publication
curl -ks -H "x-vcloud-authorization: $vcloud_token" -H "Accept: application/json" "https://$vcloud_host/cloudapi/extensions/ui/$plugin_id/tenants/"
```

To (re-)publish UI plugin for all organizations back:

```bash
# Publish for ALL
curl -ks -H "x-vcloud-authorization: $vcloud_token" -H "Accept: application/json" -X POST "https://$vcloud_host/cloudapi/extensions/ui/$plugin_id/tenants/publishAll"
```
