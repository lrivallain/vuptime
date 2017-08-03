---
layout: post
title: VMware - Explore vCloud Director catalog publishing feature
category: VMware
tags: vmware curl catalog vcloud vcd
---

VMware introduced in version 5.5 of vCloud Director, a feature to externaly expose catalogs and if necessary, to subscribe to an externaly exposed one.

This is useful to synchronize catalog between two (or more) vCloud Director instances.

* Table of contents
{:toc}

# Basic usage

The two following sections are extracts from the [VMware documentation about VCD Catalogs](http://pubs.vmware.com/vcd-820/index.jsp#com.vmware.vcloud.admin.doc/GUID-1A098021-07C4-44BA-AB9D-9D48FD4CA812.html).

## Publish a Catalog to an External Organization

You can publish a catalog externally to make its vApp templates and media files available for subscription by organizations outside the vCloud Director installation.

1. Enable external catalog publishing for the organization
2. Click Catalog and select My Organization's Catalogs in the left pane.
3. On the Catalogs tab, right-click the catalog name and select Publish Settings.
4. On the External Publishing tab, select Enabled and supply a password for the catalog feed.

The subscription URL is provided and can be shared with external organizations for subscription.

## Subscribe to an External Catalog Feed

1. Click Catalogs and select My Organization's Catalogs in the left pane.
1. Click Add Catalog and type a name and optional description for the catalog feed.
1. Select Subscribe to an external catalog and click Next.
1. Select the type of storage to use for this catalog feed and click Next.
1. Add other members if necessary
1. Review the catalog feed settings and click Finish.

# Exploring the catalog content

Previous section are describing trivial usage of Externaly shared catalogs on vCloud Director. The following will explore the catalog content and how to retrieve Metadata or data of catalog from outside a vCloud Director environment.

## What is behind the shared URI

Let see what is available through the given subscription link:

```bash
curl -s -u :MyPassword  \
	https://moncloud.enfrance.net/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d
```
```json
{
  "vcspVersion" : "1",
  "version" : "3",
  "id" : "urn:uuid:4c8f39ca-b7ef-4bac-acf4-c377401a729d",
  "name" : "Catalogue France",
  "description" : "Catalog items from France Cloud",
  "created" : "2017-07-19T15:18:52.923Z",
  "itemType" : "vcsp.CatalogItem",
  "itemsHref" : "items",
  "capabilities" : {
    "transferIn" : [ "httpGet" ],
    "transferOut" : [ "httpGet" ],
    "generateIds" : true
  },
  "metadata" : [ ]
}
```

> **Note:** `-u` option is used to pass authentification informations to the HTTP request header. As we do not set any user, the credentials only contains password, following the ":" separator.

> **Note:** `-s` option make culr mute the progress or error messages. Remove it to see potential error for debuging.


This request give us metadata about the catalog : name, description, version... And `itemsHref` give us clue to continue exploration and list the catalog items.

## List items

```bash
curl -s -u :MyPassword  \
	https://moncloud.enfrance.net/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d/items
```
```json
  "itemType" : "vcsp.CatalogItem",
  "items" : [ {
    "vcspVersion" : "1",
    "version" : "1",
    "id" : "urn:uuid:46713c7b-3f72-472d-bb4e-97122b99e884",
    "name" : "Puppet-Debian9x64",
    "created" : "2017-07-19T15:20:41.470Z",
    "description" : "Debian 9 for x64 with puppet pre-configuration",
    "type" : "vcsp.ovf",
    "files" : [ {
      "name" : "descriptor.ovf",
      "etag" : "95ad8688-4b1b-419f-aa34-50bcf0e5c395",
      "size" : 12302,
      "hrefs" : [ "/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d/item/46713c7b-3f72-472d-bb4e-97122b99e884/file/descriptor.ovf" ]
    }, {
      "name" : "descriptor.mf",
      "etag" : "95ad8688-4b1b-419f-aa34-50bcf0e5c395",
      "size" : 163,
      "hrefs" : [ "/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d/item/46713c7b-3f72-472d-bb4e-97122b99e884/file/descriptor.mf" ]
    }, {
      "name" : "vm-3453bb14-5093-4c6a-ac64-4f41e4380ec6-disk-0.vmdk",
      "etag" : "95ad8688-4b1b-419f-aa34-50bcf0e5c395",
      "size" : 976322048,
      "hrefs" : [ "/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d/item/46713c7b-3f72-472d-bb4e-97122b99e884/file/vm-3453bb14-5093-4c6a-ac64-4f41e4380ec6-disk-0.vmdk" ]
    } ],
    "properties" : {
    },
    "selfHref" : "/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d/item/46713c7b-3f72-472d-bb4e-97122b99e884/",
    "metadata" : [ {
      "type" : "STRING",
      "domain" : "SYSTEM",
      "key" : "vapp.origin.id",
      "value" : "fc98dff4-3239-433d-be71-6756c11c5db8",
      "visibility" : "READONLY"
    }, {
      "type" : "STRING",
      "domain" : "SYSTEM",
      "key" : "vapp.origin.name",
      "value" : "Puppet-Debian9x64",
      "visibility" : "READONLY"
    }, {
      "type" : "STRING",
      "domain" : "SYSTEM",
      "key" : "vapp.origin.type",
      "value" : "com.vmware.vcloud.entity.vapptemplate",
      "visibility" : "READONLY"
    } ],
    "vms" : [ {
      "name" : "puppet-debian9x64",
      "metadata" : [ ]
    } ]
  } ],
  "version" : "3"
}
```

This part of the catalog is much more interesting as it shows us informations about its content. There are also pointer to download the files corresponding to the catalog's files, including vAPP.

## Download files from catalog

So if we need to download the OVF file (for example):

```bash
curl -s -i -u :MyPassword  \
	https://moncloud.enfrance.net/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d/item/83f573cd-e5ab-442e-a585-53b6e2c5e820/file/descriptor.ovf
HTTP/1.1 302 Found
Date: Tue, 01 Aug 2017 14:37:22 GMT
X-VMWARE-VCLOUD-REQUEST-ID: 000000000000000000000000000000000000001
Content-Language: en-US
Location: https://moncloud.enfrance.net/transfer/0474fbe8-5ebe-4d69-ae27-790fae40c9d9/descriptor.ovf
Content-Length: 0
...
```
> **Note:** `-i` option is used to include the HTTP response headers in the output.

Oups, it's a `302` redirect so we need to follow redirect. 2 choices:
* You adapt the request with the `Location` path from the HTTP response header
* You add `-L` option to curl to follow redirects

```bash
curl -s -L -u :MyPassword  \
	https://moncloud.enfrance.net/vcsp/lib/4c8f39ca-b7ef-4bac-acf4-c377401a729d/item/83f573cd-e5ab-442e-a585-53b6e2c5e820/file/descriptor.ovf > myVapp/descriptor.ovf
```

> **Note:** `-L` option is used to make curl follow a redirect.

And you can proceed similarly for the other files for each VM of the vApp:
* descriptor.mf
* disk-\*.vmdk

Now you can explore VCD externaly published catalogs, from outside of a vCloud Director user interface. As it's possible to download catalog content, it's possible to imagine synchronization of the catalog on other product as a raw vCenter+vSphere environment.
