# Portes et conflits de surfaces — audit et correctifs 1.5

Point de contrôle du 23 novembre 2026. Sources et tests CPU inspectés ; aucune capture WebGL nouvelle n’est annoncée par cette note. La revue du jeu reste à effectuer lors de l’intégration finale.

## Pourquoi les portes devenaient démesurées

Les seuils de la Cathédrale mesurent **19, 28, 46 ou 48 unités** dans [world.js](../src/world.js), lignes 31–41 au moment de l’audit. Leur largeur sert aussi aux routes et collisions. La porte précédente divisait cette largeur en deux battants : chaque feuille mesurait donc de 9,5 à 24 unités. En tournant de 90°, elle occupait jusqu’à 24 unités dans la profondeur des passages voisins.

Le parent était déjà remis à l’échelle 1 par `sculptGates` : ce défaut provenait de la taille des battants, et non d’une double application de l’échelle. Réduire simplement la largeur de l’objet aurait séparé décor, collision et progression.

## Correctif des seuils

[art-direction.js](../src/art-direction.js), fonctions `sculptGates`, `setCraftedGateOpen`, `craftedGateRequiredClearance` et `updateCraftedGates` :

- La largeur de chaque seuil et ses règles de quête restent intactes. Des modules d’au plus 3,2 unités montent verticalement, comme une herse monumentale.
- Deux lots instanciés par seuil remplacent les feuilles ; le nombre d’appels de dessin de la porte reste borné. Les ornements sont construits à l’échelle du module, sans étirer une texture de sol sur toute la largeur.
- La profondeur des panneaux reste de **0,13 unité au maximum**, porte fermée, à mi-course et ouverte. La largeur ne devient plus une profondeur de battant.
- Le passage reste bloqué tant que les barres visibles ne dégagent pas le corps. Le dégagement minimal est de 2,5 unités ; les métadonnées `bodyHeight`, lorsqu’elles existent, incluent le corps et la couronne, avec l’échelle du modèle et une marge de 0,05. Les armes ne déterminent pas cette hauteur.
- Les panneaux complètement rétractés sont masqués et ne peuvent laisser de collision invisible, même pour un futur costume plus grand que le dégagement nominal. Leurs ombres sont coupées dès que le passage est libre, pour éviter une fausse poutre au plafond.
- Une fermeture demandée attend la sortie d’un acteur présent dans le seuil. Cette protection ne déverrouille jamais une porte qui n’a pas été ouverte légitimement.

La collision réelle utilise `craftedGate.passable` dans `solidActive`, dans [game.js](../src/game.js). Un déverrouillage de quête ne retire donc plus la collision avant que le passage soit visuellement dégagé.

## Vérification exécutée

`python tests/doors_materials.py --integration` **passe en CPU, sans renderer WebGL**. Le test charge les géométries Three.js réelles et lit les neuf seuils natifs dans le code du monde. Il vérifie :

- les boîtes englobantes des instances à ouverture 0, 0,5 et 1 : largeur conservée, profondeur bornée et dégagement égal au sommet inférieur réel ;
- les deux lots, les normales finies, le matériau métallique et l’absence de carte de dallage étirée ;
- la cohérence de `solidActive`, les protections contre l’écrasement et l’absence de déverrouillage gratuit ;
- une ouverture identique à 30, 60 et 120 Hz ; après une seconde, la progression mesurée vaut environ 0,981684 ;
- un corps plus haut, un compagnon à échelle différente, et la disparition complète des panneaux sans mur invisible.

La revue finale doit encore montrer chaque famille de seuil en jeu, depuis les deux côtés, avec le héros le plus haut, en Haute et en Léger. Ces contrôles de géométrie ne jugent pas à eux seuls la mise en scène de l’ouverture.

## Conflits de surfaces distincts des portes

Deux causes de scintillement ont été identifiées dans [journey.js](../src/journey.js) :

| Lieu | Cause constatée | Correctif présent dans les sources |
|---|---|---|
| Chapitre II, traces et Gué | Deux surfaces de traces chevauchaient le Gué sur trois unités de profondeur ; leurs sommets étaient tous à Y = 0, avec des UV différents | `uniqueGroundRectangles` soustrait les surfaces déjà dessinées. Les régions de navigation restent inchangées |
| Chapitre III, escale secrète | Les deux rectangles de l’île se superposaient sur une partie de leur surface ; les anciennes boîtes débordaient aussi certaines limites logiques | Les nouvelles dalles représentent l’union des régions secrètes sans double surface ni débordement ajouté au sol logique |

Le calcul se trouve dans [ground-layout.js](../src/ground-layout.js). `python tests/ground_layout.py` **passe en CPU** : aire de l’union, absence d’intérieur superposé, conservation du sol et cas de régions imbriquées. Aucun décalage vertical arbitraire des dalles n’a été utilisé pour cacher le problème.

Cela ne constitue pas une vérification de toutes les textures du jeu. Les densités de texels, coutures, répétitions, transitions de matières et contacts aux autres accessoires demandent encore une revue par zone. Les abîmes et espaces négatifs intentionnels ne doivent pas être confondus avec un sol manquant.

## Références de méthode

Le [référentiel du projet](REFERENTIEL-QUALITE.md) conserve les sources primaires Three.js r160 sur les [ombres](https://github.com/mrdoob/three.js/blob/r160/manual/en/shadows.html), l’[optimisation de nombreux objets](https://github.com/mrdoob/three.js/blob/r160/manual/en/optimize-lots-of-objects.html) et la [gestion des couleurs](https://github.com/mrdoob/three.js/blob/r160/docs/manual/en/introduction/Color-management.html). L’application ici vise un défaut géométrique et une surface dessinée deux fois ; augmenter la résolution des ombres ou des textures ne les aurait pas corrigés.
