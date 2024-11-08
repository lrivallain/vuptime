---
title: VMware vCloud Director REST API with Terraform
date: "2024-11-08"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
tags:
- vmware
- api
- vcloud
- terraform
toc: true
thumbnail: /images/terraform-icon.svg
splash: /images/terraform-icon.svg
---

If you work with VMware vCloud Director (vCD) and Terraform regularly, you're likely familiar with the [vcd provider](https://registry.terraform.io/providers/vmware/vcd/latest) for interacting with the vCD API. This provider is an excellent tool for automating the deployment of vCD resources and managing the lifecycle of your virtual datacenters.

However, you may have noticed some limitations in the vcd provider, particularly when it comes to managing infrastructure components. To handle these components with Terraform, you will need to interact directly with the vCD REST API. In this post, I'll share how I approach this specific use case.

## Terraform providers

In this particular situation I use the following providers:

```tf
terraform {
  required_version = ">= 1.6"
  required_providers {
    vcd = {
      source  = "vmware/vcd"
    }
    restful = {
      source = "magodo/restful"
    }
  }
}
```

- The `vmware/vcd` provider is the official VMware provider for vCloud Director. We will use it to retrieve a `refresh token` that we will use to authenticate to the vCD API.
- The `magodo/restful` will provide a simple way to authenticate using the refresh token with *oauth2* and to run requests over the REST API of vCloud.

## Authentication process

### vCD provider configuration

With a set of variables to define URI, credentials, and other parameters, we can configure the vCD provider for the System Org.

```tf
# Configure the VMware Cloud Director Provider for the System Org
provider "vcd" {
  alias                = "vcd-sys"
  user                 = var.vcloud_admin_username
  password             = var.vcloud_admin_password
  auth_type            = "integrated"
  org                  = "System"
  url                  = "${var.vcloud_uri}/api"
  max_retry_timeout    = 30
  allow_unverified_ssl = var.vcloud_insecure
}
```

### Refresh token generation

`vmware/vcd` provider provides a `vcd_api_token` resource that allows you to create a `refresh token` that you can use to authenticate to the vCD API to generate a `bearer token`.

The `refresh_token` will be stored in a file to be reused by the next provider.

```tf
# Create a refresh token
resource "vcd_api_token" "vcd_sys" {
  provider         = vcd.vcd-sys
  name             = "vcd-sys"
  file_name        = ".vcd-sys-token.json"
  allow_token_file = true
}

# Load refresh token file
data "local_file" "vcd_sys_token" {
  filename = vcd_api_token.vcd_sys.file_name
}
```

### `restful` provider configuration

In this step, we will use the `magodo/restful` provider and specify the `refresh_token` information to configure a `oauth2.refresh_token` section.

I provided an alias name to this provider in order to be able to dissociate *sysadmin* tasks and *normal* users ones.

```tf
# Create a vcd provider with the refresh token
provider "restful" {
  alias    = "vcd-sys"
  base_url = var.vcloud_uri
  security = {
    oauth2 = {
      refresh_token = {
        token_url     = "${var.vcloud_uri}/oauth/provider/token"
        refresh_token = jsondecode(data.local_file.vcd_sys_token.content)["refresh_token"]
      }
    }
  }
  header = {
    "Accept"       = "*/*;version=${var.vcloud_api_version}",
    "Content-Type" = "application/json"
  }
  client  = {
    tls_insecure_skip_verify = var.vcloud_insecure
  }
}
```

## Objects management through the REST API

We can now use the above provider and the `restful_operation` resource to create objects by using the REST API, like the creation of a vCenter Server object to associate with the vCloud Director instance:

```tf
resource "restful_operation" "register_avs_vcenter" {
  provider = restful.vcd-sys
  path     = "/cloudapi/1.0.0/virtualCenters"
  method   = "POST"
  data     = jsonencode({
    "vcId" : null,
    "name" : "vCenter01",
    "description" : "vCenter01 resources",
    "username" : var.vcenter_username,
    "password" : var.vcenter_password,
    "url" : var.vcenter,
    "isEnabled" : true,
    "vsphereWebClientServerUrl" : null,
    "hasProxy" : false,
    "rootFolder" : null,
    "vcNoneNetwork" : null,
    "vcNoneNetworkMoref" : null,
    "tenantVisibleName" : null,
    "isConnected" : true,
    "mode" : "NONE",
    "listenerState" : "INITIAL",
    "clusterHealthStatus" : "GRAY",
    "vcVersion" : null,
    "buildNumber" : null,
    "uuid" : "${var.vcenter}/sdk",
    "nsxVManager" : null,
    "proxyConfigurationUrn" : null
  })
}
```

## Conclusion

The example above demonstrates a scenario where the `vmware/vcd` provider lacks the necessary functionality to manage certain objects. In such cases, the vCD REST API can be used to manage these objects and automate the deployment of vCD resources.

However, it's important to note that the vCD REST API is not as user-friendly as the `vmware/vcd` provider and does not provide sufficient abstraction for managing other lifecycle operations like updates and deletes without significant effort. Therefore, it is recommended to use the vCD REST API only when necessary and to rely on the `vmware/vcd` provider for most operations.