---
layout: post
title: VMware vCloud Director – Change SSL certificates
category: VMware
author: lrivallain
tags: vmware vcloud director certificate vcd keytool
thumb: /images/vcd.png
---

The following procedure is a self-reminder of How-To replace the certificates of a VMware **vCloud Director** deployment.

* Table of contents
{:toc}

# Prepare informations

Here is a configuration sample for a single cell deployment. Change settings according to your needs:

> If you are using multi-cells deployment, I stronlgy recommend you to extend informations in the `-ext "san=dns:..."` parameter of the certificate creation to include each cell DNS and IP and the VIP FQDN at least. 

```bash
DOMAIN="lri.lcl"

# API and HTTP host info
HTTP_HOSTNAME='vuptime-vcd'
HTTP_IP='10.10.110.3'
HTTP_FQDN="$HTTP_HOSTNAME.$DOMAIN"

# Console proxy host info
CONSOLE_PROXY_HOSTNAME='vuptime-vcd-vmrc'
CONSOLE_PROXY_IP='10.10.110.4'
CONSOLE_PROXY_FQDN="$CONSOLE_PROXY_HOSTNAME.$DOMAIN"

# Others certificates information
VALIDITY=365
CERT_DNAME_INFO="OU=vUptime-IO, O=Example Corp, L=Rennes, S=Britain, C=FR"
CA_CERT_PATH="/tmp/ca-root.cert"

# Keytool informations
KEYTOOL_BIN="$VCLOUD_JAVA_HOME/bin/keytool"
KS_PATH="$VCLOUD_HOME/data/transfer/certificates.ks"
KS_PASSWORD='VMware1!'
```

# Create unsigned certificates

```bash
$KEYTOOL_BIN \
    -keystore $KS_PATH \
    -alias http  \
    -storepass $KS_PASSWORD \
    -keypass $KS_PASSWORD \
    -storetype JCEKS \
    -genkeypair \
    -keyalg RSA \
    -keysize 2048 \
    -validity $VALIDITY \
    -dname "CN=$HTTP_FQDN, $CERT_DNAME_INFO" \
    -ext "san=dns:$HTTP_FQDN,dns:$HTTP_HOSTNAME,ip:$HTTP_IP"

$KEYTOOL_BIN \
    -keystore $KS_PATH \
    -alias consoleproxy \
    -storepass $KS_PASSWORD \
    -keypass $KS_PASSWORD \
    -storetype JCEKS \
    -keyalg RSA \
    -genkeypair \
    -keysize 2048 \
    -validity $VALIDITY \
    -dname "CN=$CONSOLE_PROXY_FQDN, $CERT_DNAME_INFO" \
    -ext "san=dns:$CONSOLE_PROXY_FQDN,dns:$CONSOLE_PROXY_HOSTNAME,ip:$CONSOLE_PROXY_IP"
```

# Create certificate requests for CA-signing

```bash
$KEYTOOL_BIN \
    -keystore $KS_PATH \
    -storetype JCEKS \
    -storepass $KS_PASSWORD \
    -certreq \
    -alias http \
    -file $HTTP_FQDN.csr \
    -ext "san=dns:$HTTP_FQDN,dns:$HTTP_HOSTNAME,ip:$HTTP_IP"

$KEYTOOL_BIN \
    -keystore $KS_PATH \
    -storetype JCEKS \
    -storepass $KS_PASSWORD \
    -certreq \
    -alias consoleproxy \
    -file $CONSOLE_PROXY_FQDN.csr \
    -ext "san=dns:$CONSOLE_PROXY_FQDN,dns:$CONSOLE_PROXY_HOSTNAME,ip:$CONSOLE_PROXY_IP"
```

Send CSR files to your (internal/external) CA for signing, and copy them to cell:
* `ca-root.crt`: the CA certificate
* `vuptime-vcd.lri.lcl.crt`: HTTP certificate
* `vuptime-vcd-vmrc.lri.lcl.crt`: ConsoleProxy certificate

# Import signed certificates in the keystore

First, we import the CA certificate:

```bash
$KEYTOOL_BIN \
    -keystore $KS_PATH \
    -storetype JCEKS \
    -storepass $KS_PASSWORD \
    -import \
    -alias root \
    -file $CA_CERT_PATH
```

Then the 2 applications certificates:

```bash
$KEYTOOL_BIN \
    -keystore $KS_PATH \
    -storetype JCEKS \
    -storepass $KS_PASSWORD \
    -import \
    -alias http \
    -file $CONSOLE_PROXY_FQDN.crt

$KEYTOOL_BIN \
    -keystore $KS_PATH \
    -storetype JCEKS \
    -storepass $KS_PASSWORD \
    -import \
    -alias consoleproxy \
    -file $CONSOLE_PROXY_FQDN.crt
```

```bash
$KEYTOOL_BIN \
    -storetype JCEKS \
    -storepass $KS_PASSWORD \
    -keystore $KS_PATH \
    -list
```

# Apply certificates to the services

```bash
$VCLOUD_HOME/bin/cell-management-tool certificates -j -k $KS_PATH -w $KS_PASSWORD
service vmware-vcd restart
```
