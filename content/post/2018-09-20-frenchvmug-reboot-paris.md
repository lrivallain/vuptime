---
author: lrivallain
author_name: Ludovic Rivallain
categories:
- VMware
- French
date: "2018-09-20T00:00:00Z"
tags:
- vmware
- vmug
- community
thumbnail: /images/frvmug-09-2018-paris_thumb.jpg
title: Reboot French VMUG, Paris, Septembre 2018
aliases: 
- /2018/09/20/frenchvmug-reboot-paris/
---

> As an exception, I will post this article in French only as its subject is the French VMUG edition. Sorry for english speaking people.

Aujourd'hui avait lieu la reboot-edition du [VMUG France](https://community.vmug.com/events/event-description?CalendarEventKey=a806468f-34a7-407d-8526-8d93617b3442&CommunityKey=bba8d80d-5f53-404f-94ea-0009187683ae&Home=%2fcommunities%2flocalcommunityhome) dans les (tout neufs!) locaux parisiens d'OVH.

L'événènement est à présent orchestré (et bien orchestré!) par [Noham Medyouni](https://twitter.com/Noham_m) (Dell-EMC), [Fréderic Giovannacci](https://twitter.com/fredg_work) (SIB) et [Matthieu Gioia](https://twitter.com/notmg) (consultant indep.) et pour ce RDV parisien de rentrée, 2 invités de marque étaient présents:
* [Duncan Epping](https://twitter.com/DuncanYB): Chief Technologist HCI @VMware, Auteur du blog [Yellow Briks](http://yellow-bricks.com), Coauteur de la *bible* `Clustering Deepdive`.
*  [Franck Denneman](https://twitter.com/FrankDenneman): coauteur de *l'Ancien Testament* `Host Deepdive`, du Nouveau: `Clustering Deepdive`.

## OVH

Cette journée a commencé par une présentation d'OVH et de son offre de cloud privé: *SDDC*. 

OVH dans son actualité récente a notamment inauguré une nouvelle usine d'assemblage de serveurs à Croix, avec une capacité annuelle de production de 400 000 serveurs. Autant dire qu'ils voient grand et que leur appétit est grand sur le marché du Cloud Computing. 

Coté *Private Cloud/SDDC* (souvenirs, souvenirs!), l'offre s'étoffe de nouveautés:
* **vSAN** sera certainement annoncé plus officiellement lors du Summit (mi-Octobre) avec, côté technique, du full MVNE et du vSAN en version 6.6. De ce que j'ai pu avoir comme info en off, le client sera assez libre de configurer comme il le souhaite de nombreux paramètres du cluster.
* Des nouveauté coté **sécurité** avec la future possibilité de bénéficier des fonctions de chiffrement de l'écosystème vSphere via son propre HSM, ou encore, d'attacher son propre domaine Active Directory à l'authentification du produit.

Visiblement, les liens entre OVH et VMware sont forts (en témoignait déjà le rachat de vCloud Air par OVH il y a presque 2 ans) et cela se voit: OVH a été primé 7x comme meilleur partenaire VMware au cours des 9 dernières années.

Enfin, c'est plus anecdotique mais intéressant à savoir, OVH, envisage de proposer des ressources (sans SLA et limitées dans le temps) aux membres de la communauté VMUG et vExpert! A suivre.

## Duncan Epping, révolution de l'IT

Duncan a ensuite embrayé pour parler des évolutions actuelles et pré-senties du marché de l'IT.

Si on estime que dans les 5 ans à venir, plus d'applications seront créées et déployées qu'au cours des 40 dernières années: en effet on remarque que l'accélération sera dure à encaisser avec des pratiques d'il y a 10 ans. VMware essaye de son coté, d'apporter des solutions et de simplifier le travail de ses utilisateurs dans ses nouvelles et futures releases.

Nous avons notamment pu voir une démonstration de l'interface HTML5 de vSphere 6.7u1 avec un nouveau wizard de configuration de Cluster: qui n'a pas rêvé de configurer son cluster, avec vSAN, dvSwitch etc. en quelques clicks seulement? Et envoyer une support-request (les fameuses SR, un peu fastidieuses à remplir), directement depuis le vCenter concerné? Bientôt (on attend la GA), ça sera faisable!

Puis il a abordé les Tech Preview en cours sur 2 sujets:
* *Native Vsan data protection* qui permet de remplacer une solution de backup et d'exporter, au besoin, et selon ses politiques, les données sur du stockage distant, incluant quelques providers clouds.
* *vSan file services* ou l'arrivée de la consommation du vSAN dans les guestOS au travers d'une appliance conçue pour être simple à déployer, résiliente, auto-managée, distribuée, compatible object-storage etc. 

Autant dire que ça donne trèèèèès envie de tester tout ça et de l'envisager en production chez nos clients.

## Franck Denneman, Compute Deep Dive

Autant le dire directement: on passe du coté DUR du compute quand on échange avec Franck et pourtant, ça semble couler de source tellement la pédagogie est efficace.

Sa présentation a notamment été un rappel de quelques notions expliquées dans son bouquin: `Host Deepdive` (que je recommande chaudement) comme l'impact de la configuration hardware (sockets, DIMM, NUMA, channel etc.) de vos hosts. Et celui de la configuration de paramètres de VM sur les performances: nombre de *cores per socket* ou encore la configuration (sensible!) du mode *cpu  latency sensitivity: high* sur le workload d'une infrastructure.

Hyper intéressant !

## Autres présentations

Je ne m'étendrais pas sur les autres présentations (Rubrik, NetApp, PureStorage et Zerto) qui étaient très intéressantes elles aussi mais un peu plus commerciales et vastes.

## Surprises

Et comme si un VMUG avec de super guests ne suffisait pas, 2 grosses surprises sont intervenues au cours de la journée:
* La venue de Yoann Le Névé, cofondateur du 2ème festival de France, le HellFest. Quelques collègues Nantais en ont presque fait un QG et visiblement les liens sont forts puisque des places pour la prochaine édition ont été offertes aux participants par tirage au sort !
* L'intervention d'Oles (Octave Klaba) (*mon ex boss*), qu'on ne présente plus et qui a pu rappeler tout le bien qu'il pensait des liens qu'il entretient avec VMware, et de ses équipes des projets de cloud privé. Toujours dans son style décontracté et inimitable!

## Conclusion

Je crois que l'enthousiasme autour de cet évent se lit dans le billet ci-dessus mais au cas où, je le dis explicitement: *à refaire*. Un grand merci aux organisateurs pour cette très belle journée (et ce sublime T-shirt).

Merci aussi à SII, mon employeur, qui m'a permi d'assister à cet event!

Et la photo de famille:

{{< figure src="/images/frvmug-09-2018-paris.jpg" title="Photo de famille" >}}
