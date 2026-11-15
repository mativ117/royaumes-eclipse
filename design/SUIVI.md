# Suivi du projet — état 0.13

Ce document distingue ce qui est jouable de ce qui reste prévu. Il conserve les demandes du créateur ; la publication d’un prototype ne valide pas automatiquement toute la conception.

## Vérifiable dans le jeu actuel

| Engagement | État |
|---|---|
| Navigateur PC et téléphone, sans Unreal | Jouable : clavier/souris et tactile ; mobile simulé dans Chromium, appareil réel encore à essayer |
| Fantastique original, références Expédition 33 / Ghost of Tsushima | Direction inscrite ; première séquence visuellement reconstruite dans le parvis ; rendu final non achevé |
| Niveau avec exploration et défis variés | Première Cathédrale jouable : âme escortée, mélodie, Reflets, vannes/noyau, sceaux, Carillonneur, Veilleur, extraction |
| Parties de 10–15 minutes | Cible de conception ; durée active et bilan disponibles, durée humaine non confirmée |
| Contrôles et mouvement fluides | Commandes simultanées, correctif de pause mobile, guidage stable à la demande, contacts avec glissement et marche selon déplacement réel ; essais sur appareil réel encore nécessaires |
| Combat lisible et varié | Préparations, contacts différés, esquive, bouclier/bond, ennemis à règles distinctes et boss à trois phases |
| Deux héros réellement distincts | Rempart et Voltigeur ; modèles originaux à squelette et treize clips chacun dans la 0.12 |
| Carte, objets et prochaine action compréhensibles | Carte nommée avec obstacles, objets différenciés, journal et objectif suivi ; bassin indiqué dans la 0.12 |
| Suivi de progression | Reprise locale aux refuges et après rechargement ; secret local et bilan ; aucune synchronisation de compte |
| GitHub propre et versions préservées | Sources, générateur, modèles GLB, licences, tests et conception séparés ; anciens HTML et ZIP dans historique ; publication Pages vérifiée après envoi |
| Résultat visuel concret | Page avant/après 0.11 / 0.12 avec captures réelles, même position de départ ; PC et téléphone simulé |

## À conserver pour la version complète

- **Dix personnages ordinaires disponibles dès le début**, sans achat ni progression obligatoire pour les obtenir. Deux sont implémentés ; les huit autres restent à réaliser.
- **Un onzième personnage secret**, L’Éclipse incarnée : apparence ultime, capacité supplémentaire Incarnation, obtention secrète. La Marque du Reflet actuelle est un premier élément ; le personnage complet n’est pas encore jouable.
- **Trois grands niveaux** : Cathédrale vivante, Chasse aux Souverains, Convoi de l’Impossible. Seul le premier dispose aujourd’hui d’une expédition jouable.
- **Solo, coopération et battle** : coop de 2 à 4, duel et équipes ; fonctionnement PC/téléphone ensemble à développer et tester. Le jeu publié est solo.
- **Compte** : pseudo public, e-mail privé, code temporaire par e-mail et option Google ; suivi de progression, statistiques et secret ; invité puis transfert de sauvegarde. Le fournisseur et le serveur restent à choisir.
- **Qualité finale** : environnements complets, costumes et personnages définitifs, animation, audio, tutoriel, accessibilité, équilibrage et performances. Les modèles de la 0.12 sont une nouvelle base articulée, pas la livraison des dix personnages finaux.

## Ce que la 0.12 entreprend et termine

1. Deux fichiers GLB créés et exportés depuis Blender, avec squelette, manteau articulé, armes et actions réellement jouées dans Three.js.
2. Cour d’arrivée reconstruite avec bassin, mosaïque, colonnes, voûtes et monument ; collision du bassin incluse dans le guidage et la carte.
3. Caméra rapprochée, sélection de cible tactile dans le champ de vue et atténuation des colonnes masquant le héros.
4. Reflets et ombres en qualité Haute ; variante Légère qui conserve le parcours et les commandes.
5. Traînée de lame suivant le modèle, tir depuis le canon, réaction aux coups et armes masquées pendant le transport du noyau.
6. Conservation des épreuves, du secret, des sauvegardes compatibles et des anciennes versions.
7. Tests automatisés et captures avant/après ; vérification du contenu réellement publié.

## Prochaine étape de production

Faire jouer cette séquence représentative sur téléphone réel et recueillir les points précis de gêne, puis étendre le traitement visuel aux autres zones. Les fonctionnalités de compte, coop et battle restent des chantiers distincts ; elles ne sont pas annoncées comme livrées par cette passe graphique.

Passe 0.13 : voir [mouvements, collisions et ombres](PHYSIQUE-0.13.md), avec les limites physiques restantes. Les engagements futurs ci-dessus restent ouverts.
