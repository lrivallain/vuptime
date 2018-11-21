---
layout: card
title: vRealize Orchestrator – Error while migrating to 7.5
tags: vmware vrealize vro
date: 2018-11-15
---

If you want to migrate an existing vRO instance (6.X, 7.X) with built-in PostgreSQL database to vRO 7.5, you might encounter the following error during DB migration process:

![alt text](/images/vro/Error_cannot_connect_db.png)

In that case, follow these steps to correct the error:

* Connect to your source vRO using SSH.
* **Append or uncomment** if existing the following line to the `/var/vmware/vpostgres/current/pgdata/postgresql.conf` file:

```
listen_addresses =’*’
```

* **Append or uncomment** if existing the following line to the `/var/vmware/vpostgres/current/pgdata/pg_hba.conf` file:

```
host all all {ip-of-n ew-vro-appliance}/32 md5
```

* Restart the PostgreSQL server service:

```bash
service vpostgres restart
```

Retry the validation process. You should now no longer encounter this error.