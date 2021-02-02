---
layout: post
title: VMware - Dive into OVF properties
author: lrivallain
category: VMware
tags: script linux vmware ovf customization
---

In order to fully configure a virtual machine after a clone of OVF deployment, it may be useful to use settings from virtualization layer in the guest OS: for example to run [Guest OS customization](/2014/08/15/vmware-use-guestinfo-variables-to-customize-guest-os) as already discussed in this blog.

Today, we will focus on OVF properties.

* Table of contents
{:toc}

# Presentation of OVF properties

If you deploy some VM through OVF/OVA files, you are probably already familiar with OVF settings. They appear as the possibility to customize VM settings during the deployment process:

{% include lightbox.html src="/images/dive_into_ovf/ovf_properties_deploy.png" title="OVF properties deploy" %}

Typical OVF properties include: Network settings (IP address, netmask, gateway...), users configuration (username, password). As properties are not restrictives, it is possible to create custom keys to manage any other kind of customization.

OVF properties are a part of the full OVF environment encapsulating a VM deployment process and to use it inside of a VM, some scripting is necessary.

## Representation of OVF properties

XML representation of an OVF environment configuration can be retrieved in a guest OS by 2 ways:
* As a CD-ROM drive containing the XML document
* VMware Tools in the ``guestinfo.ovfEnv`` variable

Here is an example of OVF environment of a VM with customized properties:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Environment
     xmlns="http://schemas.dmtf.org/ovf/environment/1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:oe="http://schemas.dmtf.org/ovf/environment/1"
     xmlns:ve="http://www.vmware.com/schema/ovfenv"
     oe:id=""
     ve:vCenterId="vm-94765">
   <PlatformSection>
      <Kind>VMware ESXi</Kind>
      <Version>6.0.0</Version>
      <Vendor>VMware, Inc.</Vendor>
      <Locale>en_US</Locale>
   </PlatformSection>
   <PropertySection>
         <Property oe:key="dns_servers"   oe:value="10.11.12.,10.11.12.2"/>
         <Property oe:key="gateway"       oe:value="10.11.12.254"/>
         <Property oe:key="ip_address"    oe:value="10.11.12.13"/>
         <Property oe:key="netmask"       oe:value="255.255.255.0"/>
         <Property oe:key="hostname"      oe:value="myvmame"/>
         <Property oe:key="root_password" oe:value="somepassword"/>
         <Property oe:key="search_domain" oe:value="lri.ovh"/>
   </PropertySection>
   <ve:EthernetAdapterSection>
      <ve:Adapter ve:mac="00:50:56:99:c0:4c" ve:network="NestedLabs" ve:unitNumber="7"/>
   </ve:EthernetAdapterSection>
</Environment>
```

``PropertySection`` contains the list of OVF properties that can be used to customize a guest OS.

# Create new properties

When you create a new template for OVF export, it is possible to create/edit/delete custom OVF properties.

From vSphere Web client -> Edit Settings of a VM -> vApp Options: In Authoring section, it is possible to give a name/version/url to describe your future OVF and to manage properties:

{% include lightbox.html src="/images/dive_into_ovf/ovf_properties_edition.png" title="OVF properties edition" %}

In the edition/creation wizard, the most useful fields are:
* **Label**: How is named the parameter when user is prompted to fill its value
* **KeyID**: How is named the parameter in the XML file
* **Category**: a way to order parts of the customization form fields by grouping properties together
* **Description**: to give more information about the purpose of the field to end users

{% include lightbox.html src="/images/dive_into_ovf/ovf_properties_fields.png" title="OVF properties fields" %}

It is possible to choose between 2 types of properties:
* **Static propertie**: Values will be configured by user or will be fixed by the default ones.
* **Dynamic propertie**: Values will be set according to the virtualization layer information (ex: getting IP from an IP Pool attached to a PortGroup.)

Then you can choose between sub-types:
* String
* Password
* Integer
* Real
* Boolean
* (external) IP address
* ...

{% include lightbox.html src="/images/dive_into_ovf/ovf_properties_subtypes.png" title="OVF properties sub-types" %}

You can also set default value, or some requirements (like the minimal/maximal length of a string):

{% include lightbox.html src="/images/dive_into_ovf/ovf_properties_options.png" title="OVF properties options" %}

# Edit VM properties values

As we saw previously, a user deploying an OVF coming from export of VM where properties are set, will be prompted to fill the values of the properties.

it is also possible to edit properties values of an already deployed VM: From vSphere Web client -> Edit Settings of a VM -> vApp Options.

{% include lightbox.html src="/images/dive_into_ovf/ovf_values_edition.png" title="OVF properties values edition on VM" %}

In this case, you may have to run 'again' some GuestOS glue code to take the change into account.

# Get OVF properties from the guestOS

When you configure an OVF environment, you can choose between CD-ROM and VMware-tools methods to transport information into the virtual machine:

{% include lightbox.html src="/images/dive_into_ovf/ovf_transport_method.png" title="OVF transport method" %}

## VMware tools

If you choose ``VMware tools`` transport method for OVF environment, according to the used OS type, the method to retrieve properties can vary a bit. Here are two samples to get the XML representation.

On **Windows**:

```bash
"C:\Program Files\VMware\VMware Tools\VMwareService.exe" -cmd "info-get guestinfo.ovfEnv"
```

On **Linux**:

```bash
/usr/bin/vmtoolsd --cmd 'info-get guestinfo.ovfEnv'
```

## ISO image

If you choose ``ISO image`` transport method for OVF environment, you need to :

1. mount the CD-ROM drive to your guest OS
2. read the ``ovf-env.xml`` file

## Properties usage

Here is a very simple Python helper to deal with the XML blob from OVF environment to export properties:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This script retrieves information from guestInfo.ovfEnv and
    print the OVF properties.
"""

import subprocess
from xml.dom.minidom import parseString
from pprint import pprint

ovfenv_cmd="/usr/bin/vmtoolsd --cmd 'info-get guestinfo.ovfEnv'"

def get_ovf_properties():
    """
        Return a dict of OVF properties in the ovfenv
    """
    properties = {}
    xml_parts = subprocess.Popen(ovfenv_cmd, shell=True,
                                 stdout=subprocess.PIPE).stdout.read()
    raw_data = parseString(xml_parts)
    for property in raw_data.getElementsByTagName('Property'):
        key, value = [ property.attributes['oe:key'].value,
                       property.attributes['oe:value'].value ]
        properties[key] = value
    return properties

properties = get_ovf_properties()
pprint(properties, indent=1, width=80)
```

From here, it is pretty simple to customize the guest OS. For example, to change the root password based on ``root_password`` properties:

```python
chpasswd_cmd = "/usr/sbin/chpasswd"

def change_linux_password(user, new_password):
    """
        Change linux password for a user
    """
    print("Setting new password for %s" % user)
    sp = subprocess.Popen([chpasswd_cmd],
                          stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    sp.communicate(input='%s:%s' % (user, new_password))
    sp.wait()
    if sp.returncode != 0:
        print("Failed to set new password for %s" % user)

change_linux_password('root', properties['root_password'])
```

# Conclusion

Now you are ready to produce OVF appliances with customization on deployment. This can be very useful to easily script the deployment of many VM instances or to provide a 'ready-to-deploy' appliances to customers.

Full script for the customization of the guestOS can be found here: [get-ovfenv.py](https://gist.github.com/lrivallain/77d9dda42bf77ddce1fc3bf2ee69e37a)
