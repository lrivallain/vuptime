---
title: "How to retain your IP addresses while migrating to Azure VMware Solution"
date: "2025-03-26"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- Azure
tags:
- vmware
- azure
- Migrate
- Azure VMware Solution
- HCX
- Network
thumbnail: /images/thumbs/keep-ip.png
featureImage: /images/thumbs/keep-ip.png
toc: true
---

Migrating On Premises assets to a cloud solution can be a complex process, especially when it comes to considering existing IP addresses plan. One key benefit of migrating to Azure VMware Solution (AVS) is the ability to retain existing IP addresses, which can simplify the migration process and reduce downtime. However, this approach requires careful planning and consideration of network principles to ensure a smooth transition.

This post will explore some considerations for retaining IP addresses during the migration to AVS, including the importance of understanding network dependencies and the potential impact on performance. It will also discuss the benefits of leveraging VMware Hybrid Cloud Extension (HCX) Layer 2 extensions to facilitate the migration process.

## General Considerations

First and foremost, we need to align ourselves on some fundamental network principles before exploring solutions. These principles are crucial to understand when planning a migration to Azure VMware Solution (AVS) and maintaining existing IP addresses, as we cannot re-invent networking principles to suit our IP journey expectations.

### A single routed network can only be accessible from one location

It seems obvious, but it is important to understand that a routed network can only be accessible from one location at a time. This means that if you have a routed network in your on-premises environment (like 10.1.2.0/24 for example), a network with the same IP address range cannot be published from the cloud side at the same time. This is a fundamental principle of networking and must be taken into account when planning your migration.

![A single routed network can only be accessible from one location](/images/avs-keep-ip/a-single-routed-network-can-only-be-accessible-from-one-location.png)

### Assets in a single vLAN share the same broadcast domain

When assets are in the same VLAN, they share the same broadcast domain. This means that they can communicate with each other without the need for a router. This will also applied on assets in an extended L2 network.

Example of ARP broadcast over an extended L2 network:

![Assets in a single vLAN share the same broadcast domain](/images/avs-keep-ip/assets-in-a-single-vlan-subnet-share-the-same-broadcast-domain.png)

### Migrated asset will continue to use its configured gateway to reach routed peers

When you migrate an asset to the cloud and retain its IP address, it will continue to use its configured gateway to reach routed peers. This means that if you have a routed network in your on-premises environment, the migrated asset will still use its on-premises gateway to communicate with other assets in the same network. Typically, this connectivity path will be utilized for both egress and ingress traffic.

![If retaining IP address: migrated asset will continue to use its configured gateway to reach routed peers](/images/avs-keep-ip/migrated-asset-will-still-continue-to-use-its-configured-gateway-to-reach-routed-peers.png)

### Latency will exist between migrated and non-migrated assets

When you migrate an asset to the cloud and retain its IP address, latency will exist between migrated and non-migrated assets. In addition to the familiar on-premises connectivity, several other factors will contribute to latency:

- Geographical distance between the two locations
- Link quality and routing hops
- Link usage and congestion
- Tunneling techniques and protocols used
- Possible tromboning of traffic

![Latency will exist between migrated and non-migrated assets](/images/avs-keep-ip/latency-will-exist-between-migrated-and-non-migrated-assets.png)

Traffic latency can also affect cloud to cloud communication in case of extended L2 networks: this is the tromboning effect.

#### What is traffic tromboning?

Traffic tromboning occurs when traffic is sent from one location to another and then back again, rather than taking a direct path.

**Example:** One of the worst scenarios is when a migrated asset in the cloud tries to communicate with another asset in a different network. If the gateway of one asset is on-premises, the traffic will travel from the migrated asset (cloud side) to the on-premises gateway, and then back to the cloud side to reach the destination asset. The response will follow the same path: from the destination asset (cloud side) to the on-premises gateway, and finally back to the migrated asset.

This pattern can strongly affect performance and perceived latency.

![What is traffic tromboning?](/images/avs-keep-ip/traffic-tromboning.png)

## Extend network to retain IP addresses

As you may already have guessed, the solution to retain IP addresses while migrating to a cloud solution, is to extend the network(s) and to consider migration "per network" instead of per VM/application or other kind of asset.

In order to do things properly, I will recommend the following approach:

### Execution Plan

1. **Plan, plan, plan!**
   - Carefully select network(s) to extend.
   - Understand the next phases and the way to execute them with the network to extend.
   - Understand all the dependencies of the network.
2. **Extend L2 Network**
   - Network will now be able to host assets in two locations.
   - The gateway will remain on-premises (for most assets).
3. **Migrate Assets**
   - Migrated assets will retain connectivity and IP addresses.
4. **Evacuate Remaining Assets**
   - If needed: some assets may require reIP to ensure the network is free from resources on-premises.
5. **Switchover Connectivity**
   - Connectivity is now switched to the cloud side.
   - All workloads will use native connectivity.
   - L2 Extension is removed.

Regarding the migration project, each step of the execution plan has its own criticality level, which can be summarized as follows:

| Phase                     | Criticality                                      |
|---------------------------|--------------------------------------------------|
| Plan                      | <span style="color: #ff5733;">Critical</span>  |
| Extend L2 Network         | <span style="color: #33e0ff;">Low</span>       |
| Migrate Assets            | <span style="color: #ff9f33;">Medium</span>    |
| Evacuate Remaining Assets | <span style="color: #33e0ff;">Low</span>       |
| Switchover Connectivity   | <span style="color: #ff5733;">Critical</span>* |

\* *Depends a lot on the planning phase.*

### How does it work?

Here is a simplified diagram of how the network extension works:

![How does it work?](/images/avs-keep-ip/how-does-it-work.png)

After carreful planning:
1. The network extension is implemented using extension technology (examples will be provided later).
1. Assets from this network are either migrated (retaining their IP addresses) or evacuated from the network (Re-IP, decommission, etc.).
1. The network extension is removed, and connectivity is switched to the cloud side.

### How is my network currently built?

While planning the migration, it is important to understand how your network is currently built and what are your ambitions for the migration project. This will help you identify potential issues and plan for a successful migration.

| <span style="color:rgb(75, 194, 81);">Best Case Scenario</span> | <span style="color: #ff5733;">Worst Case Scenario</span> |
| --- | --- |
| Small Layer 2 (L2) subnets with only VMware assets. | A flat network topology. |
| All assets will migrate to the cloud. | Not all resources will switch to the cloud |
| A good understanding of network dependencies between networks and assets. | Limited knowledge of network dependencies. |
| No dependencies with on-premises after migration. | Lots of dependencies with on-premises after migration. |

{{% notice info "Note" %}}
If we can easily determine best and worst case scenarios criteria, **all shades can exist** between these two extreme scenarios.
{{% /notice %}}

## Risks mitigation

In the following section, we will oversee some possible mitigation strategies for the previous risks.

### Networks with VMware and non-VMware assets

- Per network: consider the level of effort to re-IP one or the other category. Example:
  - *80% of my assets will remain on-premises: change IP addresses for the 20% migrated?*
  - *80% of my assets will migrate to the cloud: change IP addresses for the 20% remaining on-premises?*
- L2 extension can still help to migrate resources, even if considering a re-IP strategy for the migrated workload.

### Dependencies with on-premises after migration

- Consider a cloud migration of services hosted on-premises: PaaS/IaaS etc.
- Adapt connectivity methods between environments: more bandwidth, less latency, etc.

### Limited knowledge of network dependencies

- *Azure Migrate* can help to [map all the dependencies of network and assets](https://learn.microsoft.com/en-us/azure/migrate/concepts-dependency-visualization).
  - \+ [Azure Migrate Network Flows Analysis](https://az-mdv.az.vupti.me/)
- Other tools like *VMware Aria Operations for Networks*.

## VMware Hybrid Cloud Extension (HCX)

VMware HCX is a powerful tool that can help you extend your network and retain your IP addresses during the migration to Azure VMware Solution (AVS). It provides a seamless way to migrate workloads while maintaining their existing IP addresses, which can simplify the migration process and reduce downtime.

{{% notice info "Note" %}}
HCX Enterprise is a **free add-on for AVS**: you can use it to migrate workloads from on-premises to AVS without any additional cost.
{{% /notice %}}

### Prerequisites to consider for HCX L2 Extensions

| Prerequisites | Mitigation |
| ------------- | ---------- |
| (Standard) vSwitch are not supported by HCX to extend L2 network. <br>→ Consider migrating to *Distributed-vSwitch* | <ul><li>Easy to validate,</li><li>Relatively easy to remediate</li></ul> |
| HCX support of NSX-V to NSX-T migration is [deprecated in version 4.11](https://techdocs.broadcom.com/us/en/vmware-cis/hcx/vmware-hcx/4-11/hcx-4-11-release-notes/vmware-hcx-411-release-notes.html) | <ul><li>Easy to validate,</li><li>Currently supported</li></ul> |
| HCX support migration for vSphere and vCenter 6.5 [with limited support](https://knowledge.broadcom.com/external/article?articleNumber=321571) | <ul><li>Easy to validate,</li><li>Currently supported</li></ul> |

### Traffic tromboning mitigation with HCX Mobility Optimized Network (MON)

One of the key benefits of using HCX is its ability to optimize network traffic and reduce latency. *HCX Mobility Optimized Network (MON)* is a feature that helps to minimize the tromboning effect by optimizing the path that traffic takes between migrated and non-migrated assets or with resources in other networks.

In a previous post ([VMware HCX: To the MON & Back](https://vuptime.io/post/2023-08-17-hcx-to-the-mon-and-back/#mobility-optimized-network-enablement)), we had the opportunity to see how HCX MON is working and how to configure it to greatly reduce the tromboning effect.

![Network path example with HCX L2 network extension and MON feature enabled](/images/hcx-mon/scenario5-no-policy-routes.png)


## NSX Autonomous Edge

An alternative approach to HCX is to use NSX Autonomous Edge (NSX AE) to extend your network and retain your IP addresses during the migration to Azure VMware Solution (AVS). This approach will rely on NSX-T VPN features to create tunnels between the on-premises and cloud environments, allowing you to extend your network and retain your IP addresses while migrating workloads.

{{% notice info "Note" %}}
Note: Standard vSwitch are supported with NSX AE.
{{% /notice %}}

### Prerequisites and limitations to consider for NSX L2 Extensions

| Prerequisites | Mitigation |
| ------------- | ---------- |
| Trunk interface required to extend multiple VLANs.<br><ul><li>Promiscuous Mode required.</li><li>Forget Transmit required.</li></ul>| <ul><li>Easy to validate,</li><li>Easy to remediate</li></ul> |
| No HCX MON-like optimization.| Network extension cutover is recommended as soon as migration is completed. |
| Download NSX AE OVF requires Broadcom entitlement.| n/a |

## Conclusion

In conclusion, retaining your IP addresses while migrating to Azure VMware Solution (AVS) is not a complex process but requires **careful planning and consideration of network principles**.

By leveraging VMware Hybrid Cloud Extension (HCX) Layer 2 extensions or NSX Autonomous Edge, you can simplify the migration process and avoid/reduce downtime while maintaining existing IP addresses.
