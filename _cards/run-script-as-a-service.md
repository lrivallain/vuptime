---
layout: card
title: Run script as a service
author: aharlaut
tags: linux script service systemd
date: 2018-08-20
---

Daemon *systemd* allows to manage custom services and run a script as a service if it needs to be executed continuously ( Ex : REST API ).

# Create the unit file

Create a unit file with the extension *service* on the following path :
```
/etc/systemd/system
```

Example :

```
/etc/systemd/system/my-custom-service.service
```

Once created, configure the unit file with the following sections :

### Unit
```
[Unit]
Description=" My custom service"
After="network-online.target"
```


The description of the custom service will be shown when querying its status.

On this case, the service will be started once the network will be up.

### Service

 ```
[Service]
ExecStart=/usr/bin/env python3 /scripts/my-script.py
Restart=on-failure
RestartSec=5
```

*ExecStart* defines command to launch.

This service will restart every 5s in case of failure.



### Install

```
[Install]
WantedBy=multi-user.target
Alias=my-custom-service.service
```

*WantedBy* defines the target run-level (0 to 6).

*Alias* is a custom name to call the service.


# Starting the custom service

The custom service can be now launched with the following command :

```
service my-custom-service start
```

Check the status :

```
service my-custom-service status
```

# Documentation

All the options for the unit file are described on this [link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system_administrators_guide/sect-Managing_Services_with_systemd-Unit_Files#tabl-Managing_Services_with_systemd-Service_Sec_Options)

