---
layout: card
title: Resolve error migrating vRO to 7.5
author: bclouet
tags: vmware vrealize vro
date: 2018-11-15
---

You want to migrate an existing vRO instance (6.X, 7.X) to 7.5.
After following the procedure and clicking **Validate** on the Migrate tab of the target vRO 7.5, you encounter the following error:

![alt text](https://github.com/lrivallain/vuptime/tree/master/images/vro/Error_cannot_connect_db.png)

In that case, follow these steps to correct the error: 
If your source vRO database is a built-in PostgreSQL database, edit its database configuration files.
1.	Connect to your source vRO using SSH.
2.	Append or uncomment if existing the following line to the `/var/vmware/vpostgres/current/pgdata/postgresql.conf` file. `listen_addresses =’*’`
3.	Append or uncomment if existing the following line to the `/var/vmware/vpostgres/current/pgdata/pg_hba.conf` file. `host all all {ip-of-n ew-vro-appliance}/32 md5`
4.	Restart the PostgreSQL server service. service vpostgres restart
Retry the validation process. You should now no longer encounter this error.


