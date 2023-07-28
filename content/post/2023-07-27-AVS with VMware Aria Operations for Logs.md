---
title: "Azure VMware Solution integration with VMware Aria Operations for Logs Cloud service"
date: "2023-07-27"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
- Azure
tags:
- vmware
- azure
- azure vmware solution
- vmware cloud
- logs
- eventhub
toc: true
thumbnail: /images/avs-aria-logs/arialogs-avs.png
---

VMware Aria Operations for Logs (formerly vRealize Log Insight and vRealize Log Insight Cloud) is a log management solution that provides visibility across physical, virtual, and cloud environments. It enables you to search and analyze logs in real time, and it provides a scalable platform for managing log data. VMware Aria Operations for Logs can be deployed on-premises or in the cloud. The cloud version is a SaaS offering that is hosted and managed by VMware.

In the following post we will see how to collect logs from Azure VMware Solution (AVS), leverage on Azure Event Hub to forward the logs to the VMware Aria Operations for Logs Cloud Service.

## Prerequisites

In order to proceed with the following steps, you will need the following:

* An Azure VMware Solution SDDC deployed in your Azure Subscription
* A VMware Cloud Services account with the VMware Aria Operations for Logs service enabled

We will also need to create a few resources in Azure:

* An *Event Hub Namespace*
* An *Event Hub* to receive and forward the logs
* Two *Event Hub Authorization Rules*
  * 1 to allow AVS SDDC diagnostic log forwarded to sent logs to the Event Hub
  * 1 to allow an Azure Function to listen to event hub messages and to send logs to the VMware Aria Operations for Logs Cloud Service

### Example of Terraform code to create the Event Hub Namespace, Event Hub

```terraform
resource "azurerm_eventhub_namespace" "eventhubnamespace" {
  name                = "${var.sddc_name}-eventhubnamespace"
  resource_group_name = azurerm_resource_group.avs_rg.name
  location            = var.sddc_location
  sku                 = "Standard"
  capacity            = 1
}

# Authorization Rule to allow AVS SDDC diagnostic log forwarded to sent logs to the Event Hub
resource "azurerm_eventhub_namespace_authorization_rule" "eventhubnamespace-authorization-rule" {
  name                = "${var.sddc_name}-authorization-rule"
  namespace_name      = azurerm_eventhub_namespace.eventhubnamespace.name
  resource_group_name = azurerm_resource_group.avs_rg.name

  listen = false
  send   = true # AVS SDDC diagnostic log forwarded to sent logs to the Event Hub
  manage = false
}
```

### Example of Terraform code to create Authorization Rules

```terraform
# Authorization Rule to allow an Azure Function to listen to event hub messages and
#  to send logs to the VMware Aria Operations for Logs Cloud Service
resource "azurerm_eventhub_namespace_authorization_rule" "eventhubnamespace-af-authorization-rule" {
  name                = "af-authorization-rule"
  namespace_name      = azurerm_eventhub_namespace.eventhubnamespace.name
  resource_group_name = azurerm_resource_group.avs_rg.name

  listen = true # Azure Function will listen to event hub messages
  send   = false
  manage = false
}

resource "azurerm_eventhub" "eventhub" {
  name                = "${var.sddc_name}-eventhub"
  resource_group_name = azurerm_resource_group.avs_rg.name
  namespace_name      = azurerm_eventhub_namespace.eventhubnamespace.name
  partition_count     = 2
  message_retention   = 1
}
```

## Azure VMware Solution SDDC Diagnostic Logs

In order to forward the logs from the Azure VMware Solution SDDC to the Event Hub, we will leverage on the Azure Diagnostic Settings.

From Azure Portal: *Azure VMware Solution > SDDCs > Select your SDDC > Diagnostic Settings*

Then we select the logs we want to forward, the event hub namespace, the event hub and the *send* authorization rule we created earlier.

![Azure VMware Solution SDDC Diagnostic Settings](/images/avs-aria-logs/avs-diagnostic-settings.png)

When saved, we can go to the next step: preparing VMware Aria Operations for Logs Cloud Service.

## Configuration of VMware Aria Operations for Logs Cloud Service

In VMware Aria Operations for Logs Cloud Service, generate API Key from here [mgmt.cloud.vmware.com/li/api-keys/keys](https://www.mgmt.cloud.vmware.com/li/api-keys/keys).

![VMware Aria Operations for Logs Cloud Service API Keys](/images/avs-aria-logs/aria-create-api-key.png)

Once created, copy the `API URL` and `API Token` to a temporary location, we will need them later.

## Deploy Azure Function

In order to forward the logs from the Event Hub to the VMware Aria Operations for Logs Cloud Service, we will leverage on an Azure Function to listen incoming messages in the hub and forwarding to the Aria service.

A sample Azure Function is provided by VMware here: [github.com/vmware/vmware-log-collectors-for-public-cloud/blob/master/azure/](https://github.com/vmware/vmware-log-collectors-for-public-cloud/blob/master/azure/) and can be easily deployed by using this template:

[![](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fvmware%2Fvmware-log-collectors-for-public-cloud%2Fmaster%2Fazure%2Fdeployments%2FeventHub%2Fazure-template-existing-eventhub.json)

In the configuration process, provide the `API URL` and `API Token` generated earlier:

![Azure Function Configuration::picture-border](/images/avs-aria-logs/azure-functions-configure-deployment.png)

### Post Deployment configuration of Azure Function

When the function has been created, you need to setup the Event Hub connection string as a configuration of the Azure Function.

1. To get Event Hub connection string ([created earlier](#example-of-terraform-code-to-create-authorization-rules)) from Azure Portal:  `*Event Hub Namespace > Shared access policies > your-eventhubnamespace-af-authorization-rule > Connection string-primary key*`
2. Then go to the deployed function App to set new environment variable : `*Function App > Configuration > New application setting*` and add the connection string as a new application setting:
    * Name: `AzureEventHubLogsConnectionString`
    * Value: `<Event Hub connection string>`
3. Save the configuration

![Add new application setting with event hub connection string::picture-border](/images/avs-aria-logs/azure-function-app-settings.png)

4. When saved, open the function and go to the *Integrations* tab

![Azure Function Integration tab::picture-border](/images/avs-aria-logs/azure-function-integrations.png)

5. Select the Event Hub Trigger and select the `Azure Event Hubs` trigger to edit it.
6. Select the `AzureEventHubLogsConnectionString` connection string from the `Event Hub Connection` drop-down menu and update the `Event Hub name` in the appropriate field.

![Azure Function Event Hub Trigger parameters::picture-border](/images/avs-aria-logs/af-trigger-event-hub-name.png)

7. Save the configuration


## Log analysis in VMware Aria Operations for Logs Cloud Service

At this point, the logs from the Azure VMware Solution SDDC should be forwarded to the VMware Aria Operations for Logs Cloud Service.

I will not cover the features of the VMware Aria Operations for Logs Cloud Service in this post, but you can find more information here: [vmware.com/products/aria-operations-for-logs.html](https://www.vmware.com/products/aria-operations-for-logs.html). Instead, I will just highlight some filtering capabilities to help you to find the logs from the Azure VMware Solution SDDC.

### Azure VMware Solution content pack

The Azure VMware Solution content pack is a pre-built VMware Aria Operations for Logs content pack that provides a set of dashboards and queries to help you to analyze the logs from the Azure VMware Solution SDDC. It also provides a big set of new *extracted fields* to help you to filter the logs.

![List of dashboard in the Azure VMware Solution content pack](/images/avs-aria-logs/ContentPack_AVS.png)

### Filtering logs from a specific Azure VMware Solution SDDC

If you are running multiple Azure VMware Solution SDDCs, you can filter the logs from a specific SDDC by using the `resourceId` field.

![Filter logs on resourceId](/images/avs-aria-logs/filter-logs-on-resourceId.png)

### Filtering fields

The following fields can also be very effective to optimize a log search:

| Field name     | Example            | Description |
|----------------|--------------------|------------ |
| appname        | *vpxd*             | The name of the application that generated the log message. |
| category       | *vmwaresyslog*     | The category of the log message selected in AVS troubleshooting pane. |
| event_provider | *AZURE_AVS*        | The provider of the log message. |
| eventsource    | *PRIVATECLOUDS*    | The source of the log message. |
| hostname       | *vc*               | The name of the host that generated the log message. Could be ESXi, vCSA, NSX-T hostnames. |
| location       | *southafricanorth* | The Azure region where the SDDC is deployed. |
| severity       | *info*             | The severity of the log message. |

### Dashboards

Dashboards can also be very useful to visualize the logs from Azure VMware Solution SDDCs.

You can use pre-built dashboards from the *Azure VMware Solution* content packs to monitor:

* NSX-T Application events
* Firewall events
* General AVS events
* Events by severity

Or you can create custom dashboard to visualize logs for specific needs:

![Example of Azure VMware Solution SDDC Dashboard in VMware Aria Operations for Logs](/images/avs-aria-logs/CustomDashboards.png)

### Explore logs

With the log exploration feature of VMware Aria Operations for Logs, you can easily search for specific logs and visualize them in a table or in a chart.

In this example, we are looking for the last logs for snapshots creation tasks.

![Explore logs in VMware Aria Operations for Logs](/images/avs-aria-logs/lookup-for-snapshot-logs.png)

You can also use the *Live tail* feature to monitor the logs in real time.

![Live tail in VMware Aria Operations for Logs](/images/avs-aria-logs/LiveLogsTail.png)
