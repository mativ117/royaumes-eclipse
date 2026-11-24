# Prise en charge de la qualité — candidate 1.5-rc1

État au 24 novembre 2026. Les [contrôles locaux 1.5](VALIDATION-1.5.md) ont été exécutés ; le transfert WebRTC natif et les appareils physiques restent hors de cette preuve. La cible [proche AAA pour le jeu entier](EXIGENCE-QUALITE.md) demeure une exigence de production. Aucun résultat automatisé ne constitue une validation artistique ou une partie humaine.

**RECHERCHÉ** relie une référence documentée à un problème. **APPLIQUÉ** décrit le code et les ressources présents, sans déduire leur validation de leur existence. **À VÉRIFIER / À PRODUIRE** conserve les limites et preuves nécessaires.

| Axe | RECHERCHÉ | APPLIQUÉ | À VÉRIFIER / À PRODUIRE |
|---|---|---|---|
| Onze héros | Blender, proportion, déformation, PBR, bibliothèques Quaternius Standard CC0 | Lame approuvée conservée ; dix fabrications originales détaillées, sources éditables, exports adaptés et profils d’arme présents ; jeu/atelier et onze kits contrôlés | Raccords et revue humaine de chaque profil ; une ligne par héros dans la couverture |
| Mouvement | GDC animation-driven locomotion, appuis et métadonnées des clips | Marche/course/garde retargetées ; cadence et contacts calibrés ; contrôleur générique pour les héros concernés | Revue à 1×, demi-tours, départ/arrêt, glissement et poids ; pas orientés et esquives conservent des solutions analytiques antérieures |
| Combat | Anticipation, engagement et fenêtre de contact | Préparation orientable bornée, direction active verrouillée, buffer de combo, récupération libérée ; contacts de mêlée et cadence de tir liés aux métadonnées | Contact visible/sonore pour chaque arme, réactions, ressenti et équilibrage humain ; pas de mocap annoncée |
| Déplacement tactile | Séparation intention de déplacement / intention de combat | Course libre hors combat, assistance quand le joueur attaque et hystérésis de cible | Fuite, attaque en déplacement et changements de cible sur téléphones physiques |
| Physique et couvert | Contrôleur plan, balayage, volumes ; Rapier évalué seulement | Tirs sous-échantillonnés contre les couverts minces ; Bastion soumis à la ligne de vue | Tous les accessoires du parcours ; pas de pentes, marches, plateformes ou corps rigides ajoutés |
| Portes | Anciennes feuilles de 9,5–24 unités dans des seuils de 19–48 | Modules verticaux limités, collision selon dégagement réel et protection d’acteur ; CPU avec intégration passé | Captures en mouvement de chaque seuil, gros héros/couronne, deux côtés et Haute/Léger |
| Matières et ombres | Three r160 couleur, instancing, ombres ; union de surfaces | Suppression des doubles surfaces identifiées sans changer la navigation ; contacts Léger indépendants du monde du chapitre I | UV, matières, ombres mobiles et contacts dans chaque chapitre et l’arène ; aucune refonte globale de décors annoncée |
| Créatures et boss | Riot Clarity, Guerrilla Horizon AI | Fauche-Cendre conservé ; autres mécaniques héritées ; nouveau bot jouant un kit de héros | Anatomie, locomotion, préparation/réaction et mise en scène propres à chaque autre famille et boss |
| Duel tactique | Perception, délai, utilité et géométrie de couvert | Bot local déterministe, deux profils, mémoire bornée, portée, couvert/contournement, pouvoirs et réaction finie ; CPU passé | Parcours intégré passé ; difficulté et contre-jeu humains ; aucun bonus caché de PV/dégâts |
| LAN entre appareils | MDN/W3C WebRTC, DTLS, appairage et OWASP adaptés | WebRTC direct sans STUN/TURN ni serveur de rendez-vous, partage invitation/réponse, hôte autoritaire, invité par intentions | **Connexion native et deux téléphones non validés** : Chromium géré bloque ICE. Synchronisation testée par pont en mémoire, pas preuve de Wi-Fi/DTLS |
| Sécurité | Liste de valeurs admises, autorité, quotas, confidentialité et CSP | Schémas bornés, rôles/session/séquence/débit, expiration, nettoyage ; imports/cache durcis ; scripts à empreinte, attributs de script interdits | Régressions finales, appareils/réseaux visés ; pas d’identité de compte ni d’anti-triche contre un hôte modifié |
| Interface | WAI-ARIA Dialog, commandes configurables et erreurs explicites | Trois modes utiles, remappage/manette partagé, états de connexion distincts, nettoyage et sauvegarde d’aventure préservée | Textes longs, zoom, retour après interruption, lecteur d’écran et manette physique ; anciennes variantes inutiles archivées |
| Niveaux et rythme | Composition, orientation et narration par le décor | Trois chapitres, épreuves, conclusions, ancres et secret conservés ; surfaces/portes ciblées | Recomposition des zones, variété, transitions et rythme novice ; 10–15 min non mesurées en parties humaines |
| Récit, musique et effets | Narration environnementale, Web Audio, volume et spatialisation | Chronique, objectifs, trois thèmes synthétiques, master/pause/silence/stéréo conservés | Mise en scène, conséquences, timbres, variantes, transitions et écoute sur appareils ; pas de doublage ni d’orchestre enregistré annoncés |
| Performance | Chargement différé, cycle de vie, budgets de voix/dessin | Modèle choisi chargé à la demande ; atelier suspendu et libéré ; optimisations antérieures conservées | Octets, mémoire, p50/p95/p99 et chauffe sur matériel identifié ; navigateur logiciel ≠ preuve de performance mobile |
| Historique et livraison | Reproductibilité et distinction des preuves | Sources, licences, anciens ZIP et rapports conservés ; source ZIP GitHub pour le projet complet | Validation, captures réelles, intégrité et publication vérifiées ; essai matériel encore requis pour le LAN |

## Bibliothèques : attribution exacte

Les sélections réellement retargetées viennent des éditions **Standard gratuites Quaternius Universal Animation Library 1 et 2**, sous CC0. Les profils distinguent notamment garde/tir de fusil, geste magique, dagues, lame et arme lourde. L’adaptation des proportions, des prises et des poids reste une production du projet. Les actions et leur chronologie figurent dans les métadonnées finales ; ne pas compter une action analytique ou un alias de marche comme un nouveau mouvement externe.

KayKit Character Animations Free 1.1 a été obtenu et évalué. Les exports courants ne doivent pas être crédités comme utilisant ses mouvements sans preuve dans leur provenance. Aucune bibliothèque ne doit être qualifiée de capture de mouvement sur la seule base de sa présence.

## État des preuves

La [validation 1.5](VALIDATION-1.5.md) donne les commandes exécutées, les correctifs révélés et les limites. Les onze modèles, leurs appuis et kits, les trois campagnes, le duel, les profils, le rendu, l’interface et les frontières réseau ont des contrôles locaux. `lan_game` emploie un pont en mémoire entre deux vrais contextes : il ne remplace pas une connexion directe. Le transport natif est **SKIP**, selon la politique décrite dans la note LAN.

## Documents liés

- [Audit profond](AUDIT-PROFOND-1.5.md), [couverture de tous les contenus](COUVERTURE-QUALITE.md) et [suivi](SUIVI.md).
- [Modes](MODES-1.5.md), [duel et IA](DUELS-1.5.md), [LAN téléphone](LAN-TELEPHONES-1.5.md) et [sécurité LAN](LAN-SECURITE-1.5.md).
- [Portes et matières](PORTES-MATIERES-1.5.md), [référentiel](REFERENTIEL-QUALITE.md), [workflow](WORKFLOW-QUALITE.md) et [skill local](skills/quality-pass/SKILL.md).
