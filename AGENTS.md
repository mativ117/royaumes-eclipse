# Consignes du projet — Les Royaumes de l’Éclipse

## Exigence globale confirmée

L’utilisateur demande explicitement de pousser **le jeu entier aussi près que possible de la qualité des meilleurs jeux AAA**, dans notre univers. Cette cible de production concerne tous les héros, ennemis, mouvements, combats, niveaux, décors, lumières et ombres, récit, mise en scène, musiques, effets sonores, interface, physique et performances PC/téléphone. Elle ne se limite pas à la Lame ou à une séquence de démonstration. Ne pas présenter cette qualité comme déjà atteinte.

Lire [l’exigence durable](design/EXIGENCE-QUALITE.md) et l’appliquer aux travaux suivants. Une séquence de référence sert à établir puis étendre une méthode ; elle ne réduit pas le périmètre final du jeu.

## Reprise et continuité

- Identifier la version dans `VERSION` et le périmètre dans `README.md`. Lire `design/SUIVI.md`, la matrice de prise en charge de la livraison courante et son relevé de validation pour distinguer implémentation, vérification et travail restant.
- Lire les parties pertinentes de `design/REFERENTIEL-QUALITE.md` et `design/WORKFLOW-QUALITE.md`, ainsi que les notes et la provenance des ressources concernées. Réutiliser les recherches documentées ; les actualiser si la version, le défaut ou la mesure le justifie.
- Inspecter l’état réel du code et les changements locaux avant de reprendre. Ne pas annoncer une tâche terminée à partir d’une intention, d’un ancien rapport ou de la seule existence d’un test.
- Poursuivre les travaux déjà autorisés et les corrections nécessaires sans recréer une demande d’approbation. Poser une question seulement lorsqu’un choix nouveau et déterminant ne peut pas être résolu avec les décisions existantes, tout en avançant sur le travail indépendant.

## Choix à préserver

- Jeu par lien dans le navigateur sur PC et téléphone ; pas de migration de moteur imposée.
- Sans serveur cloud ni appel API pour le jeu ou les bots. Nouvelle demande confirmée : conserver l’aventure solo et ajouter des duels contre une IA tactique locale ainsi qu’entre navigateurs du même réseau, y compris téléphone ↔ téléphone sans PC. WebRTC direct avec appairage manuel ; ne pas réintroduire les anciens modes inutiles. Les archives restent intactes.
- Détails visuels privilégiés avec réglage Léger. Une baisse de qualité doit préserver les informations, les contacts et les règles nécessaires pour jouer.
- Trois chapitres, dix héros disponibles au départ et un héros secret ; profils locaux, export/import, anciennes reprises et archives à conserver.
- Étendre explicitement le niveau de fabrication et de jouabilité de la Lame aux dix autres personnages, avec identité visuelle, gestuelle et pouvoirs propres.
- Direction de la Lame déjà approuvée. Univers noir/ambre, monumental et drapé ; les références artistiques guident une production originale, sans prétendre reproduire leur qualité à ce stade.

## Production et preuves

- Chaque passe doit améliorer un défaut perceptible de cohérence, lisibilité, sensation ou jouabilité. Davantage de particules, de polygones ou de ressources ne suffit pas.
- Conserver une source éditable, un export reproductible et la provenance/licence des ressources. Vérifier le résultat dans le jeu et l’atelier lorsqu’ils sont concernés.
- Comparer avant/après à vitesse normale depuis la caméra réelle du jeu. Distinguer concepts générés, captures du moteur et mesures techniques ; ne pas substituer une illustration à une preuve du rendu.
- Exécuter les régressions appropriées au changement. Les tests GPU sont séquentiels dans cet environnement. Un test réussi ne valide ni l’esthétique, ni le plaisir, ni la durée humaine d’un niveau.
- Mesurer la cadence et les ressources sur un PC et un téléphone identifiés avant de revendiquer une performance matérielle. Un navigateur simulé ou WebGL logiciel ne prouve pas les performances d’un iPhone.
- Mettre à jour le suivi avec les axes et contenus couverts, les preuves réelles, les limites et le prochain travail. Garder la cible de qualité sur l’ensemble du jeu, y compris les héros, familles ennemies et zones encore provisoires.

Le skill `design/skills/quality-pass/SKILL.md` est une procédure locale réutilisable. Sa présence ne crée pas de connecteur cloud et ne forme pas le modèle.
