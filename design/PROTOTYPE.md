# La nef des serments — prototype 3D 0.7

Cette version travaille la direction artistique sans changer les règles de combat, les personnages disponibles ou les parcours.

## Cathédrale

Arches latérales et fenêtres stylisées orangées, colonnes en pierre texturée, incrustations métalliques au sol, statues monumentales à l’extérieur de l’arène et halo au sol. Le quadrillage de développement est remplacé par un dallage procédural. Le sol est éclairci pour conserver le contraste avec les ennemis et les zones dangereuses.

La lumière orange des fenêtres et les halos des braseros renforcent l’ambiance. Une brume basse très discrète anime le sol. Ce sont des effets simples : pas de lumière volumétrique calculée, de reflets réalistes ou d’ombres dynamiques coûteuses.

## Personnages et lisibilité

Le Rempart reçoit des épaulières, un équipement dorsal, une ceinture et des détails de bottes et de genoux. Le Voltigeur reçoit une cape animée, des ornements de tenue et une écharpe plus vivante. Les silhouettes restent des modèles procéduraux provisoires.

Les messages sont déplacés pour libérer le personnage, et les longues inscriptions sont raccourcies ou ajustées à leur support. Les avertissements de combat et les interactions restent prioritaires sur la décoration.

## Mode léger

Le mode léger réduit la résolution de rendu, cache la brume, les grandes statues extérieures et la moitié des halos. Les fenêtres, les arches principales et les silhouettes restent visibles. Aucune collision ni zone dangereuse ne dépend de ce réglage.

Les bandes répétées au sol utilisent une géométrie instanciée. Aucun modèle, texture ou moteur n’est téléchargé à l’ouverture : toutes les textures sont produites localement par le navigateur. Les mêmes ressources sont réutilisées entre les salles.

## Sources et vérifications

`src/art.js` contient la décoration et les textures procédurales. `src/game.js` conserve la logique et les animations des héros. `python scripts/build.py` intègre ces fichiers et le moteur dans la page publiée.

`tests/art.py` vérifie l’affichage en 1280×800, 844×390 et 390×844, les textures, l’absence de grille, le budget de soumissions de rendu, le mode léger, la stabilité des collisions et l’absence de pause sur une perte de focus. Les captures sont examinées pour le contraste et le placement des textes. Ces tests Chromium/WebGL logiciel ne mesurent pas la fluidité sur téléphone physique.

Les autres tests restent disponibles. [Mécaniques de la 0.6](PROTOTYPE-0.6.md), [héros](PROTOTYPE-0.5.md), [publication](PUBLICATION.md).

## Suite et limites

Toujours deux personnages et trois salles du premier niveau. Les modèles définitifs, les autres héros, les deux niveaux suivants, les comptes et les modes réseau restent à développer. Les ombres et reflets réalistes ne font pas partie de cette version.
