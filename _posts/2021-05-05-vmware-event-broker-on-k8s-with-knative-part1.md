---
layout: post
title: VMware Event Broker on Kubernetes with Knative functions - part 1
category: VMware
author: lrivallain
tags: vmware veba kubernetes event-driven knative
thumb: /images/veba-first-steps/knative-logo.png
splash: /images/splash/desktop-jonathan-kemper.jpg
splash_credits: Jonathan Kemper @ unsplash.com
---

As mentioned in some previous posts ([here](https://vuptime.io/2020/11/02/vmware-event-broker-on-k8s-first-steps/) or [here](https://vuptime.io/2020/12/17/vmware-event-broker-0.5.0-on-k8s-first-steps/)), I do not deploy the instance-based packaging of the [VMware Event Router](https://vmweventbroker.io/): aka VEBA. I prefer to reuse existing Kubernetes cluster(s) to host the `vmware event router` and the associated functions.

Currently, most of my automation work relies on [OpenFaaS®](https://www.openfaas.com/) functions, and [Argo workflows](https://argoproj.github.io/) for long running tasks (triggered by OpenFaaS).

Since [v0.5.0 release](https://github.com/vmware-samples/vcenter-event-broker-appliance/releases/tag/v0.5.0), the VMware Event Broker, supports a new processor: `knative`.

This **part 1** post will cover the deployment of Knative components, in order to prepare the deployment of VMware Event Broker through `helm` chart mentioned in [**part2**](/2021/05/06/vmware-event-broker-on-k8s-with-knative-part2).

* Table of contents
{:toc}

# About Knative

[**Knative**](https://knative.dev) is a Google-held Kubernetes-based platform to build, deploy, and manage modern serverless workloads. The project is made of three major components:

* [Knative Serving](https://knative.dev/docs/serving/): Easily manage stateless services on Kubernetes by reducing the developer effort required for auto-scaling, networking, and rollouts.
* [Knative Eventing](https://knative.dev/docs/eventing/): Easily route events between on-cluster and off-cluster components by exposing event routing as configuration rather than embedded in code.

Some major *serverless** cloud services are now based or compatible with knative API like [Red Hat OpenShift Serverless](https://www.openshift.com/learn/topics/serverless) or [Google Cloud Run](https://cloud.google.com/run).

The **Knative Eventing** provide an abstraction of the messaging layer supporting multiple and pluggable event sources. Multiple delivery modes are also supported (fanout, direct) and enable a variety of usages. Here is an overview of events way within the Eventing component:

{% include lightbox.html src="/images/veba-first-steps/kn-broker-trigger-overview.svg" title="Broker Trigger Diagram (src: https://knative.dev/docs/eventing/)" %}

The **Knative Serving** project provides middleware primitives that enable the deployment of serverless containers with automatic scaling (up and down to zero). The component is in charge of traffic routing to deployed application and to manage versioning, rollbacks, load-testing etc.

{% include lightbox.html src="/images/veba-first-steps/kn-object_model.png" title="Knative service overview (src: https://knative.dev/docs/serving/)" %}


## Deploy Knative on your cluster

### Setup description

In the following setup, we will deploy **Serving** and **Eventing** components with [Kourier](https://github.com/knative-sandbox/net-kourier) as Ingress for Knative Serving.

> Kourier is a lightweight alternative for the Istio ingress as its deployment consists only of an Envoy proxy and a control plane for it.

I assume that you already have a working Kubernetes cluster. 

> If not, you can try [`kind`](https://kind.sigs.k8s.io/docs/user/quick-start/) to deploy a local, dev-purpose, cluster.

The following process also relies on `helm` to deploy the vmware event router.

We will use the (current) latest version of knative, but you can probably change the value of the following setting according to the [knative latest available release](https://github.com/knative/operator/releases).

```bash
export KN_VERSION="v0.22.0"
```

### Knative Serving

[Knative documentation](https://knative.dev/docs/install/install-serving-with-yaml/) is really helpful for the following steps. I will only put together the commands I used in my setup:

```bash
# custom resources definitions
kubectl apply -f https://github.com/knative/serving/releases/download/${KN_VERSION}/serving-crds.yaml

# Knative Serving core components
kubectl apply -f https://github.com/knative/serving/releases/download/${KN_VERSION}/serving-core.yaml
```

A new `knative-serving` namespace will be deployed on the cluster with some core resources.

Then we install and configure Kourier to act as our Ingress controller:

```bash
# Install and configure Kourier
kubectl apply -f https://raw.githubusercontent.com/knative/serving/${KN_VERSION}/third_party/kourier-latest/kourier.yaml

# Specfiy knative Serving to use Kourier
kubectl patch configmap/config-network --namespace knative-serving --type merge --patch '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
```

Depending on the target platform you use, you may, or may not have a value already set for the `External-IP` of the `kourier` service.

```bash
kubectl -n kourier-system get service kourier
# Output
NAME      TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
kourier   LoadBalancer   10.43.165.137   pending    80:30471/TCP,443:32405/TCP   10m
```

If you have a pending value (like in my on-premise setup), you can manually assign an IP address to the service:

```bash
kubectl patch service kourier -p '{"spec": {"type": "LoadBalancer", "externalIPs":["192.168.1.36"]}}' -n kourier-system

kubectl -n kourier-system get service kourier
# Output
NAME      TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
kourier   LoadBalancer   10.43.165.137   192.168.1.36    80:30471/TCP,443:32405/TCP   10m
```

You can have a quick look at running pods on your `` namespace to see if everything is running fine:

```bash
kubectl get pods -n knative-serving
# Output
NAME                                      READY   STATUS    RESTARTS   AGE
3scale-kourier-control-67c86f4f69-6mnwr   1/1     Running   0          11m
activator-799bbf59dc-s6vls                1/1     Running   0          11m
autoscaler-75895c6c95-mbnqw               1/1     Running   0          11m
controller-57956677cf-74hp9               1/1     Running   0          11m
webhook-ff79fddb7-gjvwq                   1/1     Running   0          11m
```

### Knative Eventing

As for the Serving component, you can rely on a very clear [documentation to install the Eventing component](https://knative.dev/docs/install/install-eventing-with-yaml/).

```bash
# custom resources definitions
kubectl apply -f https://github.com/knative/eventing/releases/download/${KN_VERSION}/eventing-crds.yaml

# Knative Eventing core components
kubectl apply -f https://github.com/knative/eventing/releases/download/${KN_VERSION}/eventing-core.yaml

# Prepare In-memory channel (messaging) layer
kubectl apply -f https://github.com/knative/eventing/releases/download/${KN_VERSION}/in-memory-channel.yaml

# Prepare MT-channel based broker
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/mt-channel-broker.yaml
```

> **Channels** are Kubernetes custom resources that define a single event forwarding and persistence layer. [[More details]](https://knative.dev/docs/eventing/channels/)

> **Brokers** can be used in combination with subscriptions and triggers to deliver events from an event source to an event sink.

Here, the default *MT Channel Based Broker* relies on a default, unsuitable for production, *In-Memory* channel.

We will only use the *clusterDefault* settings but, if needed, you can edit the broker configuration by using the next command:

```bash
kubectl edit cm -n knative-eventing config-br-defaults
```

### knative CLI

Event if `kubectl` could be used to manage knative components, a `kn` CLI tool is also available with completion of otherwise complex procedures such as auto-scaling and traffic splitting.

```bash
curl https://github.com/knative/client/releases/download/${KN_VERSION}/kn-linux-amd64 -L > kn
chmod +x kn
sudo mv  kn /usr/local/bin/kn
# Test it
kn version
```

# Part 2: Deploy VMware Event Broker

See you in [**Part 2**](/2021/05/06/vmware-event-broker-on-k8s-with-knative-part2) to deploy the VMware Event Broker and some functions.


## Credits

Title photo by [Jonathan Kemper](https://unsplash.com/@jupp) on [Unsplash](https://unsplash.com/photos/H488ymQgIgM)