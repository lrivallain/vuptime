---
layout: card
title: vCloud Director – Change the timeout configuration for extensibility
tags: vmware vcloud director extension plugin timeout
author: lrivallain
date: 2020-04-20
---

Use following commands to set a customized value for request timeout for API extension services:

SSH to the vCloud cell(s) then:

```bash
cd /opt/vmware/vcloud-director/bin
# Get the current value
./cell-management-tool manage-config -n extensibility.timeout -l
# Change value
./cell-management-tool manage-config -n extensibility.timeout -v 40
```
