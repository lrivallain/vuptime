---
author: lrivallain
categories:
- VMware
date: "2017-09-04T00:00:00Z"
tags:
- vmware
- scsi
- fsck
- psc
- vcsa
- boot
- timeout
title: VMware - VCSA 6.5u0 or PSC appliance - change SCSI block timeout
aliases: 
- /2017/09/04/vmware_vcsa65u0_change_scsi_block_timeout/
toc: true
---

In a previous post, I've already talk about an issue occuring in a lab environment with vCSA 6.5u0 and PSC appliance : [VCSA or PSC appliance won't boot after hard shutdown](/2017/05/10/VMware-VCSA-PSC-wont-boot/).

As the issue became more regular with time, I tried to figure out the root cause of those events.

As system's logs reports SCSI timeout on write operations, I remember myself that the default 30 seconds timeout could be insufficient in some virtualized environment. So the proposal to fix it, is the modification of timeout to a higher value.

# Default appliance's settings

We can display the current (default at this time) value of SCSI timeout for any block device of the system with the following command (based on `sysfs`, a [pseudo file system provided by the Linux kernel](https://en.wikipedia.org/wiki/Sysfs) since version 2.6):

```bash
for d in `ls /dev/sd* | egrep "sd[a-z]$"`; do
    printf "`basename $d`: "
    cat /sys/block/`basename $d`/device/timeout;
done
```

```
sda: 30
sdb: 30
sdc: 30
sdd: 30
sde: 30
sdf: 30
sdg: 30
sdh: 30
sdi: 30
sdj: 30
sdk: 30
sdl: 30
```

Following command shows the same informations:

`find /sys/class/scsi_generic/*/device/timeout -exec grep -H . '{}' \;`
```
/sys/class/scsi_generic/sg0/device/timeout:30
/sys/class/scsi_generic/sg10/device/timeout:30
/sys/class/scsi_generic/sg11/device/timeout:30
/sys/class/scsi_generic/sg12/device/timeout:30
/sys/class/scsi_generic/sg1/device/timeout:30
/sys/class/scsi_generic/sg2/device/timeout:30
/sys/class/scsi_generic/sg3/device/timeout:30
/sys/class/scsi_generic/sg4/device/timeout:30
/sys/class/scsi_generic/sg5/device/timeout:30
/sys/class/scsi_generic/sg6/device/timeout:30
/sys/class/scsi_generic/sg7/device/timeout:30
/sys/class/scsi_generic/sg8/device/timeout:30
/sys/class/scsi_generic/sg9/device/timeout:30
```

As mentionned in [KB #1009465 *Increasing the disk timeout values for a Linux 2.6 virtual machine*](http://kb.vmware.com/kb/1009465), VMware tools creates a `udev` rule at `/etc/udev/rules.d/99-vmware-scsi-udev.rules` that sets the timeout to 180 seconds for each VMware virtual disk device and reloads the `udev` rules so that it takes effect immediately. But on the Photon appliance this udev rule doesn't exists anymore :

`ls -l  /etc/udev/rules.d/*vmware*`
```
-rw-r--r-- 1 root root 268 Sep 30  2016 /etc/udev/rules.d/99-vmware-hotplug.rules
-rw-r--r-- 1 root root 104 Oct 22  2016 /etc/udev/rules.d/99-vmware-udev.rules
```

__To compare only__: on a "non-Photon based" Linux VM, a `/etc/udev/rules.d/99-vmware-scsi-udev.rules` file exists (created by the VMware-tools installer) and contains:

```
#
# VMware SCSI devices Timeout adjustment
#
# Modify the timeout value for VMware SCSI devices so that
# in the event of a failover, we don't time out.
# See Bug 271286 for more information.

ACTION=="add", SUBSYSTEMS=="scsi", ATTRS{vendor}=="VMware  ", ATTRS{model}=="Virtual disk    ", RUN+="/bin/sh -c 'echo 180 >/sys$DEVPATH/timeout'"
```

So we probably need to increase the value by ourselves at each system startup : by using `rc.local` file for exemple.

[@tsugliani](https://twitter.com/tsugliani) remembers me the NetApp recommandations about disk timeout on virtualized guest OS : *[What are the guest OS tunings needed for a VMware vSphere deployment?](https://kb.netapp.com/support/s/article/ka21A0000000k7GQAQ/what-are-the-guest-os-tunings-needed-for-a-vmware-vsphere-deployment?language=en_US)*

| Guest OS Typ     | Historical Guest OS Tuning for SAN | Updated Guest OS Tuning for SAN |
|---               |---                                 |---                              |
| **Windows**      | disk timeout = 190                 | disk timeout = 60               |
| **Linux**        | disk timeout = 190                 | disk timeout = 60               |
| **Solaris**      | disk timeout = 190<br>busy retry = 300<br>not ready retry = 300<br>reset retry = 30<br>max.throttle = 32<br>min.throttle = 8 | disk timeout = 60<br>busy retry = 300<br>not ready retry = 300<br>reset retry = 30<br>max.throttle = 32<br>min.throttle = 8<br>corrected VID/PID specification |

VMware Support team confirms that the expected value is 180 seconds as configured in **VCSA 6.0 build-3339084**:

`find /sys/class/scsi_generic/*/device/timeout -exec grep -H . '{}' \;`
```
/sys/class/scsi_generic/sg0/device/timeout:180
/sys/class/scsi_generic/sg1/device/timeout:180
/sys/class/scsi_generic/sg10/device/timeout:180
/sys/class/scsi_generic/sg11/device/timeout:30
/sys/class/scsi_generic/sg2/device/timeout:180
/sys/class/scsi_generic/sg3/device/timeout:180
/sys/class/scsi_generic/sg4/device/timeout:180
/sys/class/scsi_generic/sg5/device/timeout:180
/sys/class/scsi_generic/sg6/device/timeout:180
/sys/class/scsi_generic/sg7/device/timeout:180
/sys/class/scsi_generic/sg8/device/timeout:180
/sys/class/scsi_generic/sg9/device/timeout:180
```


# Fix SCSI timeout

There is multiple ways to fix the SCSI timeout value:
1. Upgrade to VCSA 6.5u1 (aka build 5973321)
1. Manually add the udev rule
1. Add a `rc.local` file (not recommended)

## VCSA upgrade way

It's not mentionned in the [Relase Notes](https://docs.vmware.com/en/VMware-vSphere/6.5/rn/vsphere-vcenter-server-651-release-notes.html#storage-issues-resolved), but **VCSA 6.5 build 5973321** include a fix for the missing udev rule with openvm-tools :

`find /sys/class/scsi_generic/*/device/timeout -exec grep -H . '{}' \;`
```
/sys/class/scsi_generic/sg0/device/timeout:30
/sys/class/scsi_generic/sg10/device/timeout:180
/sys/class/scsi_generic/sg11/device/timeout:180
/sys/class/scsi_generic/sg12/device/timeout:180
/sys/class/scsi_generic/sg1/device/timeout:180
/sys/class/scsi_generic/sg2/device/timeout:180
/sys/class/scsi_generic/sg3/device/timeout:180
/sys/class/scsi_generic/sg4/device/timeout:180
/sys/class/scsi_generic/sg5/device/timeout:180
/sys/class/scsi_generic/sg6/device/timeout:180
/sys/class/scsi_generic/sg7/device/timeout:180
/sys/class/scsi_generic/sg8/device/timeout:180
/sys/class/scsi_generic/sg9/device/timeout:180
```

An upgrade is the best way to avoid this issue.

## Manually add the udev rule

It's possible to manually add the missing udev rule and to apply it :

```bash
echo "
ACTION==\"add\", SUBSYSTEMS==\"scsi\", ATTRS{vendor}==\"VMware*\" , ATTRS{model}==\"Virtual disk*\", RUN+=\"/bin/sh -c 'echo 180 >/sys$DEVPATH/device/timeout'\"
ACTION==\"add\", SUBSYSTEMS==\"scsi\", ATTRS{vendor}==\"VMware*\" , ATTRS{model}==\"VMware Virtual S\", RUN+=\"/bin/sh -c 'echo 180 >/sys$DEVPATH/device/timeout'\"
" > /etc/udev/rules.d/99-vmware-scsi-udev.rules
```

A **reboot is necessary** to apply the new rule (the hot command `udevadm control --reload-rules && udevadm trigger` didn't work for me).

## The rc.local way

By default , there is no created rc.local file on the Photon based appliance to run simple commands at every system startup. But it's simple to find out where to create this file by displaying the  systemd `rc-local` service configuration:

`systemctl cat rc-local`
```
# /etc/systemd/system/rc-local.service
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.

# This unit gets pulled automatically into multi-user.target by
# systemd-rc-local-generator if /etc/rc.d/rc.local is executable.
[Unit]
Description=/etc/rc.d/rc.local Compatibility
ConditionFileIsExecutable=/etc/rc.d/rc.local
After=network.target

[Service]
Type=forking
ExecStart=/etc/rc.d/rc.local start
TimeoutSec=0
RemainAfterExit=yes
```

As mentionned, the `/etc/rc.d/rc.local` must be created and executable. Let's do it !

`vi /etc/rc.d/rc.local`
```
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.


# Change defaut SCSI timeout on all disks
for d in `ls /dev/sd* | egrep "sd[a-z]$"`
do
  echo 180 > /sys/block/`basename $d`/device/timeout
done

exit 0
```

When saved, we change the file permission to make it executable:

`chmod +x /etc/rc.d/rc.local`

Then we activate the `rc-local` on system startup:

`systemctl enable rc-local`

And we test it

`systemctl start rc-local`

No restart is needed to apply the new timeout settings. At every system startup, the `rc.local` file will be instantiate and the timeout value increased from 30 seconds to 180.

# Check new timeout value

```bash
for d in `ls /dev/sd* | egrep "sd[a-z]$"`; do
    printf "`basename $d`: "
    cat /sys/block/`basename $d`/device/timeout;
done
```

```
sda: 180
sdb: 180
sdc: 180
sdd: 180
sde: 180
sdf: 180
sdg: 180
sdh: 180
sdi: 180
sdj: 180
sdk: 180
sdl: 180
```

Each block device should now use a 180 second timeout for SCSI commands.
