---
author: lrivallain
categories:
- Kubernetes
date: "2021-02-02T00:00:00Z"
tags:
- kubernetes
- event-driven
- book
thumbnail: /images/kubernetes_logo.svg
title: My Kubernetes Book
aliases: 
- /2021/02/02/my-kubernetes-book/
---

I recently started my journey to the Kubernetes world, switching from theory knowledge to practical use-cases for customers.

This is a wonderful new technical area to discover with a lot of **new**:

* Tools
* Features/Capabilities
* Documenations
* Communities
* Best-practices
* …

Of course, I am far-far-away to master those new competencies but I learn more and more on a daily basis.

At the begining, I started a small wiki for my own usage to keep some useful commands, tips, how-to documentations. But I know think that this content may help others to centralize some re-usable content.

So I started a new side project to this blog: **My Kubernetes Book**: [https://k8s-book.vupti.me/](https://k8s-book.vupti.me/)

{{< figure src="/images/my-k8s-book.png" title="Screenshot of My Kubernetes Book" >}}

> This is not a substitution to official projects documentation, just a quick way for me to get the information I need.

## Content

Currently, the '*book*' content is the following:

1. [Deploy a K3S cluster](https://k8s-book.vupti.me/k3s-cluster-deployment/)
    1. [All nodes pre-requisites](https://k8s-book.vupti.me/k3s-cluster-deployment/all-nodes-pre-requisites/)
    1. [Initial master node](https://k8s-book.vupti.me/k3s-cluster-deployment/initial-master-node/)
    1. [Worker node(s)](https://k8s-book.vupti.me/k3s-cluster-deployment/worker-node-s/)
    1. [Additional master nodes](https://k8s-book.vupti.me/k3s-cluster-deployment/additional-master-nodes/)
1. [Setup a powerful Kubernetes client](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/)
    1. [Basics tools](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/basics/)
    1. [Arkade](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/arkade/)
    1. [k9s](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/k9s/)
    1. [kubens & kubectx](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/kubens-and-kubectx/)
    1. [jsonnet](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/jsonnet/)
    1. [Octant](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/octant/)
    1. [Argo cli](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/argo-cli/)
    1. [OpenFaaS CLI](https://k8s-book.vupti.me/setup-a-powerful-kubernetes-client/openfaas-cli/)
1. [Cluster customizations](https://k8s-book.vupti.me/customizations/)
    1. [Traefik as ingress controler](https://k8s-book.vupti.me/customizations/traefik/)
    1. [Monitoring with Prometheus](https://k8s-book.vupti.me/customizations/kube-prometheus/)
1. [Cluster usage](https://k8s-book.vupti.me/usage/)
    1. [Kubectl tips](https://k8s-book.vupti.me/usage/kubectl-tips/)

Of course, the content will hopefully increase in the next months or years.

## Engine

This website is built on [Hugo](https://gohugo.io/) static website engine with the [learn theme](https://learn.netlify.app/en/).

## Contributions

This new website is open to external contributions through:

* Comments: All pages contains a comment feature based on GitHub issues (with [utterances](https://utteranc.es/) integration)
* Direct [GitHub issues](https://github.com/lrivallain/git-book-kubernetes/issues) ([**+**](https://github.com/lrivallain/git-book-kubernetes/issues/new/choose))

You can also submit changes through GitHub *pull request* features:

1. As a pre-requesite to local build, you will need Hugo engine installed: [Quick Start](https://gohugo.io/getting-started/quick-start/)
2. Clone the repository with submodules:

```bash
git clone --recursive https://github.com/lrivallain/git-book-kubernetes.git
```

3. Push changes to a new branch:

```bash
# new branch:
git checkout -b "my-changes"
# <do changes here !>
# test your changes with:
hugo server
# <git add / git commit / git push>
```

4. Create a pull request on the project.
5. Once accepted and merged to master, the static will be run through this
[Publish GitHub Action](https://github.com/lrivallain/git-book-kubernetes/actions?query=workflow%3A%22Publish+Site%22)
