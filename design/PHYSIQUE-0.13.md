# Déplacements et ombres — 0.13

Cette passe améliore les fondations du niveau existant ; elle n’ajoute pas de nouvelles zones.

## Changements

- Contrôleur au sol circulaire : contacts cercle/rectangle et cercle/cercle, correction selon la normale, glissement et subdivision des déplacements à 12 cm maximum. Les coins des rectangles ne sont plus traités comme des coins carrés agrandis.
- Socles interactifs, refuges et torches solides ; montants de cloche distincts pour conserver le passage central. Les objets masqués après consommation cessent de bloquer. Âme et miroir de sol restent intangibles. Le bassin inclut maintenant son rebord.
- La vitesse réellement parcourue pilote la marche du héros : pousser contre un obstacle ne maintient plus une animation de course. Suppression du double rebond ajouté au squelette animé.
- En qualité Haute, les ennemis et accessoires matériels projettent leur ombre, les disques de substitution ennemis sont masqués. Projection directionnelle stabilisée dans le repère de la lumière ; correction du saut de cible lorsque z vaut zéro.
- En qualité Légère, contacts adoucis ; l’ombre du héros s’élargit et s’efface pendant le bond. Ce mode reste une approximation et ne reproduit pas les silhouettes animées.
- Le calcul d’itinéraire trouve une cellule libre voisine si l’arrondi tombe dans un socle. L’escorte conserve son trajet intangible jusqu’au refuge.

## Références

- [Rapier — contrôleur de personnage](https://rapier.rs/docs/user_guides/javascript/character_controller/) : mouvement demandé et mouvement corrigé, glissement aux contacts, marge de contact. Principes repris dans le contrôleur existant ; Rapier n’est pas ajouté comme dépendance.
- [Glenn Fiedler — Fix Your Timestep](https://gafferongames.com/post/fix_your_timestep/) : conserver une simulation à pas fixe et borner les rattrapages. Le jeu conserve son pas de 1/60 s et subdivise davantage les déplacements rapides.
- [Three.js — DirectionalLightShadow](https://threejs.org/docs/pages/DirectionalLightShadow.html) : caméra orthographique et carte d’ombre locale. Stabilisation ajoutée par quantification dans le plan de projection.

## Vérifications et limites

`tests/physics.py` vérifie une traversée rapide vers les socles et torches, le glissement, l’arrêt de la course contre un pilier, les raccords de plateformes, le vide, la stabilité de projection et l’ombre pendant le bond. Les suites existantes vérifient le parcours complet, les interactions, la sauvegarde, la carte et les commandes tactiles simulées.

Le contrôleur reste sur un plan : pas encore de physique volumique avec gravité, escaliers, pentes ou corps rigides. Le bond reste une capacité visuelle au-dessus de ce plan et ne franchit pas les obstacles solides. Les adversaires ne possèdent pas encore une séparation physique entre eux et le joueur. Certains décors composés gardent une enveloppe simplifiée. Tests Chromium ; fluidité sur téléphone réel à confirmer. Le réglage Haute est nécessaire pour les silhouettes d’ombre animées.
