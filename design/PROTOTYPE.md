# La nef des serments — prototype 3D 0.4

Une séquence solo de trois salles du premier grand niveau, la Cathédrale vivante. Cette version approfondit les décisions, leurs conséquences et un secret facultatif. Les modèles restent procéduraux ; les trois grands niveaux complets, les dix personnages, les comptes et le multijoueur restent à développer.

## Publication

Le jeu actuel est généré dans `docs/index.html` ; le lien `docs/cathedrale-v03.html` redirige vers cette page. Suivre [PUBLICATION.md](PUBLICATION.md) pour modifier ou publier. L’accueil affiche **Version 0.4**.

## Trois salles avec des décisions

1. **Le choix des cendres** : contourner des obstacles et examiner deux offrandes. Les gardiens sont facultatifs. Approcher ne suffit plus à accepter : un écran expose le don, le prix et la conséquence sur le monde. Le joueur peut annuler pour comparer l’autre offrande.
2. **La nef respirante** : traverser les pièges et atteindre l’éclat. La forme des passages dépend du serment. Un indice dans la première salle invite à observer une anomalie dans la nef.
3. **Le Veilleur du seuil** : lire les attaques, esquiver et exploiter les fenêtres de vulnérabilité. Deux phases ; l’ombre d’Élan peut détourner le ciblage, tandis que Braise permet de charger une riposte avec le bouclier. Le secret rend les préparations du boss plus lentes.

## Serments : don et prix

| Serment | Don | Prix | Conséquence dans la nef |
| --- | --- | --- | --- |
| Braise | 190 PV ; les impacts bloqués par le bouclier donnent jusqu’à trois charges au prochain tir | Esquive rechargée en 2,4 s | Passages centraux ; brasier actif plus longtemps |
| Élan | Esquive rechargée en 1,05 s ; leurre pendant 1,8 s, ciblé par les ennemis à proximité | 120 PV maximum | Passages latéraux alternés ; brasier actif moins longtemps |

Le tir normal fait 34 dégâts ; chaque charge de Braise ajoute 20 dégâts, puis le tir consomme les charges. L’armure du boss réduit aussi ces dégâts hors de sa fenêtre de vulnérabilité. Un délai de 0,35 s entre gains de charge évite de multiplier les charges lors d’impacts simultanés.

Le leurre remplace la cible des ennemis proches lors du choix d’une attaque ; il ne détourne pas les projectiles déjà lancés ou les zones déjà verrouillées. Un seul leurre peut exister à la fois. Le bouclier reste utilisable avec les deux serments et peut interrompre le boss à courte portée pendant sa préparation.

## Secret du Reflet

Dans la nef, approcher l’anomalie et maintenir l’interaction pendant 1,5 s, sans bouger ni tirer. Les dégâts interrompent l’observation. La Marque du Reflet allonge de 0,45 s les préparations et avertissements du boss. Elle reste facultative pour terminer.

La marque est sauvegardée sur cet appareil via le stockage local du navigateur, si disponible ; aucune donnée personnelle n’est collectée. Ce prototype ne synchronise rien entre appareils. Il s’agit d’un premier indice vers l’Éclipse, pas du déblocage complet du onzième personnage.

## Commandes et confort

PC : ZQSD/WASD/flèches ; souris pour viser ; clic pour tirer ; Espace pour esquiver ; E pour le bouclier ; **F pour examiner / maintenir F pour observer** ; Échap pour pause ou retour depuis un choix.

Téléphone : joystick, tir à visée automatique, esquive, bouclier et bouton contextuel près d’un objet. Maintenir ce dernier pour observer. Le dialogue de serment permet de confirmer ou revenir. Paysage conseillé ; qualité légère disponible. Son synthétisé désactivable.

Accélération et freinage progressifs, rotations et caméra lissées. Simulation à pas fixe. Les murs et obstacles bloquent déplacements, esquives et projectiles. Les tireurs annoncent leur direction par une ligne au sol ; les projectiles ennemis sont rouges.

Le correctif de pause 0.3.1 est conservé : une perte de focus ne met pas le jeu en pause. Masquer la page déclenche la pause automatique. La pause manuelle fonctionne au bouton ou avec Échap. Une défaite permet de reprendre au début de la salle avec le serment conservé ; les rencontres sont réinitialisées et les PV restaurés. Cette reprise reste en mémoire, sans sauvegarde de l’expédition au rechargement.

## Sources et tests

Three.js 0.160.1 est intégré au HTML, sans dépendance externe au lancement. `src/game.js` contient la logique ; `src/template.html` contient l’interface ; `vendor/three.min.js` contient le moteur. `python scripts/build.py` régénère `docs/index.html` et le lien historique `docs/cathedrale-v03.html`.

Tests Python Playwright / Chromium (`/usr/bin/chromium`) :

- `tests/design.py` : choix explicite, annulation et gel du temps pendant le dialogue ; absorption et tir chargé ; coût en PV et leurre ; terrains différents ; secret interrompu par déplacement/tir, stockage local réel et récupération après rechargement ; bénéfice sur les avertissements du boss ; victoire sans le secret ; confirmation et observation tactiles en portrait/paysage.
- `tests/smoke.py` : déplacements, collisions, pièges, transitions, armure du boss, interruption, deuxième phase, victoire par projectiles, défaite et multitouch.
- `tests/input_regression.py` : régression de pause, perte de focus, visibilité, trois doigts, commandes clavier et reprises.

Les tests accélèrent certaines situations et utilisent des états contrôlés. Chromium/WebGL logiciel ne garantit pas la fluidité ou la compatibilité Safari sur téléphone réel ; celle-ci doit être confirmée avec le joueur.

## Limites

Un personnage et trois variations de la même architecture. Pas encore de coop, battle, comptes, sauvegarde d’expédition, modèles détaillés, ombres dynamiques ni reflets réalistes de l’eau. La marque est un secret de prototype ; l’équilibrage des deux serments reste à tester sur de vraies parties.

Three.js est sous licence MIT, incluse dans le HTML et `vendor/THREE-LICENSE.txt`. Cela ne définit pas la licence des créations du jeu. Les anciennes versions sont conservées dans `historique` à la racine du projet.
