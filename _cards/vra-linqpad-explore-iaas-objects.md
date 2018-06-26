---
layout: card
title: vRealize Automation – Explore IaaS objects with Linqpad
tags: vmware vrealize automation iaas vra
date: 2018-06-21
---

Get [Linqpad](https://www.linqpad.net/) and run the setup.

# Connect

Once installed, you can connect LinqPad with your IaaS server:
* URL: `https://iaas-manager.domain.tld/Repository/Data/ManagementModelEntities.svc`
* Type: *ODATA3*
* Credential: *IaaS Service Account*

After validation, and a couple of minutes to load the database schema, you should see the list of tables:

![]()

And on the right part of screen you can enter *C# Expression* (by default) requests.

# Requests

Here are some requests samples:

To get a subset list of VMs in the IaaS db:
```
VirtualMachines.Take(100)
```

To filter on VM name:
```
VirtualMachines.Where(vm=> vm.VirtualMachineName == "MyVMName")
```

To display expanded properties of an object, it's possible to use:
```
VirtualMachines.Expand("StaticIPv4Addresses").Where(vm=> vm.VirtualMachineName == "MyVMName")
```

# Credits

This card is highly inspired by the two following blog posts:
* [Pierrelx's LAB – vRealize Automation/Orchestrator Find Objects and Properties](http://pierrelx.com/vrealize-automationorchestrator-find-objects-and-properties)
* [Tom@clearascloud – Common LINQ Queries for vCAC](https://clearascloud.com/2013/01/20/common-linq-queries-for-vcac/)
