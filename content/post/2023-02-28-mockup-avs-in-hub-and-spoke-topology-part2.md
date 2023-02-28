---
title: Mock-up Azure VMware Solution in Hub-and-Spoke topology – Part 2
date: "2023-02-28"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
- Azure
tags:
- vmware
- azure
- azure vmware solution
- avs
- network
- hub and spoke
toc: true
thumbnail: /images/avs-nva/icon2.png
---

In the [previous blog post](/post/2023-02-22-mockup-avs-in-hub-and-spoke-topology-part1/), we have seen how to deploy a basic environment to start mocking-up an Azure VMware Solution (AVS) environment in a hub and spoke topology. In the [last section](/post/2023-02-22-mockup-avs-in-hub-and-spoke-topology-part1/#stage-3--user-defined-route-on-spokes--gw-propagation-false), we discovered a glitch-in-the-Matrix when we lookup for the traffic between VPN and spoke VMs. We will see in this blog post [how to fix this issue](#stage-4--user-defined-routes-on-gatewaysubnet).

We will also [introduce the first components of an AVS transit vNet](#stage-5--introduction-of-an-avs-transit-vnet) to land the Express Route circuit from an AVS deployment and [how to inject a default BGP route to VMware workloads](#stage-6--advertise-a-default-routes-to-avs).

> As a reminder, the components and network design described in this blog post are only for demonstration purposes. They are not intended to be used in a production environment and does not represent Azure best practices. They are provided as-is for mock-up and learning purposes only.

Please refer to [part 1](/post/2023-02-22-mockup-avs-in-hub-and-spoke-topology-part1/) to get details about the lab environment and the 3 first steps we already covered.

## Stage 4 – User Defined Routes on GatewaySubnet

In order to **mitigate the asymmetric routing issue**, we will add a User Defined Routes to the `GatewaySubnet` to ensure that the traffic incoming from the VPN client will be routed to the NVA appliance.

![User Defined Routes on GatewaySubnet](/images/avs-nva/stage4/hub_and_spoke_avs-Step4.drawio.png)

The User Defined Route (UDR) on `GatewaySubnet` will configured as below:

* 10.100.201.0/24 (aka `spoke1-vnet`) via `nva-vm.nic[0].ipaddress`
* 10.100.202.0/24 (aka `spoke2-vnet`) via `nva-vm.nic[0].ipaddress`

In Azure Portal, it looks like this:

![User Defined Routes on GatewaySubnet](/images/avs-nva/stage4/UserDefinedRoute_GatewaySubnet.png)

> Of course, depending on the used IP address plan, it is possible to simplify and group multiple routes under a common prefix.

### Routes analysis (s4)

From this point we can see that both VPN-client-to-spokes and spokes-to-VPN-destinations, passing through the `hub-nva` appliance:

![Routes analysis with symmetric traffic](/images/avs-nva/stage4/hub_and_spoke_avs-Step4-SymmetricTraffic.drawio.png)

Example: During a ping session from a VPN client to `spoke-1-vm`, we can only see both echo *request* and echo *reply* going through the `hub-nva`:

```bash
ubuntu@hub-nva:~$ sudo tcpdump -nni eth0  icmp
# output
IP 10.100.204.2 > 10.100.201.4: ICMP echo request, id 1002, seq 1, length 64
IP 10.100.200.68 > 10.100.201.4: ICMP echo request, id 1002, seq 1, length 64
IP 10.100.201.4 > 10.100.200.68: ICMP echo reply, id 1002, seq 1, length 64
IP 10.100.201.4 > 10.100.204.2: ICMP echo reply, id 1002, seq 1, length 64
```

All the network traffic is now passing through the `hub-nva`. Meaning that we fixed the asymmetric routing issue.

### Additional information about Azure UDR

If you need to learn more about UDR in Azure, I strongly recommend you to read the following posts:

* [User Defined Routes](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview#user-defined) in Azure documentation
* [How Azure selects a route](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview#how-azure-selects-a-route) in Azure documentation
* [Don’t let your Azure Routes bite you](https://blog.cloudtrooper.net/2020/11/28/dont-let-your-azure-routes-bite-you/) by Jose Moreno

## Stage 5 – Introduction of an AVS transit vNet

Azure VMware Solution (AVS) is provided with an external connectivity based on Express Route Circuit. This requires to 'land' the Express Route circuit out of the AVS environment. The most common way to do this is to map the AVS Express Route circuit to an existing On Premises Express Route circuit and to rely on [Express Route Global Reach for providing the connectivity between the two circuits](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-global-reach): transitive connectivity.

But this setup will not provide a way to consider the AVS deployment as a spoke in a hub-and-spoke topology, as the network traffic between AVS and On Premises, will bypass the `hub-nva`. In order to fix this situation, we will introduce a *transit vNet* to land the Express Route circuit from the AVS deployment and to ensure that the traffic between AVS and On Premises will be routed through the `hub-nva`.

In this `avs-transit-vnet`, we will need an Express Route Gateway to land the Express Route circuit from the AVS deployment.

![Introduction of an AVS transit vNet](/images/avs-nva/stage5/hub_and_spoke_avs-Step5.drawio.png)

### Routes analysis (s5)

When the creation of the vNet is completed and the connection of AVS ER circuit setup, we could look at effective routes to see if there is any chance to communicate with AVS based VMs at this stage:

```bash
az network nic show-effective-route-table \
  --ids /subscriptions/<sub-id>/resourceGroups/nva-testing-RG/providers/Microsoft.Network/networkInterfaces/hub-nva-nic \
  -o table
# output
Source                 State    Address Prefix    Next Hop Type          Next Hop IP
---------------------  -------  ----------------  ---------------------  -------------
Default                Active   10.100.200.0/24   VnetLocal
Default                Active   10.100.202.0/24   VNetPeering
Default                Active   10.100.201.0/24   VNetPeering
Default                Active   10.100.203.0/24   VNetPeering
VirtualNetworkGateway  Active   10.100.204.0/24   VirtualNetworkGateway  20.160.147.74
```

And, of course, if there is no route, there is no connectivity:

```bash
ubuntu@hub-nva:~$ ping 10.100.100.2 -c3
# output
PING 10.100.100.2 (10.100.100.2) 56(84) bytes of data.
--- 10.100.100.2 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2029ms
```

Depending on **AVS connectivity settings**, if we rely on routes announced from the Express Route connection to reach Internet or other Azure resources: we cannot communicate with resources out of AVS due to the lack of announced routes.

### Additional information about AVS connectivity

If you need to learn more about AVS connectivity, I strongly recommend you to read the following posts:

* [Azure VMware Solution networking and interconnectivity concepts](https://learn.microsoft.com/en-us/azure/azure-vmware/concepts-networking) in Azure documentation
* [Azure VMware Solution network design considerations](https://learn.microsoft.com/en-us/azure/azure-vmware/concepts-network-design-considerations) in Azure documentation
* [Azure VMware Solution networking voodoo](https://blog.cloudtrooper.net/2022/05/16/azure-vmware-solution-networking-voodoo/) by Jose Moreno

## Stage 6 – Advertise a default routes to AVS

In the current stage, we will introduce a default route (0.0.0.0/0) announcement to AVS. According to the leitmotif of this blog post series, we will go step by step and we will start with the simplest solution: a default route announced from the `avs-transit-vnet` to AVS. And we will temporarily ignore the previous components of our hub-and-spoke topology.

Firstly, we will need some extra components added to our *AVS transit* topology:

* VM, `avs-bgp-vm` to:
  * Initiate the BGP route announcement
  * Route the traffic incoming from AVS
* An *Azure Route Server* (ARS) to propagate the route announcements in the Azure SDN
  * This ARS component will be peered with the `avs-bgp-vm` and will provide routes incoming from this BGP peer, to AVS, through the *Virtual Network Gateway*.
* A *Route Table* (UDR) to override the default route advertised by the `avs-bgp-vm`. Otherwise, the VM advertises itself as the default route for the whole vNET and will keep sending the Internet-bound traffic, [including the one sent by the VM back to the VM itself](https://learn.microsoft.com/en-us/azure/route-server/troubleshoot-route-server#why-does-my-nva-lose-internet-connectivity-after-it-advertises-the-default-route-00000-to-azure-route-server).

![Advertise a default routes to AVS](/images/avs-nva/stage6/hub_and_spoke_avs-Step6.drawio.png)

> As mentioned earlier, this is a first and temporary step. Validating this setup where the Internet breakout is made in the `avs-transit-vnet` for the AVS deployment will help to understand and prepare for the next steps.

### AVS Internet connectivity settings

Azure VMware Solution provides three options for Internet connectivity:

* [Microsoft-managed SNAT](https://learn.microsoft.com/en-us/azure/azure-vmware/concepts-design-public-internet-access#azure-vmware-solution-managed-snat)
* [Public IP addresses down to the NSX-T edges](https://learn.microsoft.com/en-us/azure/azure-vmware/concepts-design-public-internet-access#azure-public-ipv4-address-to-nsx-t-data-center-edge)
* [Customized Internet connectivity through the Express Route circuit routes announcements](https://learn.microsoft.com/en-us/azure/azure-vmware/concepts-design-public-internet-access#internet-service-hosted-in-azure)

In this blog post series, we will consider that AVS is configured to get its [Internet connectivity from a default route announced through the Express Route circuit](https://learn.microsoft.com/en-us/azure/azure-vmware/concepts-design-public-internet-access#internet-service-hosted-in-azure).

![AVS Internet connectivity settings](/images/avs-nva/stage6/avs-internet-connectivity-settings.png)

### Routes analysis (s6)

When the creation of the new components and connections is completed, we could look at effective routes to see the result:

From the deployed *Azure Route Server*, we can see the BGP peer:

```bash
az network routeserver peering show -g nva-testing-RG \
  -n avs-rs-bgp-connection --routeserver AVSTransitRouterServer \
  -o table
# output
Name                   PeerAsn    PeerIp         ProvisioningState    ResourceGroup
---------------------  ---------  -------------  -------------------  ---------------
avs-rs-bgp-connection  65002      10.100.203.68  Succeeded            nva-testing-RG
```

And we **should** see the learned route, advertised by the BGP peer:

```bash
az network routeserver peering list-learned-routes \
  -g nva-testing-RG -n avs-rs-bgp-connection \
  --routeserver AVSTransitRouterServer -o table
# output
Issue: no route displayed there!
```

{{% notice warning "Issue: no route displayed there" %}}
The `list-learned-routes` command does not work as expected. The issue is currently under investigation.
In the meantime, we will use the PowerShell command `Get-AzRouteServerPeerLearnedRoute` to display the routes.
{{% /notice %}}

Using PowerShell, the advertised routes are displayed:

```powershell
$routes = @{
    RouteServerName = 'AVSTransitRouterServer'
    ResourceGroupName = 'nva-testing-RG'
    PeerName = 'avs-rs-bgp-connection'
}
Get-AzRouteServerPeerLearnedRoute @routes | ft
LocalAddress  Network   NextHop       SourcePeer    Origin AsPath Weight
------------  -------   -------       ----------    ------ ------ ------
10.100.203.36 0.0.0.0/0 10.100.203.68 10.100.203.68 EBgp   65002   32768
10.100.203.37 0.0.0.0/0 10.100.203.68 10.100.203.68 EBgp   65002   32768
```

We can see that the `avs-bgp-vm` is advertising itself as the next hop for the default route. This is the expected behavior.

### Tests (s6)

From a VM hosted in AVS, we can now reach Internet, by going through the `avs-bgp-vm`:

```bash
ubuntu@avs-vm-100-10:~$ mtr 1.1.1.1 --report
HOST: avs-vm-100-10                Loss%   Snt   Last   Avg  Best  Wrst StDev
  1.|-- _gateway                   0.0%    10    0.1   0.2   0.1   0.2   0.0
  2.|-- 100.64.176.0               0.0%    10    0.2   0.3   0.2   0.3   0.0
  3.|-- 100.72.18.17               0.0%    10    0.9   0.8   0.7   0.9   0.1
  4.|-- 10.100.100.233             0.0%    10    1.0   1.0   0.9   1.1   0.1
  5.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
  6.|-- 10.100.203.68              0.0%    10    3.2   4.0   2.6   7.3   2.0
  7.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
  8.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
  9.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 10.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 11.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 12.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 13.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 14.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 15.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 16.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 17.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
 18.|-- one.one.one.one            0.0%    10    5.7   4.9   3.9   9.6   1.7
```

In previous route-tracing report, `10.100.203.68` is the IP of `avs-bgp-vm`, acting like a router or NVA, as expected for this scenario.

But obviously, this is not the behavior of a standard spoke for the rest of the h&s topology. This step was only there to prepare some of the components we will need further.

### Additional information about AVS connectivity with Azure Route Server

If you need to learn more about AVS connectivity with Azure Route Server in Azure, I strongly recommend you to read the following posts:

* [Injecting routes to Azure VMware Solution with Azure Route Server](https://learn.microsoft.com/en-us/azure/route-server/vmware-solution-default-route) in Azure documentation
* [Network Virtual Appliance in Azure Virtual Network to inspect all network traffic](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/azure-vmware/eslz-network-topology-connectivity) in Azure documentation

## Part 2 – Conclusion

In this second part, we have seen how to mitigate the asymmetric routing issue by configuring a new *Route Table* applicable to VPN Gateway and we created the network components to advertise BGP routes to the *Azure VMware Solution* deployment with the help of *Azure Route Server*.

In the next (and probably last) part, we will see how to configure this AVS transit topology as a normal spoke in the hub and spoke topology. We will also cover a simplification of the On-Premises connectivity configuration, relying on *Azure Route Server*.
