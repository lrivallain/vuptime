---
layout: post
title: Extending VMware vCloud Director functionalities
category: VMware
author: lrivallain
tags: vmware vcloud director vcd python rabbitmq extension sii opensource
thumb: /images/lumext-for-vcd/preview_userlisting.png
---

This post is the English translation of the one published on [blog.groupe-sii.com](https://blog.groupe-sii.com/etendre-les-capacites-du-portail-vmware-vcloud-director/) to present a new kind of development activities in SII Group: the extension of the *VMware vCloud Director* portal.

The post will explain the concept that enables the extension of this VMware product to add new functionalities to the native portal and to provide a consistent user experience to final customers.

## Introduction to VMware vCloud Director

VMware vCloud Director is a quite common reference in virtualized infrastructures, especially for *Service Providers* (for mutualized cloud hosting) or major companies with sizable infrastructure.

Its concept is based on a simplified view, targeting VM users, to consume IaaS (*Infrastructure-as-a-Service*) resources with tenant or service-based restrictions.

Natively, vCloud Director (vCD) interface is an overlay of other VMware's product as vCenter/vSphere, et NSX-V (for *Software-Defined Networking*) and its features are limited to the consumption of VM, storage and network resources (both *L2* & *L3*).

## VMware vCloud Director extensions

Since the 9.1 version ([2018, march](https://docs.vmware.com/en/vCloud-Director/9.1/rn/rel_notes_vcloud_director_91.html)), vCloud Director cames with an extensibility feature. This allows to the platform administrator to extend the features perimeter.

Indeed, through a dedicated development, it is possible to create the technical context to execute the automation linked to new features to add to the vCD portal (UI, API, backend, third party interconnect...).

> **Example** : Provide to end-users a [support-ticketing-interface integrated to the vCD portal](https://github.com/vmware/vcd-ext-sdk/tree/master/ui/samples/ticketing).

The publication perimeter for a custom extension can be set according to the plateform needs and the extension. So it is possible to publish it for:

* Platform system administrators
* Customer's organizations with, at choice:
  * All organizations at the same time
  * Only some selected organizations

{% include lightbox.html src="/images/lumext-for-vcd/vcd_extensionpublish.png" title="Example of the choice for extension's publication" %}

### Extend vCD's UI

Probably the most obvious benefit of the extensibility feature of vCloud Director is the capacity to integrate in a single user interface (*UI*), new sections to give access to added features.

This includes the addition of a customized item in the main navigation menu:

{% include lightbox.html src="/images/lumext-for-vcd/vcd_extensionmenu.png" title="Example of navigation menu extension" %}

It also includes the ability to add custom pages to display the content of extension(s). As those pages are loaded inside the vCD UI, it is recommended to reuse style and components of the native interface to offer an unified user experience (*UX*).

As vCD uses the open-source [Clarity](https://clarity.design/) framework, mainly developed by VMware, for the HTML5 interface, it is possible to reuse its components (**Angular**), styles and best practices.

### Extend vCD's API

A second possibility offer by the extensibility kit of vCloud Director is to extend the perimeter of URI allowed in the vCloud API. With this API extension, it is now possible to use a standard vCloud API path (`https://<vcloudserver>/api/`) to request information and actions for an extension.

Let's take an example:

> Our `coffee` extension aims to provide a feature to create *coffee machine* order through vCD portal.
>
> Requests sent to  vCloud API at this path : `https://<vcloudserver>/api/coffee/order` and for instance, a `POST` request type (and its appropriate parameters) will start a new order to the coffee machine. A `GET` request will list the previous commands etc.

To handle the extension related customized requests, a backend server is necessary. This server can be hosted on a dedicated host (or the vCD server (*cell*) but not recommended) and can be written in any language of your choice (Python, Java, Node etc.). Messages received by vCD on the extension path (`coffee`) will be forwarded to an intermediate RabbitMQ server to be consumed by the extension backend. Once the request content is processed, response content is sent to the AMQP server and consumed by vCD to provide an answer.

For our example:

{% include lightbox.html src="/images/lumext-for-vcd/architecture_overview.png" title="Used paths for requests on Coffee extension" %}

1. The user initiates a request (through the UI or directly through the exposed API extension).
1. vCD compiles this request to an AMQP message with an extension-specific routing key fro the RabbitMQ server.
1. The Extension's backend server can consume the message, make appropriate pre-checks (rights management, pre-requisites, open external connections etc.)
1. One or many API requests are sent to the *coffee machine* to create the order.
1. The *Coffee machine* answers with appropriate data: Ex: *"Order preparation in progress"* or the list of previous orders.
1. Extension's backend server process the data from the *Coffee machine* (formatting, selection of items etc.) and is able to sent back the answer to initial vCD message through a dedicated queue (known from `reply-to` field in initial AMQP message).
1. vCD can now consume the answer from RabbitMQ and use the content as a response from the API call initiated by the user.

### Extensibility kit of vCloud Director

To help the development of vCD's extensions, VMware provides a *SDK* that contains:

* Minimal code for a UI extension ([*vcd-plugin-seed*](https://github.com/vmware/vcd-ext-sdk/tree/master/ui/vcd-plugin-seed)).
* Some simple [extensions samples](https://github.com/vmware/vcd-ext-sdk/tree/master/ui/samples):
  * *About page*: no API
  * *Ticketing*: Extension to create and display support tickets with a non-persistent API in Python.

## Practical implementation from SII Group: LUMExt

As the *coffee machine* is purely fictitious (even if it could be very useful ☺️), but the need for extensions in vCloud Director is not lacking.

At SII Group, we had chosen to develop an interface to manage LDAP based users trough the vCloud Director portal.

### Présentation

Natively, vCloud Director supports the authentication from both local and LDAP based users. Sadly, for LDAP based users, it is not possible to edit user's information or to create new one from vCD. Only attachment to an organization is possible.

If you are a *Service Provider* hosting customers that do not want to manage their own LDAP server to create users for vCD access, but aim to use  a single source of authentication for multiple usages (vCD, VM's OS etc.): a mutualized LDAP server can be a useful service.

**LUMExt** (**L**DAP **U**ser **M**anagement **Ext**ension for vCloud Director) aims to provide a vCD-integrated management of LDAP-based users.

Once a user is created in the LDAP server, it is possible to associate it with an organization and a role to allow its connection to the vCD portal.

### API

This extension API is based on a Python script `lumext` that initiates a new applicative *thread* for each request from the AMQP queue. In the benefits of using per-request Python *thread*, we can mention:

* Processing of multiples requests at the same time
* The process of a request does not affect the process of other request (current or future ones), even in case of error.

To consume and publish (*consumer/publisher* roles) messages with AMQP protocol, we use the [`Kombu`](https://pypi.org/project/kombu/) Python package as it turns out to be very reliable and to provide easy support for *thread* usage.

> **Note :** VMware's examples use the [`Pika`](https://pypi.org/project/pika/) module for the same kind of usage.

We also have developed a *MessageWorker* named [`VcdExtMessageWorker`](https://pypi.org/project/VcdExtMessageWorker/) to start business-related threads. These extension-*threads* represent the potential complexity of the feature to add to vCD (applicative workflow, data analysis, third party requests, etc.). *MessageWorker* is generic and can be attached to other kind of extension-threads for other kind of purposes.

In the case of **LUMExt**, `VcdExtMessageWorker` initiates a new thread of *lumext worker* for each request. This one is in charge of the request-analysis (is it a listing request or a user-creation one, user-edition ?). Once the request is processed, the answer is published to the `reply-to` queue of the RabbitMQ server and consumed by vCD.

REST API extension provides the following paths to the users:

* `/api` : root of vCD APIs (native)
  * `/api/{org_id}` : root of an organization (native)
    * `/api/{org_id}/lumext` : root of the extension (lumext)
      * `/api/{org_id}/lumext/user` : (lumext)
        * `GET` : list users
        * `POST` : create user
        * `/api/{org_id}/lumext/user/{login}` : (lumext)
          * `DELETE` : delete current user
          * `PUT` : edit current user

Same API is available for both organization's administrators to setup automation tools (to create users, for example) and for the UI that fully relies on this API to access data.

Finally, the usage of AMQP protocol, *stateless threads* and our *MessageWorker* based on Kombu allows to horizontally scale our extension backend to multiple nodes if necessary (to ensure high availability or load balancing).

### UI

The **LUMExt** user interface is fully integrated to the vCD portal and is based on the same UI components (*Angular*) and the same graphic charter (based on open-source [Clarity](https://clarity.design/) framework from VMware).

The main navigation menu is supplemented with a new link to access to the **LUMExt** pages.

{% include lightbox.html src="/images/lumext-for-vcd/preview_menu.png" title="Main navigation menu" %}

By default, LDAP based users list is displayed:

{% include lightbox.html src="/images/lumext-for-vcd/preview_userlisting.png" title="LUMExt, users list" %}

In the following screenshot, it is interesting to notice that only the middle part is developed for the extension. Navigation menu on top and tasks list on the bottom are vCD natives (and cannot be modified).

{% include lightbox.html src="/images/lumext-for-vcd/preview_userlisting_zoning_en.png" title="LUMExt, users list - Zoning" %}

To create a new user, some form fields are requested:

* Login
* Name
* Password (customized or client-side generated with minimal security requirements)
* Password confirmation
* Description (optional)

The data are sent to the backend and store in the LDAP server in appropriate directory fields.

{% include lightbox.html src="/images/lumext-for-vcd/preview_usercreation.png" title="LUMExt, user creation" %}

**LUMExt** UI also provides user edition and user deletion and a specific wizard for password reset operation.

> **Note :** LDAP based groups support is intended but not yet developed.

## Conclusion

**LUMExt** is an internal SII project that we "opensource" (MIT license) on [github](https://github.com/groupe-sii/lumext) to demonstrate the extensibility abilities of vCloud Director with a technical and complete use-case.

Since about 6 months, our teams have working on these kind of *plugins*  development for our customers to extend the available features of the vCD portal with tools for their customers (as *"Service Provider"*).

It is also a great example of the combined work of developers and infrastrucure engineering in our teams, when, in computer science history, both jobs are more and more linked together.

Illustration credits go to:

* Applications-ristretto.svg - [Sebastian Kraft - GPL](https://commons.wikimedia.org/wiki/File:Applications-ristretto.svg)
* RRZE-icon-set - [Regional Computing Centre of Erlangen (RRZE) - CC-by-sa/3.0](https://github.com/RRZE-PP/rrze-icon-set/)
* Screenshots from LUMExt are SII group own work
