---
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
date: "2020-10-20T00:00:00Z"
tags:
- easyvirt
- dcscope
- greenit
thumbnail: /images/dcscope74/dcscope-logo.png
title: Easyvirt – DCScope 7.4 – Green IT Beta feature
aliases: 
- /2020/10/20/Easyvirt-DCScope-74-GreenIT/
---

With some french vMUG members, we add the opportunity to assist to a demonstration of the new features of [**DC Scope**](https://www.easyvirt.com/en/dcscope-operations-management/) 7.4 from the French company: [**Easyvirt**](https://www.easyvirt.com/en/).

Thanks a lot to [@MartinDargent](https://twitter.com/martindargent) for this invitation and the nice demo.

## Green IT (*Beta*)

The major new feature in the new 7.4 version it the addition of a new **Green IT** tab (still in Beta). This new capability of DC Scope can be linked to the initial purpose of DC Scope to avoid wasting resources by monitoring the consumption of VMware ESXi servers, providing recommendation and estimating the future behaviour. Now, users can also monitor the green-efficiency of their DataCenter and Desktop stock.

By making a partnership with [**Quantis**](https://quantis-intl.com/) (a leading sustainability and [**LCA** (*Life Cycle Assessment*)](https://en.wikipedia.org/wiki/Life-cycle_assessment) Swiss consultancy), is now able to provide back the DC administrators, reliable metrics about:

* [Embodied energy](https://en.wikipedia.org/wiki/Embodied_energy): raw-material production, manufacture, transport, distribution, use and disposal.
* Energy consumption over time (that was already collected for both servers and per-VM)

{{< figure src="/images/dcscope74/dcscope01.png" title="Green IT Dashboard" >}}

This new dashboard provide multiples informations about:

* **Green IT score:** a score calculated based on the level of details you provide to configure the Green IT tab. You can easily increase this score by declaring your server, network, desktop, storage components details.
* **Carbon footprint evolution**: An overview of the evolution of booth grey energy (estimated over time) and the measured consumption of DC components.
* **Information about VM**: Evolution over time of the per-VM energy consumption.
* **kWh evolution**: Electrical consumption over time.

This tab also provides an **energy-efficiency** score per server with both theoretical (*TEE*) and measured (*CEE*) one.

{{< figure src="/images/dcscope74/dcscope02.png" title="energy-efficiency score" >}}

**Energy optimization** suggestions are also available to estimate the electric consumption impact if you remove some servers from the current infrastructure.

{{< figure src="/images/dcscope74/dcscope03.png" title="Energy optimization" >}}

Last but not least, it is also possible to simulate the replacement of existing servers versus new ones by estimating:

* Cost
* Per year CO² impact
* Estimated future number of VMs
* TEE (Theoretical Energy Efficiency)
* The cost per VM of the replacement

{{< figure src="/images/dcscope74/dcscope04.png" title="Replacement simulator" >}}

## Conclusion

As we globally said to Martin, this new tab is a great thing in order to make our infrastructures *green-er* or to understand the *grey energy* impact of some components replacement.

The shortcoming of the current implementation of the feature is the complexity involved in the some settings of DC configuration to improve the *Green IT score*: PUE and CO² efficiency of a datacenter could be complicated to determine in some context (on-premise, multi-sites etc.).

As it is still a *Beta* feature, I am confident that Easyvirt will find way to improve this part of the admin-experience in a near future: by the way, they are looking for feedback to evolve this feature.
