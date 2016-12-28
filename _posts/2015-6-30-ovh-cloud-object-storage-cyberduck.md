---
layout: post
title: OVH Cloud - Object Storage with cyberduck
category: Cloud
tags: cloud cyberduck object ovh public storage swift
---

> "_**Object Storage** (also known as object-based storage<sup id="cite_ref-1" class="reference">[](https://en.wikipedia.org/wiki/Object_storage#cite_note-1)</sup>) is a storage architecture that manages data as objects, as opposed to other storage architectures like [file systems](https://en.wikipedia.org/wiki/File_systems "File systems") which manage data as a file hierarchy and [block storage](https://en.wikipedia.org/wiki/Block_storage "Block storage") which manages data as blocks within sectors and tracks._" <sub>_Source: [**Wikipedia-en**](https://en.wikipedia.org/wiki/Object_storage)_</sub>

[ovh.com](https://ovh.com/cloud/ "OVH.com - cloud offers") has been providing for a few weeks, an offer on it's public cloud to manage Object-Storage. A very good way to store many things:

* Backup with private containers
* Static content for web site pictures
* Shared content for large binaries download
* ...

You can use many ways to push/get file on the object-storage as the OVH manager, the Openstack's Horizon Manager or a swift compatible client:

![OVH.com Cloud Object Storage Schema]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_00.png "OVH.com Cloud Object Storage Schema")© OVH.com

Here, I'll show how to use the provided swift API with Cyberduck (download it at: [cyberduck.io](https://cyberduck.io/ "CyberDuck")) to manage your uploaded files from your macOS or windows desk.

# Create your container

First thing to do, is to create an OVH account, then, go to the manager: [https://www.ovh.com/manager/cloud/](https://www.ovh.com/manager/cloud/ "Manager - cloud"). Now you can create your first storage container. A container is an entity where a "public/static/private" policy can be applied.

Example, for a backup container, we chose a private type policy.

![Create a container]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_01.png "Create a container")

![Create a container]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_02.png "Create a container")

Now it should be displayed on container list. You can push file through the manager, but it's not an easy way to daily manage files on your new storage location.

# Create your credentials

Now you need to create credentials in order to connect through a swift client. It'll also provide access to Horizon, an Openstack manager.

Click on "_Openstack_" tab on Manager and create a new user:

![Create an user]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_03.png "Create an user")

You only need to provide a description as username and password are randomly generated:

![Enter a description]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_04.png "Enter a description")

Then you have to remember credentials as it the only time you'll be able to see it:

![Note credentials]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_05.png "Note credentials")

## Get other informations

From that point, you should be able to join the Horizon manager for next step:

![Click on link to join horizon manager]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_06.png "Click on link to join horizon manager")

And log-in with credentials created previously:

![Log-in]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_11.png "Log-in")

In "_Access&Security_" tab, select the "_API Access_" and download the OpenStack RC file:

![Openstack RC file download]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_08.png "Openstack RC file download")

In the downloaded file you will need:

*   the OS_AUTH_URL : [https://auth.cloud.ovh.net/v2.0](https://auth.cloud.ovh.net/v2.0 "Auth URL")
*   the OS_TENANT_ID
*   the OS_USERNAME = = the username previously created

Now you can open Cyberduck :-)

# Connect with cyberduck

On cyberduck, select a new connection with "swift" type and enter :

*   URL => [https://auth.cloud.ovh.net/v2.0](https://auth.cloud.ovh.net/v2.0 "Auth URL")
*   Username => OS_TENANT_ID : OS_USERNAME _(do not forget the ":" sign between both informations)_
*   Prompted password => the password of the OS_USERNAME

![Cyberduck settings]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_09.png "Cyberduck settings")

## Push a file

Once you are connected you can download and push file easily :

![Push a file]({{ site.baseurl }}/images/swift_ovhcloud/swift_ovhcloud_10.png "Push a file")

Great, your first file is pushed on the OVH public cloud !
