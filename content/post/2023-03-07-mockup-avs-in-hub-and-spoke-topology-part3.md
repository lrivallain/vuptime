---
title: Mock-up Azure VMware Solution in Hub-and-Spoke topology – Part 3
date: "2023-03-07"
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
thumbnail: /images/avs-nva/icon3.png
---

In the previous blog posts ([part 1](/post/2023-02-22-mockup-avs-in-hub-and-spoke-topology-part1/) and [part 2](/post/2023-02-28-mockup-avs-in-hub-and-spoke-topology-part2/)), we covered the deployment of the basic components of an Hub and Spoke topology including an Azure VMware Solution (AVS) deployment.

In the first post we deployed and configured a mockup of Hub and Spoke environment. In the second post we connected the AVS environment to an *AVS transit vNet* and advertised a default route to the AVS workload. This default route was not yet using our `hub-vna` appliance but an appliance deployed in the `avs-transit-vnet` to reach out Internet.

In this step, we will integrate our `avs-transit-vnet` within the overall h&s topology and rely on the `hub-nva` VM to manage all the required filtering either for:

* Spoke-to-spoke
* Spoke-to-On-Premise (and vice versa)
* Internet breakout

As we want AVS to behave like a spoke, we will apply this rule to the `avs-transit-vnet` too.

> As a reminder, the components and network design described in this blog post are only for demonstration purposes. They are not intended to be used in a production environment and does not represent Azure best practices. They are provided as-is for mock-up and learning purposes only.

## Stage 7 – Advertise the hub default routes to AVS

First thing, we need to add some routes in a new UDR applied to the `nva-subnet`. The added routes will ensure that `hub-nva` will be able to propagate AVS related traffic through the `avs-bgp-vm`. In out lab setup, we do it for 2 prefix:

* AVS management: `10.100.100.0/22`
* AVS workload: `10.100.110.0/24`

We also need to update the UDR applied to the `bgp-subnet` within `avs-transit-vnet` to add the default route via the `hub-nva` appliance.

![Advertise the hub default routes to AVS](/images/avs-nva/stage7/hub_and_spoke_avs-Step7.drawio.png)

### Routes analysis (s7)

We can check the new routes, applicable to the `hub-nva` NIC:

```bash
az network nic show-effective-route-table \
  --ids /subscriptions/<sub-id>/resourceGroups/nva-testing-RG/providers/Microsoft.Network/networkInterfaces/hub-nva-nic \
  -o table
Source    State    Address Prefix    Next Hop Type     Next Hop IP
--------  -------  ----------------  ----------------  -------------
Default   Active   10.100.200.0/24   VnetLocal
Default   Active   10.100.202.0/24   VNetPeering
Default   Active   10.100.201.0/24   VNetPeering
Default   Active   10.100.203.0/24   VNetPeering
Default   Active   0.0.0.0/0         Internet
...
User      Active   10.100.110.0/24   VirtualAppliance  10.100.203.68 # <--- AVS workload
User      Active   10.100.100.0/22   VirtualAppliance  10.100.203.68 # <--- AVS management
```

### UDR in AVS transit `bgp-subnet`

As we want to rely on `hub-nva` for spoke-to-spoke and Internet breakout, we need to change the UDR applied to the `bgp-subnet` within `avs-transit-vnet` to ensure going through `hub-nva`.

![UDR in AVS transit bgp-subnet](/images/avs-nva/stage7/UDR-on-AVS-transit.png)

And the result on effective routes:

```bash
az network nic show-effective-route-table \
  --ids /subscriptions/<sub-id>/resourceGroups/nva-testing-RG/providers/Microsoft.Network/networkInterfaces/avs-bgp-nic \
  -o table
Source                 State    Address Prefix     Next Hop Type          Next Hop IP
---------------------  -------  -----------------  ---------------------  -------------
Default                Active   10.100.203.0/24    VnetLocal
Default                Active   10.100.200.0/24    VNetPeering
VirtualNetworkGateway  Active   10.100.100.64/26   VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.109.0/24    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.101.0/25    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.100.0/26    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.110.0/24    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.111.0/24    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.113.0/24    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.114.0/24    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.100.192/32  VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.103.0/26    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.101.128/25  VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Active   10.100.102.0/25    VirtualNetworkGateway  10.24.132.60
VirtualNetworkGateway  Invalid  0.0.0.0/0          VirtualNetworkGateway  10.100.203.68
User                   Active   0.0.0.0/0          VirtualAppliance       10.100.200.68 # <--- Default route via hub-nva
```

In the last line we can see that the default route is now going by the `hub-nva` VM (`10.100.200.68`).

### Tests (s7)

At this stage, the traffic from and to AVS will go through the `hub-nva` and the `avs-bgp-vm`. We can easily check this, either by snooping on each routing appliance or by looking at the result of a `traceroute` to a spoke VM:

```bash
ubuntu@avs-vm-100-10:~$ mtr 10.100.201.4 --report
HOST: avs-vm-100-10              Loss%   Snt   Last   Avg  Best  Wrst StDev
  1.|-- _gateway                   0.0%    10    0.2   0.2   0.1   0.2   0.0
  2.|-- 100.64.176.0               0.0%    10    0.2   0.2   0.2   0.3   0.0
  3.|-- 100.72.18.17               0.0%    10    0.8   0.8   0.7   1.1   0.1
  4.|-- 10.100.100.237             0.0%    10    1.1   1.2   1.1   1.4   0.1
  5.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
  6.|-- 10.100.203.68              0.0%    10    3.1   3.1   2.7   5.6   0.9 # <--- avs-bgp-vm
  7.|-- 10.100.200.68              0.0%    10    4.5   4.8   3.4   7.6   1.6 # <--- hub-nva
  8.|-- 10.100.201.4               0.0%    10    4.1   6.6   4.1   9.3   1.8 # <--- spoke-vm
```

Here we can see on **hop 6** and **7**, the IP address of `avs-bgp-vm` (`10.100.203.68`) and `hub-nva` (`10.100.200.68`). We can reproduce the same behavior with Internet targets.

![Overview of network flows between a spoke VM and an AVS based VM](/images/avs-nva/stage7/hub_and_spoke_avs-Step7-SymmetricTraffic.drawio.png)

Unfortunately, from on premises (VPN) resources, both `avs-transit-vnet` and AVS resources are not available as there is no route advertised for those targets.

## Stage 8 – AVS from on-Premises

As we discovered in the previous step, our on-premises resources do not have any route advertised to communicate with either `avs-transit-vnet` or AVS resources.

We will mitigate this lack in the current step by adding:

1. New routes for`avs-transit-vnet` and AVS resources in the `GatewaySubnet` UDR.
    * To simplify the routes in my lab setup, I advertise the **global prefix** of my Azure resources (including AVS ones) in a single route: `10.100.0.0/16`
    * This UDR will be used by the VPN gateway to find a network path to the resources.
2. A custom route in the VPN configuration to specify to VPN clients that the network traffic for the target resources should be going through the VPN.
    * As for the UDR, I simplify the custom route announcement in my setup by using a global prefix for all the resources: `10.100.0.0/16`

![Configure connectivity from on-Premises to AVS](/images/avs-nva/stage8/hub_and_spoke_avs-Step8.drawio.png)

### Tests (s8)

From the VPN client, it is easy to see the custom route (`10.100.0.0/16`) added to the VPN path:

And if we check the connectivity from a P2S VPN client with an AVS based VM:

```bash
ubuntu@vpn-client:~$ ping 10.100.110.10 -c3
# output
PING 10.100.110.10 (10.100.110.10) 56(84) bytes of data.
64 bytes from 10.100.110.10: icmp_seq=1 ttl=57 time=52.3 ms
64 bytes from 10.100.110.10: icmp_seq=2 ttl=57 time=30.1 ms
64 bytes from 10.100.110.10: icmp_seq=3 ttl=57 time=52.9 ms
--- 10.100.110.10 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 30.097/45.119/52.947/10.625 ms
```

### Routes analysis (s8)

![Overview of network flows between a P2S VN client and an AVS based VM](/images/avs-nva/stage8/onprem-to-avs.drawio.png)

In this **on-premises** to **AVS** exchange, the following routing components are used:

1. On VPN client side, the **custom route** advertises a path for the resources matching the Azure global prefix and/or AVS resources
2. The VPN gateway relies on its attached **UDR** to use the `hub-nva` as next hop
3. The `hub-nva` relies on its **UDR** to find a path to AVS based resources using the `avs-bgp-vm` as a next hop
4. The **vNET peering** enables the communication between resources from `hub-vnet` and `avs-transit-vnet`
5. In the `avs-transit-vnet`, the path to AVS resources is directly advertised from the **Express Route Gateway** linked to AVS and propagating the AVS BGP routes.

In the opposite direction:

6. The combination of `avs-gbp-vm` and **Azure Route server** provides a default (`0.0.0.0/0`) route for the AVS based workload:
    * 6a) The default route is announced over BGP from the `avs-transit-vnet`
    * 6b) The **Azure Route Server** propagates the route advertisement in the Azure SDN and the route can be advertised to the AVS workload through the **Express Route** circuit
7. The **vNET peering** enables the communication between resources from `hub-vnet` and `avs-transit-vnet`
8. In the `hub-vnet`, the path to VPN based workload is directly advertised from the **VPN Gateway**.

## Stage 9 – Azure Server in the hub vNet

It is possible to use a combination of the `hub-nva` BGP capabilities and *Azure Route Server* to advertise network prefixes used in Azure to the VPN *Virtual Network Gateway* and avoid maintaining the *Route Table* of the `GatewaySubnet`.

Compared to the previous setup, we **removed**:

* *Custom route* in the VPN configuration
* *UDR* attached to the *GatewaySubnet*

And we **added**:

* A new *Azure Route Server*
* A BGP route advertised from `hub-nva` (I used the global Azure Prefix of the lab but this can be more specifics announcements)
* A BGP peering between `hub-nva` and the *Azure Route Server*

![Azure Server in the hub vNet](/images/avs-nva/stage9/hub_and_spoke_avs-Step9.drawio.png)

### Routes analysis (s9)

From *Azure Route Server*, we can see that BGP peer is injecting the expected route:

```powershell
$routes = @{
    RouteServerName = 'HubRouterServer'
    ResourceGroupName = 'nva-testing-RG'
    PeerName = 'hub-rs-bgp-connection'
}
Get-AzRouteServerPeerLearnedRoute @routes | ft
# output
LocalAddress  Network       NextHop       SourcePeer    Origin AsPath Weight
------------  -------       -------       ----------    ------ ------ ------
10.100.200.36 10.100.0.0/16 10.100.200.68 10.100.200.68 EBgp   65001  32768
10.100.200.37 10.100.0.0/16 10.100.200.68 10.100.200.68 EBgp   65001  32768
```

From the *VPN gateway*, we can also see the advertised routes:

```bash
az network vnet-gateway list-learned-routes -n hub-vpn-gateway -g nva-testing-RG -o table
# output
Network            NextHop        Origin    SourcePeer     AsPath    Weight
-----------------  -------------  --------  -------------  --------  --------
10.100.200.0/24                   Network   10.100.200.5             32768
10.100.201.0/24                   Network   10.100.200.5             32768
10.100.202.0/24                   Network   10.100.200.5             32768
10.100.204.0/25                   Network   10.100.200.5             32768
10.100.204.128/25  10.100.200.4   IBgp      10.100.200.4             32768
10.100.204.128/25  10.100.200.4   IBgp      10.100.200.36            32768
10.100.204.128/25  10.100.200.4   IBgp      10.100.200.37            32768
10.100.0.0/16      10.100.200.68  IBgp      10.100.200.36  65001     32768 # <--- BGP route from hub-nva
10.100.0.0/16      10.100.200.68  IBgp      10.100.200.37  65001     32768 # <--- BGP route from hub-nva
10.100.200.0/24                   Network   10.100.200.4             32768
10.100.201.0/24                   Network   10.100.200.4             32768
10.100.202.0/24                   Network   10.100.200.4             32768
10.100.204.128/25                 Network   10.100.200.4             32768
10.100.204.0/25    10.100.200.5   IBgp      10.100.200.5             32768
10.100.204.0/25    10.100.200.5   IBgp      10.100.200.36            32768
10.100.204.0/25    10.100.200.5   IBgp      10.100.200.37            32768
10.100.0.0/16      10.100.200.68  IBgp      10.100.200.36  65001     32768 # <--- BGP route from hub-nva
10.100.0.0/16      10.100.200.68  IBgp      10.100.200.37  65001     32768 # <--- BGP route from hub-nva
```

And from the VPN client, the route is also available among the ones from vNET peerings:

![Routes from VPN client](/images/avs-nva/stage9/RoutesFromVPNClient.png)

### Tests (s9)

When reaching an AVS based VM from a VPN client we can see the components of our topology:

```bash
ubuntu@vpn-client:~$ mtr 10.100.110.10 -r
# output
Start: 2023-02-09T17:21:35+0100
HOST: vpn-client                  Loss%   Snt   Last   Avg  Best  Wrst StDev
  1.|-- vpn-client                 0.0%    10    0.5   0.5   0.3   1.0   0.3
  2.|-- 10.100.200.68              0.0%    10   21.0  53.3  20.6 307.4  89.7
  3.|-- 10.100.203.68              0.0%    10   25.4  44.5  21.6 207.4  57.8
  4.|-- 10.100.203.4               0.0%    10   36.0  42.4  21.9 120.7  29.9
  5.|-- 10.100.100.233             0.0%    10   54.0  32.0  23.8  59.9  13.5
  6.|-- 10.100.100.65              0.0%    10   49.3  39.8  24.6  55.8  12.5
  7.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
  8.|-- ???                       100.0    10    0.0   0.0   0.0   0.0   0.0
  9.|-- 10.100.110.10              0.0%    10   60.5  37.4  22.7  64.9  18.2
```

I matched the hop numbers of `mtr` trace in the following diagram (considering a set of hops are part of the AVS network stack and not documented here):

![Diagram of routing hops shown in the mtr network tool trace](/images/avs-nva/stage9/onprem-to-avs.drawio.png)

### Additional information about AVS connectivity with Azure Route Server

If you need to learn more about Azure Route Server, I strongly recommend you to read the following posts:

* [Azure Route Server: to encap or not to encap, that is the question](https://blog.cloudtrooper.net/2022/02/06/azure-route-server-to-encap-or-not-to-encap-that-is-the-question/) and [Azure Firewall’s sidekick to join the BGP superheroes](https://blog.cloudtrooper.net/2022/05/02/azure-firewalls-sidekick-to-join-the-bgp-superheroes/) by Jose Moreno
* [NVA Routing 2.0 with Azure Route Server, VxLAN (or IPSec) & BGP](https://github.com/cynthiatreger/az-routing-guide-ep5-nva-routing-2-0) by Cynthia Treger
* [Azure Route Server](https://learn.microsoft.com/en-us/azure/route-server/overview) in Azure documentation

## Part 3 – Conclusion

In the last 3 posts of this series we covered a lot of topics related to Azure networking in the context of adopting a *Hub & Spokes* topology with an Azure VMware Solution deployment.

We created this mockup setup step-by-step to demonstrate the capabilities of some Azure products (like Azure Route Server) and features (like route propagation in UDRs).

In the last step we have a working setup with a central `hub-nva` VM able to route and filter traffic from/to the AVS environment, spokes vNets, and the on-premises resources.

> **Note**: the setup described in this post is not meant to be used in production due to the lack of high availability and redundancy of the components. It is just a mockup to demonstrate the capabilities of Azure networking products and features.

I hope you enjoyed this series and learned something new about Azure networking. There will probably be more posts to extend this series in the future with new topics and use cases like:

* High availability and redundancy of the components
* Dynamic routing with BGP between the `hub-nva` and the `avs-spoke-nva`

See you in the next posts!
