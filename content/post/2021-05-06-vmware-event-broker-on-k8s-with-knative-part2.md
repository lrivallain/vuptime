---
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
date: "2021-05-06"
splash: /images/splash/desktop-james-harrison.jpg
splash_credits: James Harrison @ unsplash.com
tags:
- vmware
- veba
- kubernetes
- event-driven
- knative
toc: true
thumbnail: /images/veba-first-steps/knative-logo.png
title: VMware Event Broker on Kubernetes with Knative functions - part 2
aliases: 
- /2021/05/06/vmware-event-broker-on-k8s-with-knative-part2/
featureImage: /images/splash/desktop-james-harrison.jpg
---

This post is the second part of a small series about *VMware Event Broker on Kubernetes with Knative functions*.

> If you plan to apply the following procedure, we assume that the content mentioned in the [**Part 1**](/2021/05/05/vmware-event-broker-on-k8s-with-knative-part1) is already deployed in your target setup.


# Deploy VMware Event Broker with knative support

> **Disclaimer**: This section of the post was made with the help of [@embano1](https://github.com/embano1) who provided a knative-ready helm chart for vcenter-event-broker deployment ([PR:392](https://github.com/vmware-samples/vcenter-event-broker-appliance/pull/392)). He also provided an example of the `override.yaml` file we will use below.

## Create a namespace

The following commands will create a namespace `vmware-fn` to host and run automation functions.

```bash
cat << EOF > vmware-fn-ns.yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: vmware-fn
EOF

kubectl apply -f vmware-fn-ns.yaml

kubectl get ns vmware-fn
# Output
NAME        STATUS   AGE
vmware-fn   Active   10s
```

> Of course: you can customize this target namespace and even re-use an existing one.

## Create a Broker

```bash
cat << EOF > mt-broker.yaml
---
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: vmware-event-broker
  namespace: vmware-fn
EOF

kubectl apply -f mt-broker.yaml

kubectl get broker -n vmware-fn
# Output (I remove a loooong URL field)
NAME                 AGE    READY
vmware-event-broker  23s    True
```

### Prepare event-router configuration

Create an `override.yaml` with your settings:

```bash
cat << EOF > override.yaml
eventrouter:
  config:
    logLevel: debug
  vcenter:
    address: https://vcsa.local
    username: test@vsphere.local
    password: VMware1!
    insecure: true # ignore TLS certs if required
  eventProcessor: knative  
  knative:
    destination:
      ref:
        apiVersion: eventing.knative.dev/v1
        kind: Broker # we use a Knative broker to send events to
        name: vmware-event-broker # name of the broker
        namespace: vmware-fn # namespace where the broker is deployed
EOF
```

> Ensure to specify broker name and namespace according to the one configured in the previous section.

### Helm deployment

If not already done, we will register the *veba* helm-charts registry and get metadata locally:

```bash
# register chart repo and update chart information
helm repo add vmware-veba https://projects.registry.vmware.com/chartrepo/veba
helm repo update
```

At this time, the support of knative with `helm` *vmware event router* deployment method is only supported in chart version >= v0.6.2. Ensure that this version is available:

```bash
helm search repo event-router --versions | grep v0.6.2
# Output
vmware-veba/event-router        v0.6.2          v0.6.0          The VMware Event Router is used to connect to v...
```

Lets deploy it.

> Here we create a specific namespace `vmware` for this purpose but you can reuse `vmware-fn` or any other one.

```bash
helm install -n vmware --create-namespace veba-knative vmware-veba/event-router -f override.yaml --wait --version v0.6.2
# Output
NAME: veba-knative
LAST DEPLOYED: Wed May  5 12:55:39 2021
NAMESPACE: vmware
STATUS: deployed
REVISION: 1
TEST SUITE: None
```
We can now check that the deployment status:

```bash
helm list --namespace vmware
# Output
NAME            NAMESPACE    REVISION    STATUS      CHART                   APP VERSION
veba-knative    vmware       1           deployed    event-router-v0.6.2     v0.6.0

kubectl get pod -n vmware
# Output
NAME                     READY   STATUS    RESTARTS   AGE
router-cdc874b59-vpckd   1/1     Running   0          36s
```

# Usage

Now its time to perform some tasks based on event routing setup.

## Deploy a sample *echo* function

The first (and very useful!) thing we can do, is to *echo* cloud events occurring in the target vCenter server.

VEBA team provide multiple *echo* samples (python or powershell based). Here we will use the python-based one provided by [@embano1/kn-echo](https://github.com/embano1/kn-echo):

```bash
cat << EOF > kn-py-echo.yaml
---
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: kn-py-echo-svc
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "1"
        autoscaling.knative.dev/minScale: "0"
    spec:
      containers:
      - image: embano1/kn-echo
---
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: kn-py-echo-trigger
spec:
  broker: vmware-event-broker
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: kn-py-echo-svc
EOF

kubectl apply -n vmware-fn -f kn-py-echo.yaml
# Output
service.serving.knative.dev/kn-py-echo-svc created
trigger.eventing.knative.dev/kn-py-echo-trigger created
```

We can check what was created:

```bash
kn service list -n vmware-fn
# Output
NAME           URL                                         LATEST               AGE     CONDITIONS   READY   REASON
kn-py-echo-svc http://kn-py-echo-svc.vmware-fn.example.com kn-py-echo-svc-00001 3m34s   3 OK / 3     True

kn trigger list -n vmware-fn
# Output
NAME                BROKER                SINK                  AGE    CONDITIONS   READY   REASON
kn-py-echo-trigger  vmware-event-broker   ksvc:kn-py-echo-svc   2m8s   5 OK / 5     True

kubectl get pod -n vmware-fn
# Output
NAME                                              READY   STATUS    RESTARTS   AGE
kn-py-echo-svc-00001-deployment-7d8fcf598-5g8f7   2/2     Running   0          63s
```

As we specified `autoscaling.knative.dev/minScale: "0"` in the service definition, the deployed pods may or may not be deployed at a specific time: if there is no event fired by vCenter for a period of time, Knative Serving will terminate the pod associated to the service, and recreate it when new event will arrive:

```bash
kubectl get pod -n vmware-fn
# Output
NAME                                              READY   STATUS        RESTARTS   AGE
No resources found in vmware-fn namespace.
```

If you want to look at incoming events, get the current running pod name and look at its logs:

```bash
kubectl logs -n vmware-fn kn-py-echo-svc-00001-deployment-7d8fcf598-ngtdd user-container -f
```

## Deploy *vm-creation-attr* function

I also did a re-write of the [*vm-creation-attr* function](https://github.com/lrivallain/openfaas-fn/tree/master/vm-creation-attr-fn) I did write for OpenFaaS process to be knative compliant.

> As a reminder, I did a(nother long) post a few month back [about this function](https://vuptime.io/2020/12/17/vmware-event-broker-0.5.0-on-k8s-first-steps/#first-function). The main goal is to populate *custom attributes* values for VM object based on the user who created the VM, the creation date and the last-poweredon date.

The knative function is hosted on GitHub: [lrivallain/kn-vm-creation-attr-fn](https://github.com/lrivallain/kn-vm-creation-attr-fn). You can get the `function.yaml` file to start the deployment:

```bash
curl -LO https://raw.githubusercontent.com/lrivallain/kn-vm-creation-attr-fn/main/function.yaml
```

### Configuration

Edit the content of `function.yaml` to configure the following settings:

```bash
# In `ConfigMap` section
VC_SERVER: vcsa.local
VC_USER: test@vsphere.local
VC_SSLVERIFY: True
VC_ATTR_OWNER: event-owner
VC_ATTR_CREATION_DATE: event-creation_date
VC_ATTR_LAST_POWEREDON: event-last_poweredon

# In `Secret` section
VC_PASSWORD: Vk13YXJlMSEK
```

The `VC_PASSWORD` is base64 encoded: you can generate it by using a command like:

```bash
echo -n "YourP@ssw0rd" | base64
```

We assume that you use the previously mentioned `vmware-event-broker` broker name, but you can change it by using:

```bash
sed -i s/vmware-event-broker/NAMEOFYOURBROKER/ function.yaml
```

### Deploy


```bash
kubectl appy -n vmware-fn -f function.yaml
```

Then you can check the result with following commands:

```bash
kn service list -n vmware-fn

kn trigger list -n vmware-fn

kubectl get pod -n vmware-fn
```

> You will notice that there is multiple `kn-vm-creation-attr-fn-trigger-xxxx` triggers deployed. It is due to the filtering applied to incoming event, to only get the one matching some specific actions results.

### Test

By looking at pod logs, you can see the actions resulting from the incoming events:

```log
172.17.0.1 - - [04/May/2021 14:08:00] "POST / HTTP/1.1" 204 -
2021-05-04 14:08:00,230 INFO werkzeug Thread-3 : 172.17.0.1 - - [04/May/2021 14:08:00] "POST / HTTP/1.1" 204 -
2021-05-04 14:09:18,462 DEBUG handler Thread-4 : "***cloud event*** {"attributes": {"specversion": "1.0", "id": "42516969-218a-406f-9ccc-db387befc4bf", 
"source": "https://vcsa.local/sdk", "type": "com.vmware.event.router/event", "datacontenttype": "application/json", "subject": "DrsVmPoweredOnEvent", "time": "2021-05-04T07:33:33.773581268Z", "knativearrivaltime": "2021-05-04T07:33:33.772937393Z"}, "data": {"Key": 992270, "ChainId": 992267, "CreatedTime": "2021-05-04T07:33:32.759Z", "UserName": "VSPHERE.LOCAL\\test-user", "Datacenter": {"Name": "Datacenter", "Datacenter": {"Type": "Datacenter", "Value": "datacenter-21"}}, "ComputeResource": {"Name": "Cluster01", "ComputeResource": {"Type": "ClusterComputeResource", "Value": "domain-c84"}}, "Host": {"Name": "esxi1.local", "Host": {"Type": "HostSystem", "Value": "host-34"}}, "Vm": {"Name": "TestVM", "Vm": {"Type": "VirtualMachine", "Value": "vm-596"}}, "Ds": null, "Net": null, "Dvs": null, "FullFormattedMessage": "DRS powered On TestVM on esxi1.local in Datacenter", "ChangeTag": "", "Template": false}
}
2021-05-04 14:09:18,464 DEBUG vcenter Thread-4 : Initializing vCenter connection...
2021-05-04 14:09:18,992 INFO vcenter Thread-4 : Connected to vCenter 10.6.29.7
2021-05-04 14:09:19,483 INFO handler Thread-4 : Apply attribute > event-last_poweredon
2021-05-04 14:09:19,774 DEBUG handler Thread-4 : End of event
172.17.0.1 - - [04/May/2021 14:09:19] "POST / HTTP/1.1" 204 -
2021-05-04 14:09:19,777 INFO werkzeug Thread-4 : 172.17.0.1 - - [04/May/2021 14:09:19] "POST / HTTP/1.1" 204 -
```

## Is it serverless?

With a `autoscaling.knative.dev/minScale: "0"` annotation setting (as provided by default in the above functions), have look at the pods list to see the result of an event:

```bash
k get pods --watch -n vmware-fn
# Output
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   0/2     Pending             0          0s
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   0/2     ContainerCreating   0          1s
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   1/2     Running             0          5s
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   1/2     Running             0          6s
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   2/2     Running             0          7s
# And after about 60s without events:
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   2/2     Terminating         0          68s
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   1/2     Terminating         0          71s
kn-vm-creation-attr-fn-service-00002-deployment-848865fdd-xgvb9   0/2     Terminating         0          2m8s
```

As you can see, the function is acting as a serverless one: when needed, the appropriate number of pods is spawned, and when there is not incoming (and matching) event: no pods are kept on the cluster.

You can easily change values of `autoscaling.knative.dev/maxScale: "1"` and `autoscaling.knative.dev/minScale: "0"` according to your needs: for example, with `minScale: "1"`: at least one pod will always remain listening for events: This could improve the time to execute an action it there is no pod to spawn after an inactivity period.

So, considering that the service provider is *knative*, our functions are acting like serverless ones and the management component is in charge of scaling (up and down to 0), the components running our application code, according to the incoming requests: This enable all the benefits of serverless applications and of-course, its drawbacks.

## Credits

Title photo by [James Harrison](https://unsplash.com/@jstrippa) on [Unsplash](https://unsplash.com/photos/vpOeXr5wmR4)