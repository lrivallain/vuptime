---
layout: post
title: PowerCli - Mise à jour du VMX de templates de machines virtuelles
category: VMWare PowerShell
tags: powercli powershell template vmware vmx
---

Lorsqu'on gère plusieurs centaines de machines virtuelles, templates, virtual-appliance etc., on a pas spécialement envie de se palucher à la main, les opérations de mises-à-jour systématiques. En plus si vous cotoyez des gus comme [@fdibot](https://twitter.com/fdibot "Le compte twitter du (gentil) gus en question"), ça devient carrément un sacrilège d'envisager de faire à la main ce genre d'opération, si vous avez la possibilité de le scripter en powershell.

Si on travaille sur un environnement Windows et VMware, l'API "[PowerCli](https://www.vmware.com/support/developer/PowerCLI/ "Documentation de PowerCli")" est une facilité appréciable qui permet d'automatiser des tâches fastidieuses à réaliser à la main sur votre infrastructure vSphere. Le dernier exemple en date a été une demande pour modifier, rapidement, les paramètres VMX de templates de machines virtuelles. Or si la lecture de la configuration VMX d'une VM ou d'un template est aisée, l'écriture de modifications sur un template nécessite une petite pirouette que j'explique ici.

# Étape par étape

## Se connecter à vCenter

C'est l'étape la plus simple et la plus documentée sur Internet. Tout commence par l'ajout à votre contexte, du module adéquat qui va vous permettre d'utiliser l'extension ``PowerCli``:

    # load PowerCli Snapin
    if ((Get-PSSnapin -Name VMware.Vimautomation.Core -ErrorAction SilentlyContinue) -eq $null ) {
        Add-PsSnapin VMware.Vimautomation.Core
    }

Ensuite on se connecte à notre vCenter Server préféré:

    # vCenter server
    $VC = "monvcenter.domain.tld"
    $Username = "domain\monuser"

    # connecting vCenter
    $Credentials = get-credential  -credential $Username
    Connect-VIServer -server $($VC.IP) -Credential $Credentials

## Préparer la configuration à mettre en place

Les paramètres d'un fichier VMX sont simplement composés d'un couple clé/valeur. Le type d'objet requis est ``VMware.Vim.optionvalue``, le tout ajouté à un type d'objet correspondant à la configuration (même partielle) d'une VM: ``VMware.Vim.VirtualMachineConfigSpec``.

    # config change for updateVMWareTools
    $vmConfigSpec = New-Object VMware.Vim.VirtualMachineConfigSpec
    $vmConfigSpec.extraconfig += New-Object VMware.Vim.optionvalue
    $vmConfigSpec.extraconfig[0].Key="isolation.tools.guestInitiatedUpgrade.disable"
    $vmConfigSpec.extraconfig[0].Value="false"

Ici on va placer à "vrai" toutes les valeurs (déjà existantes ou pas) de ``isolation.tools.guestInitiatedUpgrade.disable`` (ce qui permettra de lancer la mise à jour des VMwareTools d'une machine, depuis l'OS de la VM).

## Appliquer cette modification aux templates

Dans le cas figure présenté ici, on ne va pas filtrer les templates sur lesquels appliquer ce changement de configuration. Il est toutefois envisageable de placer un filtre (via ``| filter``) ou de placer des tests ``if`` pour, par exemple, ne sélectionner que les templates dont le ``GuestOS`` déclaré est de type Windows.

    # update all templates
    $templates = Get-template
    foreach ($tpl in $templates) {
        Write-host -foreground blue "Template: $($tpl.Name)"
        Write-host -foreground gray " Converting to VM"
        $vm = **Set-Template -Template $tpl -ToVM**
        Write-host -foreground gray " updating VMX"
        ($vm | Get-View).ReconfigVM($vmConfigSpec)
        Write-host -foreground gray " Converting to Template back"
        **($vm | Get-View).MarkAsTemplate()** | Out-Null
        Write-host -foreground gray "End of update process"process
    }

L'astuce, si on peut appeler ça ainsi, est de réaliser la séquence suivante pour chaque template:

1.  conversion en machine virtuelle
2.  mise à jour du VMX
3.  conversion en template

C'est moche mais c'est rapide et ça fait bien le job.

## Quand c'est terminé

On se déconnecte:

    # clean leave
    Disconnect-VIServer -Confirm:$false

That's all folks !

# La version complète

La version complète du script présenté ici est disponible ici:  [lrivallain _(sur Github)_ / TemplatesVmxUpdater.ps1](https://gist.github.com/lrivallain/b74a87c5c01a53ee242f#file-templatesvmxupdater-ps1 "Le script sur mon profil github/gist")

Et si certains ont trouvé plus rapide et moins sale, les commentaires sont là pour ça.
