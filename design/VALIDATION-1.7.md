# Validation 1.7-rc1

Correction du 26 novembre 2026, base publiée 1.6. Critique reçue : silhouettes proches d’oiseaux/canards, attaques et dégâts visuellement faibles.

## Production

Trois sources originales Blender reprises (`author_creature_reference.py`, `build_enemy_v16.py`) : crânes courts, mâchoires profondes, masque vertical, volumes d’épaule/dos, griffes courtes et réponse moins métallique. Les noms de modules v16 désignent leur origine ; la provenance courante et `ENEMIES-PRODUCTION-1.7.json` identifient les nouveaux exports. Les anciens GLB restent dans les archives 1.6.

Le [module de combat](COMBAT-VISUEL-1.7.md) distingue contact accepté et blocage, utilise la trajectoire réelle de la lame ou du projectile et borne les ressources. Les dégâts, portées, fenêtres et collisions ne sont pas augmentés. Le court arrêt d’impact existant est conservé. Le Fauche-Cendre reçoit un recul local du thorax et de la mâchoire, sans déplacement physique inventé.

## Preuves

Les relevés `CAPTURES-COMBAT-1.7-before.json` et `CAPTURES-COMBAT-1.7-after.json` conservent versions, empreintes, qualité et cadrages. Les vidéos du moteur sont une simulation fixe lue à vitesse normale, sans audio ; elles ne prouvent pas des FPS matériels. La séquence après applique réellement 160 PV de dégâts : la capture de contact ne représente pas une frappe décorative sans effet. Les huit suites finales passent : `creature_assets_v16` (poids, skins, atlas, durées, volume replié), `enemy_direction_v16` (appuis et attaques), `combat_feedback_v17` (onze profils, fenêtres, contacts, pointes, plafonds et nettoyage), `combat_feedback_integration` (vrais PV, phase invisible, bouclier, invulnérabilité, mort, deux shaders, absence de double contact en duel), `direction_v16_integration` (créatures dans le jeu), `render_complete` (chapitres et formats Haute/Léger), `session_actors` (onze kits, couverts, duels et reprises) et `lan_game` (deux contextes via pont en mémoire). Le test `creature_reference` passe aussi pour les quatre appuis du Fauche-Cendre. Les résultats sont conservés dans [CONTROLES-1.7.json](CONTROLES-1.7.json).

Le test du paquet passe : deux ZIP identiques, manifeste et contenus contrôlés, modèle secret et nouvelles créatures chargés en HTML autonome sans requête GLB. Le projet éditable reste sous 100 Mo, environ 97,8 Mo. Les onze héros et les archives précédentes conservent leurs empreintes. Le [relevé distant](PUBLICATION-1.7.json), ajouté sans réécrire ce paquet, confirme le workflow réussi pour `a1363cb`, les fichiers publics identiques et les contrôles aventure, atelier, duel bot/lobby LAN non appairé passés. Le ZIP vérifié fait exactement 97 816 064 octets.

## Limites

La finition artistique reste à apprécier humainement. Les autres familles et boss conservent leurs anciens modèles ; les animations des héros ne sont pas remplacées par cette correction d’effets. Le LAN invité reçoit les PV mais pas le type exact de coup : son accent reste neutre. Les essais en mémoire ne valident pas WebRTC natif ou deux téléphones. Aucun gain de FPS, niveau AAA atteint ou durée humaine de partie n’est annoncé.

Les attaques reçues des anciens contrôleurs ne transmettent pas toutes une origine au retour visuel : dans ces cas, un accent local utilise une orientation par défaut. Leur attribution directionnelle complète reste à étendre.
