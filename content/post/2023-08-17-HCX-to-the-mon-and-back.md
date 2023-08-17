---
title: "VMware HCX: To the MON & Back"
date: "2023-08-17"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
tags:
- vmware
- azure
- azure vmware solution
- HCX
- network
toc: true
thumbnail: /images/hcx-mon/thumbnail.png
splash: /images/hcx-mon/thumbnail.png
---

No, we are not switching to a music blog genre to discuss the *"To the Moon & Back"* song from **Savage Garden** (I am sorry if you were expecting that) There is no typo in the title: we are going to explore VMware HCX network extensions and the MON feature, aka *Mobility Optimized Network*.


If you are not familiar with HCX, it is a VMware solution that allows you to migrate workloads from on-premises to the cloud, or from cloud to cloud. It also allows you to stretch your networks from migration source to the destination. It is a very powerful solution that can be used in many different scenarios to accelerate a migration project.

In this article, we are going to focus on the network extension part of HCX, and more specifically on a poorly understood feature: *Mobility Optimized Network*.

## What are we not going to talk about

In this post, I will no cover the creation of HCX network extensions in details. I assume that this subject is already well documented on Internet, including the official documentation and does not require a lot of explanations if you are already familiar with HCX.

## Lab setup

In order to document this post, I created a lab based on the following topology:

![Lab topology](/images/hcx-mon/lab-topology.png)

In this lab we have:

* An on-premises-like environment with a vCenter and hypervisors, hosting:
  * A network (`10.100.115.0/24`)
  * A routing device (`gw` @ `10.100.115.1`) and its northbound connectivity (Internet + Cloud connectivity)
  * A set of virtual machines to be migrated to the cloud: `migration-vm-X`
* a cloud environment (Azure based) with:
  * Landing of the ExpressRoute circuit
  * A point-to-site VPN gateway for my workstation
  * A vNET: `10.100.2.0/24`
  * An Azure native VM on this vNET: `azure-vm` @ `10.100.2.36`
  * An Azure VMware Solution SDDC with:
    * Express Route (ER) + Global Reach connectivity
    * HCX Enterprise deployed and configured
    * A native NSX-T segment with direct AVS connectivity with a test VM: `10.100.110.0/24` and `Ubuntu01`

I extended the on-premises network to the cloud using HCX network extension in order to prepare the migration of the VMs. The extended network (`10.100.115.0/24`) is now available in the cloud-side.


## Default network connectivity

Before we start migrating VMs, let's have a look at the default network connectivity on premises:

![Default network connectivity on-premises](/images/hcx-mon/scenario1-onpremises.png)

`migration-vm-X` is using the on-premises `gw` device and its default route to reach the Internet <span style="color:#FF0080;font-weight:bold;">(↔ pink)</span>. The `gw` device is also used to reach the cloud environment, through the ExpressRoute circuit <span style="color:#FF9933;font-weight:bold;">(↔ orange)</span>. To reach an Azure VMware Solution based VM, the ER circuit is used in addition with Global Reach and the AVS ER circuit <span style="color:#FF2626;font-weight:bold;">(↔ red)</span>.

## Migrate a VM to the cloud environment

Let's migrate `migration-vm-2` to the cloud environment using HCX. The migration is successful and the VM is now running in the cloud environment. The VM is still using the on-premises `gw` device to reach both the Internet and the cloud environment as its default gateway is still configured to `10.100.115.1`.

![migration-vm-2 still relies on its on-premises based gateway to reach resources out-of-its L2 broadcast domain](/images/hcx-mon/scenario2-migrated-vm.png)

To reach Internet <span style="color:#FF0080;font-weight:bold;">(↔ pink)</span> or cloud based resources <span style="color:#FF9933;font-weight:bold;">(↔ orange)</span>, the network path is not optimal and this is even more obvious when we look at path to reach VM in another NSX-T segment of AVS <span style="color:#FF2626;font-weight:bold;">(↔ red)</span>. We call this situation: [*(w)* network tromboning](https://en.wikipedia.org/wiki/Anti-tromboning).

### Segment connectivity

On NSX-T, when the network extension was created, a segment with the same subnet settings was created and named with `L2E_` prefix.

![Segment connectivity of L2E network](/images/hcx-mon/scenario2-nsx-t-connectivity.png)

As you can see in the screenshot, this segment is configured with a **disabled** `gateway connectivity`. This means that the segment is not advertised to the other components of the NSX-T fabric cannot use the T1 gateway for L3 connectivity.

## Mobility Optimized Network enablement

In order to improve the network path, we are going to enable the Mobility Optimized Network feature of HCX. This feature is available in the HCX UI, in the **Network Extension** section, and can be enabled on a per-network basis.

If we enable this feature, and not change the default settings, the connectivity of the segment is switched to **enabled** and the T1 gateway **may** now be used for L3 connectivity.

![Mobility Optimized Network enablement](/images/hcx-mon/scenario3-default-mon.png)

As you probably noticed, network paths are not changed for the migrated VM. This is due to the default setting for *router-location*: `hcx-enterprise`.

> The *router-location* `hcx-enterprise` setting value means that on-premises `gw` device is still used as the default gateway for the migrated VM.

![Router location for the migrated VM with default settings::picture-border](/images/hcx-mon/scenario3-router-location.png)

### Segment connectivity

Let's have a look at the segment connectivity after enabling the Mobility Optimized Network feature:

![Segment connectivity of L2E network with MON enabled](/images/hcx-mon/scenario3-nsx-t-connectivity.png)

The `gateway connectivity` is now **enabled** on the L2E segment, and the T1 gateway could now used for L3 connectivity (depending on the *router-location* setting).

In BGP advertisement in the Express Route circuits, we can also see a new `/32` route advertised from NSX-T:

* `10.100.115.1/32`: the gateway of the extended network.

## Changing the *router-location*

To improve the network path for the migrated VM, we may be tempted to change the *router-location* setting to use the cloud side gateway for our migrated VM:

![Router location for the migrated VM with cloud side gateway::picture-border](/images/hcx-mon/scenario4-cloud-router-location.png)

The following changes will be applied to network path:

![Network path when the router location is changed to cloud side gateway](/images/hcx-mon/scenario4-cloud-router-location-network-flows.png)

* The default gateway configured at the the VM/OS is not changed: `10.100.115.1` but...
* To reach a VM in a distinct NSX-T segment, the traffic will be routed through the T1 gateway of the segment, and not through the on-premises `gw` device <span style="color:#FF2626;font-weight:bold;">(↔ red)</span>.
* To reach the Internet, the traffic will be routed through the T1 gateway of the segment, and not through the on-premises `gw` device <span style="color:#FF0080;font-weight:bold;">(↔ pink)</span>.
* To reach a VM in the native cloud environment, the traffic will be routed through the on-premises `gw` device <span style="color:#FF9933;font-weight:bold;">(⇠ orange)</span>.
  * But the return path will be through the T1 gateway of the segment <span style="color:#FF9933;font-weight:bold;">(⇠ orange)</span>.

As you can see there, if the network path to AVS hosted or Internet resources seems optimized, the path to native cloud resources is not and is asymmetric. This is because of a setting category in Mobility Optimized Network feature: **policy routes**. We will explore this setting in the next sections.

### What happened in the backstages

When we changed the *router-location* setting, the following change was applied:

If we have a look at the routing table of the T1 gateway, a new entry was added for the migrated VM:

![Routing table of the T1 gateway](/images/hcx-mon/scenario3-static-routes.png)

![Next hop of the static route for the migrated VM](/images/hcx-mon/scenario3-static-route-next-hop.png)

On the Express Route circuit, 2 new routes are also visible, advertised over BGP from NSX-T:

* `10.100.115.1/32`: the gateway of the network is now advertised from AVS (*this route was already advertised since the MON enablement*)
* `10.100.115.12/32`: the migrated VM with MON enabled and *router-location* set to HCX cloud instance.

### Asymmetric routing

As you see on the [network flow to a cloud based resource](#changing-the-router-location) (in a private network), there is an asymmetric routing. The traffic is routed through the on-premises `gw` device to reach the cloud based resource, but the reverse path is going through the T1 gateway of the segment <span style="color:#FF9933;font-weight:bold;">(⇠ orange)</span>, on cloud side.

As NSX-T is now publishing the `/32` route of the migrated VM, cloud resources can now reach the migrated VM directly through the T1 gateway of the segment. This is the reason why this, cloud resource to AVS one, path is through the T1 gateway.

The reason of the `migration-vm-X` to use the on-premises `gw` device to reach the cloud based resource is because of the default **policy routes** setup when MON is enabled:

![Default policy routes when MON is enabled::picture-border](/images/hcx-mon/scenario3-default-policy-routes.png)

By default, the **policy routes** are configured to be *allowed* to use the on-premises `gw` device as the default gateway for the traffic matching the RFC1918 address spaces:

* `10.0.0.0/8`
* `172.16.0.0/12`
* `192.168.0.0/16`

This enable the migrated VM to reach other resources of the on-premises network, via on-premises `gw` device as the default gateway, but if not customized, it also introduces an asymmetric routing for the traffic to cloud based resources.

## Let's customize the policy routes

### Remove all policy routes

A good illustration to understand the impact of the policy routes is to do a test by removing all the pre-configured policy routes.

![Network path when there is no policy routes](/images/hcx-mon/scenario5-no-policy-routes.png)

For Internet <span style="color:#FF0080;font-weight:bold;">(↔ pink)</span> or AVS based resources <span style="color:#FF2626;font-weight:bold;">(↔ red)</span>, the network path is still the one from the previous section.

For native cloud resources <span style="color:#FF9933;font-weight:bold;">(↔ orange)</span>, the network path is now symmetric as the migrated VM is using the T1 gateway of the segment to reach all the resources out-of its L2 broadcast domain.

**This setup could be sub-optimal** for the migrated VM to reach on-premises resources, but this is something that can be customized by adding a new policy route with more specific matching criteria for the on-premises resources.

### Add a very specific policy route

Another good illustration of how policy routes work in a MON enabled network extension is to add a very specific policy route to reach a specific resource with an optimal path.

In our example, we will recreate the default policy routes and add a `/32` one with a `deny` rule, matching the Azure hosted resource `azure-vm`:

* `10.0.0.0/8`: Send to source with HCX: <span style="color:#00CC00;">allow<span>
* `172.16.0.0/12`: Send to source with HCX: <span style="color:#00CC00;">allow<span>
* `192.168.0.0/16`: Send to source with HCX: <span style="color:#00CC00;">allow<span>
* `10.100.2.36/32`: Send to source with HCX: <span style="color:#FF2626;">deny<span>

In this new setup, network path to the Azure hosted resource `azure-vm` is now optimized in both directions:

![Network path when there is a very specific policy routes](/images/hcx-mon/scenario6-specific-policy-route.png)

* To reach on premises resources in a private RFC1918 ranges (like in `10.0.0.0/8`), the on-prem `gw` device is used <span style="color:#4D27AA;font-weight:bold;">(↔ purple)</span>.
* To reach a cloud based specific resource (`10.100.2.36/32`), the cloud side gateway is used <span style="color:#FF9933;font-weight:bold;">(↔ orange)</span>.

> Note: I removed the internet connectivity to simplify the diagram but there is no change in the network path to reach Internet.

## Use policy routes for internet connectivity

In the previous section, we saw that we can use policy routes to optimize the network path to reach a specific resource. We can also use policy routes to optimize or guide the network path to reach Internet (or `0.0.0.0/0`).

### Internet egress with default policy routes

Let's have a look at the network path to reach Internet with the default policy routes (*router-location* is set to cloud side gateway):

![Network path to reach Internet with default policy routes and router-location set to cloud side gateway](/images/hcx-mon/scenario7-internet-with-default-policy-routes.png)

As Internet (`0.0.0.0/0`) is not part of the RFC1918 address spaces configured to use the On-Prem gateway (with the default policy routes), the migrated VM is using the T1 gateway and the Azure egress connectivity of the segment to reach Internet <span style="color:#FF0080;font-weight:bold;">(↔ pink)</span>.

> **Note**: The azure egress path to reach Internet may vary depending on the configuration of the Azure VMware Solution SDDC. In this example, the Azure egress is configured to the default [*Microsoft Managed SNAT*](https://vuptime.io/post/2022-08-12-azure-vmware-solution-public-ip-on-nsx-edge/#enable-outbound-internet-access-using-snat).
> You can find some details about the Internet connectivity for AVS, in the following post: [Azure VMware Solution – Use public IP on NSX-T Edge](https://vuptime.io/post/2022-08-12-azure-vmware-solution-public-ip-on-nsx-edge/).

### Internet egress with a specific policy route

Let's add a specific policy route to reach Internet through the on-premises `gw` device (*router-location* is still set to cloud side gateway):

* `0.0.0.0/0`: Send to source with HCX: <span style="color:#00CC00;">allow<span>

![Network path to reach Internet with a specific policy route and router-location set to cloud side gateway](/images/hcx-mon/scenario8-internet-with-specific-policy-route.png)

With this new policy route, the migrated VM is now using the on-premises `gw` device to reach Internet <span style="color:#FF0080;font-weight:bold;">(↔ pink)</span>. You can then apply some firewall rules on the on-premises `gw` device to control the Internet access of the migrated VM.

Without additional policy routes, all the network flows will also use this on-premises `gw` device: it could be counter-productive to enable MON in this case without adding additional policy routes to optimize the network path to reach other resources.

## An art-of-balance

{{% notice info "Disclaimer" %}}
Do not reproduce the previous examples on a production environment.
{{< /notice >}}

Previous examples are provided to illustrate the behavior of MON enabled resources and network flows based on settings changes. You will probably need to consider carefully how-to apply global and/or specific flows policies based on your deployment to avoid any issue and to maintain the expected level of security on the network flow path.

For example, once a flow is using the NSX-T Tier1, it is not secured anymore by the on-premises firewall and may require to have some firewall rules setup on NSX-T level.

Also, MON is coming with [some limitations to consider](https://docs.vmware.com/en/VMware-HCX/4.7/hcx-user-guide/GUID-BEC26054-D560-46D0-98B4-7FF09501F801.html) and may not be suitable for all the use cases. A good review of existing documentation is mandatory before proceeding in MON enablement. A good starting-point for AVS resources is the following documentation page: [VMware HCX Mobility Optimized Networking (MON) guidance](https://learn.microsoft.com/en-us/azure/azure-vmware/vmware-hcx-mon-guidance).

Finally, I will strongly suggest to consider network-extension *cutover* operation as a critical step of your migration project and to plan it carefully. Mobility Optimized Networking feature is a great helper to optimize the network flow path, avoid or limit network tromboning scenario but should be considered as a tool to help you to achieve your migration goal and not as a magic feature that will solve all your network issues or provide a way to skip network extension cutovers operations. For long term network extensions, changing the default gateway of the migrated VM to the cloud side gateway may be a good option to optimize network flows.