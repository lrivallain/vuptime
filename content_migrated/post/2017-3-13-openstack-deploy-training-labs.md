---
author: lrivallain
categories:
- Openstack
date: "2017-03-13T00:00:00Z"
tags: script openstack training helper
title: Openstack - Deploy training labs
---

I'm currently working to deploy quickly OpenStack based training lab to provide a platform for practical exercises for training sessions.

According to the hosted training session, the needs may differ significantly and we need to quickly clean and recreate a *"training"* tenant.

I have developed a quick helper to produce a new environment in short term: [buildlab.sh ](https://gist.github.com/lrivallain/619c35cfb91048a635ddefc60788b3cc)

Here is an usage example:

```bash
# Following command will create:
#  * instance(s) named "training"
#  * based on ubuntu image
#  * start 10* instances
#  * append index starting from 1
#  * 5Gb disk per instance
#  * sizing based on flavor: m1.tiny
#  * connected to network: training_net
#  * security group applied:  training_sec
#  * ssh key will be: mysshkey
#  * post costumization from script: postconfig_training.sh
#  * attach floating IP from the "MyPool" repository

./buildlab.sh --name "training" \
              --image "Ubuntu 16.04 Xenial" \
              --count 10 \
              --start_index 1 \
              --volume_size 5 \
              --flavor_name "m1.tiny" \
              --network_name "training_net" \
              --sec_group "training_sec" \
              --key_name "mysshkey" \
              --postcusto "./postconfig_training.sh" \
              --floating_pool "MyPool"
```
