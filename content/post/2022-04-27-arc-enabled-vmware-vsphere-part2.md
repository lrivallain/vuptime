---
author: lrivallain
date: "2022-04-27"
thumbnail: /images/arc-vmware/icon-arc-vmw-vm.png
splash: /images/splash/siarhei-palishchuk.jpg
splash_credits: Photo by Siarhei Palishchuk on Unsplash
featureImage: /images/splash/siarhei-palishchuk.jpg
categories:
- VMware
- Azure
tags:
- vmware
- azure
- azure vmware solution
- avs
- arc
- hybrid cloud
toc: true
title: "Public preview – Azure Arc-enabled VMware vSphere – Part 2"
aliases:
- /2022/04/27/arc-enabled-vmware-vsphere-part2
---

In the [previous post (part 1)](/2022/04/25/arc-enabled-vmware-vsphere-part1), we covered the capabilities of *Azure Arc-enabled VMware vSphere*: a solution to extend Azure governance and management policies to VMware based workload.

We also deployed a *Resource Bridge* to establish the connection between a VMware environment and Azure. We can now explore vCenter inventory through Azure and manage Virtual Machines.

## Explore vCenter inventory from Azure UI

When vCenter and *Resource Bridge* are connected to Azure Arc, you can explore its content and connection status:

![vCenter details in Azure Portal](/images/arc-vmware/arc-vmware-vcenter.png)

In order to use a resource in Azure, an activation is required: Use the **Enable in Azure** to activate an existing VMware resource in Azure. As with any Azure-based resource, RBAC strategies can be applied to provide or restrict access to *Azure-enabled* resources.

> ResourcePool, Networks, Templates and Datastores will appear as *hidden resources* in Azure *ResourceGroup* you will select in the activation process. They will be used for the VM creation process but cannot be edited from Azure.

### ResourcePools

VMware *ResourcePools* cannot be created, edited or remove but can be registered for VM creation scenario. By default, all resourcePools will be displayed in the inventory list (including Cluster and Hosts resourcePool representation). You can enable a ResourcePools in Azure by selecting it and click on **Enable in Azure**. You will be prompted for an Azure *ResourceGroup* attachment and the resourcePool will then be displayed with a link to explore its details.

![ResourcePools resources in Azure Portal](/images/arc-vmware/arc-vmware-resourcepool.png)

### VM Templates

VMware *VM Templates* cannot be created, edited or remove but can be registered for VM creation scenario. By default, all VM Templates will be displayed in the inventory list. You can enable a VM Template in Azure by selecting it and click on **Enable in Azure**. You will be prompted for an Azure *ResourceGroup* attachment and the Template will then be displayed with a link to explore its details.

> **Note**: Currently, the template from the Content Library are not available. Only VM template from vCenter VM-folders inventory are usable in *Azure Arc-enabled VMware vSphere*.

![VM Templates in Azure Portal](/images/arc-vmware/arc-vmware-template.png)

### Networks

VMware *Networks* cannot be created, edited or remove but can be registered for VM creation scenario. By default, all networks (NSX-T segments, PortGroups and DvPortGroups) will be displayed in the inventory list. You can enable a network in Azure by selecting it and click on **Enable in Azure**. You will be prompted for an Azure *ResourceGroup* attachment and the Template will then be displayed with a link to explore its details.

![Networks in Azure Portal](/images/arc-vmware/arc-vmware-network.png)

### Datastores

VMware *Datastores* cannot be created, edited or remove but can be registered for VM creation scenario. By default, all Datastores will be displayed in the inventory list. You can enable a Datastore in Azure by selecting it and click on **Enable in Azure**. You will be prompted for an Azure *ResourceGroup* attachment and the Datastore will then be displayed with a link to explore its details.

![Datastores in Azure Portal](/images/arc-vmware/arc-vmware-datastore.png)

## VMware Virtual Machine management through Azure

As mentioned in the previous parts of this post, ResourcePool, Networks, Templates and Datastores cannot be created, edited or deleted through Azure (UI, API, ARM etc.) but can be registered with ReadOnly access to provide Virtual Machines deployment dependencies.

The set of actions available for VMware Virtual Machines through Azure is more significant as you can:

* Run power operations (Start/Stop/Restart)
* Reconfigure Virtual Machine:
  * CPU/Memory (for powered-off VM)
  * Disk(s) - Add/remove/resize
  * Networks - Add/remove/Change network attachment
* Enable Arc-based guest management and install extensions
* Apply RBAC and tagging policies

> *VMware Arc-based guest extensions* are [currently limited to 2 extensions](https://docs.microsoft.com/en-us/azure/azure-arc/vmware-vsphere/manage-vmware-vms-in-azure#supported-extensions-and-management-services): Log Analytics agent and cCustom Script execution.

### Azure Arc enabled servers

If *Azure Arc-enabled VMware vSphere* based guest agent is currently limited to 2 extensions, it is still possible to use the normal Arc process to integrate the guest OS management of deployed servers through Azure and to benefit from all the capabilities of [Azure Arc](https://azure.microsoft.com/en-us/services/azure-arc/#product-overview) like (as mentioned in the [Arc documentation](https://docs.microsoft.com/en-us/azure/azure-arc/overview)):

* Manage your entire environment together by projecting your existing non-Azure and/or on-premises resources into Azure Resource Manager.
* Manage virtual machines, Kubernetes clusters, and databases as if they are running in Azure.
* Use familiar Azure services and management capabilities, regardless of where they live.
* Continue using traditional ITOps while introducing DevOps practices to support new cloud native patterns in your environment.
* Configure custom locations as an abstraction layer on top of Azure Arc-enabled Kubernetes clusters and cluster extensions.

> **Personal experience**: I use this combination of *Azure Arc-enabled VMware vSphere* and *Azure Arc-enabled Servers* to fully manage, with Azure, VMware Virtual Machine objects and their Guest OS. This provide me the best of the two solutions.

### Register an existing VM

You can enable a Virtual Machine in Azure by selecting it and click on **Enable in Azure**. You will be prompted for an Azure *ResourceGroup* attachment and the VM will then be displayed with a link to explore its details.

![Details of an Azure-enabled VMware Virtual Machine](/images/arc-vmware/arc-vmware-vm-details.png)

### Create a VM

A VM object can also be fully created from Azure (UI or API).

1. From the Arc Virtual Machines or Arc-registered vCenter list of VMs, click on **Create** button to start the VM creation wizard.

![VMware Virtual Machine creation process – Step 1](/images/arc-vmware/arc-vmware-vm-creation-1.png)

2. You can select a ResourceGroup to attach the VM to, then provide some details for the VM deployment:
  * A name
  * The *custom-location* and object type (*VMware*)
  * The target *resourcePool*
  * The *VM Template* to use
  * VM CPU and Memory configuration if you choose to override the template settings
  * Administrator login and password if you choose to enable guest management during the creation process

![VMware Virtual Machine creation process – Step 2](/images/arc-vmware/arc-vmware-vm-creation-2.png)

3. The second step of the wizard is for virtual disks configuration: name, size, controller and persistence.

![VMware Virtual Machine creation process – Step 3](/images/arc-vmware/arc-vmware-vm-creation-3.png)

4. The third step of the wizard provide network settings configuration (network attachment, IP settings etc.)

![VMware Virtual Machine creation process – Step 4](/images/arc-vmware/arc-vmware-vm-creation-4.png)

5. In the fourth step, you can add tag/value to the VM object (tag will only apply on Azure side: not VMware side.)

![VMware Virtual Machine creation process – Step 5](/images/arc-vmware/arc-vmware-vm-creation-5.png)

6. The last step provide a pane to validate the requested changes and to start the deployment.

![VMware Virtual Machine creation process – Step 6](/images/arc-vmware/arc-vmware-vm-creation-6.png)

7. When the deployment process is completed, you can see its results and display the deployed resources.

![VMware Virtual Machine creation process – Step 6](/images/arc-vmware/arc-vmware-vm-creation-7.png)

You can now compare the view on the same VM object from vCenter and from Azure UI:

![VMware Virtual Machine creation process – Step 6](/images/arc-vmware/arc-vmware-vm-creation-8.png)

## Azure governance on VMware based resources

One of the main benefit from managing VMware resources from Azure is the possibility to apply standard Azure governance strategies like:

### Grouping and tagging

VMware resources that are enabled in Azure can be attached to Azure *ResourceGroups* and benefit from the governance inheritance on resource objects (RBAC, locks etc.)

VMware resources can also be tagged in order to filter resources in search operations or to manage resources costing and attributions.

![Azure ResourceGroup and Tags applied to a VMware resource](/images/arc-vmware/arc-vmware-vm-rg-tags.png)

### RBAC

You can apply Azure RBAC strategies to VMware resources that are enabled in Azure and provide, ReadOnly, Contribution or ownership to the resources.

![Azure RBAC applied to a VMware resource](/images/arc-vmware/arc-vmware-vm-rbac.png)

### Lock

You can also prevent deletion or modification by using Azure Lock and the dependencies from Subscription or ResourceGroup:

![Delete lock applied to a VMware resource](/images/arc-vmware/arc-vmware-vm-lock.png)

## Upcoming

As you may have noticed in the last screens of the deployment, it is possible to get/download the ARM template that represents the ongoing deployment. This will be covered in the upcoming post about automation capabilities provided by *Azure Arc-enabled VMware vSphere*.

### Credits

Title photo by [Siarhei Palishchuk](https://unsplash.com/@smeshny) on [Unsplash](https://unsplash.com/photos/l5QjpiLwJ_E)
