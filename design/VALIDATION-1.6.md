# Validation de la candidate 1.6-rc1

Clôture du 26 novembre 2026. Les contrôles graphiques sont séquentiels dans Chromium logiciel. Ils ne mesurent ni FPS d'un téléphone, ni qualité artistique, ni durée humaine des niveaux.

## Preuves de production

Deux modèles originaux skinnés, leurs atlas PBR, clips à 30 Hz, sockets et sources Blender sont conservés avec provenance. Les onze GLB de héros et les archives précédentes restent inchangés. Les contrôles CPU `creature_assets_v16`, `enemy_direction_v16`, `camera_direction_v16`, `environment_direction_v16` et `encounter_presentation_v16` ont passé pendant la production : chronologie, poids, appuis, gabarit, couvert, repli des ailes, cadrage, surfaces, nettoyage et audio PCM.

Les captures avant/après conservent caméra, résolution et qualité Légère. Le protocole attend l'ouverture des portes et synchronise la simulation. Les rapports `CAPTURES-DIRECTION-1.6-before.json` et `CAPTURES-DIRECTION-1.6-after.json` distinguent les builds ; ce sont des vues du moteur, pas des concepts générés.

## Contrôles de clôture

Les huit suites de clôture suivantes ont passé le 26 novembre, sur le build final et successivement pour les contrôles graphiques :

| Contrôle | Résultat et portée |
|---|---|
| `enemy_direction_v16` | PASS : chronologie à 30/60/120 Hz, couvert, charge de 4,4 m avec un seul contact, gabarit, ailes et appuis des vrais squelettes |
| `direction_v16_integration` | PASS : GLB/PBR chargés, flèche depuis le socket au temps source, charge infligeant une seule fois 18 PV, réactions, mort, matériaux et nettoyage ; les deux réglages compilent |
| `complete_campaign` | PASS : onze modèles, dix kits de départ, conclusions des trois chapitres, secret, Incarnation et reprise. Parcours contrôlé, sans mesure de durée humaine |
| `render_complete` | PASS : chapitres en bureau/portrait/paysage, shaders Haute/Léger, budgets de dessin, cartes et poses finies |
| `story_sound` | PASS : récit, focus et pause, partitions par chapitre et sortie PCM stéréo |
| `session_actors` | PASS : duel contre bot, couvert, contacts, onze kits, manches, pouvoirs, orientations et sauvegardes |
| `lan_game` | PASS pour deux contextes reliés par un pont en mémoire : rôles, dégâts, pause, manches, déconnexion et sauvegardes. Ce résultat ne valide pas WebRTC natif |
| `interaction_visibility` | PASS : fresque depuis quatre approches, lampe ciblée, indice persistant, collision/transparence des colonnes et affichage adaptatif |

Le contrôle intégré a révélé une raie initialement coincée par sa longue queue près d'une stèle. Son placement initial recherche désormais un volume libre avant l'affichage, sans traverser une porte fermée ; ce cas réel fait partie de la régression.

Les mesures de clôture figurent dans [CONTROLES-1.6.json](CONTROLES-1.6.json). Les captures fixes documentent les matières et les lieux ; aucune nouvelle vidéo comparative à vitesse normale n'est annoncée pour la 1.6. La revue humaine des transitions reste ouverte.

## Paquet et publication

`tests/package_release.py` a passé : deux constructions identiques du ZIP, manifeste et empreintes de chaque entrée contrôlés, sources éditables présentes, archives antérieures inchangées. Le modèle secret et les deux nouvelles créatures se chargent dans le HTML autonome sans requête GLB. Le paquet reste sous 100 Mo (environ 96,3 Mo). Les onze héros conservent les empreintes de la publication 1.5. Le relevé distant sera ajouté séparément après le déploiement, sans réécrire cette archive.

## Limites conservées

L'équivalence AAA n'est pas acquise. Les autres familles/boss et certaines animations de héros restent à produire, le contrôleur demeure plan, et l'esthétique, le plaisir, l'écoute et les performances exigent des essais humains sur appareils identifiés. Les musiques sont des synthèses originales ; aucune bande-son orchestrale enregistrée n'est annoncée. Le transfert LAN natif reste non vérifié dans l'environnement géré, sans contournement de ses politiques.
