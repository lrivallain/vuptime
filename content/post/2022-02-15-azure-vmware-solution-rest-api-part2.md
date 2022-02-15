---
author: lrivallain
categories:
- VMware
- Azure
date: "2022-02-15"
splash: /images/splash/laptop-joshua-reddekopp.jpg
splash_credits: Rod Long @ unsplash.com
tags:
- vmware
- azure
- azure vmware solution
- avs
- api
- rest
toc: true
thumbnail: /images/avs-api/thumb_endpoint.png
title: "Azure VMware Solutions REST API - part 2: `az rest`"
aliases:
- /2022/01/15/azure-vmware-solution-rest-api-part2/
featureImage: /images/splash/laptop-joshua-reddekopp.jpg
---

After a discovery of Azure VMware Solution REST API through the [Postman collection](/2022/01/06/azure-vmware-solution-rest-api-part1/) in *part 1*, we will use some of the fundamentals API calls through `az rest`, a useful subset of the [Azure Command-Line Interface](https://docs.microsoft.com/en-us/cli/azure/).


Compared to Postman, I consider `az rest` an easier way to discover Azure REST API in a blog post as it doesn't require to post screenshots or long code samples to narrate the exploration. But of course, you could use the [AVS Postman collection](https://github.com/lrivallain/avs-rest-api-postman-collection) to achieve the same purpose or any other REST client tool (httpie, curl etc.): this is the great power of REST APIs.

## Preparation

A big benefit of using `az rest` to manage an Azure product, like Azure VMware Solution, through its REST API is that the tool already manages the authentication or provide a simple way to connect to your tenant and to execute request without manually providing authentication tokens.

### Login

If you have not already logged-in to your tenant, you can follow the next steps:

```bash
az login

# Or, if you manage multiple tenants, you can add the --tenant parameter to login to it:
az login --tenant xxxxxxxxxxx.onmicrosoft.com
```

By default, this command will open a web browser asking you to connect to your azure tenant. Once logged-in your browser, you can close the tab and the CLI will successfully be connected.

If your terminal session cannot connect to a web browser (if you use a remote session like SSH for example), you can use:

```bash
az login --use-device-code
# To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code ********** to authenticate.
```

After opening the [provided link](https://microsoft.com/devicelogin) and used the token, your CLI should be connected.

You can check your connection information with:

```bash
az account show --output table

EnvironmentName    HomeTenantId                          IsDefault    Name                          State    TenantId
-----------------  ------------------------------------  -----------  ----------------------------  -------  ------------------------------------
AzureCloud         ********-****-****-****-************  True         Azure VMware Solutions Tests  Enabled  ********-****-****-****-************
```

### Subscription

If you use multiple subscriptions (it is recommended!), you can select to one hosting your AVS:

```bash
# List available subscriptions
az account subscription list --output table

# Select one subscription
az account set --subscription ********-****-****-****-************
```

### SDDC base URI

To achieve quick and successfully REST requests on a specific resource, it could be useful to get its *base URI* and to store it in an environment variable.

For an AVS resource, this base URI is built like:

`https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCEGROUP_NAME}/providers/Microsoft.AVS/privateClouds/${SDDC_NAME}`

With the following components:

* `https://management.azure.com`: The Azure REST API domain endpoint
* `/subscriptions/${SUBSCRIPTION_ID}`
* `resourceGroups/${RESOURCEGROUP_NAME}`
* `/providers/Microsoft.AVS`: A pointer to the AVS resources provider
* `/privateClouds/${SDDC_NAME}`

With the following commands, you can easily populate an AVS base URI:

```bash
export SUBSCRIPTION_ID="********-****-****-****-************"
export RESOURCEGROUP_NAME="resourceGroupName"
export SDDC_NAME="AVS-Tests"
export SDDC_BASE_URI="https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCEGROUP_NAME}/providers/Microsoft.AVS/privateClouds/${SDDC_NAME}"
```

### API version

When using Azure API, you need to specify the API version you want to use. For AVS, I currently use version *2021-12-01* (the last version currently available):

```bash
export API_VERSION="api-version=2021-12-01"
```

## AVS endpoints and credentials management

When you need to connect to an AVS system, you need two mandatory information:

* The endpoints name
* The credentials to use

The endpoints can be retrieved from ([Doc.](https://docs.microsoft.com/en-us/rest/api/avs/private-clouds/get)):

```bash
# The global information about the AVS deployment:
az rest -m get -u "${SDDC_BASE_URI}?${API_VERSION}"

# A filtered result from the previous request:
az rest -m get -u "${SDDC_BASE_URI}?${API_VERSION}" | jq ".properties.endpoints"
{
  "hcxCloudManager": "https://10.100.100.9/",
  "nsxtManager": "https://10.100.100.3/",
  "vcsa": "https://10.100.100.2/"
}
```

And credentials ([Doc.](https://docs.microsoft.com/en-us/rest/api/avs/private-clouds/list-admin-credentials)):

```bash
az rest -m post -u "${SDDC_BASE_URI}/listAdminCredentials?${API_VERSION}"
{
  "nsxtPassword": "***************",
  "nsxtUsername": "admin",
  "vcenterPassword": "***************",
  "vcenterUsername": "cloudadmin@vsphere.local"
}
```

> Please note that you must use the `post` HTTP method to get credentials.

With this information, you can now connect to your AVS instance.

## AVS network management

Some parts of an AVS workload management can be made through the Azure API and portal (in replacement or addition to the VMware products API or UI).

### NSX-T Tier1 gateway

When dealing with NSX-T based networks, the Tier1 gateway (T1 GW) is an important element to consider.

In a vast majority of scenarios (including the AVS deployment model), the T1 GW is considered the first router component, accessible from a workload to communicate with network items out of its subnet.

By default, a first T1 GW is deployed with AVS and you can retrieve details about it by using ([Doc.](https://docs.microsoft.com/en-us/rest/api/avs/workload-networks/get-gateway)):

```bash
az rest -m get -u "${SDDC_BASE_URI}/workloadNetworks/default/gateways?${API_VERSION}"
```

> Note: Only a `get` method is available as you cannot Create, Update or Delete T1 gateways through the Azure API/UI: actions on T1 GW are only available from NSX-T itself (including creating new GWs).


### DHCP service

It is possible to rely on the T1 GW to provide DHCP leases within network segment. The DHCP service can run as a *server* or a *relay* from another server.

The simpliest role to configure is the *server* one:

```bash
# Prepare data for the request
server_name="DHCPServer"
body=$(cat <<EOF
{
  "properties": {
    "displayName": "${DHCPServer}",
    "revision": 0,
    "dhcpType": "SERVER",
    "serverAddress": "10.100.104.1/24",
    "leaseTime":null
  }
}
EOF
)

# Create the DHCP service
az rest -m put -u "${SDDC_BASE_URI}/workloadNetworks/default/dhcpConfigurations/${DHCPServer}?${API_VERSION}" --body "${body}"
```

### NSX-T Segments

For example, you can Create, Read, Update or Delete ([C.R.U.D.](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)) **NSX-T segments** with the Azure API:

```bash
# Prepare data for the request
segment_name="VM-tests-109" # Name of segment to create
t1_gw_name="TNTXX-T1" # T1 GW name
body=$(cat <<EOF
{
  "properties": {
    "displayName": "${segment_name}",
    "connectedGateway": "${t1_gw_name}",
    "subnet": {
      "dhcpRanges": [
        "10.100.109.10-10.100.109.100"
      ],
      "gatewayAddress": "10.100.109.1/24"
    },
    "revision": 0
  }
}
EOF
)

# Create segment
az rest -m put -u "${SDDC_BASE_URI}/workloadNetworks/default/segments/${segment_name}?${API_VERSION}" --body "${body}"

# Get the new segment
az rest -m get -u "${SDDC_BASE_URI}/workloadNetworks/default/segments/${segment_name}?${API_VERSION}"

# Output
{
  "id": "/subscriptions/********-****-****-****-************/resourceGroups/resourceGroupName/providers/Microsoft.AVS/privateClouds/AVS-Tests/workloadNetworks/default/segments/VM-tests-109",
  "name": "VM-tests-109",
  "properties": {
    "connectedGateway": "TNTXX-T1",
    "displayName": "VM-tests-109",
    "provisioningState": "Fulfilled",
    "revision": 0,
    "status": "IN_PROGRESS",
    "subnet": {
      "dhcpRanges": [
        "10.100.109.10-10.100.109.100"
      ],
      "gatewayAddress": "10.100.109.1/24"
    }
  },
  "resourceGroup": "resourceGroupName",
  "type": "Microsoft.AVS/privateClouds/workloadNetworks/segments"
}
```

## AVS interconnectivity management

When your AVS instance is deployed, you will certainly need to connect it with external components like other Azure Resources, jump servers, on-premises resources etc.

I will not cover [all the available AVS interconnectivity solutions](https://docs.microsoft.com/en-us/azure/azure-vmware/concepts-networking) in this post but here is a list of supported ones:

* [Azure vNet connect](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-network-manage-subnet)
* [ExpressRoute](https://docs.microsoft.com/en-us/azure/expressroute/expressroute-introduction)
* [ExpressRoute Global Reach](https://docs.microsoft.com/en-us/azure/expressroute/expressroute-global-reach)

In this post, we will see how-to setup an *ExpressRoute* circuit.

### ExpressRoute

The first information to collect is the *ExpressRoute ID* or *Circuit ID*:

```bash
az rest -m get -u "${SDDC_BASE_URI}?${API_VERSION}" | jq ".properties.circuit"

# Output
{
  "expressRouteID": "/subscriptions/********-****-****-****-************/resourceGroups/resourceGroupName/providers/Microsoft.Network/expressRouteCircuits/tntxx-cust-p02-westeurope-er",
  "expressRoutePrivatePeeringID": "/subscriptions/********-****-****-****-************/resourceGroups/resourceGroupName/providers/Microsoft.Network/expressRouteCircuits/tntxx-cust-p02-westeurope-er/peerings/AzurePrivatePeering",
  "primarySubnet": "10.100.100.232/30",
  "secondarySubnet": "10.100.100.236/30"
}
```

We keep only the `expressRouteID` information to create a new *ExpressRoute* *authorization key*:

```bash
connection_name="expressroute-test" # name the future authorization key
sddc_er_id=$(az rest -m get -u "${SDDC_BASE_URI}?${API_VERSION}" | jq ".properties.circuit.expressRouteID") # store the expressRouteID
body=$(cat <<EOF
{
  "properties": {
    "expressRouteId": ${sddc_er_id}
  }
}
EOF
)

az rest -m put -u "${SDDC_BASE_URI}/authorizations/${connection_name}?${API_VERSION}" --body "${body}"

# Output
{
  "id": "/subscriptions/********-****-****-****-************/resourceGroups/resourceGroupName/providers/Microsoft.AVS/privateClouds/AVS-CSU-FR-LRI/authorizations/expressroute-test",
  "name": "expressroute-test",
  "properties": {
    "expressRouteAuthorizationId": "/subscriptions/********-****-****-****-************/resourceGroups/tntxx-cust-p02-westeurope/providers/Microsoft.Network/expressRouteCircuits/tntxx-cust-p02-westeurope-er/authorizations/avs_resource_expressroute-test",
    "expressRouteAuthorizationKey": "d502f9cb-91a2-4069-a474-7363e723bccc",
    "expressRouteId": "/subscriptions/********-****-****-****-************/resourceGroups/tntxx-cust-p02-westeurope/providers/Microsoft.Network/expressRouteCircuits/tntxx-cust-p02-westeurope-er",
    "provisioningState": "Succeeded"
  },
  "resourceGroup": "AVS-CSU-FR-LRI",
  "type": "Microsoft.AVS/privateClouds/authorizations"
}
```

![AVS ExpressRoute authorization from the Azure portal](/images/avs-api/expressroute-authorizations.png)

This will provide you with an authorization key: `expressRouteAuthorizationKey` to be used to create a new connection from an expressRoute compatible component, like a *Virtual network gateway*:

![Create an ExpressRoute connection to your AVS](/images/avs-api/expressroute-connection.png)

## Conclusion

As you may understand from the [AVS API reference](https://docs.microsoft.com/en-us/rest/api/avs/) or the [AVS Postman collection](https://github.com/lrivallain/avs-rest-api-postman-collection), this post is not a complete coverage of the AVS REST API capabilities but an example of what you can do with it and the `az rest` CLI tool.

To simplify the above commands, I did not mention any header like `Accept` or `Content-Type` as we used the default type of data when dealing with requests and answers: `application/json`.

Using API with `az rest` is a very easy way to manage automation of an AVS deployed instance with an [imperative approach](https://en.wikipedia.org/wiki/Imperative_programming). A [declarative approach](https://en.wikipedia.org/wiki/Declarative_programming) may be preferred to managed large AVS workloads with production and self-remediation requirements and I will try to cover it in a future (not-yet-planned) post.

### Credits

Title photo by [Joshua Reddekopp](https://unsplash.com/@joshuaryanphotog) on [Unsplash](https://unsplash.com/photos/GkFQEOubrCo)