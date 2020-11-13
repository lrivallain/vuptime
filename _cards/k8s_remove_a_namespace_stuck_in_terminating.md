---
layout: card
title: Kubernetes – Remove a namespace stuck in terminating state
tags: kubernetes kubectl
author: lrivallain
date: 2020-11-13
---

In case of a *k8s* namespace stuck in the `terminating` state, you can use the two below commands to ensure that there is no remaining ressources and to remove the `finalizers` of the ressource:

```bash
# declare the namespace that is stuck
STUCKED_NS="stucked-namespace"
```

Ensure there is no remaining ressource(s):

```bash
kubectl api-resources --verbs=list --namespaced -o name \
  | xargs -n 1 kubectl get --show-kind --ignore-not-found -n $STUCKED_NS
```

And to remove the ressource `finalizers`:

```bash
kubectl get namespace $STUCKED_NS -o json \
  | tr -d "\n" | sed "s/\"finalizers\": \[[^]]\+\]/\"finalizers\": []/" \
  | kubectl replace --raw /api/v1/namespaces/$STUCKED_NS/finalize -f -
```

Thanks to teoincontatto @ stackoverflow.com for [this tip](https://stackoverflow.com/a/59667608/8375999)
