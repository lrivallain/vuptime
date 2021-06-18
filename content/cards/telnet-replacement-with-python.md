---
layout: card
title: Replace telnet with a python script
author: lrivallain
tags:
- linux
- python
- gist
date: 2018-06-26
---

On some editor's Linux based appliance(s), there is not telnet binary installed. To test TCP netwotk flows, it's possible to use python's socket module with a short script:

```python
#!/usr/bin/python

import socket
import sys

if len(sys.argv) != 3:
    print("usage: telnet.py IPADDRESS PORT")
    exit(-1)

print("Opening connection on %s port %s" % (sys.argv[1], sys.argv[2]))

try:
    conn=socket.create_connection((sys.argv[1],sys.argv[2]),timeout=30)
except socket.timeout:
    print("Connection error: timeout")
    exit(-1)
except:
    print("Connection error: unknown")
    exit(-1)
print("Connection succeed")
exit(0)
```

Usage:
```bash
$ python telnet.py
usage: telnet.py IPADDRESS PORT
```

✅ Successful test:
```bash
$ python telnet.py 10.10.10.10 443
Opening connection on 10.10.10.10 port 443
Connection succeed
```

❌ Failed test:
```bash
$ python telnet.py 10.10.10.10 10443
Opening connection on 10.10.10.10 port 10443
Connection error: unknown
```

