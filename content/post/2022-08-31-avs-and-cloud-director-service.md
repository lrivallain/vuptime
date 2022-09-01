---
author: lrivallain
author_name: Ludovic Rivallain
date: "2022-08-31"
thumbnail: /images/avs-cds/VMware_Cloud_Director_Icon.png
splash: /images/splash/otter-kier-in-sight.jpg
splash_credits: Photo by Kier In Sight on Unsplash
featureImage: /images/splash/otter-kier-in-sight.jpg
categories:
- VMware
- Azure
tags:
- vmware
- azure
- azure vmware solution
- avs
- vcloud director
- cds
toc: true
title: Public preview – Azure VMware Solution and VMware Cloud Director Service
---

## Introduction

[VMware Cloud Director Service](https://gateway.performance.vcd.cloud.vmware.com/cloud-director-instances/) (aka *CDS*) is a cloud service that provides a unified view of VMware based resources and multi-tenant support, allowing an IT administrator to split resources capacity between tenants. For tenant users, it provides a single pane of glass to manage all VMware-based, cloud resources, including virtual machines, storage, networks, and networks services.

> VMware Cloud Director Service is the SaaS version of the well known [VMware (v)Cloud Director](https://www.vmware.com/products/vcloud-director/).

Associated to [Azure VMware Solution](https://azure.microsoft.com/en-us/services/azure-vmware/) (aka *AVS*), a large part of the multi-tenants and self-service SDDC stack, is managed by the cloud providers:

* **VMware**: manage the CDS instance components (cells and service)
* **Microsoft** Azure: manage the AVS instance components (vCenter, vSphere, NSX-T, vSAN etc.)

{{% notice info "Azure Service terms" %}}
Cloud Director service (CDs) is now available to use with Azure VMware Solution under the Enterprise Agreement (EA) model only. It's not suitable for MSP / Hoster to resell Azure VMware Solution capacity to customers at this point. For more information, see [Azure Service terms](https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure/EAEAS#GeneralServiceTerms).
{{% /notice %}}

In this post, we will cover how the two solutions can be linked together in order to provide this *"fully-managed-vCloud-Director"* experience.

You can also refer to the following links to explore more about the AVS and CDS combination:

* [VMware's blog: Cloud Director Service Expanding Multi-Cloud Services on Azure VMware Solution](https://blogs.vmware.com/cloudprovider/2022/08/cloud-director-service-expanding-multi-cloud-services-on-azure-vmware-solution.html?utm_source=feedly&utm_medium=rss&utm_campaign=cloud-director-service-expanding-multi-cloud-services-on-azure-vmware-solution)
* [Azure update announcement](https://azure.microsoft.com/fr-fr/updates/public-preview-enterprise-vmware-cloud-director-service-for-azure-vmware-solution/)
* [Azure documentation](https://docs.microsoft.com/en-us/azure/azure-vmware/enable-vmware-cds-with-azure)

### High level design

![Multi-tenancy capabilities of AVS and CDS - High level design](/images/avs-cds/avs-cds-high-level-design.png)

The Azure documentation provides a [multi-tenant network design](https://docs.microsoft.com/en-us/azure/azure-vmware/enable-vmware-cds-with-azure).

### Prerequisites

#### Subscriptions

In the following post, we will assume that you already have subscriptions for the following services:

* [VMware Cloud](https://console.cloud.vmware.com/) organization
  * *Cloud Director Service* must be enabled for your VMware Cloud organization
* [Azure](https://portal.azure.com/) tenant and subscription(s)
  * At least on active [Azure VMware Solution](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.AVS%2FprivateClouds) deployment

#### Technical requirements

In Azure VMware Solution:

* An outbound internet connection is required
* A private IP address to deploy CDS proxy appliance (either DHCP or static one) with internet connectivity
* Working DNS resolution
* vCenter and NSX-T credentials

{{% notice warning "Warning" %}}
In the following post, default AVS-provided credentials will be used for the vCenter and NSX-T. Of course, for a production setup, we highly recommend to use service accounts for this purpose in order to limit the exposure of credentials and privileges.
{{% /notice %}}

#### Knowledge

As we will not cover the usage of Cloud Director Service, we will assume that you already have some basic knowledge of this product or its on-premise counterpart: [VMware Cloud Director](https://www.vmware.com/fr/products/cloud-director.html).

We will also assume that you already have some basic knowledge of the vCenter usage (at least to deploy an OVF template), and of the NSX-T usage (at least to create logical segments and to configure DNS and DHCP services).

## Create a CDS instance

For anyone who already deployed an on-premise instance of vCloud Director, the following deployment experience is a drastic change: by providing a name for the instance, a deployment region and a password, you can deploy a fully working Cloud Director instance and avoid the complexity of the on-premise deployment.

![Wizard to create a CDS instance](/images/avs-cds/create-cds-instance.png)

... about 12 minutes later:

![CDS instance was deployed in about 12 minutes](/images/avs-cds/cds-instance-fully-created.png)

## Interconnect your AVS instance

### Proxy Appliance

In order to provide connectivity for the CDS instance to the AVS vCenter and NSX-T manager, a reverse-proxy appliance is required.

Deployed on the AVS SDDC and using a outbound internet connection, the proxy appliance (aka *transporter* appliance) creates a secured tunnel with CDS services to provide connectivity up to the AVS management components.

![Proxy appliance connectivity](/images/avs-cds/avs-cds-proxy-appliance.png)

Once deployed, the proxy appliance will be autonomous to create the tunnel with the CDS instance.

### Generate an API token

In order to register a new reverse proxy, you need to create an API token with *"Network Administrator"* role. This token will be used by the reverse proxy to connect back to VMware Cloud deployments and provide connectivity between CDS and the AVS SDDC instances.

1. In [VMware Cloud Director service console](https://console.cloud.vmware.com), click on your user name and click *My Account*.
1. Select the API Tokens tab.
1. Click Generate a new API token.
1. Enter a meaningful name of the token and in Token TTL define for how long the token is valid.
1. Define the scopes for the token: *"Network Administrator"* is requested for the reverse proxy.

![Generate an API token for reverse proxy](/images/avs-cds/generate-new-api-token.png)

When created, copy the API token:

![Copy the generated API token](/images/avs-cds/generate-new-api-token-2.png)

### Generate and deploy the Reverse Proxy OVA

Back on the CDS instance, you can generate a reverse proxy OVA by clicking on `ACTIONS` menu and then on `Generate Reverse Proxy OVA`.

![Wizard for reverse-proxy OVA generation](/images/avs-cds/generate-vmware-reverse-proxy-ova.png)

When submitted, You can monitor the task status from instance's activity logs and when finished, select *view files* to download the generated OVA file.

![Click on view files to get access to the Reverse PRoxy OVA](/images/avs-cds/download-vmware-reverse-proxy-ova.png)

![Download Reverse PRoxy OVA file](/images/avs-cds/download-vmware-reverse-proxy-ova-2.png)

Then you can deploy it on the target vCenter server and provide the requested OVF environment properties, like appliance root password or IP address settings.

{{% notice info "Additional Proxy Targets" %}}
In order to allow the reverse proxy to connect to each component of the AVS instance (NSX-T manager, vCenter server, ESXi hosts), I suggest to consolidate the value of *Additional Proxy Targets* property with the management subnet of the AVS instance or at least, adding the /25 subnet of the hosts management IP addresses.
{{% /notice %}}

![Deploy Reverse PRoxy OVA file and provide requested OVF environment properties](/images/avs-cds/deploy-vmware-reverse-proxy-ova.png)

Power-on the VM and wait for the VMware tools to show up with the IP address details.

### Associate the AVS datacenter via the Reverse Proxy

From VMware cloud console, select your instance and click on *Associate a Datacenter via VMware Proxy* in the `ACTIONS` menu.

![Click on: Associate a Datacenter via VMware Proxy](/images/avs-cds/associate-sddc-0.png)

Provide the details of your AVS deployment:
![Provide details about AVS components](/images/avs-cds/associate-sddc-1.png)

Submit credentials:
![Provide credentials for AVS components](/images/avs-cds/associate-sddc-2.png)

Acknowledge costs and submit:
![Acknowledge costs](/images/avs-cds/associate-sddc-3.png)

Check the status of the task from *Activity Logs*.
![Successful association of a Datacenter via VMware Proxy](/images/avs-cds/associate-sddc-succeed.png)

## Deploy your workload on AVS by using CDS

When you AVS datacenter is properly associated with CDS, you can use CDS provider UI to deploy some workload.

Use `OPEN INSTANCE` button to access to the CDS provider UI.

### Check association AVS components

As CDS instance administrator, check the status of the association with AVS components:

![Check the status of the association of vCenter server](/images/avs-cds/check-association-vcenter.png)

![Check the status of the association of NSX-T Manager](/images/avs-cds/check-association-nsx.png)

{{% notice info "Inventory" %}}
*Hosts*, *Datastores* (vSAN one at least), *ResourcesPools* and *Storage Policies* will also be populated with the discovered information from AVS inventory.
{{% /notice %}}

### Provider's cloud resources

From this point, you can now create provider's cloud resources, like with any other (v)Cloud Director deployment:

* 1 or more, provider VDC
* 1 or more, external networks
* Pre-provision NSX-T T1 gateways if needed
* Provider's user accounts

### Create Organizations and associated resources

Like for provider's cloud resources, you can create organizations and associated resources:

* Organizations
* Organization's vDCs
* Quota definitions and storage policies
* Organization's networks
* Users and org settings

I recommend that you test the deployment of a VM (using catalog based clone or vSphere import) to validate the following:

* Network connectivity
* Storage policies
* Access to VM console

![Fully configured AVS Organization's VDC](/images/avs-cds/avs-based-org-vdc.png)

## Overview of CDS instance resources capacity and usage

From VMware cloud portal, you can now see the resources capacity and usage of your CDS instance:

![Overview of CDS instance resources and usage](/images/avs-cds/cds-instance-capacity-and-usage.png)

## Troubleshoot

### Support levels

VMware provide 4 levels of support for CDS instances:

* **Level 1**: As a service provider, only you have access to the VMware Cloud Director software. To receive technical support, collect logs and upload them to VMware Global Support Services for review and analysis. see How Do I Report a Problem.
* **Level 2**: VMware uses automated monitoring to review VMware Cloud Director operations for technical support purposes.
* **Level 3 (Recommended)**: VMware technical support personnel can access the VMware Cloud Director instance to provide support and maintenance.
* **Level 3 (Escalated VMware support)**: A larger number of VMware technical support personnel has access and can interact with the VMware Cloud Director instance to provide active support and maintenance.

You can easily switch between levels of support by clicking on the **Modify Cloud Director Instance support level** button in the CDS instance's **ACTIONS** menu.

### Generate CDS instance log bundles

As CDS instance administrator, you can generate log bundles to troubleshoot your CDS instance, using *Create Support Bundle* button in the CDS instance's **ACTIONS** menu.

From instance's details (or **Activity Logs**), you can download the generated log bundle:

![Download CDS instance log bundle](/images/avs-cds/download-cds-instance-log-bundle.png)

### Check the reverse proxy appliance status

To check the reverse proxy appliance status you can:

1. Run the following command by SSH on the appliance:

```bash
transporter-status.sh
```

2. or, remotly get the JSON content from reverse proxy API:

```bash
curl -s http://10.100.110.50:9082/actuator/health | jq .components.reverseProxyClient
```

```json
{
  "status": "UP",
  "details": {
    "server": "proxy-pre-intrepid.cds.cloud.vmware.com",
    "port": "443",
    "optionalIdentifier": "ebe11b93-f7f4-4b84-be4d-efe20f220594",
    "clientVersion": "ob-19852460",
    "clientId": "016b9cff-7789-4622-8a0c-b06371270a3c",
    "organizationId": "309d33bd-****-****-****-************",
    "networkName": "AVS-CSU-FR-LRI",
    "command_channel_1": "CONNECTED",
    "command_channel_2": "CONNECTED",
    "allowedTargets": {
      "10.100.100.2": "REACHABLE",
      "10.100.100.3": "REACHABLE",
      "10.100.101.0/25": "NOT_CHECKED_CIDR",
      "vc.970e82e4d*************.northeurope.avs.azure.com": "REACHABLE",
      "nsx.970e82e4d*************.northeurope.avs.azure.com": "REACHABLE"
    }
  }
}
```

### Check the reverse proxy appliance logs

You can check the reverse proxy appliance logs by SSH on the appliance:

```bash
transporter-logs.sh -f
```

You can also filter on error and warning messages with: `-e` and `-w` flags:

```bash
transporter-logs.sh -e # Will grep for errors
transporter-logs.sh -w # Will grep for warnings
```

### Change a value of OVF properties

If you want to change a value of OVF properties, you can:

* Shutdown the proxy/transporter appliance VM
* Go to VM *Configure* tab
* Then *vApp Options*
* Select the property to edit and click on *Set Value*
* Validate change and start the VM

The on-boot script will fetch OVF's new values and update the deployed proxy services accordingly.

## Conclusion

The combination of Azure VMware Solution with VMware Cloud Service, is a powerful tool to provide a self-service experience for end users to consume VMware based resources.

With the *reverse proxy* concept, it is possible to link VMware SDDC deployment in a private network with the SaaS version of vCloud Director. This IaaS & SaaS deployment model, delegates management responsibility to both VMware and Microsoft Azure but provides the same UI experience for both vCD administrator and end users.

### Acknowledgment

Thanks a lot [@Timo](https://twitter.com/tsugliani) for the great help and support provided when testing this deployment.

### Credits

Title photo by <a href="https://unsplash.com/@kierinsight?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Kier In Sight</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
