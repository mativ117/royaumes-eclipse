# Validation — Ambre et obsidienne, 1.1-rc2

Contrôles locaux du 17 novembre 2026. Le déploiement distant est vérifié séparément après l’envoi du commit ; le ZIP conserve le résultat local à cet instant.

## Identité du jeu

- Version : `1.1-rc2`.
- HTML généré, SHA-256 : `0b9467268ee21870775019d9ab7e66caba5c9e370d45614c00cb1b20efb9a9a4`.
- Sources intégrées, SHA-256 : `e3a8da2ba8c5ed34a518dfca71020db5bb35f0bbafc6d2dca6b9d94ec95ef315`.
- Onze modèles actualisés : empreintes dans `docs/version.json` et `assets/characters/PROVENANCE.json`.

## Contrôles de cette passe

Les suites art_direction, dynamics, expedition, feel et sanctuary ont passé les contrôles de rendu, navigation, progression et animation de cette passe. Après l’ajout du récit et du son, onze suites ont été exécutées de nouveau avec succès :

| Suite | Résultat vérifié |
|---|---|
| animation_layers | Marche pendant le tir, appuis, prise du fusil, recul, esquive et lame |
| physics | Contacts et glissement, bordures, immobilité face au mur et projection stable des ombres |
| mobile_world | Deux orientations, vrai multitactile simulé, attaque avec déplacement, carte, serment et reprise |
| readability | Routes sûres, objectifs, formes et états des objets, cartes défilantes et largeur d’écran |
| complete_campaign | Onze modèles, dix kits accessibles, progression et conclusion des trois chapitres, secret et reprise |
| local_modes | Coopération, relevage, clavier et manettes simulées, duel et Couronne |
| profiles | Export/import, refus d’import invalide, secret, réglages et continuation |
| story_sound | Chronique, fins protégées, pause, navigation, thèmes et rendu PCM stéréo non silencieux sans saturation dans le test |
| presentation | Capes orientées vers le bas, matières, rendu HDR, mode léger, chute et nettoyage des ennemis |
| publication | Build reproductible, anciennes adresses, accueil et configuration actuelle à la racine |
| render_complete | PC, téléphone vertical et paysage, deux qualités, shaders et limites de commandes de dessin |

Le test des ombres mesure la stabilité dans le plan de projection du nouvel éclairage en contre-jour, tout en contrôlant la continuité du suivi en profondeur. Il ne suppose plus que le point visé par la lumière reste fixe sur les trois axes.

La suite package_release a passé les contrôles : archives précédentes intactes, ZIP déterministe et version autonome contenant les onze modèles, sans requête de modèle distante. Les dix-sept suites de la passe sont donc validées dans les limites indiquées ci-dessous.

## Preuves et limites

Les captures comparatives 1.0/1.1 sont réalisées dans le moteur, mêmes positions et caméra, par `scripts/capture_presentation.py`. La chronique possède sa propre capture. Les images historiques 0.11/0.12 restent inchangées.

Les tests de campagne contrôlent les états et les règles. Ils ne démontrent ni une durée humaine de 10–15 minutes, ni une qualité artistique équivalente aux grands jeux cités. Chromium et les entrées simulées ne remplacent pas un essai sur téléphone et manettes physiques. Le mix musical nécessite encore une écoute critique en situation.

La publication effective sera contrôlée par `scripts/verify_live.py` (HTML, onze modèles, comparaison et ZIP identiques aux fichiers locaux) et `scripts/smoke_live.py` (jeu public, chargement d’un héros distant, chapitre II, récit et musique).
