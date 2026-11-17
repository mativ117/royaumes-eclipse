# Validation 1.2-rc1 — première production de la Lame

Le 17 novembre 2026 : direction du concept approuvée, Web PC/téléphone conservé. Le modèle réel reste plus simple que la planche et doit être revu séparément.

## Vérifications locales

Suites passées après intégration : input_settings, animation_layers, stance_motion, complete_campaign, local_modes, physics, interaction_visibility, profiles, publication et lame_reference. L’archive autonome et les archives antérieures passent également package_release.

- Mini-carte et barre PC : avant, recouvrement de 18 pixels ; après, la mini-carte commence 14 pixels sous la barre, aux largeurs 1024, 1366 et 1920.
- Remappage clavier solo effectif, ancienne touche neutralisée, conflits, annulation, répétition, attaque maintenue, saisie de formulaire, clavier partagé, reset et persistance locale vérifiés. La touche Échap ferme aussi correctement le guide.
- Modèle Lame : deux groupes skinnés compatibles, textures PBR intégrées et 23 clips. Le choix direct via `?hero=lame` prépare son modèle avant le démarrage.
- Trois trajectoires de lame distinctes, garde, strafe et appuis évalués dans le jeu. Atelier 3D chargé et rendu en 1100×760 et 390×844, gestes sélectionnés et textures vérifiées.
- Campagne, personnages, profils, modes locaux, collisions et ancienne URL conservés.

Les essais sont contrôlés dans Chromium ; ils ne constituent ni un essai sur iPhone physique, ni une validation artistique, ni une mesure de durée humaine. Le modèle et ses déformations restent en première production : drapés, coiffure, textures fines, transitions et contacts demandent encore une revue.

HTML SHA-256 : `04d5af3b4e96b7f4ae1a2b580f9f8cfea303ee1d40837600e09cfa1806bb183c`.
Source intégrée SHA-256 : `136e25772c3432784362533a315c713644d2b1c483dbb460af1bc14bce9fca38`.
Lame GLB SHA-256 : `d6c2066da95dac821b39632f59b2a524ef43d64ef82bd7d6280a1652927c2ec5`.

La publication distante est vérifiée ensuite avec verify_live, smoke_live et smoke_lame_live. Le ZIP garde le contenu local validé avant le relevé distant.
