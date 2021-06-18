---
author: lrivallain
categories:
- VMware
date: "2017-05-10T00:00:00Z"
tags: vmware psc vcsa boot fsck
title: VMware - VCSA or PSC appliance won't boot after hard shutdown
---

I started using the VMware *Photon* based appliances to deploy vCenter services (VCSA) and PSC with the 6.5 version several months ago.

It's really stable and I appreciate to use it daily and to replace the windows based services with the appliance ones. But a couple of days ago, I had a bad suprise in a lab environment where 2 PSC instances were unable to boot after a hard power-off.

Here is a screenshot of the PSC console during the boot sequence:

{% include lightbox.html src="/images/psc-wont-boot-1.png" title="PSC console during the boot sequence" %}

When logging with root credentials, I wasn't able to start services (as network) but I was able to manually set an IP address to the ethernet interface.

It tooks me quite a lot of time, searching in logs, to find out the root cause:

```
journalctl -xb
```

{% include lightbox.html src="/images/psc-wont-boot-2.png" title="The root cause" %}

``/dev/mapper/log_vg-log`` partition was in error during the boot filesystem check.

To fix it quickly (and dirty):

```
fsck.ext4 /dev/mapper/log_vg-log -y
```

The ``-y`` option is set to accept the default error fixing suggested by the fsck.ext4 tool.

From that point, a simple reboot was necessary to get back the lab service up.
