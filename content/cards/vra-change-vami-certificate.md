---
layout: card
title: vRealize Automation – Change the VAMI certificate
author: lrivallain
author_name: Ludovic Rivallain
tags:
- vmware
- vrealize
- automation
- vra
- vami
- certificate
date: 2018-07-25
---

Set the certificate private key password in a shell variable

```bash
INKEY="<<CERT_PASSPHRASE>>"
```

Get a PFX file from original cert

```bash
openssl pkcs12 -export \
    -in <<fqdn>>.crt \
    -inkey <<fqdn>>.key \
    -certfile ca-root.crt \
    -name "rui" \
    -passout pass:$INKEY \
    -out <<fqdn>>.pfx
```

Get PEM file from orginial cert

```bash
openssl pkcs12 \
    -in <<fqdn>>.pfx \
    -inkey <<fqdn>>.key \
    -out <<fqdn>>.pem \
    -nodes \
    -passin pass:$INKEY
```

Replace lighttpd certificates

```bash
mv /opt/vmware/etc/lighttpd/server.pem /opt/vmware/etc/lighttpd/server.pem-bak
cp <<fqdn>>.pem /opt/vmware/etc/lighttpd/server.pem
service vami-lighttp restart
```
