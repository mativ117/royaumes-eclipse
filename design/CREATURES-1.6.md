# Deux familles originales — fabrication 1.6

Le Veilleur des fils remplace l'apparence d'`archer` ; la Raie du reflet remplace celle de `shade`. Ce sont deux sculptures originales avec squelette, peau déformée, atlas PBR et gestes propres. Elles ne remplacent ni les boss ni le Fauche-Cendre. Leur niveau artistique reste à revoir depuis la caméra du jeu.

## Ressources livrées

| Famille | Anatomie et signal | Actions et événements |
|---|---|---|
| Veilleur des fils | Thorax continu noir, jambes digitigrades, crête et mandibule, côtes céramiques, bras-arc vivant asymétrique et fissure sternale ambrée | `idle` 2,4 s ; `move` 1 s ; `windup` 1,1 s ; `release` 0,2 s ; `recover` 1,1 s ; `hit` 0,3 s ; `death` 1,1 s. Départ du projectile à 2/30 s du clip de libération |
| Raie du reflet | Thorax flottant, tête et mâchoire, membranes nervurées, appendices de prise et queue à quatre segments | `idle` 2,4 s ; `move` 1,4 s ; `windup` 0,9 s ; `release` 0,4 s ; `recover` 1,3 s ; `hit` 0,3 s ; `death` 1,1 s ; `phase` 1,2 s |

Les corps, matières et clés proviennent de [build_enemy_v16.py](../scripts/build_enemy_v16.py), sans ressource artistique externe. Il ne s'agit pas de capture de mouvement. La fabrication n'ajoute pas une licence externe aux créations originales du projet.

Chaque export GLB contient six matériaux et trois images embarquées : couleur 1024², normale et carte de données ORM 512². Les sources Blender compressées sont dans `assets/source/creatures/`. Les caractéristiques, durées et empreintes sont dans [ENEMIES-PRODUCTION-1.6.json](../assets/creatures/ENEMIES-PRODUCTION-1.6.json) et les fichiers de provenance individuels. Les sauvegardes d'éditeur `.blend1` restent exclues du dépôt.

## Contrat d'intégration

- Les deux exports regardent vers **−Z en GLTF**, sans ajouter un demi-tour dans le runtime. Origine au sol ; la Raie flotte par son anatomie. Nœud `head` disponible sur les deux, socket `muzzle` sur le Veilleur, matériau `Threat glow` pour le signal d'attaque.
- Les noms d'os à points sont normalisés par le chargeur Three.js : `wing.L` devient `wingL`, `wing_tip.L` devient `wing_tipL`, `tail.1` devient `tail1`. Les alternatives d'origine peuvent être acceptées par le runtime.
- Le squelette et les matériaux d'un ennemi doivent être clonés par instance ; les buffers géométriques et cartes peuvent être partagés puis libérés avec leur modèle source. Les modifications de pose et les réactions ne doivent pas déformer les autres instances.
- La Raie ouverte atteint environ ±1,160 m latéralement. Un repli **après la pose animée**, par multiplication locale autour de X de **+1,2 rad pour les deux ailes** et **+0,66 rad pour les deux extrémités**, réduit son rayon latéral de repos à 0,516 m. Le signe est le même des deux côtés. Le sommet replié monte à environ 2,24 m ; ne pas replier une aile vers le sol.
- L'empreinte longitudinale de la Raie ne se réduit pas à sa capsule centrale : **avant 1,102 m vers −Z**, **arrière 1,963 m vers +Z**. Le contrôleur doit tester cette anatomie lors du déplacement et des rotations près des obstacles, en plus du repli des ailes. Ces dimensions ne justifient pas le passage à travers un seuil fermé.
- L'archer possède une origine de pied proche du sol. Cela ne constitue pas une mesure de foot planting pendant son déplacement : cadence, contact et éventuelle IK sont vérifiés dans le runtime. La Raie n'annonce aucun appui de pied.

## Vérification réellement exécutée

`python3 tests/creature_assets_v16.py` : **PASS CPU** sur les deux GLB réels. Vérification des empreintes, cartes embarquées, UV/normales, poids normalisés, durées de chaque clip, géométrie skinnée finie pendant toutes les actions, pieds de repos et socket frontal du Veilleur, et sommets des ailes repliées de la Raie. [Mesures détaillées](CREATURES-MESURES-1.6.json).

Un premier export utilisait par erreur une scène Blender à 24 Hz avec des clés à 30 Hz. Il a été remplacé : la scène et les clés finales sont à 30 Hz, commencent à zéro et leurs durées sont vérifiées contre les données GLB. Les images de revue CPU sont de vrais rendus Blender sous `/tmp/enemy-v16-review/`; elles ne constituent pas des captures du jeu publié. La validation WebGL, le combat intégré, les collisions en mouvement et les performances physiques restent du ressort de l'intégration.

Pour régénérer :

```sh
blender -b -t 4 --python scripts/build_enemy_v16.py -- archer shade
python3 tests/creature_assets_v16.py
```

L'option `--no-render` conserve la production des modèles et des sources en sautant uniquement les vues CPU de revue.
