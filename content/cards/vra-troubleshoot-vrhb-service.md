---
layout: card
title: vRealize Automation – Troubleshoot Health broker service
author: lrivallain
author_name: Ludovic Rivallain
tags:
- vmware
- vrealize
- automation
- vra
- troubleshoot
date: 2018-07-15
---

# Simple restart of health broker service

```bash
service vrhb-service on # ensure that service is activated
service vrhb-service restart
```

# Reset health broker service data

In case of non-working health management page (error message displayed or white/missing content), and after having tested the previous troubleshoot method it could be necessary to reset the data generated by the service.
> Warning: This action remove all existing content of the health broker service!

```bash
service vrhb-service stop
rm -r /var/lib/vrhb/service-host/sandbox
rm -r /var/lib/vrhb/vra-tests-host/sandbox
service vrhb-service start
```
