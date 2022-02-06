---
author: lrivallain
categories:
- VMware
- Azure
date: "2022-02-06"
splash: /images/splash/azure-rod-long.jpg
splash_credits: Rod Long @ unsplash.com
tags:
- vmware
- azure
- azure vmware solution
- avs
- api
- postman
toc: true
thumbnail: /images/avs-api/postman-collection.png
title: "Azure VMware Solutions REST API - part 1: Postman collection"
aliases:
- /2022/01/06/azure-vmware-solution-rest-api-part1/
featureImage: /images/splash/azure-rod-long.jpg
---

Working on Azure VMware Solution since a couple of months now, I found very usefull to have a prepared list of API calls on a notebook or quick-reference document.

After a period of time, I did collect enought sample to consider doing a full [Postman](https://www.postman.com/) collection and by doing that, I was also considering to cover the complete [Azure VMware REST API](https://docs.microsoft.com/en-us/rest/api/avs/) (and not only the parts that I already used).

## The Postman collection

I can find a complete Postman collection to use AVS REST API in the following GitHub repository: [Azure VMware Solution REST API Postman collection](https://github.com/lrivallain/avs-rest-api-postman-collection) `avs-rest-api-postman-collection.json`.

This repository also contains an *environment example* you could use to populate your API calls: `avs-rest-api-postman_environment.json`.

With the AVS REST API you could easly the following parts of you AVS deployment:

* The SDDC itself
  * Credentials
  * Endpoints
* The *Express Route* authorizations
* *Global Reach* connections
* Clusters
  * Datastores
  * Virtual machines grouping
  * Placement policies
* Addons
* AVS scripts
* HCX
* Quota and Trial availability
* Workload networks:
  * DHCP
  * DNS
  * Segments
  * Public IPs
  * Port mirroring
  * Gateways (NSX-T Tiers 1)
  * Virtual Machine grouping
* Other AVS clouds links

> This collection does not cover the VMware side of the API available when deploying an AVS cluster. If you need to use VMware products REST APIs, the documentation and endpoints are the same ones than with on-prem SDDC products. It is another benefit of using VMware managed-products instances: You do not change your habits and your existing automation tooling.

### Collection import

From Postman, web or desktop client, you could import the collection by refering to the following link: [https://raw.githubusercontent.com/lrivallain/avs-rest-api-postman-collection/master/avs-rest-api-postman-collection.json](https://raw.githubusercontent.com/lrivallain/avs-rest-api-postman-collection/master/avs-rest-api-postman-collection.json).

You may also need to import the *environment* sample to populate your own data: [https://github.com/lrivallain/avs-rest-api-postman-collection/raw/master/avs-rest-api-postman_environment.json](https://github.com/lrivallain/avs-rest-api-postman-collection/raw/master/avs-rest-api-postman_environment.json).

### Login

In order to use the collection, you will have to enter some information like:

* subscription ID: `subscriptionId`
* resource-group name: `resourceGroupName`
* authorization token: `resourceGroupName`

The easiest way to get an authentication token is by using [Azure Command-Line Interface](https://docs.microsoft.com/en-us/cli/azure/):

```bash
az account get-access-token --subscription 01010101-0101-0101-0101-010101010101
```

You can pick the `accessToken` value returned or use `jq` to only get this value:

```bash
az account get-access-token --subscription 01010101-0101-0101-0101-010101010101 | jq ".accessToken"
```

Eventually, use the value in the `accessToken` section of your environment.

> The token generated with `get-access-token` is valid for only one hour. For other token generation methods you can refer to the [Azure documentation](https://docs.microsoft.com/en-us/rest/api/azure/#register-your-client-application-with-azure-ad).

#### Setup `accessToken` for all API calls

Sadly in the export/import process of Postman collection, a variable used for authentication is lost and needs to be set manually:

![Set the token value to a variable reference](/images/avs-api/authentication-configuration.png)

**Procedure**:

1. Click on the collection name
2. On the right pane, select the *current token/access token* field
3. Enter: `{{accessToken}}` to reference your token variable
4. Save and quit this tab

> This has to be done only once when you import the collection. When you will generate a new access-token, this variable will remain and map to the updated token value.

### Testing

You can now test the collection by listing the AVS deployments in your subscription:

![List AVS SDDC](/images/avs-api/list-avs-sddc.png)


## Conclusion

Even if this collection covers the 100% of the current AVS REST API (version 2021-12-01), the official reference documentation remains the one from the Azure docs website: [Azure VMware REST API](https://docs.microsoft.com/en-us/rest/api/avs/) which contains **much more documentation** to explain the content of each request and response. I strongly encourage everyone to have a look to this documentation before using the Postman collection.

In the next post, we will review some examples of the AVS REST API by using a very useful tool: `az rest`.

### Credits

Title photo by [Rod Long](https://unsplash.com/@rodlong) on [Unsplash](https://unsplash.com/photos/vpOeXr5wmR4)