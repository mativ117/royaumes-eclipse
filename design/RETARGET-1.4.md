# Retarget de la Lame — passe 1.4

État : **production en cours, résultat à vérifier en poses et à vitesse normale**. La géométrie originale, les matériaux et le squelette de la Lame sont conservés ; l’adaptation des animations ne vaut pas encore validation de leur qualité dans le jeu.

## Sources et licence

Les éditions Standard gratuites de [Universal Animation Library](https://quaternius.itch.io/universal-animation-library) et [Universal Animation Library 2](https://quaternius.itch.io/universal-animation-library-2) ont été obtenues le 17 novembre 2026 via leurs pages officielles. Les fichiers `_RM` d’origine et leurs licences sont conservés dans `assets/animations/quaternius/`.

La licence fournie dans chaque archive est **CC0 1.0 Universal**. Les versions Pro et Source n’ont pas été téléchargées. L’annonce de 120+ animations concerne le produit complet et ne décrit pas la quantité de l’édition gratuite. Les fichiers source ont chacun 43 animations ; le pipeline sélectionne les clips utiles, sans publier tous ces gestes comme des capacités du personnage.

Les mouvements sont des animations attribuées à Quaternius et à ses animateurs. Aucune provenance de capture de mouvement n’est annoncée. Le mannequin livré par la bibliothèque sert de source de squelette et de mouvements ; l’apparence de la Lame reste originale.

Voir la [provenance exacte](../assets/animations/quaternius/PROVENANCE.json) pour les SHA-256 des archives et des GLB, les noms de membres, les identifiants de fichiers publics et les animations disponibles. Les licences et README originaux accompagnent les fichiers. Aucune URL signée temporaire n’est stockée.

## Fabrication intégrée

Le générateur dédié est `scripts/retarget_lame_animations.py`. Il ouvre la sculpture existante, importe les deux rigs Standard puis échantillonne leurs poses à 30 Hz. Les animations `idle`, `guard`, `walk`, `run`, `attack1`, `attack2` et `attack3` sont remplacées ; seize actions de la base restent compatibles. Les pas arrière, latéraux, petits départs/pivots et esquives ne sont pas annoncés comme des clips capturés ou refaits par Quaternius.

La course utilise **Jog_Fwd_Loop**, pas Sprint_Loop : son cycle de 0,933333 s couvre 5 m dans la source. Après le rapport de longueur des jambes (1,062104), cela donne 5,310519 unités modèle ; avec l’échelle du jeu, la lecture à 5,5 unités/s reste proche de 0,90×. Le sprint de la bibliothèque correspondrait à plus de 9 unités/s dans notre personnage et aurait donné une course visiblement ralentie à notre vitesse de jeu. La marche utilise **Walk_Loop**, cycle 1,333333 s et 1,380735 unité modèle.

Les fenêtres de contact des pieds sont dérivées de la hauteur et de la vitesse des chevilles dans la source avec déplacement racine. Le contrôleur reçoit les distances par cycle et ces supports, plutôt qu’une longueur de foulée arbitraire. Les clips exportés restent sur place dans le plan horizontal ; le mouvement vertical du bassin est conservé. Les nouvelles clés commencent à la frame zéro pour éviter une frame de décalage entre les contacts et le GLB.

Le transfert corrige la différence entre la T-pose des sources et les bras déjà inclinés de la sculpture. Sans cette calibration, les bras se seraient abaissés deux fois. Le bras droit reprend la garde d’épée pendant marche/course, avec le mouvement du torse ; le bras libre conserve le mouvement de locomotion.

## Arme et vêtements

Un socket `weaponGrip` sous `hand.R` permet de respecter l’axe de la paume source sans faire pivoter artificiellement le poignet. Les sommets de l’arme sont liés à ce socket. Les points `blade_base` et `blade_tip` suivent le départ et l’extrémité de la lame pour le balayage de collision et la traînée. Les anciens joints conservent leur repos ; les anciens clips restent utilisables. La pointe ne passe plus sous le sol dans les trois attaques échantillonnées.

Les longs pans frontaux reçoivent au moins 85 % d’influence du bassin pour éviter de monter devant le visage pendant une flexion de cuisse. Les deux joints de cape gardent une direction gravitaire et compriment la longueur lors des accroupissements. Cela corrige le principal effet de panneau horizontal ; **ce n’est pas une simulation physique du tissu**. Les plis restent rigides et peuvent masquer une partie du torse pendant les rotations. La silhouette et la prise des doigts demandent encore une revue artistique.

## Attaques et contacts livrés

| Action | Source | Durée | Fenêtre active mesurée | Avancée maximale modèle |
|---|---|---:|---:|---:|
| `attack1` | Sword_Regular_A puis début de récupération A_Rec | 0,933333 s | 0,233333–0,333333 s | 0,872115 |
| `attack2` | Sword_Regular_B puis début de récupération B_Rec | 1,033333 s | 0,200000–0,333333 s | 0,150000 |
| `attack3` | Sword_Regular_C, fin raccourcie | 1,400000 s | 0,600000–0,733333 s | 1,200000 |

Les poses sources sont lues à vitesse normale. Les récupérations tronquées se fondent vers la même garde sur leurs huit dernières poses ; elles ne sont pas simplement coupées. La fenêtre active est dérivée de la trajectoire de la pointe retargetée, avec un seuil de vitesse autour du balayage. Elle définit une période de test de collision ; elle ne doit pas infliger des dégâts à un cône entier en un instant. L’équilibrage de ces durées et ouvertures reste à essayer dans une partie.

`motionCalibration` est exporté dans les extras du rig et repris dans `assets/characters/LAME-PRODUCTION.json`. Il contient les foulées, contacts, esquive cible et durées/fenêtres d’attaque. Les masques, matériaux, textures et coordonnées de la sculpture sont conservés ; leur empreinte géométrie/UV est vérifiée contre la livraison 1.3.

## Reproduire et vérifier

Pour une reconstruction complète, lancer d’abord le générateur de sculpture, puis l’adaptateur d’animation :

```sh
blender -b -t 4 --python scripts/author_lame_reference.py
blender -b -t 4 --python scripts/retarget_lame_animations.py
python tests/retarget_assets.py
```

L’option `-- --preview` du second script produit des vues CPU non retouchées dans `/tmp/lame-retarget/`. Le fichier Blender final conserve les 23 actions éditables et les matériaux empaquetés. Les sources d’animation restent séparées et créditées. Le transfert n’importe aucun mannequin supplémentaire dans le jeu.

`retarget_assets.py` passe sans renderer : géométrie/UV conservées, atlas PBR, 23 clips, sockets, durées exactes, cadence, clés finies, racine sur place et sources CC0 intactes. Ces vérifications ne valident pas à elles seules le naturel, le rythme du combat ou les déformations : la revue à vitesse normale dans le moteur reste nécessaire.
