---
layout: post
title: Play with VM snapshots and linked-clones with ESXi command line tools
author: lrivallain
category: VMWare
tags: clone esx esxi linked snapshot vim-cmd vm vmware
---

In this article, we will see how to create, commit, revert-to virtual machine snapshots from ESXi command line. We will also talk about the very useful "linked clones" that are related to the snapshot feature.

* Table of contents
{:toc}

# Prerequisites

You only need to have a running VM on the ESXi and to know its Vmid:

{% highlight bash %}
    $ vim-cmd vmsvc/getallvms
    Vmid      Name                           File                           Guest OS       Version   Annotation
    3      CentosTest   [LocalDatastore_001] CentosTest/CentosTest.vmx   otherLinuxGuest   vmx-10
{% endhighlight %}

# Snapshots

Here is the VMware definition of VM snapshot feature ([source](https://www.vmware.com/support/ws4/doc/preserve_snapshot_ws.html "Snapshot definition")):

> The snapshot feature is most useful when you want to preserve the state of the virtual machine so you can return to the same state repeatedly.

> You can take a snapshot of a virtual machine at any time and revert to that snapshot at any time.

> You can take a snapshot while a virtual machine is powered on, powered off or suspended. A snapshot preserves the virtual machine just as it was when you took the snapshot - the state of the data on all the virtual machine's disks and whether the virtual machine was powered on, powered off or suspended.

## Create snapshots

To create a snapshot, you can use the 'vim-cmd' command:

    $ vim-cmd vmsvc/snapshot.create 3 snap01 'snap01 description'

Command usage is:

> Usage: snapshot.create vmid [snapshotName] [snapshotDescription] [includeMemory] [quiesced]

So you can make a snapshot with VM memory and quiesced:

    vim-cmd vmsvc/snapshot.create 3 "SnapName" "Snap Description" 1 1

## Get snapshot(s) list

You may need to get the list of VM snapshots:

    $ vim-cmd vmsvc/snapshot.get 3
    Get Snapshot:
    |-ROOT
    --Snapshot Name        : snap01
    --Snapshot Id          : 1
    --Snapshot Desciption  : snap01 description
    --Snapshot Created On  : 2/23/2015 18:12:50
    --Snapshot State       : powered on
    --|-CHILD
    ----Snapshot Name        : snap02
    ----Snapshot Id          : 2
    ----Snapshot Desciption  : snap02 description
    ----Snapshot Created On  : 2/23/2015 18:13:15
    ----Snapshot State       : powered off
    ----|-CHILD
    ------Snapshot Name        : snap03
    ------Snapshot Id          : 3
    ------Snapshot Desciption  : snap03 description
    ------Snapshot Created On  : 2/23/2015 18:13:32
    ------Snapshot State       : powered off
    ------|-CHILD
    --------Snapshot Name        : snap04
    --------Snapshot Id          : 4
    --------Snapshot Desciption  : snap04 description
    --------Snapshot Created On  : 2/23/2015 18:13:59
    --------Snapshot State       : powered off

The list is displayed as a tree according to the parents or children of a snapshot.

## Remove/Commit a snapshot

As you can create and list snapshot(s) for a VM, you can remove them. Deletion operation is also called the "commit" as all recent changes made from the moment the snapshot is taken, are committed to the based disk or the parent snapshot disk file.

To remove or commit a snapshot for a VM:

> Usage: snapshot.remove vmid snapId

    $ vim-cmd vmsvc/snapshot.remove 3 4
    Remove Snapshot:
    |-ROOT
    --Snapshot Name        : snap01
    --Snapshot Id        : 1
    --Snapshot Desciption  : snap01 description
    --Snapshot Created On  : 2/23/2015 18:12:50
    --Snapshot State       : powered off
    --|-CHILD
    ----Snapshot Name        : snap02
    ----Snapshot Id        : 2
    ----Snapshot Desciption  : snap02 description
    ----Snapshot Created On  : 2/23/2015 18:13:15
    ----Snapshot State       : powered off
    ----|-CHILD
    ------Snapshot Name        : snap03
    ------Snapshot Id        : 3
    ------Snapshot Desciption  : snap03 description
    ------Snapshot Created On  : 2/23/2015 18:13:32
    ------Snapshot State       : powered off

There is also a ``snapshot.removeall`` argument to remove... all snapshots on a VM. \o/

## Revert to a snapshot

Goal of VM snapshot is not to only create, list or remove snapshots... It's to be able to revert the VM state to the moment you take the snapshot. To do so, you can use the ``snapshot.revert`` argument.

> Usage: snapshot.revert vmid snapshotId suppressPowerOff

So to revert to the first snapshot of the VM with Vmid 3:

    $ vim-cmd vmsvc/snapshot.revert 3 1 0
    Revert Snapshot:
    |-ROOT
    --Snapshot Name        : snap01
    --Snapshot Id          : 1
    --Snapshot Desciption  : snap01 description
    --Snapshot Created On  : 2/23/2015 18:12:50
    --Snapshot State       : powered on
    ...

This will restore VM, powered-on (!), at the state where you take the first snapshot. Last option is to revert to snapshot with or without memory content:

    suppressPowerOff = 0 
    |-> With RAM content
        |-> Virtual machine is restored with power-on state
    suppressPowerOff = 1
    |-> Without RAM content
        |-> Virtual machine is restored with power-off state

# Linked clone

Linked-clone definition ([source](https://pubs.vmware.com/workstation-9/index.jsp?topic=%2Fcom.vmware.ws.using.doc%2FGUID-BA264A65-C50F-4345-A787-DCC5C5324DD1.html "Linked clone definition")):

> A linked clone is a copy of a virtual machine that shares virtual disks with the parent virtual machine in an ongoing manner.

> Because a linked clone is made from a snapshot of the parent, disk space is conserved and multiple virtual machines can use the same software installation. All files available on the parent at the moment you take the snapshot continue to remain available to the linked clone.

> Ongoing changes to the virtual disk of the parent do not affect the linked clone, and changes to the disk of the linked clone do not affect the parent. A linked clone must have access to the parent. Without access to the parent, you cannot use a linked clone.

## Create a linked clone

Create a reference snapshot on a source VM. This will be our base for clones.

    $ vim-cmd vmsvc/snapshot.create 3 "ReferenceSnapshot" "Used for linked clones of Centos VM"
    Create Snapshot:
    $ vim-cmd vmsvc/snapshot.get 3
    Get Snapshot:
    |-ROOT
    --Snapshot Name        : ReferenceSnapshot
    --Snapshot Id          : 7
    --Snapshot Desciption  : Used for linked clones of Centos VM
    --Snapshot Created On  : 2/24/2015 21:22:25
    --Snapshot State       : powered off

To have more understandable command lines, we set in variable the reference and destination path:

    src="/vmfs/volumes/LocalDatastore_001/CentosTest"
    dst="/vmfs/volumes/LocalDatastore_001/LinkedClone1"

First step for a linked clone from command line, is to create a destination folder :

    mkdir $dst

Then we copy reference VM's ``.vmx`` file and the ``.vmdk`` (including the ``-delta`` file) corresponding to our reference snapshot:

    $ cat $src/CentosTest.vmx | grep fileName
    ide1:0.fileName = "cdrom0"
    scsi0:0.fileName = "CentosTest-000001.vmdk" **cp $src/CentosTest-000001*.vmdk $dst/
    $ cp $src/CentosTest.vmx $dst/

    $ ls $dst
    CentosTest-000001-delta.vmdk  CentosTest-000001.vmdk        CentosTest.vmx

Then we rename files:

    $ mv $dst/*-delta.vmdk $dst/LinkedClone1-000001-delta.vmdk
    mv $dst/*000001.vmdk $dst/LinkedClone1-000001.vmdk
    mv $dst/*.vmx $dst/LinkedClone1.vmx
    $ ls $dst
    LinkedClone1-000001-delta.vmdk  LinkedClone1-000001.vmdk        LinkedClone1.vmx        

Great ! Now we need to edit ``LinkedClone1.vmx`` file to made some changes:

*   remove ``sched.swap.derivedName`` line
*   remove ``uuid.location`` line
*   remove ``uuid.bios`` line
*   remove ``ethernet0.generatedAddress`` line (if generated mac address)
*   remove ``extendedConfigFile`` line if present

Then, edit the following lines:

*   ``displayName`` according to the name you whant to display in ESXi list of VMs
*   ``scsi0:0.fileName`` with vmdk new name
*   ``ethernet0.address`` if not a generated address

Last changes to made are in on the ``LinkedClone1-000001.vmdk`` file:

*   ``Extent description``, adapt the file name according to the delta file name of you linked clone.
*   ``parentFileNameHint`` with absolute path of the source vmdk file: ex: ``/vmfs/volumes/LocalDatastore_001/CentosTest/CentosTest.vmdk``

Last step is to register and start our VM:

    $ vim-cmd solo/registervm $dst/LinkedClone1.vmx
    $ vim-cmd vmsvc/getallvms
    Vmid      Name                             File                             Guest OS       Version
    3      CentosTest   [LocalDatastore_001] CentosTest/CentosTest.vmx       otherLinuxGuest   vmx-10
    6      CentosTest   [LocalDatastore_001] LinkedClone1/LinkedClone1.vmx   otherLinuxGuest   vmx-10
    $ vim-cmd vmsvc/power.on 6 && echo "Powered ON"
    Powering on VM:
    Powered ON

You can now check the benefits of a linked clone by looking at the size of the vdisk of this new VM:

    $ ls -lh delta.vmdk
    -rw-------    1 root     root       16.0M Feb 24 22:19 LinkedClone1-000001-delta.vmdk

And if we modify or create some file in the linkedClone VM, the vdisk usage increase:

    $ ls -lh delta.vmdk
    -rw-------    1 root     root       32.0M Feb 24 22:24 LinkedClone1-000001-delta.vmdk

Very useful to have tiny VM for specific usage !

## Convert a linked clone to a full clone

If you need to convert your LinkedClone VM to a virtual machine without link to the reference VM, you can use the vmkfstool:

    $ vmkfstools -d thin -i /vmfs/volumes/LocalDatastore_001/LinkedClone1/LinkedClone1-000001.vmdk /vmfs/volumes/LocalDatastore_001/LinkedClone1/LinkedClone1_full.vmdk
    Destination disk format: VMFS thin-provisioned
    Cloning disk '/vmfs/volumes/LocalDatastore_001/LinkedClone1/LinkedClone1-000001.vmdk'...
    Clone: 100% done.

Then you can compare the ``linked-cloned`` and the ``full-cloned`` vmdk(s):

    $ ls -lh *.vmdk
    -rw-------    1 root     root       32.0M Feb 25 01:23 LinkedClone1-000001-delta.vmdk
    -rw-------    1 root     root         369 Feb 24 22:17 LinkedClone1-000001.vmdk
    -rw-------    1 root     root        8.0G Feb 25 18:34 LinkedClone1_full-flat.vmdk
    -rw-------    1 root     root         528 Feb 25 18:34 LinkedClone1_full.vmdk

Finally you can (with powered-off VM) change vmdk path on the vmx file to use the newly created vmdk, and reload the vmx by using:

    $ vim-cmd vmsvc/reload 6

End ! Enjoy with VM snapshots and linked clones !
