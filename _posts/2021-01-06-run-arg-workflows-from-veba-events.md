---
layout: post
title: Run Argo workflow from a VEBA event through OpenFaaS
category: VMware
author: lrivallain
tags: vmware veba kubernetes event-driven argo openfaas
thumb: /images/argo/argo-wheel.logo.png
---

I recently made posts about the [VMware Event Broker](https://vmweventbroker.io/) (aka VEBA) to explain basic on-boarding in the *FaaS* and *Event-Driven* worlds.

As you may have noticed, the FaaS concept is perfect for use-case where the automation will be:

* Stateless
* Fast running
* No latency sensitive
* Responsible of a single thing
* Deterministic

> BTW, there is a nice list of FaaS Best Practices on the VEBA documentation: [Writing your own functions](https://vmweventbroker.io/kb/contribute-functions).

When you need to break one (or more) of the above rules, it may be necessary to rely on other kinds of automation, like **Workflows**.

In the following post, I will demonstrate how it is possible to forward VEBA events to a very powerful Workflow engine named [**Argo**](https://argoproj.github.io) to run, for example:

* long-running automation
* multi steps automation
* stateful functions
* retry-able functions

This work relies on an OpenFaaS function: [veba-to-argo-fn](https://github.com/lrivallain/openfaas-fn/tree/master/veba-to-argo-fn).

## How does it works ##

This OpenFaaS function is a simple *forwarder* (or *proxy*) to execute a pre-definied [Worklow Template](https://argoproj.github.io/argo/workflow-templates/) by providing the incoming cloud-event as an input parameter of the Workflow excecution.

![VEBA to Argo](/images/argo/veba-to-argo-fn.png)

### Pre-requisites

You need:

* A deployed VEBA instance (appliance based or K8S based): [How-to on vUptime blog](https://vuptime.io/2020/12/17/vmware-event-broker-0.5.0-on-k8s-first-steps/#openfaas-deployment)
* A deployed OpenFaaS instance (+`faas-cli`)
* A deployed Argo instance (+`argo` cli): [Quick Start](https://argoproj.github.io/argo/quick-start/)

A clone of the below repository:

```bash
git clone https://github.com/lrivallain/openfaas-fn.git
cd openfaas-fn/veba-to-argo-fn
```

## Deploy the Argo *echoer* template WF

```bash
argo template create echoer-argowf.yaml
argo template list

# Expected output
NAME
echoer
```

> This `echoer` workflow template is a very simple workflow that just repeats the incoming data in its stdin (logs).

## Configure the function

### Argo config secret

Copy and customize the `argoconfig.example.yaml` file:

```bash
cp argoconfig.example.yaml argoconfig.yaml
```

```yaml
argoserver:
  server: argo.vlab.lcl
  protocol: http
  namespace: argo
  serviceaccount: argo-svc
  template: echoer
  event_param_name: message
  labels:
    through: openfaas
    coming-from: veba
    foo: bar
```

Deploy this configuration file as a new *faas* secret.

```bash
faas-cli secret create argoconfig --from-file=argoconfig.yaml
faas-cli secret list

# Expected output
NAME
argoconfig
```

### `stack.yaml`

Edit the `stack.yaml` according to your needs:

```yaml
version: 1.0
provider:
  name: openfaas
  gateway: http://openfaas.vlab.local
functions:
  veba-to-argo-echoer:
    lang: python3
    handler: ./handler
    image: lrivallain/veba-to-argo
    environment:
      write_debug: true
      read_debug: true
    secrets:
      - argoconfig
    annotations:
      topic: VmCreatedEvent, VmClonedEvent, VmRegisteredEvent, DrsVmPoweredOnEvent, VmPoweredOnEvent
```

Now we need to pull the OpenFaaS language template for the specified lang in our stack.yml file:

```bash
faas template store pull python3
```

## Deploy the function

```bash
faas-cli deploy -f stack.yaml
faas-cli list

# Expected output
Function                        Invocations     Replicas
veba-to-argo-echoer            0               1
```

### Test

You can also check the function from the UI and do a first test by running:

```bash
echo '{"id": "test", "source": "sourcetest", "subject": "any", "data": {}}' \
  | faas-cli invoke veba-to-argo-echoer
```

This should produce an excecution of a Worklow based on the echoer template in Argo.

### Results

```bash
argo get @latest

# Expected output

Name:                echoer-7ldps
Namespace:           argo
ServiceAccount:      argo-svc
Status:              Succeeded
Conditions:
 Completed           True
Created:             Wed Jan 06 09:56:19 +0000 (44 seconds from now)
Started:             Wed Jan 06 09:56:19 +0000 (44 seconds from now)
Finished:            Wed Jan 06 09:56:22 +0000 (47 seconds from now)
Duration:            3 seconds
ResourcesDuration:   1s*(100Mi memory),1s*(1 cpu)
Parameters:
  message:           {"id": "test", "source": "sourcetest", "subject": "any", "data": {}}

STEP             TEMPLATE     PODNAME       DURATION  MESSAGE
 ✔ echoer-7ldps  echoer/echo  echoer-7ldps  26s
```

And in the logs:

```bash
argo logs @latest

# Expected output
echoer-7ldps: {"id": "test", "source": "sourcetest", "subject": "any", "data": {}}
```

### UI

Argo provide an UI to have a quick-view on the content status.

Here is the view of an echoer instance:

![echoer instance in the UI](/images/argo/echoer-ui.png)

and a view of the *printed* logs:

![echoer instance in the UI](/images/argo/echoer-ui-logs.png)

### Retries

If needed, you can re-run an existing instance of a workflow (with the same inputs) with the following kind of command:

```bash
argo resubmit @latest --watch
```

## VEBA event

In the same way, if you trigger on of the vCenter events configured in your `stack.yaml` file (like `VmCreatedEvent, VmClonedEvent, VmRegisteredEvent, DrsVmPoweredOnEvent, VmPoweredOnEvent` in the provided example) from you vCenter server:

1. VEBA event router will trigger the OpenFaaS function with event as an incoming data
2. OpenFaaS function will trigger the Argo worklow with the event as an incoming data

With the `echoer` workflow, you will be able to get the content of the event sent by VEBA and of course, you can now run a (more or less complex) workflow(s) catching the event data and making multiple actions.

## Conclusion

The above example is just a very simple sample of the enabled capabilities and it was difficult to demonstrate in this blog post the behavior of the full setup without being too complex for readers.

But I strongly encourage you to test it by yourself and to provide me a feedback.

You can also fill a GitHub issue on the project if needed: [**New issue**](https://github.com/lrivallain/openfaas-fn/issues/new/choose).