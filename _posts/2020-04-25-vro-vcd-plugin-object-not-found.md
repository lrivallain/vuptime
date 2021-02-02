---
layout: post
title: Object notfound in vRO using the vCloud Director plugin
category: VMware
author: aharlaut
tags: vmware vcloud director vro plugin javascript connector api rest
thumb: /images/vro-vcd-object-notfound/vro_inventory_vcd.png
---

A strange behavior has happened just after vRO installation and vCloud director plugin configuration, I wasn't able to interact with any objects managed by the vcloud director plugin.

I created a simple workflow on my lab to illustrate the issue.

The workflow cannot be more basic as it has only a single line of code to display the name of the *vcloud:organization* object provided on the input.

{% include lightbox.html src="/images/vro-vcd-object-notfound/start_workflow_to_get_org_name.png" title="Display organization" %}

{% include lightbox.html src="/images/vro-vcd-object-notfound/result_workflow_to_get_org_name.png" title="Display organization name" %}

This simple workflow cannot display the organization name even if I respected the documentation. The attribut *name* should be present on a object of type : *vcloud:organization*

{% include lightbox.html src="/images/vro-vcd-object-notfound/api_doc_vcloud_organization.png" title="vcloud:organization-doc" %}

So I tryied to display the object *vcloud:organization* to be sure that the object is correctly fetched.

{% include lightbox.html src="/images/vro-vcd-object-notfound/result_workflow_to_get_org.png" title="Display organization" %}

vRO was not even able to display the *vcloud:organization* object itself and I was facing the same kind of issue for the organization-vdcs and the virtual machines objects. That's weird. Espacially when the vcloud inventory seems to work.

{% include lightbox.html src="/images/vro-vcd-object-notfound/vro_inventory_vcd.png" title="Display organization" %}

I struggled to fix to issue, I registered the vcloud director connector, change the API versions, reinstall the vcloud director plugin, change to version of the plugin, nothing works.

I checked the vcloud director configuration and I found on the *public addresses* tab that the *HTTP base URL* attribut was different than the *HTTP Rest API base URL*. It was prefixed by *api-*.

{% include lightbox.html src="/images/vro-vcd-object-notfound/vcloud_director_public_addresses.png" title="public_addresses" %}

Remember that the *HTTP Rest API base URL* are used to change the base URL on the REST API (obvious) and can be different that the *HTTP base UR*L:

{% include lightbox.html src="/images/vro-vcd-object-notfound/vcd_api_results.png" title="public_addresses" %}

I registered the vcloud director on vRO using the *HTTP base URL* but not with the API one.

So I reconfigured the connector, try again the workflow and magic happens. I'm now able to fetch the organization and display it's name :

{% include lightbox.html src="/images/vro-vcd-object-notfound/result_workflow_to_get_org_successful.png" title="Display organization" %}

{% include lightbox.html src="/images/vro-vcd-object-notfound/result_workflow_to_get_org_name_successful.png" title="Display organization name" %}

vRO was probably trying to get the organization by building it's href (*https://vcd.lab65.local/org.ea1bc7eb-d39c-48b5-acd2-2c3a78990567*) using the connector URL but was not able to get it as it was registered on the inventory with the API base URL (*https://api-vcd.lab65.local/org.ea1bc7eb-d39c-48b5-acd2-2c3a78990567*) as displayed on the vcd plugin inventory.

{% include lightbox.html src="/images/vro-vcd-object-notfound/vro_inventory_vcd_api_2.png" title="Display organization name" %}

I had also to troubleshoot the same kind of issue on an another platform, even if the HTTP base URL was the same that the API one. The first letter of the API base URL was in capital letter instead of the HTTP base URL that was not. A small difference probably due a wrong copy-paste that had a huge impact on the platform.

Hope it helps.
