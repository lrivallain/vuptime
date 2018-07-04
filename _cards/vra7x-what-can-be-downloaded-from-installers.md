---
layout: card
title: vRealize Automation 7.x – What can be downloaded from appliance "installers" folder
author: lrivallain
tags: vmware vrealize automation vra
date: 2018-06-20
---

If you are familiar with the vRealize Automation installation process, you probably already know that it is possible to download some usefull files from the *"installers"* page. You can access to the *"installers"* with two URLs: `https://vrava.domain/installers` (most commun URL) or `https://vrava.domain/i` (the shortcut one).

The *"installers"* page let you to download easly some files by clicking on the available links:

![The vRA installers page](/images/vra-installers.png)

But it also contains *hidden* files that you can also download from this path if you know the filename. To get the list of available files, list the content of the `/opt/vmware/share/htdocs/service/iaas/download/` folder of an appliance.

For example with vRealize Automation 7.4:

```bash
ls -lh /opt/vmware/share/htdocs/service/iaas/download/
total 452M
-rwxr--r-- 2 root root  17M Apr  5 08:33 Burma.Dem.Installer.msi
-rwxr--r-- 1 root root 1.8M Apr  5 08:33 DBInstall.zip
-rwxr--r-- 1 root root 1.9M Apr  5 08:33 DBUpgrade.zip
-rwxr--r-- 1 root root  14M Apr  5 08:33 DesignCenter-Setup.exe
-rwxr--r-- 1 root root  14M Apr  5 08:33 DesignCenter.msi
-rwxr--r-- 1 root root 2.0M Apr  5 08:33 GuestAgentInstaller.exe
-rwxr--r-- 1 root root 2.4M Apr  5 08:33 GuestAgentInstaller_x64.exe
-rwxr--r-- 1 root root  54M Apr  5 08:33 LinuxGuestAgentPkgs.zip
-rwxr--r-- 1 root root 8.0M Apr  5 08:00 VMware-Log-Insight-Agent.msi
-rwxr--r-- 1 root root 9.8M Apr  5 08:33 VrmAgentInstaller.msi
-rwxr--r-- 2 root root  17M Apr  5 08:33 WorkflowManagerInstaller.msi
-rwxr--r-- 1 root root    8 Apr  5 12:49 bootstrap-iaas_build.txt
-rw-r--r-- 1 root root 6.3M Apr  5 08:33 bootstrap-vCAC-IaaSManagementAgent-Setup.msi
-rwxr--r-- 1 root root    8 Apr  5 12:49 iaas_build.txt
-rw-r--r-- 1 root root  707 Apr 10 19:52 index.html
lrwxrwxrwx 1 root root   75 Apr 10 19:54 jre-win32.zip -> /usr/lib/vcac/server/webapps/ROOT/software/download/jre-1.8.0_161-win32.zip
lrwxrwxrwx 1 root root   75 Apr 10 19:54 jre-win64.zip -> /usr/lib/vcac/server/webapps/ROOT/software/download/jre-1.8.0_161-win64.zip
drwxr--r-- 2 root root 4.0K Apr 10 19:52 scripts
-rwxr--r-- 2 root root  13M Apr  5 08:33 setup.exe
-rwxr--r-- 1 root root 9.8M Apr  5 08:33 vCAC-Agent-Setup.exe
-rwxr--r-- 1 root root  17M Apr  5 08:33 vCAC-Dem-Setup.exe
-rwxr--r-- 1 root root 6.3M Apr  5 08:33 vCAC-IaaSManagementAgent-Setup.msi
-rwxr--r-- 1 root root 201M Apr  5 08:33 vCAC-Server-Setup.exe
-rwxr--r-- 1 root root  17M Apr  5 08:33 vCAC-Wapi-Setup.exe
-rwxr--r-- 2 root root  13M Apr  5 08:33 vCACSuiteInstaller.exe
-rwxr--r-- 1 root root 9.0M Apr  5 08:33 vRA-IaaS-Migration.zip
-rwxr--r-- 1 root root 2.7M Apr  5 08:33 vRA.ExecutePowerShellScript_7.4.0.13461.zip
-rwxr--r-- 1 root root 5.7M Apr  5 08:33 vRA.Hotfix_7.4.0.13461.zip
-rwxr--r-- 1 root root 2.7M Apr  5 08:33 vRA.Installation_7.4.0.13461.zip
-rwxr--r-- 1 root root  57K Apr  5 08:33 vRA.LogBundling_7.4.0.13461.zip
-rwxr--r-- 1 root root  12K Apr  5 08:33 vRA.PoC_7.4.0.13461.zip
-rwxr--r-- 1 root root 4.5M Apr  5 08:33 vRA.Prerequisites_7.4.0.13461.zip
-rwxr--r-- 1 root root 2.7M Apr  5 08:33 vRA.Reconfiguration_7.4.0.13461.zip
-rwxr--r-- 1 root root 6.8K Apr  5 08:33 vRA.Shutdown_7.4.0.13461.zip
-rwxr--r-- 1 root root 2.8M Apr  5 08:33 vRA.Upgrade_7.4.0.13461.zip
lrwxrwxrwx 1 root root   80 Apr 10 19:54 vRAIaaSAppDependencies.zip -> /usr/lib/vcac/tools/initial-config/sample-oob-content/vRAIaaSAppDependencies.zip
lrwxrwxrwx 1 root root   78 Apr 10 19:54 vRAIaaSAppForvSphere.zip -> /usr/lib/vcac/tools/initial-config/sample-oob-content/vRAIaaSAppForvSphere.zip
```

And to download an item, just add the file name to the `https://vrava.domain/i/` URL. For example: `https://vrava.domain/i/jre-win64.zip` to download the Java JRE content for a win64 server (like an IaaS server).

As you can see, it is possible to download lot of tools or installers from this path, even if they are not available from the index page.
