# Couverture de la qualité — point d’audit 1.5

Audit initial du 23 novembre, complété par les contrôles locaux du 24 novembre 2026. La [validation 1.5](VALIDATION-1.5.md) consigne les onze kits, le rendu, les appuis, la campagne et les duels. Les colonnes conservent la distinction entre fabrication intégrée, preuve technique et revue humaine encore requise.

La cible [proche AAA sur le jeu entier](EXIGENCE-QUALITE.md) s’applique à toutes les lignes. Les compteurs de matériaux ou de clips ne sont pas des notes de qualité.

## Onze héros

Les dix sources éditables existent dans `assets/source/roster/` et les dix exports adaptés sont présents dans `assets/characters/`. Au point de rédaction, leurs empreintes correspondent aux dix enregistrements de [ROSTER-PRODUCTION.json](../assets/characters/ROSTER-PRODUCTION.json). Les exports compacts utilisent huit matériaux, trois cartes, une carte couleur de 1024 et des cartes de données de 512 pixels. Elles relient les profils de mouvement aux sources Quaternius Standard CC0 ; les pas orientés, esquives et transitions gardent des actions analytiques ou alias hérités. La présence des exports et leurs empreintes ne prouvent ni le rendu final ni la qualité en mouvement. Les onze parcours de kit et les contrôles de modèle passent ; les captures réelles et les rapports de mouvement sont liés depuis la validation.

| Héros | Base publiée 1.4 | Fabrication 1.5 présente | Points à éprouver en parties humaines |
|---|---|---|---|
| Dernier Rempart | Ancien modèle et gestes procéduraux, tir et Bastion fonctionnels | Nouveau corps, casque fermé, armure et PBR ; export adapté profil fusil | Visée et recul du fusil, prise à deux mains, course en combat, Bastion, corps au sol |
| Voltigeur | Ancien modèle ; combo, bond et impact fonctionnels | Nouvelle silhouette mobile et costume ; export adapté profil lame | Appuis, trois frappes, décollage/atterrissage, contrôle pendant le bond et esquive |
| Lame d’Éclipse | Référence détaillée : 23 actions, mouvements Quaternius, appuis/contacts calibrés | Ressource approuvée conservée comme référence | Raccords avec la nouvelle commande tactile, drapés, préparation orientable, récupération et essais humains |
| Tisseuse de Failles | Ancien modèle ; portails et projectiles fonctionnels | Nouveau corps et costume de lanceuse ; export adapté profil magique | Geste magique, position du sceptre, visée, passage des corps/tirs, seuils scellés et présentation des deux portails |
| Porte-Cendres | Ancien modèle ; canon, chaleur et zone persistante fonctionnels | Nouvelle silhouette armée et matières ; export adapté profil fusil | Masse du canon, tir/surchauffe, appuis, libération de chaleur et lecture de la zone |
| Voleur d’Ombres | Ancien modèle ; dagues, double et échange fonctionnels | Nouvelle silhouette légère ; export adapté profil dagues | Deux armes et gestes courts, déplacement sous attaque, échange, écho et collisions après permutation |
| Bergère des Astres | Ancien modèle ; astre, attraction et soin fonctionnels | Nouveau corps et costume astral ; export adapté profil magique | Geste du sceptre, astre mobile, portée, soin/protection et intelligibilité en duel |
| Colosse de Porcelaine | Ancien modèle ; marteau et abris fonctionnels | Nouveau corps lourd et costume ; export adapté profil lourd | Poids du marteau, anticipations/récupérations, esquive lourde, abris et hauteur de passage |
| Accordeur | Ancien modèle ; pulsations et bonus de rythme fonctionnels | Nouveau corps et silhouette du diapason ; export adapté profil magique | Fréquence des frappes/tirs, rythme visible et sonore, synchronisation des pulsations |
| Enfant du Néant | Ancien modèle ; ombre et métamorphose fonctionnelles | Nouvelle silhouette et matières ; export adapté profil ombre | Croissant, ombre combattante, transformation, appuis et lisibilité dans les noirs |
| Éclipse incarnée | Secret et Incarnation fonctionnels ; ancien modèle | Nouvelle fabrication ultime ; export adapté profil ultime | Arme, soleil noir, jauge/Incarnation/fragilité, couronne au passage des portes, secret préservé |

Pour clôturer une ligne : modèle final exporté avec provenance, mouvements appropriés à l’arme, semelles et prises contrôlées, trois attaques ou le tir et son cycle, esquive, pouvoir, réaction, transition vers le déplacement, atelier et scène jouable. Les modes Haute/Léger, commandes PC/tactiles et chemin de retour au menu doivent rester cohérents. La fabrication et les validations finales doivent préciser les profils réellement utilisés ; elles ne doivent pas attribuer une animation de sabre à tous les personnages.

## Familles ennemies et boss

| Famille | État observé | Écart restant |
|---|---|---|
| Fauche-Cendre / `warden` | Quadrupède original de référence, quatre membres, préparation directionnelle, charge et récupération ; tests 1.4 de contact et de ressources | Raffiner anatomie, transitions et réactions ; valider la lecture en groupe et sur appareil |
| Archer | Comportement de distance distinct, corps/animation hérités | Nouvelle anatomie, tenue, tir et repositionnement ; réaction au couvert et son propre |
| Sentinelle | Garde orientée et préparation spécifiques, ressources héritées | Modèle et locomotion propres ; poids du blocage et de la contre-attaque |
| Oracle | Marques/attaques à distance distinctes, ressources héritées | Créature dédiée, geste de préparation, contact avec le décor et diversité du rituel |
| Reflet / `shade` | Mécanique de révélation et matérialisation | Silhouette, transformation et réactions dédiées ; lisibilité hors couleur seule |
| Carillonneur / `porter` | Chaînes et interruption, modèle humanoïde hérité | Production de boss, locomotion, phases et réactions propres |
| Ancres | Objets de progression destructibles | Cohérence des formes, retours d’impact et distinction des objets interactifs |
| Veilleur / Souverain / Mange-Aube | Phases et géométrie de terrain scriptées ; base anatomique héritée avec ajouts | Chaque boss doit recevoir une silhouette, un langage d’attaque et une mise en scène propres |

L’amélioration des onze héros ne refait donc pas automatiquement tout le bestiaire. Le nouveau bot de duel est un adversaire jouant un kit ; il ne remplace pas cette production des créatures.

## Trois chapitres et zones

| Contenu | Couverture fonctionnelle de base | Production et revue restantes |
|---|---|---|
| Cathédrale : atrium, jardins, cloître, croisée, Archives, forge, nef et cour | Pactes, escorte, carillon, deux ailes, transport, sceaux, boss et extraction ; reprise locale | Revue des neuf seuils modulaires, props/colliders, densité des matières, rythme des transitions et lecture novice |
| Chasse aux Souverains : traces, Gué, jardin et observatoire | Traces, interprétation des appels, duel, secret et terrain de boss | Vérifier la disparition des sols superposés ; composer les lieux et transitions au-delà des grandes surfaces planes ; refaire le boss |
| Convoi : réveil, liens, traversée, escale, cœur, île secrète et affrontement final | Réparations, vent, route et ravitaillement, défense, secret et fin | Vérifier l’union des sols de l’escale, le cadrage du colosse, les signes d’orientation, la variété visuelle et le rythme humain |
| Cercle des deux lunes | Nouvelle arène de duel intégrée et testée | Deux appareils, mêmes règles/collisions, retour aux sauvegardes, distinction de l’arène et des chapitres d’aventure |

La durée de 10–15 minutes par chapitre reste à mesurer en parties novices. Les anciens parcours contrôlés utilisent des positions et dégâts préparés : ils ne mesurent pas une durée de découverte.

## Systèmes transversaux

| Axe | Correctif ou base observée | Preuve à conserver pour la livraison |
|---|---|---|
| Portes | Modules verticaux, dégagement réel et protection des acteurs ; CPU avec collision passé | Captures des deux côtés à trois ouvertures, héros lourd/couronne, Haute/Léger |
| Sols et matières | Union sans double surface dans les cas identifiés ; CPU passé | Captures rapprochées et déplacement dans les deux zones, UV et relief |
| Combat | Contrôle de couvert entre échantillons, visée tactile stabilisée, commande préparatoire et récupération reprises | Séquences jouées à 1× pour chaque profil, impacts et son, tests PC/tactiles |
| Physique | Contrôleur plan avec volumes et sous-pas | Couverture des accessoires dans les chemins ; pas de pentes, plateformes ou corps rigides annoncés |
| Ombres | Stabilisation Haute héritée ; nouvelle couche de contacts Léger pour les autres chapitres présente dans les sources | Ombres mobiles, pieds/roulis/corps lourds et absence de faux plafond dans tous les chapitres et duels |
| Histoire | Chronique et objectifs progressifs | Compréhension des enjeux, mise en scène et conséquences perçues sans lecture du code |
| Musique et effets | Master, silence zéro, pause et stéréo testés en 1.4 ; motifs synthétiques | Écoute des timbres, variété, fatigue, transitions et mix sur les appareils visés |
| Interface | Règles de focus, carte et commandes remappées héritées ; nouveaux modes intégrés et testés | Nouveaux menus, partages et états d’attente/erreur, viewport, textes longs et entrées prévues |
| LAN | Transport WebRTC direct et validation bornée ; protocole et jeu simulé passés, transfert natif non vérifié | Connexion réelle, rôle, délais, pause, déconnexion, reprise, absence d’API et deux appareils physiques |
| IA de duel | Planificateur local, perception et réaction bornées ; CPU et duel intégré passés | Difficultés distinctes et justes, couvert, punition, ressources et absence de lecture instantanée des entrées adverses |
| Sécurité | Identifiants propres, bornes de sauvegarde et protocole ; durcissement CSP ajouté à la construction | Régressions malveillantes et démarrage du jeu/atelier sous la CSP générée |
| Performance | Chargement différé, cycle de vie de l’atelier et budgets de dessin | Octets, textures/mémoire, temps de chargement, p50/p95/p99 et chauffe sur PC/téléphones identifiés |

La [matrice de l’audit](AUDIT-PROFOND-1.5.md) et la [note portes/matières](PORTES-MATIERES-1.5.md) donnent les causes et les critères de fermeture. La validation de livraison doit ensuite relever les tests réellement exécutés et les écarts encore ouverts, sans transformer cette couverture en label AAA.
