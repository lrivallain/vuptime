---
layout: post
title: Ansible/VMware modules - first steps
author: lrivallain
category: VMware
tags: vmware ansible module tutorial
---

Ansible is a well known software to automates software provisioning, configuration management, and application deployment. In concrete terms, it's possible to manage infrastructure deployment and configuration during life cycle from sets of configuration files.

In the following post, I will try to explain how to use it with some VMware modules from ansible installation to the management of a vCenter based infrastructure.

* Table of contents
{:toc}

# Ansible installation

I suggest to use Ansible from the [github repository](https://github.com/ansible/ansible) to be able to use the most recent modules from the repository as there is a lot of work in progress on the VMware related modules:

```bash
git clone https://github.com/ansible/ansible.git && cd ansible/
```

Personally, I prefer to use a python virtual environment to manage a test or stable environment:

```bash
sudo pip install virtualenv
virtualenv --system-site-packages venv
. venv/bin/activate
```

Install the ansible requirements, and the VMware python sdk:

```
pip install -r requirements.txt
pip install pyvmomi
```

We are now ready to use ansible with VMware modules.

# Ansible usage with VMware vCenter

The following sample consist of VM deployment in a existing vCenter infrastructure from a linked-clone operation.

> *A linked clone is made from a snapshot of the parent. All files available on the parent at the moment of the snapshot continue to remain available to the linked clone. Ongoing changes to the virtual disk of the parent do not affect the linked clone, and changes to the disk of the linked clone do not affect the parent.*

## Inventory

We will create a simple inventory with virtual machines items representing a scalable 2 tiers application with:
* web frontend
* backend workers

```
        [10.10.10.107.0/24]                     External Network
        +--------------------+-------------+-------------------+
                             |             |
                             |             |
                       +-----+----+  +-----+----+
                       |          |  |          |
                       |          |  |          |
                       |   Web    |  |   Web    |
                       | Frontend |  | Frontend |
                       |   # 1    |  |   # 2    |
                       |          |  |          |
                       |          |  |          |
                       +-----+----+  +-----+----+
                             |             |
        [10.10.10.108.0/24]  |             |    Internal Network
        +----------+---------+----+--------+-----+-------------+
                   |              |              |
                   |              |              |
              +----+----+    +----+----+    +----+----+
              |         |    |         |    |         |
              |         |    |         |    |         |
              | Backend |    | Backend |    | Backend |
              | Worker  |    | Worker  |    | Worker  |
              |   # 1   |    |   # 2   |    |   # 3   |
              |         |    |         |    |         |
              |         |    |         |    |         |
              +---------+    +---------+    +---------+
```

To simplify the sample, all virtual machines will not be configured at the application level: we will only cover the deployment of new VM with OS ready for usage.

We create an *INI-like* (one of Ansible's defaults) inventory file named `sample-app01.inv` with the following content:


```ini
[frontweb]
web01 ip="10.10.107.1"
web02 ip="10.10.107.2"

[workers]
worker01 ip="10.10.108.1"
worker02 ip="10.10.108.2"
worker03 ip="10.10.108.3"

[app01:vars]
datastore='Datastore01'
memory='256'
cpucount='1'
guest_id='ubuntu64Guest'
folder='app01'
respool='prod'
snapshot_name='20180129'
dns_domain='lri.lcl'
netmask='255.255.255.0'
dns_server='10.10.10.99'
os_password='VMware1!'
datacenter='DC-Rennes'
cluster='Cust01'

[frontweb:vars]
network1='pg_frontweb'
network2='pg_frontweb'
gateway='10.10.107.254'
template='LinkedCloneRef_Ubuntu16.04_frontweb'

[workers:vars]
network1='pg_backend'
gateway='10.10.108.254'
template='LinkedCloneRef_Ubuntu16.04_worker'
```

In the sample inventory file we have:
* A frontend and workers categories with details about hosts members (including a specific parameters for each one: the IP address): `[frontweb]` + `[workers]`
* An *app01* category including both frontend and workers sub categories: `[app01:children]`
* a group a variables used for all the *app01* members: `[app01:vars]`
* a group a variables used for *frontweb* members
* a group a variables used for *backend* members


## Playbook

From [Ansible Docs about Playbooks](http://docs.ansible.com/ansible/latest/playbooks.html):

> Playbooks are Ansible's configuration, deployment, and orchestration language. They can describe a policy you want your remote systems to enforce, or a set of steps in a general IT process. If Ansible modules are the tools in your workshop, playbooks are your instruction manuals, and your inventory of hosts are your raw material.

### Dynamic input for some values

To manage VM in the vCenter inventory, it's necessary to have credentials for the target. In the following playbook part, we ask user to enter credentials when running the playbook:

```yaml
---
- name: Credentials for vCenter API
  hosts:
    - workers
    - frontweb
  gather_facts: no
  vars_prompt:
    - name: "vcenter_hostname_tmp"
      prompt: "Enter vcenter hostname"
      default: "vcsa01-rennes.lri.lcl"
    - name: "vcenter_user_tmp"
      prompt: "Enter vcenter username"
      default: "administrator@vsphere.local"
    - name: "vcenter_pass_tmp"
      prompt: "Enter vcenter password"
      private: yes

  tasks:
    - set_fact:
        vcenter_hostname: "{% raw %}{{ vcenter_hostname_tmp }}{% endraw %}"
        vcenter_user : "{% raw %}{{ vcenter_user_tmp }}{% endraw %}"
        vcenter_pass : "{% raw %}{{ vcenter_pass_tmp }}{% endraw %}"
```

This playbook part will be applied for both *workers* and *frontweb* servers and we set up global facts to be used in other parts of the playbook.


### Clone specification with vmware_guest module

Ansible's *vmware_guest* module is used to manages virtual machines in vCenter or standalone ESXi. It allows to check the presence and configuration of VM and to proceed changes according to the result: clone, reconfiguration...

Here is a sample task based on the *vmware_guest* to deploy a *worker*'s VM from a linked-clone operation:

```yaml
- hosts: workers
  gather_facts: no
  connection: local

  tasks:
    - name: Deploy workers nodes
      vmware_guest:
        hostname: "{% raw %}{{ vcenter_hostname }}{% endraw %}"
        username: "{% raw %}{{ vcenter_user }}{% endraw %}"
        password: "{% raw %}{{ vcenter_pass }}{% endraw %}"
        name: "{% raw %}{{ inventory_hostname }}{% endraw %}"
        datacenter: "{% raw %}{{ datacenter }}{% endraw %}"
        cluster: "{% raw %}{{ cluster }}{% endraw %}"
        state: poweredon
        template: '{% raw %}{{ template }}{% endraw %}'
        resource_pool: '{% raw %}{{ respool }}{% endraw %}'
        validate_certs: no
        folder: "{% raw %}{{ datacenter }}{% endraw %}/vm/{% raw %}{{ folder }}{% endraw %}"
        guest_id: "{% raw %}{{ guest_id }}{% endraw %}"
        networks:
          - name: "{% raw %}{{ network1 }}{% endraw %}"
            ip: "{% raw %}{{ ip1 }}{% endraw %}"
            netmask: "{% raw %}{{ netmask }}{% endraw %}"
            gateway: "{% raw %}{{ gateway }}{% endraw %}"
            device_type: "vmxnet3"
            dns_servers:
              - "{% raw %}{{ dns_server }}{% endraw %}"
        snapshot_src: "{% raw %}{{ snapshot_name }}{% endraw %}"
        linked_clone: yes
        customization:
          dns_servers:
            - "{% raw %}{{ dns_server }}{% endraw %}"
          domain: "{% raw %}{{ dns_domain }}{% endraw %}"
          dns_suffix: "{% raw %}{{ dns_domain }}{% endraw %}"
          password: "{% raw %}{{ os_password }}{% endraw %}"
        wait_for_ip_address: yes
```

We do the same for the *frontweb* servers with 2 network attachement. See this gist for the full playbook content : [file-create_linked_vms_2tiers-yml](https://gist.github.com/lrivallain/a2fc8443ef4433623d0add3601ab7115#file-create_linked_vms_2tiers-yml).

# Run an Ansible playbook on inventory

To run the playbook:

```bash
./bin/ansible-playbook -i sample-app01.inv create_linked_vms_2tiers.yml
Enter vcenter hostname [vcsa01-rennes.lri.lcl]:
Enter vcenter username [administrator@vsphere.local]:
Enter vcenter password :

PLAY [Credentials for vCenter API] *****************************************************************

TASK [set_fact] ************************************************************************************
ok: [worker01]
ok: [worker02]
ok: [worker03]
ok: [web01]
ok: [web02]
```

In the first part of the execution, credentials are requested to continue. Then Ansible will check if inventory VM's are well `poweredon` are requested in the playbook and if not, will start creation task :

```bash
PLAY [workers] *************************************************************************************

TASK [Deploy workers nodes] ************************************************************************
changed: [worker03]
changed: [worker02]
changed: [worker01]

PLAY [frontweb] ************************************************************************************

TASK [Deploy frontweb nodes] ***********************************************************************
changed: [web01]
changed: [web02]

PLAY RECAP *****************************************************************************************
web01                      : ok=2    changed=1    unreachable=0    failed=0
web02                      : ok=2    changed=1    unreachable=0    failed=0
worker01                   : ok=2    changed=1    unreachable=0    failed=0
worker02                   : ok=2    changed=1    unreachable=0    failed=0
worker03                   : ok=2    changed=1    unreachable=0    failed=0
```

# Idempotency

> Modules should be idempotent, that is, running a module multiple times in a sequence should have the same effect as running it just once. One way to achieve idempotency is to have a module check whether its desired final state has already been achieved, and if that state has been achieved, to exit without performing any actions. If all the modules a playbook uses are idempotent, then the playbook itself is likely to be idempotent, so re-running the playbook should be safe.

In our case, if VMs are already present, re-run the playbook with same settings won't produce new changes.

By replacing the `state: poweredon` by `state: absent` for VMs, it's possible to unprovision the deployed infrastructure.

In the next post(s) I will try to explain the management of vCenter and ESXi hosts configuration through ansible playbooks.
