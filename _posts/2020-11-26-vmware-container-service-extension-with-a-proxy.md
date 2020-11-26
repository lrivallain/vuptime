---
layout: post
title: Use VMware Container Service Extension with a corporate proxy
category: VMware
author: lrivallain
tags: vmware kubernetes cse vcloud director extension
thumb: /images/vmwopensource.jpg
---

The current post is a quickstart to VMware open-source project Container Service Extension (CSE), a Kubernetes as a Service for VMware vCloud Director.

The project is already well documented ([CSE documentation](https://vmware.github.io/container-service-extension/)) and you should not have any trouble to set it up by following the installation steps.

Except... if you plan to use it behind a corporate proxy to access to Internet. The goal of this post is to be a reminder to me for this kind of setup.

* Table of contents
{:toc}

## CSE server appliance

The first step to setup CSE is to prepare an appliance that will host the CSE server component. In my case, I used a freshly deployed Ubuntu 20.04 LTS server, deployed from the ubuntu cloud images repository: https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.ova

Once the appliance is up and running, I setup the proxy information:

`W.X.Y.Z` is the IP address of my HTTP based proxy.

```bash
echo "HTTP_PROXY=W.X.Y.Z:3128
HTTPS_PROXY=W.X.Y.Z:3128
NO_PROXY=.vlab.lcl,192.168.0.0/16,127.0.0.1,localhost" | sudo tee -a /etc/environment >/dev/null

export HTTP_PROXY="W.X.Y.Z:3128"
export HTTPS_PROXY="W.X.Y.Z:3128"
export NO_PROXY=".vlab.lcl,192.168.0.0/16,127.0.0.1,localhost"

echo "Acquire::http::proxy \"http://W.X.Y.Z:3128\";" | sudo tee -a /etc/apt/apt.conf >/dev/null
```

A quick test:

```bash
curl https://google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="https://www.google.com/">here</A>.
</BODY></HTML>
```

It works.

### CSE server components

Let's install software components required for CSE:

```bash
# vcd-cli + CSE
sudo apt-get install python3-pip gcc -y
sudo pip3 install vcd-cli
sudo pip3 install container-service-extension==2.6.1
```

Yep, still using CSE 2.6 for backwards compatibility.

Next, we install `kubectl`:

```bash
# kubectl
curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
# Test it:
kubectl version --client
```

### `vcd` CLI integration

Quick method to integrate the `cse` CLI to the `vcd` CLI:

```bash
mkdir -p ~/.vcd-cli/
echo "extensions:
- container_service_extension.client.cse" >> ~/.vcd-cli/profiles.yaml
# Test it:
vcd cse version
```

### Authentication key pairs

If needed, create a SSH key pair to be used from this appliance, to the K8S nodes for maintenance:

```bash
ssh-keygen
```

## CSE configuration

Once our appliance is ready to host CSE server, we can configure it:

```bash
mkdir ~/.cse
cse sample -o ~/.cse/decrypted-config.yaml
```

This command will create a `~/.cse/decrypted-config.yaml` file to configure according to the [reference documentation](https://vmware.github.io/container-service-extension/cse2_6/CSE_CONFIG.html).

To ease the testing, I made a *fork* of the [official templates repository](https://github.com/vmware/container-service-extension-templates) to my GitHub workspace with [only one ubuntu based template](https://github.com/lrivallain/container-service-extension-templates):

```yaml
templates:
  - compute_policy: ""
    cpu: 2
    deprecated: false
    description: "Ubuntu 16.04, Docker-ce 19.03.12, Kubernetes 1.18.6, weave 2.6.5"
    mem: 2048
    name: ubuntu-16.04_k8-1.18_weave-2.6.5
    revision: 1
    kind: native
    sha256_ova: 3c1bec8e2770af5b9b0462e20b7b24633666feedff43c099a6fb1330fcc869a9
    source_ova: "https://cloud-images.ubuntu.com/releases/xenial/release-20180418/ubuntu-16.04-server-cloudimg-amd64.ova"
    source_ova_name: ubuntu-16.04-server-cloudimg-amd64.ova
    os: "ubuntu-16.04"
    docker_version: "19.03.12"
    kubernetes: "upstream"
    kubernetes_version: "1.18.6"
    cni: "weave"
    cni_version: "2.6.5"
    upgrade_from:
    - "ubuntu-16.04_k8-1.17_weave-2.6.0"
    - "ubuntu-16.04_k8-1.18_weave-2.6.5"
```

Now we encrypt the file:

```bash
cse encrypt ~/.cse/decrypted-config.yaml --output ~/.cse/config.yaml
chmod 600 config.yaml
rm ~/.cse/decrypted-config.yaml # otherwise it will be useless to encrypt it
```

If you need to decrypt it (for example to edit the content):

```bash
cse decrypt  ~/.cse/config.yaml --output ~/.cse/decrypted-config.yaml
```

Then you can run the install process...

> **!!!BUT!!!** We will kill it when the process will download the OVA file(s) in order to hack the content of customization scripts:

```bash
cse install -c ~/.cse/config.yaml --ssh-key ~/.ssh/id_rsa.pub
# !! cut the execution when the OVA is downloading !! CTRL+C
```

When the script is stopped, it is possible to edit the content of customization scripts to insert the proxy settings. In my case:

```bash
vi ~/.cse_scripts/ubuntu-16.04_k8-1.18_weave-2.6.5_rev1/cust.sh
```

I added the following lines at the beginning  of the file, just after the line `set -e`:

```bash
# proxy setup
echo "HTTP_PROXY=W.X.Y.Z:3128
HTTPS_PROXY=W.X.Y.Z:3128
NO_PROXY=.vlab.lcl,192.168.0.0/16,127.0.0.1,localhost" >> /etc/environment
echo "Acquire::http::proxy \"http://W.X.Y.Z:3128\";" >> /etc/apt/apt.conf
export HTTP_PROXY="W.X.Y.Z:3128"
export HTTPS_PROXY="W.X.Y.Z:3128"
export NO_PROXY=".vlab.lcl,192.168.0.0/16,127.0.0.1,localhost"
```

Save+quit etc. And we re-run the CSE initialisation command:

```bash
cse install -c ~/.cse/config.yaml --ssh-key ~/.ssh/id_rsa.pub
```

And your template will now being built using the HTTP proxy you specified. After the template preparation, the template is added to the available ones:

```bash
cse template list -c ~/.cse/config.yaml
Password for config file decryption:
Decrypting 'config.yaml'
name                                revision  compute_policy    local    remote
--------------------------------  ----------  ----------------  -------  --------
ubuntu-16.04_k8-1.18_weave-2.6.5           1                    Yes      Yes
```
> *(I removed some columns to ease the post reading)*

### Patching Pika for Python 3.8

In the next steps, if you use Python version 3.8 (you can check it by running ` python3 -V` command), you may have an issue with an error message like:

```bash
 vcd cse template list
Usage: vcd cse template list [OPTIONS]
Try "vcd cse template list -h" for help.

Error: maximum recursion depth exceeded
```

You can patch the Pika library by applying a patch made from this [Pull request from @lukebakken](https://github.com/pika/pika/pull/1254).

Two choices:

 1. Download manually this [patch file](https://gist.github.com/lrivallain/be77cd8ffd731649705ae7b1e139d8d3#file-pika-1254-patch) and run `patch` command:

```bash
sudo patch /usr/local/lib/python3.8/dist-packages/pika/compat.py < pika-1254.patch
```

2. All in one command (you should check the content of a downloaded file before applying it to you environment):

```bash
curl -s 'https://gist.githubusercontent.com/lrivallain/be77cd8ffd731649705ae7b1e139d8d3/raw/d35069fab35f179dd1a76f29607367424d87314a/pika-1254.patch' | sudo patch /usr/local/lib/python3.8/dist-packages/pika/compat.py
```


### Tests

The following command will run the CSE server services in foreground mode

```bash
cse run -c ~/.cse/config.yaml
```

After a series of checks, the process should display a message like:

> `waiting for requests (ctrl+c to close)`

You can test it by running the following commands from another terminal instance:

```bash
vcd login vcd.vlab.lcl <org> <username>
vcd cse template list
```

And you should get a list of templates ready for deployment:

```bash
name                                revision  is_default    catalog
--------------------------------  ----------  ------------  ---------
ubuntu-16.04_k8-1.18_weave-2.6.5           1  Yes           cse
```
> *(I removed some columns to ease the post reading)*

### Finalize installation

Using the CSE server in foreground mode is not the easiest way for day-to-day operations, so we will enable it as a system service:


```bash
# get the service files from the CSE repository
curl -L https://github.com/vmware/container-service-extension/raw/2.6.1_ga/cse.service > ~/.cse/cse.service
curl -L https://github.com/vmware/container-service-extension/raw/2.6.1_ga/cse.sh > ~/.cse/cse.sh
chmod +x ~/.cse/cse.sh
```

Edit the `CSE_CONFIG_PATH` value of `~/.cse/cse.sh` according to the path where is stored your configuration file. For my setup:

```bash
CSE_CONFIG_PATH=/home/ubuntu/.cse/config.yaml
```

Edit the `ExecStart`, `User`, `WorkingDirectory` value of `~/.cse/cse.service` according to your environment. I also add an `Environment` statement to store the password of the configuration file and my proxy settings.

For my setup:

```ini
[Unit]
Description=Container Service Extension for VMware vCloud Director
Wants=network-online.target
After=network-online.target

[Service]
ExecStart=/home/ubuntu/.cse/cse.sh
User=ubuntu
WorkingDirectory=/home/ubuntu/.cse/
Type=simple
Restart=always
Environment=CSE_CONFIG_PASSWORD="VMware1!"
Environment=HTTP_PROXY="W.X.Y.Z:3128"
Environment=HTTPS_PROXY="W.X.Y.Z:3128"
Environment=NO_PROXY=".vlab.lcl,192.168.0.0/16,127.0.0.1,localhost"

[Install]
WantedBy=default.target
```

Then you can enable, start and check this new service:

```bash
sudo cp .cse/cse.service /etc/systemd/system/
sudo systemctl enable cse
sudo systemctl start cse
sudo systemctl status cse
```

## Conclusion

You now have a fully working CSE appliance, running behind a corporate proxy and you can use it from any location with an access to the vCD instance.

You can find more details on the way to create/manage CSE K8S clusters in the [CSE documentation](https://vmware.github.io/container-service-extension/cse2_6/CLUSTER_MANAGEMENT.html).

Of course, if you can afford to store a fork of the [official templates repository](https://github.com/vmware/container-service-extension-templates) with your proxy informations and your customisations, it could ease the deployment of new templates when needed: for example by setting up a *private* or *internal* git repository.