---
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
date: "2017-08-30T00:00:00Z"
tags:
- vmware
- vcd
- vcloud
- java
- jre
- certificate
title: VMware - Patch the vCloud Director cacerts file
aliases: 
- /2017/08/30/VMware-Patch-vCloudDirector-cacerts-file/
toc: true
---

When you install a VMware vCloud Director instance, it comes with an embedded JRE (*Java Runtime Environment*). For example, vCloud Director includes JRE 1.8.0_121 :

```bash
$VCLOUD_HOME/jre/bin/java -version
java version "1.8.0_121"
Java(TM) SE Runtime Environment (build 1.8.0_121-b13)
Java HotSpot(TM) 64-Bit Server VM (build 25.121-b13, mixed mode)
```

JRE includes it's own keystore for trusted SSL certificates, the `cacerts` file. This file is depending on both oracle/Java and VMware/vCloud releasing and if your certification authority root certificate isn't included, you may experienced issue when trying to communicate with products securized with SSL certificates (example : [Catalog synchronization between two vCloud Director entities](/2017/08/02/VMware-ExploreVCD-catalog-publishing-feature/)).

It's possible to find SSL related issues by looking at the `$VCLOUD_HOME/logs/vcloud-container-debug.log` file where you may find errors like:
```
...
javax.net.ssl.SSLHandshakeException: sun.security.validator.ValidatorException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
...
```

The following post shows how to add a new trusted (root and/or intermediate) certificates to the JRE cacerts keystore.

# Is you certification authority already trusted ?

According to the authority that issued your certificates, get the corresponding `crt` files and their sha1 fingerprint.

For example, if you use [Let's Encrypt](https://letsencrypt.org) :

In [Let's Encrypt case, you need 2 certificates](https://letsencrypt.org/certificates/):
* DST Root CA X3
* Let's Encrypt Authority X3

```bash
# get crt files
curl -s "https://pastebin.com/raw/63dQV36A" > DSTRootCAX3.crt
curl -s "https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem.txt" > LetsEncryptAuthorityX3.crt
# calculate fingerprint
intermediate=$(openssl x509 -in /tmp/LetsEncryptAuthorityX3.crt -fingerprint -sha1 -noout | cut -d'=' -f2)
root=$(openssl x509 -in /tmp/DSTRootCAX3.crt -fingerprint -sha1 -noout | cut -d'=' -f2)
```

Now you have two variables `$root` and `$intermediate` with cert authority sha1:
```bash
echo "$root
$intermediate"
DA:C9:02:4F:54:D8:F6:DF:94:93:5F:B1:73:26:38:CA:6A:D7:7C:13
E6:A3:B4:5B:06:2D:50:9B:33:82:28:2D:19:6E:FE:97:D5:95:6C:CB
```

Let's look in the keystore to check if the certificates are already trusted. For this, we use the Java `keytool` script that allow to manage the Java's keystore :

```bash
$VCLOUD_HOME/jre/bin/keytool -list -keystore $VCLOUD_HOME/jre/lib/security/cacerts -storepass changeit | grep -i -B1 $root
$VCLOUD_HOME/jre/bin/keytool -list -keystore $VCLOUD_HOME/jre/lib/security/cacerts -storepass changeit | grep -i -B1 $intermediate
```

If there is no result, for both commands, you should add your certification authority to the trusted ones.

By default, the JRE keystore is *protected* with a password: `changeit`.

> **Note** : The letsencrypt sample is purely fictional as the Root certificate `DSTRootCAX3` is already included in the included JRE keystore. But for the post, we will act as it is not.

# Update JRE keystore

So your certification authority, possible internal and self-signed, is not known from the JRE keystore and you need to communicate between your vCloud Director and product using certificates issued from this authority. Therefore an update of the trusted certificates is required.

We still use the (*fabulous*) Java `keytool` script to insert new certificates to the keystore.

These operations needs to be done on **each cells** of your vCloud Director instance as the JRE keystore is not shared between members.

## Take a backup of cacerts file

Take a backup of the embedded keystore, to be able to rollback if necessary (md5sum is used to quiclky check that we copy the file without error):

```bash
cp -f $VCLOUD_HOME/jre/lib/security/cacerts ~/cacerts_jre.backup
md5sum ~/cacerts_jre.backup $VCLOUD_HOME/jre/lib/security/cacerts
```

```
#2ecfd7e5a8789c3f0e68ae85a26dea23  ~/cacerts_jre.backup
#2ecfd7e5a8789c3f0e68ae85a26dea23  $VCLOUD_HOME/jre/lib/security/cacerts
```

## Add the CA certs to the keystore

Time to update keystore content :

```bash
$VCLOUD_HOME/jre/bin/keytool \
    -import -trustcacerts \
    -alias identrustdstx3 \
    -file /tmp/DSTRootCAX3.crt \
    -keystore $VCLOUD_HOME/jre/lib/security/cacerts \
    -storepass changeit

$VCLOUD_HOME/jre/bin/keytool \
    -import -trustcacerts \
    -alias letsencryptx3 \
    -file /tmp/LetsEncryptAuthorityX3.crt \
    -keystore $VCLOUD_HOME/jre/lib/security/cacerts \
    -storepass changeit
```

And we check:
```bash
$VCLOUD_HOME/jre/bin/keytool -list -keystore $VCLOUD_HOME/jre/lib/security/cacerts -storepass changeit | grep -i $root -c
1
$VCLOUD_HOME/jre/bin/keytool -list -keystore $VCLOUD_HOME/jre/lib/security/cacerts -storepass changeit | grep -i $intermediate -c
1
```

One result is found for each certificate : good.

It's also possible to look in keystore for a specific alias entry without `grep`, but depending on used alias, I consider that it's possible to miss a match (that's why I prefer to calculate the fingerprint and made a search on it):

```bash
$VCLOUD_HOME/jre/bin/keytool -list -keystore $VCLOUD_HOME/jre/lib/security/cacerts -storepass changeit -alias "identrustdstx3"
identrustdstx3, Aug 25, 2016, trustedCertEntry,
Certificate fingerprint (SHA1): DA:C9:02:4F:54:D8:F6:DF:94:93:5F:B1:73:26:38:CA:6A:D7:7C:13
```

# Shutdown cell

Once done, each cell needs to be 'service-restarted' in order to use the new keystore:

> **Note** :Do not forget to move the vCenter proxy role before restarting cells.

Quiesce the cell, to not accept new incoming job on this specific cell:

```bash
$VCLOUD_HOME/bin/cell-management-tool -u administrator -p '********' cell -quiesce true
```

Check that there is no more running job:

```bash
$VCLOUD_HOME/bin/cell-management-tool -u administrator -p '********' cell -status
```

> **Note:** Since a couple of versions, when you use the `quiesce true` command, the command is not returning prompt until there is no more job left on the cell. The status command could be considered as useless.

Shutdown services:

```bash
$VCLOUD_HOME/bin/cell-management-tool -u administrator -p '********' cell -shutdown
```

Then restart services:

```bash
service vmware-vcd start
```

Have a look on the startup of the service through the logs:

```bash
tail -f $VCLOUD_HOME/logs/cell.log | grep -i "Application Initialization"
```

> **Note** : A better documentation about the cell shutdown is available in [official VMware documentation about vCD](http://pubs.vmware.com/vcd-820/index.jsp#com.vmware.vcloud.install.doc/GUID-65C8B7B6-EC5E-4BDA-8564-56DD6671F5FE.html?resultof=%2522%2573%2568%2575%2574%2564%256f%2577%256e%2522%2520)

When all cells are restarted, your issue with certificate chain should be solved.
