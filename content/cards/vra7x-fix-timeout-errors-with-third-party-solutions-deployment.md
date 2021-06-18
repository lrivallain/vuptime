---
layout: card
title: vRealize Automation 7.x – Fix timeout errors with third party solutions deployment
tags:
- vmware
- vrealize
- automation
- vra
date: 2018-07-02
---

The time required to fetch information on a third party deployment platform (like Azure virtual machine's current and available public address) through vRealize Orchestrator can take too long and raise SocketTimeout errors. The process times out in vRealize Automation with this error message: "The connection to vCenter Orchestrator Server time out.".
To resolve this issue, connect on vRA appliances through SSH to run the following commands:

```bash
# STOP vRA service
service vcac-server stop

sed -i.bak -r 's/socketTimeout(.*)30000/socketTimeout\1300000/' /etc/vcac/webapps/o11n-gateway-service/WEB-INF/classes/META-INF/spring/root/o11n-gateway-service-context.xml

echo "# increase timeout for vco socket requests
vco.socket.timeout.millis=300000" >> /etc/vcac/vcac.properties

sed -i.bak 's/shindig.http.client.read-timeout-ms=150000/shindig.http.client.read-timeout-ms=300000/' /var/lib/vcac/server/webapps/vcac/WEB-INF/classes/shindig.properties

echo '# increase timeout for vco socket requests
VCAC_OPTS="$VCAC_OPTS -Dclient.system.socket.timeout=300000"' >> /etc/vcac/setenv-user

# start vRA service
service vcac-server start
```
