---
layout: card
title: OpenSSL - Get certificate as file
author: lrivallain
tags: openssl certificate bash
date: 2018-07-16
---

Export the SSL certificate(s) of a server to a `.pem` file:

```bash
TARGET_HOST="fqdn_of_target_host"
TARGET_PORT="443"
openssl s_client -showcerts -connect $TARGET_HOST:$TARGET_PORT </dev/null 2>/dev/null|openssl x509 -outform PEM > $TARGET_HOST.pem
```

