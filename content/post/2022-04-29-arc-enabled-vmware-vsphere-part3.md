---
author: lrivallain
author_name: Ludovic Rivallain
date: "2022-04-29"
thumbnail: /images/arc-vmware/vm-panel.png
splash: /images/splash/birger-strahl-unsplash.jpg
splash_credits: Photo by Birger Strahl on Unsplash
featureImage: /images/splash/birger-strahl-unsplash.jpg
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
title: "Public preview – Azure Arc-enabled VMware vSphere – Part 3"
aliases:
- /2022/04/29/arc-enabled-vmware-vsphere-part3
---

In the two first posts of this series on *Azure Arc-enabled VMware vSphere*, we managed to extend Azure governance and management capabilities on VMware-based resources and to demonstrate the creation of a VMware virtual machine from the Azure portal.

If you missed on of the 2 firsts posts:

* [Azure Arc-enabled VMware vSphere – Part 1](/2022/04/25/arc-enabled-vmware-vsphere-part1)
* [Azure Arc-enabled VMware vSphere – Part 2](/2022/04/27/arc-enabled-vmware-vsphere-part2)

In the following sections we will see examples of automation solutions that are available to manage VMware resources through Azure tools.

## Azure CLI

*Azure Arc-enabled VMware vSphere* provides an Azure CLI extension named `connectedvmware` to manage VMware resources through Azure CLI. The [extension documentation](https://docs.microsoft.com/en-us/cli/azure/connectedvmware?view=azure-cli-latest) provides a full reference of the available commands and arguments.

Here are some examples of what you can achieve with this extension:

List vCenter servers registered in Azure Arc:

```bash
az connectedvmware vcenter list --output table --query "[].{resourceGroup:resourceGroup, name:name, location:location, version:version}"
ResourceGroup    Name               Location    Version
---------------  -----------------  ----------  ---------
arc-RG           north-eu-avs-vcsa  westeurope  6.7.0
```

List all inventory items from a vCenter server:

```bash
az connectedvmware vcenter inventory-item list --output table --resource-group "arc-RG" --vcenter "north-eu-avs-vcsa" --query "[].{kind:kind, name:moName}"
Kind                    Name
----------------------  --------------------------------------------------------------
VirtualNetwork          VM-tests-110
Host                    esx19-r18.p01.**********************.northeurope.avs.azure.com
VirtualMachineTemplate  Arc-Template
ResourcePool            Resources
...
```

List Virtual Machines registered in Azure Arc:

```bash
az connectedvmware vm list --output table --query "[].{resourceGroup:resourceGroup, name:name, location:location, instanceUuid:instanceUuid}"
ResourceGroup    Name        Location    InstanceUuid
---------------  ----------  ----------  ------------------------------------
arc-RG           Ubuntu04    westeurope  67bc57b8-6464-4658-8e04-7cc9d6d5cb04
arc-RG           Windows01   westeurope  caccc302-e28b-4c70-b2c0-24a614d470e6
arc-RG           Ubuntu03    westeurope  39f8ef01-efd5-4268-88a0-2831bece69e7
arc-RG           Windows03   westeurope  f111aa56-f755-494d-9871-72154779792b
arc-RG           Windows02   westeurope  1fba47c2-dba5-4ee3-b295-3bdbd043fbb8
```

Restart a virtual machine

```bash
az connectedvmware vm restart --name Windows02 --resource-group arc-RG
 \ Running ..
```

## ARM deployment

According to [Microsoft documentation](<https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/overview>):

> **Azure Resource Manager** is the deployment and management service for Azure. It provides a management layer that enables you to create, update, and delete resources in your Azure account. You use management features, like access control, locks, and tags, to secure and organize your resources after deployment.

ARM is the core engine used by API, UI & Azure tools to manage Azure resources and it provide a declarative Infrastructure-as-code language to deploy and maintain resources: ARM Templates. ARM Templates can use [JSON](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/compare-template-syntax) or [Bicep](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview) syntax.

As other resources, Azure-enabled components of a VMware infrastructure can be managed through ARM and ARM Templates.

Lets see a minimal ARM Template to deploy a VMware virtual machine: **[Download the Bicep file](/images/arc-vmware/vmware-vm-template.bicep)**


```bash
curl https://vuptime.io/images/arc-vmware/vmware-vm-template.bicep > ./vmware-vm-template.bicep
# edit the file to set proper resources ids and customize your deployment parameters

# Start the deployment
az deployment group create --name vm-creation --resource-group arc-RG --template-file ./vmware-vm-template.bicep --parameters VMName=Ubuntu08

# Display some information about the deployed VM
az connectedvmware vm show --output table --resource-group "arc-RG" --name "Ubuntu06" --query "{resourceGroup:resourceGroup, name:name, location:location, instanceUuid:instanceUuid}"
ResourceGroup    Name      Location    InstanceUuid
---------------  --------  ----------  ------------------------------------
arc-RG           Ubuntu08  westeurope  18f07c4f-88f9-4cfd-adc7-0dc13007984c
```

## Conclusion

In the last three posts about *Azure Arc-enabled VMware vSphere* we have discovered the benefits of managing VMware resources with the help of Azure Resource Manager by using Azure Arc.

By extending Azure governance policy to infrastructure components out of the Azure native scope, it is possible to maintain a global security posture, to easily provide self-service VMware resources and to profit of Azure tools to manage a VMware environment.

As the *Azure Arc-enabled VMware vSphere* feature is [still in a preview stage](https://azure.microsoft.com/en-us/updates/public-preview-azure-arc-integration-with-vmware-vsphere/), there will be a bunch of changes and enhancements before the Global Availability.

If you missed the 2 first posts of this series:

* [Azure Arc-enabled VMware vSphere – Part 1](/2022/04/25/arc-enabled-vmware-vsphere-part1)
* [Azure Arc-enabled VMware vSphere – Part 2](/2022/04/27/arc-enabled-vmware-vsphere-part2)

### Credits

Title photo by [Birger Strahl](https://unsplash.com/@bist31) on [Unsplash](https://unsplash.com/photos/1XhmIcBB-EA)
