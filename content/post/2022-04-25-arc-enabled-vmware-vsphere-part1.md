---
author: lrivallain
author_name: Ludovic Rivallain
date: "2022-04-25"
thumbnail: /images/arc-vmware/icon-arc-resource-bridge.png
splash: /images/splash/sea-joseph-barrientos.jpg
splash_credits: Photo by Joseph Barrientos on Unsplash
featureImage: /images/splash/sea-joseph-barrientos.jpg
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
title: "Public preview – Azure Arc-enabled VMware vSphere – Part 1"
aliases:
- /2022/04/25/arc-enabled-vmware-vsphere-part1
---

## Manage your VMware Datacenter through Azure Cloud tools

Announced in [private preview stage](https://azure.microsoft.com/en-us/updates/private-preview-new-azure-arc-capabilities-in-november-2021/) during the [Microsoft Ignite](https://aka.ms/IgniteNov21/InnovateAnywhereBlog) on November 2021, the [Azure Arc](https://azure.microsoft.com/en-us/services/azure-arc/#product-overview) integration with VMware vSphere is now [available in public preview](https://azure.microsoft.com/en-us/updates/public-preview-azure-arc-integration-with-vmware-vsphere/) since March 31<sup>th</sup>, 2022.

The feature, still in development process, is now labeled *Azure Arc-enabled VMware vSphere*, and provides a unified governance and management solution for lifecycle and guest OS operations of VMware VMs through Azure Arc.

> As [Azure VMware Solutions](https://azure.microsoft.com/en-us/services/azure-vmware/) private clouds relies on a [standardized VMware SDDC](https://www.vmware.com/products/cloud-foundation.html), you can also use *Azure Arc-enabled VMware vSphere* to operate your AVS-based workloads.

### How it works ?

*Azure Arc-enabled VMware vSphere* relies on a *Resource Bridge* appliance deployed in the target environment (or in a VMware environment with network access to the target one). This bridge will act a the access-point for Azure Arc to get and manage data from vCenter APIs.

As of now, the *Resource Bridge* requires an outbound connectivity to Internet (specifically to to Azure APIs over HTTPS(443)) and can only be deployed on a VMware environment.

![The Azure Arc Resource Bridge act as a gateway for Azure Arc to access and manage VMware based workloads.](/images/arc-vmware/arc-resource-bridge.png)

When the appliance is fully deployed and reports to the Azure Arc APIs, you can browse the inventory and enable some VMware components to be accessible as Azure objects. Azure-Enabled resources from the VMware environment will be attached to:

* A **custom location** representing your VMware Datacenter in Azure
* A **resource group** to provide ability to organize your resources and to apply RBAC (Role-Based Access Control) strategy

### Benefits

As for Azure Arc, the main goal of *Azure Arc-enabled VMware vSphere* is to extend Azure governance and management capabilities on non-Azure environments. In this case to a VMware vSphere infrastructure.

This provides a **consistent management experience across Azure and VMware vSphere infrastructure** like:

* VMware virtual machine (VM) lifecycle operations: create/register, start/stop, resize, and delete.
* Apply RBAC strategy to provide users and application teams to self-serve VM operations.
* Apply Azure governance strategies across Azure and VMware VMs by enabling guest management (Azure Policies, Update Management, Monitoring etc.).
* Use Azure Resource Manager based API to manage VMware workload (ARM or Bicep templates, Azure APIs and CLI tools).

## Resource Bridge Deployment

> **Disclaimer**: This walkthrough deployment process is not a substitution of the Microsoft Documentation about [*Azure Arc-enabled VMware vSphere*](https://docs.microsoft.com/en-us/azure/azure-arc/vmware-vsphere/). This blog post will not receive major updates to synchronize with the development status of *Azure Arc-enabled VMware vSphere* feature and only reflect the process at a specific moment in time.

### Pre-requisites

In order to have access to all *Azure Arc-enabled VMware vSphere* features, I had to register the following Azure resources providers to my subscription:

* `Microsoft.ConnectedVMwarevSphere`
* `Microsoft.HybridCompute`
* `Microsoft.GuestConfiguration`

I used [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/):

```bash
export AZURE_SUBSCRIPTION_ID='********-****-****-****-************'
az provider register --wait --subscription "${AZURE_SUBSCRIPTION_ID}" --namespace Microsoft.ConnectedVMwarevSphere
az provider register --wait --subscription "${AZURE_SUBSCRIPTION_ID}" --namespace Microsoft.HybridCompute
az provider register --wait --subscription "${AZURE_SUBSCRIPTION_ID}" --namespace Microsoft.GuestConfiguration
```

### Resource requirements

The *Resource Bridge* appliance requires the following resources assignment:

* 4 vCPU
* 16GB RAM
* 100GB free disk space


### Create the vCenter Resource Bridge

From Azure portal, select the **Azure Arc** product then:

1. VMware vCenters (preview)
2. (+) Add

![Resource Bridge creation from Azure UI – step 1](/images/arc-vmware/arc-resource-bridge-creation-01.png)

You will be requested to:

1. Attach the *Resource Bridge* to a subscription, a resource-group and a region (only East US and West Europe are available by now).
2. Provide a name for a *custom location*

> The *custom location* will represent, in Azure, the location of your vCenter deployment.

3. Provide a name for the vCenter in Azure

![Resource Bridge creation from Azure UI – step 2](/images/arc-vmware/arc-resource-bridge-creation-02.png)

In the next screen of the wizard, you can attach *tags* to your new resource. In the third step, you are invited to download a PowerShell-based (Windows) or Azure CLI-based (Linux) version of a script.

> If your subscription is not registered with all the required resource providers, a **Register** button will appear.

![Resource Bridge creation from Azure UI – step 3](/images/arc-vmware/arc-resource-bridge-creation-03.png)

The downloaded script needs to be run from a workstation or *jump server* with direct or proxyfied access to the vCenter where the resource bridge will be deployed.

The last wizard step provide an insight on the resource bridge deployment status, but does not affect the resource creation.

![Resource Bridge creation from Azure UI – step 4](/images/arc-vmware/arc-resource-bridge-creation-04.png)

#### (Windows) Powershell script

> [Azure PowerShell](https://docs.microsoft.com/fr-fr/powershell/azure/?view=azps-7.4.0) module is required.

If you choose the PowerShell (Windows) version of the script:

```ps1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Install-Module -Name Az -Scope CurrentUser -Repository PSGallery
Connect-AzAccount
./resource-bridge-onboarding-script.ps1
```

#### (Linux) Azure CLI script

> [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) is required.

If you choose the PowerShell (Windows) version of the script:

```bash
az login
bash resource-bridge-onboarding-script.sh
```

#### Running the deployment script

The deployment script will ask for a set of information in order do deploy and configure the *resource bridge* appliance.

* Proxy settings for the current workstation
* Target vCenter FQDN, username, password
* VM deployment details:
  * VMware logical-datacenter
  * Network
  * ResourcePool
  * Datastore
  * VM Folder
  * Appliance IP settings

![Resource Bridge creation from Azure UI – step 5](/images/arc-vmware/arc-resource-bridge-creation-05.png)
![Resource Bridge creation from Azure UI – step 6](/images/arc-vmware/arc-resource-bridge-creation-06.png)

The script will run for about 15 minutes to download, deploy and configure the Resource Bridge appliance. When fully deployed, the *verification* step of the UI wizard will display a green check to validate that both Azure API and the appliance are communicating together.

## Upcoming

In the upcoming posts, we will cover the functional capabilities of having VMware resources managed through Azure, from UI or with automation tools.

* [Azure Arc-enabled VMware vSphere – Part 2](/2022/04/27/arc-enabled-vmware-vsphere-part2)
* [Azure Arc-enabled VMware vSphere – Part 3](/2022/04/29/arc-enabled-vmware-vsphere-part3)

### Credits

Title photo by [Joseph Barrientos](https://unsplash.com/@jbcreate_) on [Unsplash](https://unsplash.com/photos/oQl0eVYd_n8)
