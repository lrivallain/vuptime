---
layout: card
title: vRealize Orchestrator – Enable HTTP basic Authentication over SSO
tags: vmware vrealize vro
author: lrivallain
date: 2019-02-25
---

In order to use the embedded swagger interface of a vRO instance (`/vco/api/docs/index.html`) it is necessary to enable HTTP basic Authentication over SSO through the `vmo.properties` file:

Log-in by SSH, add a line to the vmo properties file and restart service:

```bash
echo "com.vmware.o11n.sso.basic-authentication.enabled=true" >> /etc/vco/app-server/vmo.properties
service vco-server restart
```

Then you can use the swagger interface as a vRO API Explorer !

![Swagger UI of vRO instance](/images/vro/swagger_ui.png)
