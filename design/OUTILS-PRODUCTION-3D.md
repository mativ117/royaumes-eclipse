# Outils de production 3D et choix de plateforme

Le jeu actuel ne se réduit pas à HTML : le navigateur charge du JavaScript, Three.js assure la 3D, les personnages sont des fichiers GLB et Blender sert déjà à leur génération. La fabrication actuelle repose toutefois largement sur des assemblages de primitives et des poses analytiques. C’est la qualité et la variété de cette fabrication qu’il faut faire progresser.

## Pipeline recommandé pour la première revue

Blender pour le modelage, la topologie, les UV, les matières, le rig et les animations. Le premier personnage doit être validé en conception, puis en poses et en mouvement, avant sa généralisation. Le GLB permet de conserver une ressource portable entre moteurs.

Pour garder le jeu accessible par lien PC/téléphone, Three.js peut continuer à servir la séquence de référence. Un moteur avec éditeur apporte des outils de scène, d’animation, de physique et de profilage, mais la migration doit préserver les fonctionnalités et les sauvegardes ou prévoir leur conversion explicitement.

Si une application installable est acceptée, Unity avec URP est une option solide pour une production 3D ambitieuse et son écosystème ; Godot est une alternative libre pertinente pour une direction stylisée, avec un pipeline GLB pratique. Le choix confirmé pour cette étape est de rester ici avec un accès Web PC/téléphone. Aucune migration de moteur n’est engagée ; la ressource GLB reste portable.

## Contraintes Web vérifiées dans les documentations officielles

- Godot Web utilise WebGL 2 et le renderer Compatibility. Les renderers Forward+ et Mobile ne sont pas proposés pour cet export. La documentation indique que les exports mobiles natifs sont nettement plus performants.
- Threads et GDExtensions Web demandent une isolation COOP/COEP ou le contournement PWA documenté. Les réglages d’hébergement doivent donc être vérifiés pour GitHub Pages.
- La documentation Unity actuelle prend en charge certains navigateurs mobiles, dont Safari iOS 15+ et Chrome Android. L’affirmation générale « Unity Web ne supporte pas les téléphones » serait incorrecte.
- Un export Unity Web peut demander des en-têtes adaptés à la compression, ou Decompression Fallback lorsque ces en-têtes ne peuvent pas être configurés.

Sources officielles consultées le 17 novembre 2026 :

- https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html
- https://docs.unity3d.com/Manual/webgl-browsercompatibility.html
- https://docs.unity3d.com/Manual/webgl-deploying.html

## Héros et créatures

Le partage d’un squelette ou de fonctions d’animation ne doit pas imposer la même personnalité gestuelle à tous les héros. Chaque fiche doit définir silhouette, posture, rythme, appuis, arme, attaques, esquive, pouvoir et sons. Les animations propres viennent ensuite, avec retargeting et contraintes lorsque cela convient.

Les ennemis suivent la même exigence. Une créature demande une anatomie, un moyen de locomotion, des articulations, une perception, une anticipation et une récupération lisibles. Les actuels corps prismatiques et manteaux restent des placeholders à remplacer progressivement. On valide aussi une créature de référence avant de multiplier les variantes.
