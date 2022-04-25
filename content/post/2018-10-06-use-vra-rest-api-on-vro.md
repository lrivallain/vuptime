---
author: aharlaut
author_name: Antoine Harlaut
categories:
- VMWare
date: "2018-10-06T00:00:00Z"
tags:
- vmware
- vra
- vro
- rest
- api
- endpoint
- javascript
title: Use the vRealize Automation REST API on vRealize Orchestrator
aliases: 
- /2018/10/06/use-vra-rest-api-on-vro/
toc: true
---

The vRealize Automation REST API can be used on vRealize Orchestrator directly with the ``vCACCAFE`` plugin, instead of using the ``HTTP-REST`` plugin, which can be much more simplier.


# Get the vRA REST endpoint

If you have already used the vRealize Automation REST API, you should have noticed that there is around twenty [endpoints](https://code.vmware.com/apis/39/vrealize-automation) ! 

On this article, we'll take the example of listing all the blueprints using vRO.

The REST API call to perform this operation is : 
```
https://vra-fqdn/composition-service/api/blueprints
```


Thereby the endpoint is ``composition service``.

# Find the vCAC endpoint

Once the vRealize Automation REST endpoint defined, you need to find it on the vCAC plugin.

With your favorite REST client ( like ``Postman`` ), perform the following REST call on your vRealize Automation server after being authenticated : 

    https://vra-fqdn/component-registry/endpoints?$filter=endPointType/protocol eq 'REST'&limit=9999


It will collect all the vRealize Automation REST endpoints.

On the result, locate your endpoint and get the ``typeId`` which is the endpoint name on the vCAC plugin.  
In this case, the vCAC endpoint found is  ``com.vmware.csp.core.cafe.catalog.requested.item.info.provider`` for the ``composition-service``.

```json
    {
      "@type": "EndPoint",
      "id": "ed42c762-1487-458a-bc33-b7efc285b426",
      "createdDate": null,
      "lastUpdated": null,
      "url": "https://my-vra-server/composition-service/api",
      "endPointType": {
        "typeId": "com.vmware.csp.core.cafe.catalog.requested.item.info.provider",
        "protocol": "REST"
      },
      "serviceInfoId": "b7d3fdea-4808-45d8-af95-cf3aac0c8259",
      "endPointAttributes": null,
      "sslTrusts": null
    },
```
Great ! The vCAC endpoint now found, you can use it directly on vRO.

# Using the vRA REST API on vRO

On vRealize Orchestrator, you can create a rest client with the [vCACCAFEHost](http://vroapi.com/Class/vCACCAFE/7.3.0/vCACCAFEHost)
 object and its method [createRestClient()](http://vroapi.com/Method/vCACCAFE/7.3.0/vCACCAFEHost/createRestClient) with the vCAC endpoint on the parameter.

You will be able to do some basic REST operations like [GET, POST and PUT](http://vroapi.com/Class/vCACCAFE/7.3.0/vCACCAFERestClient).

Here is the code to list all the blueprints defined on a vRA tenant : 

```javascript
/*
 * List all the blueprints defined on a tenant
 *
 * @param {vCACCAFEHost}   host  Targeted vCACAFE Host Tenant.
 *
*/

//Create the rest client for the targeted tenant
restClient = host.createRestClient("com.vmware.csp.core.cafe.catalog.requested.item.info.provider");

//List all the blueprints defined on the tenant
blueprints = restClient.get("/blueprints").getBodyAsJson();

//Display the name for each blueprint found
for each(var blueprint in blueprints){
    System.log("Blueprint found : "+blueprint.name);
}
```
