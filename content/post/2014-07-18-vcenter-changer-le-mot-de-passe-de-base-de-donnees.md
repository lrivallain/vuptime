---
author: lrivallain
categories:
- VMWare
date: "2014-07-18T00:00:00Z"
tags:
- database
- dbuser
- password
- vcenter
- vmware
title: vCenter - changer le mot de passe de base de données
aliases: 
- /2014/07/18/vcenter-changer-le-mot-de-passe-de-base-de-donnees/
---

Un petit article plus, pour me rappeler moi même de la manipulation que pour vraiment générer du contenu sur ce blog. Ce matin j'ai eu à changer, sur un vCenter Server, le mot de passe par lequel le service communique avec sa base de données, voici la manipulation.

## Changer l'utilisateur de BDD

_(si nécessaire)_

Pour celà, il faut ouvrir l'éditeur de registre Windows: ``regedit.exe``

Puis chercher le chemin: ``HKEY_LOCAL_MACHINE\SOFTWARE\VMware, Inc.\VMware VirtualCenter\DB``

Dans ce dossier du registre, sont stockées les informations relatives à la connexion à la base de données du service vCenter.

{{< figure src="/images/vCenter_changeDBsettings_user.png" title="Changement de l'utilisateur de bdd pour le service vCenter" >}}

Il suffit de mettre à jour la valeur nommée "2" avec votre éventuel nouvel utilisateur de base de données (et de relancer votre service après avoir mis à jour le mot de passe).

## Changer le mot de passe d'accès à la BDD

Si vous regardez la suite des clés de registre à l'emplacement de l'étape du dessus, vous remarquerez que l'entrée 3 stocke le mot de passe, haché, pour cet utilisateur (un truc genre: ``*P8Juhn9L7f3pFZsYcCYvZ....``). Pour le mettre à jour il ne suffit donc pas de modifier à la main cette valeur par votre nouveau mot de passe.

Heureusement il y a un outil qui va vous aider à le faire: vpxd.exe

Il faut se placer dans le dossier dans lequel vCenter Server est installé et lancer la commande avec l'argument "-p":

    C:> cd C:\Program Files\VMware\Infrastructure\VirtualCenter Server\
    C:\Program Files\VMware\Infrastructure\VirtualCenter Server> vpxd.exe -p
    ------ In-memory logs start --------
    2014-07-18T11:46:22.991+02:00 [05588 info 'Hooks'] Hooks Initialized

    ------ In-memory logs end   --------
    2014-07-18T11:46:23.209+02:00 [05588 info 'Default'] Initialized channel manager

    2014-07-18T11:46:23.209+02:00 [05588 info 'Default'] Current working directory:
    c:\Program Files\VMware\Infrastructure\VirtualCenter Server
    2014-07-18T11:46:23.209+02:00 [05588 info 'Default'] Log path: C:\ProgramData\VM
    ware\VMware VirtualCenter\Logs
    2014-07-18T11:46:23.209+02:00 [05588 info 'Default'] Initializing SSL
    2014-07-18T11:46:23.209+02:00 [05588 info 'Default'] Vmacore::InitSSL: doVersion
    Check = true, handshakeTimeoutUs = 120000000
    Enter new DB password:
    again:
    2014-07-18T11:46:40.718+02:00 [05588 info 'Default'] Reset DB password succeeded
    .
    C:\Program Files\VMware\Infrastructure\VirtualCenter Server>

Ensuite il faut relancer le service vCenter Server à l'aide du gestionnaire de services et le tour est joué.
