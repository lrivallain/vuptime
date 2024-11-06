---
title: Azure Elastic SAN to extend Azure VMware Solution storage
date: "2024-11-05"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
tags:
- vmware
- azure
- azure vmware solution
- storage
toc: true
thumbnail: /images/avs-esan/thumbnail.png
splash: /images/avs-esan/thumbnail.png
---

Azure VMware Solution (AVS) is a managed service that relies mostly on Hyper-converged infrastructure (HCI) and VMware vSAN to provide storage capacity to host Virtual Machines (VMs) workloads. Each host deployed in the solution is providing its local storage devices and capabilities to the distributed storage capacity.

By default, the scalability of such HCI solutions is based on the addition of new hosts to the cluster, increasing the storage capacity and compute resources available to the VMs.

However, there are some scenarios where you might need to extend the storage capacity of your AVS cluster without requiring additional compute resources.

# Extend AVS storage capacity

Let's do a quick overview of the different options available to extend the storage capacity of your AVS cluster without expanding the compute resources.

## Azure NetApp Files

The initial solution to expand storage capacity was to utilize Azure NetApp Files (ANF) as the storage backend for Azure VMware Solution (AVS). ANF volumes are mounted as NFS datastores on the ESXi hosts within the AVS cluster. Network connectivity is managed through a dedicated Azure Virtual Network (vNet) and subnet, along with an ExpressRoute gateway. 

{{% notice info "Note" %}}
ANF is a first party service in Azure.
{{% /notice %}}

[AVS+Azure NetApp Files documentation](https://learn.microsoft.com/en-us/azure/azure-vmware/attach-azure-netapp-files-to-azure-vmware-solution-hosts?tabs=azure-portal)

## Pure Cloud Block Store

A second approach is to rely on Pure Cloud Block Store (CBS) to extend the storage capacity of your AVS cluster. Pure Cloud Block Store is a fully managed service that provides block storage to your AVS cluster.

{{% notice info "Note" %}}
Pure Storage is a third party service in Azure.
{{% /notice %}}

[AVS+Pure Cloud Block Store documentation](https://learn.microsoft.com/en-us/azure/azure-vmware/configure-pure-cloud-block-store)

## Azure Elastic SAN

GA since October 2024, Azure Elastic SAN integration with AVS provides a new way to extend the storage capacity of your AVS cluster. Azure Elastic SAN is a fully managed service that provides block storage to your AVS cluster. 

{{% notice info "Note" %}}
Azure Elastic SAN is a first party service in Azure.
{{% /notice %}}

[AVS+Azure Elastic SAN documentation](https://learn.microsoft.com/en-us/azure/azure-vmware/configure-azure-elastic-san)


# Azure Elastic SAN and AVS

I will not cover all the differences with other available services in this post, but I encourage you to get a look at the [Azure Elastic SAN documentation](https://learn.microsoft.com/en-us/azure/storage/elastic-san/elastic-san-introduction) to get more details.

From my point of view, the two main benefits of Azure Elastic SAN in AVS storage extension are:
* The **performances**: each provisioned TB of *Base* Azure Elastic SAN provides 200MB/s throughput and 5000 IOPS.
* The **cost** optimization.

In this post we will see how to integrate Azure Elastic SAN with AVS and benefit from external storage capacity by this way.

## Localization

Azure Elastic SAN is [available in multiple Azure regions](https://learn.microsoft.com/en-us/azure/storage/elastic-san/elastic-san-create). When integrating Azure Elastic SAN with AVS, it is recommended to deploy the storage service in the same Azure region and Availability Zone (AZ) as the AVS cluster to minimize latency and optimize performances.

## Network topology

![Azure Elastic SAN and AVS: Network topology](/images/avs-esan/eSAN-and-AVS-network-topology.png)

The previous illustration shows the network topology when integrating Azure Elastic SAN with AVS. 

ESXi hosts in the AVS cluster are connected to the Azure Elastic SAN service through the following components

### New VMKernel interfaces per ESXi host: *External Storage Block*

To use Elastic SAN with AVS, you need to provision a new IP address block/range to configure the SDDC's *External Storage Block*. The address block should be a /24 network ([Documentation](https://learn.microsoft.com/en-us/azure/azure-vmware/configure-azure-elastic-san#configure-external-storage-address-block)).

When configuring the new *External Storage Block*, each ESXi host in the AVS cluster will have two VMKernel interfaces configured within the new IP address block:
![New VMKernel interfaces::picture-border](/images/avs-esan/esxi-new-vmkernels.png)

The two new network interfaces will be used to initiate the iSCSI connections to the Azure Elastic SAN service by using a newly created iSCSI Software adapter:
![New iSCSI Software adapter::picture-border](/images/avs-esan/esxi-new-storage-adapter.png)

### AVS Express Route circuit

Azure VMware Solution uses the concept of Express Route circuit (ER) to provide connectivity out of the boundaries of the NSX-T and management networks. It enables the connection to Azure services like Azure Elastic SAN, and also the connectivity with the on-premises environments if needed.

In the case of external storage resources, a dedicated Express Route Gateway is recommended to maximize the performances and limit the noisy neighbor effect of other services.

The Express Route gateway will "land" the AVS ER to an Azure vNet were the connectivity with Elastic SAN can be established. Sizing this component according to the expected throughput and latency requirements is crucial to ensure the performances of the storage service:

* AVS Express Route circuit is a 10GBps link
* It is recommended to provision a gateway with the same bandwidth capacity like `ErGw3AZ`.

{{% notice info "Note" %}}
As **FastPath** is [currently not supported with Private Endpoints](https://learn.microsoft.com/en-us/azure/expressroute/about-fastpath), there is no need to enable it.
{{% /notice %}}

### Azure vNet and Private Endpoints

In order to connect to the Azure Elastic SAN service, you need to create a Private Endpoint in an Azure vNet.

To increase performance and reliability, multiple Private Endpoints should be created to establish multiple sessions between hosts and the storage service. The Azure documentation provide a set of recommendations to optimize the performances of the storage service: [configuration recommendations](https://learn.microsoft.com/en-us/azure/azure-vmware/configure-azure-elastic-san#configuration-recommendations).
![Set of Private Endpoints to access Elastic SAN::picture-border](/images/avs-esan/azure-private-endpoints.png)

In the Azure vNet diagram, we can see the Private Endpoints, their Network Interface Cards (NICs), and the connection to the Azure Elastic SAN service.
![Azure vNet and Private Endpoints components in the Azure UI diagram::picture-border](/images/avs-esan/azure-private-endpoints-ui-diagram.png)

## Storage configuration

Mounting the Elastic SAN on Azure VMware Solution is managed through the Azure Portal or API and the process is quite straightforward: you select the Elastic SAN service, the volume group, then the volume to mount and the target cluster.

When mounted on nodes, the storage is visible as datastore in both vCenter and Azure Portal.
![Mounted Elastic SAN volume on AVS: from Azure Portal::picture-border](/images/avs-esan/avs-mount-esan-ui.png)

![Mounted Elastic SAN volume on AVS: from vCenter UI::picture-border](/images/avs-esan/avs-mount-esan-vcenter.png)

# Conclusion

It is now time to migrate workloads to this new storage capacity and benefit from the performances and cost optimization of Azure Elastic SAN. To preserver workload runtime, **Storage vMotion** is the recommended method to move VMs from one datastore to another.

Keep in mind that the vSAN cluster will probably provide the best performances for the VMs that require the lowest latency and the highest throughput. Azure Elastic SAN is a good candidate for VMs that require a good balance between performances, capacity and cost optimization.