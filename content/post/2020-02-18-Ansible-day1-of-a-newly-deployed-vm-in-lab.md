---
author: lrivallain
author_name: Ludovic Rivallain
categories:
- Ansible
date: "2020-02-18T00:00:00Z"
tags:
- ansible
- devops
thumbnail: /images/ansible.png
title: Ansible/Day 1 of a newly deployed VM in my home lab
aliases: 
- /2020/02/18/Ansible-day1-of-a-newly-deployed-vm-in-lab/
toc: true
---

Ansible is [a great tool for someone as lazy as I can be](/2018/02/07/ansible-vmware_modules_-_first_steps/) and it helps me daily to automatize some regular or time consuming tasks.

Ansible way to manage remote resources Linux based OS is mainly based on SSH protocol when it deals with OS or application customization/settings/configuration. By using public-key authentication mechanism it is possible to avoid using password and being prompt for every action.

This post will explain how I setup a newly deployed VM in my lab environment to be usable by Ansible+public-key authentication.

> **Warning:** Most of the following described tasks may affect the security of the target environment. I mainly use them in a lab environment for testing / debugging purposes. Be carreful of using those examples for other needs.
>
> * `root` password expiration policy and *shell idle timeout* are security policies that can be required in a production environment (and so, do not apply the example tasks in such case.)
> * SSH server authentication keys are very important for security concerns too and should not be blindly trusted.


## Server authentication

When you connect by SSH to a remote server, you need to trust the key provided by the server. You probably already know the below message:

```bash
ssh root@mynewserver
The authenticity of host 'mynewserver (10.10.100.2)' can't be established.
ECDSA key fingerprint is SHA256:u0cQf5a5f1DAoCWwqDGfCOjtWR+LdXrmSFo5XJKnEsE.
Are you sure you want to continue connecting (yes/no)?
```

And as most of users, you probably never check the fingerprint before accepting to store it in a `known_hosts` file.

In a highly secure environment, it is highly recommended to cross-check this fingerprint from the server itself before trusting it. This can be achieved by using the `ssh-keygen -l` command:

```bash
ssh-keygen -l -f /etc/ssh/ssh_host_ecdsa_key.pub
256 SHA256:u0cQf5a5f1DAoCWwqDGfCOjtWR+LdXrmSFo5XJKnEsE root@mynewserver (ECDSA)
```

> In cloud instances using `cloud-init` the fingerprints of key generated during the instance deployment, is commonly available in the console logs: it could help to retrieve it for comparison.

In the above example, the *ECDSA* fingerprint match and you can trust it by accepting the confirmation from the SSH client.

### Blind trust SSH servers keys with Ansible

For system out of production (testing purpose), I do not make the above check and I make a *"blind"* consent on the first seen key.

I use the following Ansible tasks to do so:

{% raw  %}
```yaml
tasks:
- name: Remove any existing fingerprints from known_hosts
  local_action:
    shell
    ssh-keygen -R {{ inventory_hostname }};
    ssh-keygen -R {{ inventory_hostname_short }};
    ssh-keygen -R {{ lookup('dig', '{{ inventory_hostname }}')}}
  retries: 1
  delay: 3

- name: Add host rsa and ecdsa fingerprints to known_hosts
  local_action:
    shell
    ssh-keyscan {{ inventory_hostname_short }} >> $HOME/.ssh/known_hosts
    ssh-keyscan {{ inventory_hostname }} >> $HOME/.ssh/known_hosts
```
{% endraw %}

Applied to a specific inventory or host group, it will remove existing key from the `known_hosts` file and add it again based on the result of a `ssh-keyscan`.

## Public key user authentication

As we have seen, server can be authenticated using SSH public keys. We can also use this mechanism to authenticate user(s) against a server.

Here is a quick(&dirty) explanation of the process:

1. User generates a personal private key
2. User provides the public key (generated from the private key) to the server where he needs to connect to.
3. The user's public key is stored in an `authorized_keys` file (`'~/.ssh/authorized_keys` or `/etc/ssh/authorized_keys/%u`.
4. When user connect to this server+account, he uses its private key to authenticate and a check is made between the provided informations and the content of `authorized_keys` file.
5. If key is trusted, user can access to the server. If not, user connection is rejected (or he needs to use another method, like password prompt.)

> In cloud instances using `cloud-init` it is possible to provide public keys to store on the instance at deployment. In that case, public key authentication is immediately available on the server.

If you don't use a `cloud-init` based clone or server creation, you can use an Ansible playbook to push keys to the target server:

{% raw  %}
```yaml
tasks:
- name: Upload ssh key
  authorized_key:
    user: root
    path: "{{ authorized_keys_path }}"
    state: present
    manage_dir: yes
    key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
```
{% endraw %}

And if there is no already deployed authorized key to enable Ansible user to connect to your instance, you can use a one-shot `--ask-pass` option to run your playbook:

```bash
ansible-playbook playbooks/ssh_setup.yml -i inventories/lab.yml --ask-pass
SSH password: *********
```

You will be prompt to provide the account password. Once pushed, you can use the public key as an authentication mechanism for Ansible instead of passwords:

```bash
ansible-playbook playbooks/ssh_setup.yml -i inventories/lab.yml
```

> Please note that `--ask-pass` is no more necessary to run a playbook, based on SSH protocol to your target once the ansible user public key is installed.

## Password expiration

When using editor's appliance (like VMware's ones), you may need to reconfigure the password expiration for the `root` account. For lab and testing purposes, I fully disable the expiration policy with the following tasks:

{% raw  %}
```yaml
tasks:
  - name: "Check expiration for {{ admin_user }} password"
    shell: "getent shadow {{ admin_user }} | cut -d':' -f5"
    register: pw_invalid_expiration
    changed_when: False

  - name: "Unset expiration for {{ admin_user }} password"
    shell: "chage -M -1 {{ admin_user }}"
    when: pw_invalid_expiration.stdout != ''
```
{% endraw %}

## Shell idle timeout

As for the above policy, I have a couple of ansible tasks to disable the [*shell idle timeout*](https://www.thegeekstuff.com/2010/05/tmout-exit-bash-shell-when-no-activity/) in lab and testing environments:

```yaml
tasks:
  - name: Changing SSH session TMOUT - part 1
    lineinfile:
      path: /etc/profile.d/tmout.sh
      regexp: '^TMOUT.*'
      line: 'TMOUT=""'

  - name: Changing SSH session TMOUT - part 2
    lineinfile:
      path: /etc/profile.d/tmout.sh
      regexp: '.*readonly TMOUT'
      line: '#readonly TMOUT'
```

> **Warning:** As mentionned above, most of the previous tasks may affect the security of the target environment: use this content with caution.