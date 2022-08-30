---
author: lrivallain
author_name: Ludovic Rivallain
date: "2022-08-17"
thumbnail: /images/avs-public-ip/Public-IP-Addresses.svg
splash: /images/splash/clement-duguerre-0Lr-rMp_rhM-unsplash.jpg
splash_credits: Photo by Clément Duguerre on Unsplash
featureImage: /images/splash/clement-duguerre-0Lr-rMp_rhM-unsplash.jpg
categories:
- VMware
- Azure
tags:
- vmware
- azure
- azure vmware solution
- nsx-t
toc: true
title: "Azure VMware Solution – Use public IP on NSX-T Edge"
---

A few days ago, Microsoft released a new feature for Azure VMware Solution: *[Enable Public IP to the NSX Edge](https://docs.microsoft.com/en-us/azure/azure-vmware/enable-public-ip-nsx-edge)*. I take the opportunity to review this new feature and the other options available to provide Internet connectivity to your Azure VMware Solution (both for In or Out-bound traffic).

## Internet access options for Azure VMware solution

To provide internet access (inbound and/outbound) to an Azure VMware Solution deployment, 3 options are available:

1. Use a Microsoft-managed SNAT (outbound connectivity only) ([doc.](https://docs.microsoft.com/en-us/azure/azure-vmware/enable-managed-snat-for-workloads))
2. Advertise a default route using Azure Firewall, Azure vWAN or a third-party Network Virtual Appliance (NVA) ([doc.](https://docs.microsoft.com/en-us/azure/azure-vmware/disable-internet-access))
3. Use Public IP address(es) published down to the NSX-T Edge ([doc.](https://docs.microsoft.com/en-us/azure/azure-vmware/enable-public-ip-nsx-edge))

Each option has its own [advantages and disadvantages](https://docs.microsoft.com/en-us/azure/azure-vmware/concepts-design-public-internet-access) and is summarized below.

### Microsoft-managed SNAT

The Microsoft-managed SNAT option ([doc.](https://docs.microsoft.com/en-us/azure/azure-vmware/enable-managed-snat-for-workloads)) is the easiest and cost-effective option for **outbound** (only) **connectivity** as the public IP addresses are fully managed by Microsoft **free of charge**.

In this scenario, 2 public IPs are used and rotated to provide outbound connectivity to the Azure VMware Solution workloads with up to 128 000 concurrent connections.

This comes with the following limitations:

* No inbound connectivity
* No control of outbound SNAT rules
* No connection logs
* Hard limit of 128 000 concurrent connections

### Advertise a default route

The second option for Internet connectivity in Azure VMware Solution is based on the default route advertisement from another component in the Azure infrastructure ([doc.](https://docs.microsoft.com/en-us/azure/azure-vmware/disable-internet-access)).

This advertisement can be done using:

* [Azure Firewall](https://docs.microsoft.com/en-us/azure/firewall/overview)
* [Azure vWAN](https://docs.microsoft.com/en-us/azure/virtual-wan/virtual-wan-about)
* [Third-party Network Virtual Appliance](https://docs.microsoft.com/en-us/azure/architecture/reference-architectures/dmz/nva-ha) (NVA)
* A routing component deployed on-premises

If no default-route is advertised to AVS, the VMs will not be able to access the internet: this option is also the one used to **disable internet access on AVS deployment**.

This option could provide inbound connectivity, control of SNAT and DNAT rules, connections logs but is more complex to deploy and will involve additional charges (for public IP addresses, Firewall or routing devices etc.)

### Public IP address published down to the NSX-T Edge

What was recently announced as a new GA feature in Azure VMware Solution is the publication of public IP address(es) down to the NSX-T Edge ([doc.](https://docs.microsoft.com/en-us/azure/azure-vmware/enable-public-ip-nsx-edge)). This is the third option for Internet connectivity in Azure VMware Solution and it provides the best of the 2 previous options.

* Inbound and outbound connectivity
* Control of SNAT and DNAT rules
* Connection logs
* No additional components to deploy (Azure Firewall, Azure vWAN, third-party NVA)

On top of this, this new feature also enables:

* A unified experience based on AVS native components only: Azure Resource Manager and NSX-T
* The ability to receive up to 64 public IPs (soft limit)
  * This quota can be increased by request to 1000s of Public IPs allocated if required
* DDoS Security protection against network traffic in and out of the Internet.
* HCX Migration support over the Public Internet.

#### Pricing considerations

With this new feature, Public IP addresses published for an AVS instance are billed separately from the AVS instance itself as IP addresses used for other Azure purposes.

The pricing details are explained here: [IP Addresses pricing](https://azure.microsoft.com/en-us/pricing/details/ip-addresses/) and to summarize it:

| Type                                  | Standard (ARM)        |
|---------------------------------------|-----------------------|
| Public IP prefix (block of addresses) | $.006 per IP per hour |

{{% notice info "Public IP addresses pricing" %}}
Always check the [pricing details from the official Azure documentation](https://azure.microsoft.com/en-us/pricing/details/ip-addresses/) before you purchase an IP address. The above table is only an extract at the time of this writing.
{{% /notice %}}

## Reserve public IP addresses for Azure VMware Solution

Since the publication of the new feature providing public IPs on NSX-T Edge, a new section *Internet Connectivity* is available in the Azure portal to manage AVS internet access options.

![AVS Internet Connectivity section in Azure portal](/images/avs-public-ip/internet-connectivity-section.png)

To enable internet access with public IPs on NSX-T Edge, at least one public IP block is needed. You can create one by providing a name and the number of IPs you want to allocate.

![Create Public IPs block](/images/avs-public-ip/create-ip-block.png)

When the block request is submitted, you can save the new internet access settings. The block will be created and the IPs will be allocated in the background while the block is advertised to the AVS deployment.

![Save the new internet connectivity option](/images/avs-public-ip/set-internet-option.png)

It may take around 10 to 15 minutes to complete the new configuration. If internet access was already enable on the AVS deployment, a downtime is expected during the re-configuration and NSX-T configuration will be required.

When the configuration is completed, the new block will be available in the list of public IP blocks:

![List of public IP spaces provisioned for the current AVS instance](/images/avs-public-ip/public-ip-spaces.png)

## Enable outbound internet access using SNAT

Enabling outbound internet access requires to configure (at least) a SNAT rule on the NSX-T T1 router.

1. Logging to NSX-T manager
1. In the *networking* tab, access to the *NAT* section
1. Select the appropriate T1 router to provision the SNAT rule on
1. Create a new SNAT rule with name, and an IP address from the provisioned block to use for outbound connectivity
1. Save

![Create a NSX-T SNAT rule to enable outbound internet connectivity](/images/avs-public-ip/create-nsx-snat.png)

{{% notice info "Firewall configuration" %}}
Depending on the firewall configuration on NSX-T, you may have to create firewall rules to allow the traffic to pass through.
{{% /notice %}}

## Enable inbound internet access

### Inbound connectivity with DNAT

The inbound internet access could rely on a DNAT rule, forwarding the traffic from the public IP address to the internal IP address of the workload (either a VM or a network service).

1. Logging to NSX-T manager
1. In the *networking* tab, access to the *NAT* section
1. Select the appropriate T1 router to provision the DNAT rule on
1. Provide a name, a public IP address from the provisioned block and an internal IP address to forward the traffic to
1. Save

![Create a NSX-T DNAT rule to enable inbound internet connectivity](/images/avs-public-ip/create-nsx-dnat.png)

{{% notice info "Firewall configuration" %}}
Depending on the firewall configuration on NSX-T, you may have to create firewall rules to allow the traffic to pass through.
{{% /notice %}}

### Inbound connectivity with DNAT and port redirection

With the DNAT rule, you can also redirect traffic to a different port. For example, you can redirect traffic from the public IP address on port 80 to a different port on the internal workload, like 8000.

For this, you need to specify a *service* matching the port of the internal workload during the DNAT rule creation (8000 in our example).

![Creation of a dev-http service matching port 8000](/images/avs-public-ip/dev-http-service.png)

Then to specified as the Translated Port, the port exposed on the public IP address (80 in our example).

![Create a NSX-T DNAT rule to enable inbound internet connectivity with port redirection](/images/avs-public-ip/create-nsx-dnat-with-port-redirect.png)

### Inbound connectivity using NSX-T Load Balancer

As public IP address can now land directly on the NSX-T edge, it is possible to setup a NSX-T **Load Balancer** to provide inbound connectivity to the AVS workloads.

First step is to create a Load Balancer service, attached to the NSX-T T1 gateway and to specify a sizing.

![Load Balancer service creation](/images/avs-public-ip/load-balancer-1.png)

Second step is to create a *Virtual Server*, attached to the Load Balancer service and to specify the port and the IP address of the workload.

![Creation of the Virtual Server](/images/avs-public-ip/load-balancer-2.png)

Then *Server Pool* is created and attached to the *virtual server*. It contains a list of workers hosting the load-balancer application.

![Server Pool creation](/images/avs-public-ip/load-balancer-3.png)

Last but not least: an *Active Monitor* is created to monitor the *Server Pool*.

![Active monitor creation](/images/avs-public-ip/load-balancer-4.png)

## Conclusion

With the new *Public IP address down to the NSX-T edge* feature now available for AVS, new capabilities are available to manage the internet connectivity of the AVS workloads. One of the most important advantages is the ability to rely on NSX-T components to configure and securise both inbound and outbound internet connectivity. It is also possible to directly use public IP addresses with NSX-T services like Load Balancer or VPN.

Of course, this setup will not satisfy all the thinkable internet connectivity requirements but it offers a new set of possibilities and is a real asset to consider to host internet-facing applications or to control outgoing internet connections.

### Credits

Photo by <a href="https://unsplash.com/@clementduguerre?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Clément Duguerre</a> on <a href="https://unsplash.com/s/photos/pyrenee?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
