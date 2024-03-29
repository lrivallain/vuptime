---
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
date: "2020-12-17T00:00:00Z"
tags:
- vmware
- veba
- kubernetes
- event-driven
thumbnail: /images/veba-first-steps/veba_otto_the_orca_md.png
title: VMware Event Broker 0.5.0 (aka VEBA) on Kubernetes – First steps
aliases: 
- /2020/12/17/vmware-event-broker-0.5.0-on-k8s-first-steps/
toc: true
---

> This post is a re-edition of a previous one: [VMware Event Broker (aka VEBA) on Kubernetes – First steps](2020/11/02/vmware-event-broker-on-k8s-first-steps/), update to be applicable to the new 0.5.0 release of *VEBA*, including the support of `helm` chart deployment.

In the following post, we will (re)discover how to deploy the VMware Event Broker services (VEBA) within an existing Kubernetes (K8S) cluster and use it to add/edit custom attributes information to virtual machines.

The goal of the VEBA deployment is to be able to listen for events in the VMware vCenter infrastructure and to run specific tasks when filtered events occurs: it is the [*event driven automation*](https://octo.vmware.com/vsphere-power-event-driven-automation/) concept.

To be accurate, VEBA stands for **"VMware Event Broker Appliance"**: a Photon OS based virtual machine, available in OVA format, with an embedded small K8S cluster to support the **"VMware Event Broker"** services.
In the following post, I re-use an existing K8S cluster to support the "VMware Event Broker" services but I will use the VEBA acronym to simplify the redaction: even if I do not use the appliance deployment method.

If you need more details about VEB(A), the official website if well documented: [vmweventbroker.io](https://vmweventbroker.io/) and lot of other use-cases are listed: notification, automation, integration, remediation, audit, analytics…

## VMware Event Broker components

{{< figure src="/images/veba-first-steps/veba-architecture-v0.5.0.png" title="VEBA Architecture" >}}

### VMware Event Router

The *VMware Event Router*, is the VEBA component, watching for new events generated by an *Event Stream Source* and routing the event to the **Event Stream Processors**. In the mean time, the *VER* translate the events to the [*cloudevents*](https://cloudevents.io) format: a specification for describing event data in a common way.

### Event Stream Source

Currently, the VEBA only support one source for event stream: the vCenter Server.

As announced at VMworld2020 (**VEBA and the Power of Event-Driven Automation – Reloaded \[HCP1358\]**), a Cloud Director *event stream source* is in preparation.

### Event Stream Processors

The *Event Stream Processor* is in charge of handling the event propagated by the *VMware Event Router* to the appropriate automation tasks that are configured to run for the specific type of event.

As the time I write this post, 3 processors are available:

* [Amazon EventBridge](https://aws.amazon.com/eventbridge/): to run on AWS *serverless* event services, your automation tasks.
* [OpenFaaS®](https://www.openfaas.com/): An open-source project to run *Function as a Service* (FaaS) automation task over a K8S deployment.
* [KNative](https://knative.dev/) **NEW in 0.5.0**: a Google-sponsored industry-wide project to extends Kubernetes to provide developers with a set of tools that simplify the process of deploying and managing event-driven applications that can run anywhere.

In my setup, I use the OpenFaaS processor.

## Pre-requisites

### Kubernetes

To proceed, we consider that an existing cluster is deployed.

If you need to deploy a really light and simple lab setup, I can highly recommend to use `k3s` to deploy your own K8S cluster: [K3S: Quick-Start Guide](https://rancher.com/docs/k3s/latest/en/quick-start/).

In my own lab, I use a K8S cluster deployed by [Rancher](https://rancher.com/) with the vSphere node driver (but that doesn't change anything to the current use-case).

### `kubectl` cli

[`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl/) is the standard CLI tool to operate K8S resources.

Once installed, you need to link your K8S cluster configuration file. There are multiple methods to do so, so I prefer to link the official documentation for [Organizing Cluster Access Using kubeconfig Files](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/).

You can check the setup by running:

```bash
# Display the current configuration
kubectl config view

# Get client and server version
kubectl version --short
```

The last command should output something close to this:

```bash
Client Version: v1.19.3
Server Version: v1.19.2
```

### `helm` cli

The `helm` cli will provide a simple way to deploy both OpenFaaS and VEBA stacks:

```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | sudo bash
```

### `faas-cli`

The [`faas-cli`](https://github.com/openfaas/faas-cli) requirement is linked to the usage of the OpenFaaS processor in the following setup.

Here is one installation method:

```bash
curl -sSL https://cli.openfaas.com | sudo sh
```

> You can also use an alternative installation method described in the [`faas-cli` project GitHub repository](https://github.com/openfaas/faas-cli).


## OpenFaaS deployment

```bash
kubectl create ns openfaas
kubectl create ns openfaas-fn
helm repo add openfaas https://openfaas.github.io/faas-netes
helm repo update
helm upgrade openfaas --install openfaas/openfaas \
  --namespace openfaas \
  --set functionNamespace=openfaas-fn \
  --set generateBasicAuth=true
```

You can check the deployment status by running:

```bash
kubectl -n openfaas get deployments -l "release=openfaas, app=openfaas"
```

Once deployed, you can get the generated password and the endpoint URL by:

```bash
# Get password
export OF_PASS=$(echo $(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode))
echo $OF_PASS

# Get URI
echo "export OPENFAAS_URL=http://"$(kubectl -n openfaas describe pods $(kubectl -n openfaas get pods | grep "gateway-" | awk '{print $1}') | grep "^Node:" | awk -F "/" '{print $2}')":31112"
```

### Ingress access to OpenFaaS

If you want to access with a friendly URI to your OpenFaaS instance, you can use an ingress like the following one:

1. Create a DNS record for your new openfaas fqdn then
2. Create the following file:

```bash
mkdir openfaas
vi openfaas/ingress.yml
```

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: openfaas-gateway-ingress
  namespace: openfaas
  annotations:
    kubernetes.io/ingress.class: traefik
spec:
  rules:
  - host: openfaas.vlab.lcl
    http:
      paths:
      - backend:
          serviceName: gateway
          servicePort: 8080
```

Deploy it:

```bash
kubectl apply -f ingress.yml
kubectl get ingress -n openfaas
echo "export OPENFAAS_URL=http://$(kubectl get ingress -n openfaas 2>/dev/null| grep "gateway-" | awk '{print $3}')"
```

### Check the deployment

If you requested the OpenFaaS deployment, you now have a set of pods in the `openfaas` namespace:

```bash
kubectl get pods -n openfaas
# You should get a new set of running pods
NAME                                READY   STATUS    RESTARTS   AGE
basic-auth-plugin-bc899c574-6hzhf   1/1     Running   0          18h
nats-7d86c64647-nj9mm               1/1     Running   0          18h
queue-worker-5d8986f858-cql9c       1/1     Running   1          18h
alertmanager-677f4db47f-s92xs       1/1     Running   0          18h
prometheus-7797994d65-74pvn         1/1     Running   0          18h
gateway-7f6d9cb855-xptmw            2/2     Running   0          18h
faas-idler-7f66c658bf-gs98m         1/1     Running   3          18h
```

### Login to your OpenFaaS cli and UI

#### Login to `faas-cli`

We now need to get the OpenFaaS URI to use the `faas-cli` client:

```bash
echo $OF_PASS | faas-cli login --password-stdin
```

> A warning will recommend you to use an HTTPS endpoint instead of the HTTP one: let's ignore it for the moment.

At least, you should get a message like: "credentials saved for admin `http://openfaas.vlab.lcl"` meaning that you successfully configured your `faas-cli` client.

#### Login to the UI

Use the same URL to login with the `admin` account to the web UI and you should get something like that:

{{< figure src="/images/veba-first-steps/empty_OpenFaaS_UI.png" title="Empty OpenFaaS UI" >}}

## VEBA deployment on Kubernetes

The VEBA deployment on K8S is quite simple and does not require a lot of configuration.

### Prepare an override file

Prepare an `override.yml` file to provide to veba its deployment settings:

```bash
mkdir veba
vim veba/override.yml
```

```yaml
eventrouter:
  config:
    logLevel: debug
  vcenter:
    address: https://vcsa.vlab.lcl
    username: administrator@vsphere.local
    password: ---------
    insecure: false # ignore TLS certs ?
  openfaas:
    address: http://openfaas.vlab.lcl
    basicAuth: true
    username: admin
    password: ---------
```

### Deploy VEBA to your Kubernetes cluster

VEBA team provides a *helm* chart to handle the deployment:

```bash
helm repo add vmware-veba https://projects.registry.vmware.com/chartrepo/veba
helm repo update
helm install -n vc-veba --create-namespace vc-veba vmware-veba/event-router -f veba/override.yml
kubectl -n vc-veba logs deploy/router -f
```

You should get logs from the startup of the envent router pod.

### Check the deployment

Few minutes later, you should have a new VEBA deployment:

```bash
kubectl -n vc-veba get deployments
# You should get a ready router
NAME     READY   UP-TO-DATE   AVAILABLE   AGE
router   1/1     1            1           18h

kubectl get pods -n vc-veba
# You should get a running pod
NAME                                   READY   STATUS    RESTARTS   AGE
vmware-event-router-859b97c894-bxx94   1/1     Running   0          25m
```

This pod, in the `vmware` is the [*VMware Event Router*](#VMware%20Event%20Router) as explained previously in this post.

## First function

Time to describe our first function use case:

We have a lab vCenter with multiple users, multiple projects, PoC etc. And it's a bit hard to know which VM belongs to which user, and if the project is still active.

A way I found to handle this, is to set *Custom Attributes* to the VM objects in vCenter, and to populate values when specific event occurs:

* `event-creation_date`: To store the creation date
* `event-last_poweredon`: To store the last powered on date
* `event-owner`: To store the user that created the VM

{{< figure src="/images/veba-first-steps/custom_attributes.png" title="Custom attributes created for this function" >}}

### Function files/folders structure

An VEBA OpenFaaS function is made of the following items:

* `handler/`: this folder will store the content of our function code (folder name can be personalized)
* `stack.yaml`: This file will describe our function
* A config file, passed as a K8S  secret to our function, used to store credentials and other environment specific variables. In my example, it's a *YAML* file: `vcconfig.yml`.

To simplify this post, I invite you to clone this sample repository:

```bash
git clone https://github.com/lrivallain/veba-sample-custom-attribute.git
cd veba-sample-custom-attribute/
```

#### `stack.yaml` file

This description file is used by VEBA to create the function run on our function-processor.

```yaml
version: 1.0
provider:
  name: openfaas
  gateway: http://openfaas.vlab.lcl
functions:
  vm-creation-attr:
    namespace: openfaas-fn
    lang: python3
    handler: ./handler
    image: lrivallain/veba-vc-vm-creation-attr
    environment:
      write_debug: true
      read_debug: true
    secrets:
      - vcconfig
    annotations:
      topic: VmCreatedEvent, VmClonedEvent, VmRegisteredEvent, DrsVmPoweredOnEvent, VmPoweredOnEvent, VmPoweringOnWithCustomizedDVPortEvent
```

As you see, we specify here the:

* OpenFaaS URI gateway (the one in `OPENFAAS_URL`)
* The target namespace: `openfaas-fn`
* A language type: `python3`
* The function folder: `./handler`
* A base image to run the function: `lrivallain/veba-vc-vm-creation-attr`
  * This image contains the appropriate dependencies to run our function
* The configuration as a K8S *secret* name.
* And in the annotations: the topic(s) to subscribe for this function.
  * Depending on your vCenter version, you can find an Event list in the [vcenter-event-mapping](https://github.com/lamw/vcenter-event-mapping) repository of William Lam.

#### `handler/` folder

The handler folder is made of:

* An `index.py` file, use to handle the function instantiation: keep it like it is provided to start: of course, you can inspect the content to analyse the (simple) behaviour.
* A `function/` subfolder:
  * The `handler.py` file contains the code run each time the function is triggered
  * The `requirements.txt` file contains some function specific dependencies.
* The `Dockerfile` used to build the base image: `lrivallain/veba-vc-vm-creation-attr`: {{< figure src="https://img.shields.io/docker/cloud/build/lrivallain/veba-vc-vm-creation-attr" title="Docker Cloud Build Status" >}}

### `vcconfig.yaml`

This is a quite simple configuration file to rename to the expected name:

```bash
cp vcconfig.example.yaml vcconfig.yaml
```

```yaml
vcenter:
  server: vcsa-fqdn
  user: service-account@vsphere.local
  password: "**********"
  ssl_verify: false

attributes:
  owner: event-owner
  creation_date: event-creation_date
  last_poweredon: event-last_poweredon
```

You need to setup your VCSA instance, credentials and the name of custom attributes to use for each need.

#### Custom attributes creation

The script currently does not handle the custom attribute creation so you need to create them before using the function:

{{< figure src="/images/veba-first-steps/custom_attributes.png" title="Custom attributes" >}}

## Deploy our function

We now got function code, configuration, and the VEBA over K8S deployed. Let's deploy our function.

First step is to create the "*secret*" to store our local configuration:

```bash
faas-cli secret create vcconfig --from-file=vcconfig.yml
```

And to confirm if it worked, we can lookup for the `vcconfig` secret in a new namespace named: `openfaas-fn` (for OpenFaaS Function)

```bash
kubectl get secrets -n openfaas-fn vcconfig
# Output:
NAME       TYPE     DATA   AGE
vcconfig   Opaque   1      2m53s
```

Now we need to pull the OpenFaaS language template for the specified `lang` in our `stack.yml` file:

```bash
faas template store pull python3
```

> In fact, this command will pull all (12) the languages templates from the `openfaas` registry, not only the one you are looking for.

We are ready to deploy our *Function-as-a-Service*:

```bash
faas-cli deploy -f stack.yml
# Output
Deploying: vm-creation-attr.
Deployed. 202 Accepted.
URL: http://openfaas.vlab.lcl/function/vm-creation-attr.openfaas-fn
```

We can check that a new pod is now part of the `openfaas-fn` namespace:

```bash
$ kubectl get pods -n openfaas-fn
# Output:
NAME                                READY   STATUS    RESTARTS   AGE
vm-creation-attr-65d9f75464-lf2sk   1/1     Running   0          94s
```

And our function is well listed in `faas-cli`

```bash
faas-cli list
# Output:
Function                        Invocations     Replicas
vm-creation-attr                0               1
```

The same in UI (need a refresh):

{{< figure src="/images/veba-first-steps/first-function-ready-UI.png" title="First Function deployed in the OpenFaaS UI" >}}

## Invoke function

Invocation is now easy: juste create or power-on a VM in your vCenter and the event will be catched by VEBA, forwared to your OpenFaaS function and the code will run, inspecting the `cloudevents` incoming data and doint the expected tasks.

### Follow function invocation

There is two way to follow the function invocation(s).

By using `kubectl` logs and specifing the `openfaas-fn` namespace, the pod name (from above commands), and the `--tail` and/or `--follow` args:

```bash
kubectl logs -n openfaas-fn vm-creation-attr-65d9f75464-lf2sk --tail 100 --follow
# Output:
2020/11/01 14:41:26 Version: 0.18.1     SHA: b46be5a4d9d9d55da9c4b1e50d86346e0afccf2d
2020/11/01 14:41:26 Timeouts: read: 5s, write: 5s hard: 0s.
2020/11/01 14:41:26 Listening on port: 8080
2020/11/01 14:41:26 Writing lock-file to: /tmp/.lock
2020/11/01 14:41:26 Metrics listening on port: 8081
```

Or with `faas-cli` command:

```bash
faas-cli logs vm-creation-attr --tail 100
# Output:
2020-11-01T14:41:26Z 2020/11/01 14:41:26 Version: 0.18.1        SHA: b46be5a4d9d9d55da9c4b1e50d86346e0afccf2d
2020-11-01T14:41:26Z 2020/11/01 14:41:26 Timeouts: read: 5s, write: 5s hard: 0s.
2020-11-01T14:41:26Z 2020/11/01 14:41:26 Listening on port: 8080
2020-11-01T14:41:26Z 2020/11/01 14:41:26 Writing lock-file to: /tmp/.lock
2020-11-01T14:41:26Z 2020/11/01 14:41:26 Metrics listening on port: 8081
```

Both outputs are very similar, so you can use the one that is the more convenient to you.

#### VM creation

In the case of a VM creation, we have the following output:

{{< figure src="/images/veba-first-steps/logs-vm-creation.png" title="Logs for the VM creation event" >}}

And the attributes are populated according to the expected behavior:

{{< figure src="/images/veba-first-steps/attributes-vm-creation.png" title="Attributes for the VM creation event" >}}

#### VM powered-On

If we power On a VM:

{{< figure src="/images/veba-first-steps/logs-vm-poweredon.png" title="Logs for the VM poweredOn event" >}}

And the attributes are populated according to the expected behavior:

{{< figure src="/images/veba-first-steps/attributes-vm-poweredon.png" title="Attributes for the VM poweredOn event" >}}


## Conclusion

We successfully covered the deployment of our first *Event-Driven* *Function-as-a-Service* use-case, greatly helped by the **VMware Event Broker** services.

There is a [multitude of events](https://github.com/lamw/vcenter-event-mapping) you can subscribe in your VMware virtual datacenter to imagine an infinity list of use cases: it is time to unlock your creativity!