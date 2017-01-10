---
layout: post
title: Openstack - Migrate keystone endpoint URL
category: Openstack
tags: openstack keystone endpoint
---

After a DNS record change for the controller node of our lab OpenStack infrastructure, Horizon client was still displaying the old endpoint DNS hostname in the ``API access``.

![Old API access settings](/images/MigrateOpenstackKeystoneUrl/before.png "Old API access settings")

This information is coming from the keystone database, so we need to proceed a c

List endpoints list, filtered on interface ``public``:

```bash
$ openstack endpoint list --interface public"
+----------------------------------+-----------+--------------+--------------+---------+-----------+----------------------------------------------------------+
| ID                               | Region    | Service Name | Service Type | Enabled | Interface | URL                                                      |
+----------------------------------+-----------+--------------+--------------+---------+-----------+----------------------------------------------------------+
| ********199a432b9da62586f978b2ee | RegionOne | glance       | image        | True    | public    | http://controller:9292                                   |
| ********de5b490d8d51b45dc1766999 | RegionOne | cinder       | volume       | True    | public    | http://controller:8776/v1/%(tenant_id)s                  |
| ********a042463397613d0304812f38 | RegionOne | cinderv2     | volumev2     | True    | public    | http://controller:8776/v2/%(tenant_id)s                  |
| ********a4e446169a4ff9f0e6865f54 | RegionOne | keystone     | identity     | True    | public    | http://controller:5000/v3                                |
| ********8ce74fcd860f0f63000cf2f4 | RegionOne | swift        | object-store | True    | public    | http://controller:8080/v1/AUTH_%(tenant_id)s             |
| ********1dcb42ac8f6592ae2c0aacab | RegionOne | neutron      | network      | True    | public    | http://controller:9696                                   |
| ********b0ba4d6c87e4c20e18230a39 | RegionOne | nova         | compute      | True    | public    | http://controller:8774/v2.1/%(tenant_id)s                |
+----------------------------------+-----------+--------------+--------------+---------+-----------+----------------------------------------------------------+
```

The same information from database side:

```
$ mysql keystone
MariaDB [keystone]> select id,url from keystone.endpoint where interface='public' ;
+----------------------------------+----------------------------------------------+
| id                               | url                                          |
+----------------------------------+----------------------------------------------+
| ********199a432b9da62586f978b2ee | http://controller:9292                       |
| ********de5b490d8d51b45dc1766999 | http://controller:8776/v1/%(tenant_id)s      |
| ********a042463397613d0304812f38 | http://controller:8776/v2/%(tenant_id)s      |
| ********a4e446169a4ff9f0e6865f54 | http://controller:5000/v3                    |
| ********8ce74fcd860f0f63000cf2f4 | http://controller:8080/v1/AUTH_%(tenant_id)s |
| ********1dcb42ac8f6592ae2c0aacab | http://controller:9696                       |
| ********b0ba4d6c87e4c20e18230a39 | http://controller:8774/v2.1/%(tenant_id)s    |
+----------------------------------+----------------------------------------------+
7 rows in set (0.00 sec)
```

The query to change the endpoint url:

```
MariaDB [keystone]> update keystone.endpoint SET url = REPLACE(url, 'controller', 'newurl.domain.tld') WHERE interface='public';
Query OK, 7 rows affected (0.00 sec)
Rows matched: 7  Changed: 7  Warnings: 0
```

And the result:

```
MariaDB [keystone]> select id,url from keystone.endpoint where interface='public' ;
+----------------------------------+----------------------------------------------------------+
| id                               | url                                                      |
+----------------------------------+----------------------------------------------------------+
| 30da1779199a432b9da62586f978b2ee | http://newurl.domain.tld:9292                            |
| 4b14eeb0de5b490d8d51b45dc1766999 | http://newurl.domain.tld:8776/v1/%(tenant_id)s           |
| 62fb579da042463397613d0304812f38 | http://newurl.domain.tld:8776/v2/%(tenant_id)s           |
| 976bf154a4e446169a4ff9f0e6865f54 | http://newurl.domain.tld:5000/v3                         |
| c158b4718ce74fcd860f0f63000cf2f4 | http://newurl.domain.tld:8080/v1/AUTH_%(tenant_id)s      |
| df0b3f6f1dcb42ac8f6592ae2c0aacab | http://newurl.domain.tld:9696                            |
| ee2b5119b0ba4d6c87e4c20e18230a39 | http://newurl.domain.tld:8774/v2.1/%(tenant_id)s         |
+----------------------------------+----------------------------------------------------------+
7 rows in set (0.00 sec)
```

To apply the change, we restart memcached and keystone service:
```bash
service keystone restart
service memcached restart
```

Now the endpoint displayed from the horizon portal is updated with the new URL :

![New API access settings](/images/MigrateOpenstackKeystoneUrl/after.png "New API access settings")
