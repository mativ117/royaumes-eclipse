# Obtenir un vrai saut de qualité

Les retours du 17 novembre 2026 montrent que le jeu reste visuellement et gestuellement un prototype. Les corrections de fonctionnement ne valident pas sa qualité artistique. Le contenu existant doit être conservé pendant que l’effort se concentre sur une séquence de référence de deux à trois minutes.

## Le segment à produire

Un héros, une arme, une salle de la Cathédrale, une stèle, deux adversaires et une courte scène narrative. Une arrivée met en scène une silhouette et la lumière ambrée ; le joueur lit la stèle, traverse un passage où la caméra doit conserver sa lisibilité, affronte deux rôles distincts et découvre une conséquence de son action. Les références noir/ambre doivent être reconnaissables depuis la caméra réellement utilisée pour jouer.

## Priorités de production

1. Un personnage dont silhouette, visage/casque, costume, plis et arme sont travaillés ensemble. Modelage, retopologie, UV, matières et rig doivent être conçus pour les plans du jeu. Une silhouette différente et une couleur ne suffisent pas à finir un personnage.
2. Une locomotion avec départs, freinages, pivots, pas latéraux et arrière, bassin et contacts des pieds. Les attaques demandent anticipation, contact et récupération, avec prises crédibles de l’arme. L’IK complète ces animations ; il ne remplace pas leur travail.
3. Une scène composée à une échelle cohérente : volumes, sol, arrière-plan, matériaux, lumière motivée et ombres. Le ciel orange et le halo solaire restent des éléments de composition, pas une preuve de qualité du décor.
4. Une caméra qui anticipe les occultations et une interface qui laisse voir les actions. Les stèles doivent être utilisables depuis les approches normales, sans devoir décaler le héros pour lire.
5. Des événements narratifs joués dans l’espace et un habillage sonore cohérent : ambiances, pas, gestes d’arme, contacts et thème musical avec transitions. Les sons synthétiques actuels sont un point de départ.

## Critères de validation

- Quatre approches d’une stèle : bon objet ciblé, anneau et bouton cohérents, message lisible immédiatement et assez longtemps.
- Le héros reste identifiable en passant devant/derrière les colonnes et objets, en portrait et paysage.
- Les pieds ne glissent pas visiblement pendant l’appui ; les arrêts, pivots et transitions doivent aussi être revus à vitesse normale.
- Cible de départ : 60 images/s sur un PC de référence et 30 images/s stables sur un téléphone de référence, avec temps de trame et saccades mesurés. Le modèle exact du téléphone reste à préciser.
- Captures et courtes vidéos du jeu réel, depuis la caméra de jeu ; évaluation sur appareil physique et essai humain sans assistance.
- Les réglages détaillé et léger doivent partager la même direction artistique. Leur coût et leurs concessions doivent être mesurés.

Une capture statique, un test de logique, un budget de commandes de dessin ou Chromium en émulation mobile ne démontrent pas ces critères de fluidité et de finition.

## Outils et assets

Three.js permet de réaliser une belle séquence stylisée dans le navigateur. Blender et un pipeline d’assets élaborés sont nécessaires pour produire des modèles et des animations plus aboutis. Des bibliothèques de ressources peuvent aider si leurs licences conviennent. Un moteur avec éditeur et des versions natives peuvent devenir pertinents selon le résultat mesuré de ce segment ; la migration doit être décidée sur ces besoins concrets.

Le travail automatisable comprend intégration, contrôleur, caméra, collisions, retargeting, shaders, mix interactif, profilage et tests. La qualité des modèles, des clips, de la composition et du son doit être réellement travaillée et revue. L’extension aux autres héros et chapitres vient après validation du segment.
