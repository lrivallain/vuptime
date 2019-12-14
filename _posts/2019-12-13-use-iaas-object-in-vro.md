---
layout: post
title: Interact with the vRealize Automation IaaS objects on vRealize Orchestrator
author: aharlaut
category: VMWare
tags: vmware vra vro iaas vrealize orchestrator automation modelmanager javascript
---

As described on another [blog post](/cards/vra-linqpad-explore-iaas-objects/), vRA IaaS objects can be gathered using the model manager.
This article will show you how to interact with this kind of object using ``vRealize Orchestrator``.

On this first sample, we are trying to get a virtual machine named ``TESTVM02`` on the model manager.
The VirtualMachine object has a property called ``VirtualMachineName`` that we can used to filter the virtual machine by its name.

![Image](/images/iaas_vro/model_manager_vm.png)

Here is the javascript code in order to get this virtual machine machine.
It will return a object of type [VCAC:Entity](http://www.vroapi.com/Class/vCAC/7.2.0/VCACEntity).

```javascript
// Inputs : vcacHost : vCAC:vCACHOST

// Define the virtual machine name to search
var vmName = 'TESTVM02';

// Use the management model
var modelName = 'ManagementModelEntities.svc';
// Get the virtual machines object
var entitySetName = 'VirtualMachines';
// Filter the result by the property VirtualMachineName
var filter = "VirtualMachineName eq '"+vmName+"'";
var orderBy = null;
var top = null;
var skip = 0;
var headers = null;
var select = null;

// Query the model manager
var vms = vCACEntityManager.readModelEntitiesBySystemQuery(vcacHost.id, modelName, entitySetName, filter, orderBy, select, top, skip, headers);
// Check if the virtual machine has been found
if(vms == null || vms == ''){
	var message = 'There is no virtual machine named '+vmName;
	System.warn(message);
}
else{
	var message = 'Virtual machine '+vmName+' found';
	System.log(message);
}
```
Workflow in action : 

![Image](/images/iaas_vro/workflow_iaas_get_vm.png)

Great ! Once the virtual machine captured, we can access to all its properties.
For instance, we need to know the vCPU and RAM configured on the virtual machine.
The request is simple, we'll use the method ``get_property`` on the object  ``VCAC:Entity``

You just need to get the corresponding properties names:
![Image](/images/iaas_vro/model_manager_vm_request.png)



```javascript
// Get the first virtual machine on the result (There is only one as we used the filter)
var vm = vms[0];
var vmVcpu = vm.getProperty('VMCPUs');
var vmRam = vm.getProperty('VMTotalMemoryMB');
System.log('The virtual machine '+vmName+' is configured '+vmVcpu+' vCPU and '+vmRam+' RAM');
```

![Image](/images/iaas_vro/workflow_iaas_get_vm_vcpu_ram.png)

Everything is working well, but now we also want to display the virtual machine hard-disks.
There is a property name called ``VMDiskHardware`` but not directly accessible because this is a child object of ``VirtualMachine``.

Using LINQPAD, we can access to this property by using the method ``expand``

```c#
VirtualMachines.Expand("VMDiskHardware").Where (v => v.VirtualMachineName == "TESTVM02")
```

![Image](/images/iaas_vro/model_manager_vm_disks.png)

With vRO, we have to use the the method ``get_link`` of the corresponding ``VCAC:Entity``
This method has 2 parameters :

* The first one is your IaaS manager ( ``vCAC:vCACHost`` object on vRO )
* The second is the link name ( the child object name ).

```javascript
var vmDisks = vm.getLink(vcacHost, 'VMDiskHardware');
for each(var vmDisk in vmDisks){
	diskName = vmDisk.getProperty('DiskName');
	diskSize = vmDisk.getProperty('Capacity');
	System.log(diskName+' is configured with '+diskSize+' GB');

}
```

![Image](/images/iaas_vro/workflow_iaas_get_vm_disks.png)

Perfect ! We can now request the IaaS database in order to get a lot of usefull information to extend the use on vRealize Automation.

To end this blog post, here is another sample to get the VirtualMachine created after a defined date :

![Image](/images/iaas_vro/model_manager_vm_date.png)

```javascript
// Inputs : startDate : Date; vcacHost : vCAC:vCACHOST

startDateFormatted = System.formatDate(startDate, "yyyy-MM-dd")+'T00:00:00';

//Define the model name
var modelName = 'ManagementModelEntities.svc';
//Get the virtual machines
var entitySetName = 'VirtualMachines';

//Get all the vcac vm created after the defined date
var filter = "VMCreationDate ge datetime'"+startDateFormatted+"'";
var orderBy = null;
var top = null;
var skip = 0;
var headers = null;
var select = null;

//Query the database
var vms = vCACEntityManager.readModelEntitiesBySystemQuery(vcacHost.id, modelName, entitySetName, filter, orderBy, select, top, skip, headers);
if(vms == null || vms == ''){
	var message = 'There is no created virtual machine after '+startDateFormatted;
	System.warn(message);
}
else{
	var message = 'There is '+vms.length+' created virtual machine after '+startDateFormatted
	System.log(message);
}
```
![Image](/images/iaas_vro/workflow_iaas_get_vm_by_date.png)

You are now ready the use the IaaS object directly in vRO ;)

