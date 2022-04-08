---
layout: card
title: Azure VMware Solution - Parse vmwaresyslog from storage account export
tags:
- vmware
- avs
- azure
- troubleshooting
- logs
date: 2022-04-08
---

When you configure an AVS (Azure VMware Solution) logs export to a Storage Account, the logs are encapsulated in a JSON wrapping.

```bash
tail PT1H.json | jq
```

```json
{
  "message": "2022-04-07T13:59:59.685Z esx07-r07.p01.westeurope.avs.azure.com VSANMGMTSVC: info vsand[2103808] [opID=Thread-2 VsanInternalSystem::get_diskdata] Get local host UUID 60d101eb-dfb2-ec4a-1d65-98039b92960e",
  "resourceId": "/SUBSCRIPTIONS/B1E061C8-xxxx-xxxx-xxxx-1241FD840A48/RESOURCEGROUPS/TEST-RG/PROVIDERS/MICROSOFT.AVS/PRIVATECLOUDS/TESTAVS001",
  "operationName": "Microsoft.AVS/vcenter/vmwaresyslog",
  "category": "vmwaresyslog",
  "properties": "{}"
}
{
  "message": "2022-04-07T13:59:59.685Z esx07-r07.p01.westeurope.avs.azure.com VSANMGMTSVC: info vsand[2103808] [opID=Thread-2 VsanInternalSystem::get_diskdata] get_diskdata took 0.004s",
  "resourceId": "/SUBSCRIPTIONS/B1E061C8-xxxx-xxxx-xxxx-1241FD840A48/RESOURCEGROUPS/TEST-RG/PROVIDERS/MICROSOFT.AVS/PRIVATECLOUDS/TESTAVS001",
  "operationName": "Microsoft.AVS/vcenter/vmwaresyslog",
  "category": "vmwaresyslog",
  "properties": "{}"
}
```

This could be difficult to read from a command line but you can easly unwrap the syslog formated `message` by using `jq`:

```bash
tail PT1H.json | jq ".message" |sed 's/^\"\(.*\)\"$/\1/'
# Output
2022-04-07T13:59:59Z esx07-r07.p01.westeurope.avs.azure.com nsx-proxy: NSX 2105074 - [nsx@6876 comp=\"nsx-esx\" subcomp=\"nsx-proxy\" s2comp=\"mpa-proxy-lib\" tid=\"2105123\" level=\"INFO\"] ForwardingEngine: Processing SignalEvent(IDLE)
2022-04-07T13:59:59Z esx07-r07.p01.westeurope.avs.azure.com nsx-proxy: NSX 2105074 - [nsx@6876 comp=\"nsx-esx\" subcomp=\"nsx-proxy\" s2comp=\"mpa-proxy-lib\" tid=\"2105123\" level=\"INFO\"] Idle event during ready
```

> `jq` will only provide the content of the `message` attribute for each JSON item and sed will remove the front and trailing double quotes.