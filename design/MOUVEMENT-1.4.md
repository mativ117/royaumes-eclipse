# Mouvement 1.4 — calibration de la Lame

Ce travail améliore le contrôleur web actuel. Il ne transforme pas un rig simple et des animations retargetées en animation AAA. Les dix autres héros gardent leur comportement antérieur ; la Lame sert de premier personnage mesuré.

## Défauts identifiés

- L'ancienne course associait une distance de cycle arbitraire de 1,5 unité à 5,5 unités/s. Avec le clip de 0,75 s, cela donnait un temps de lecture de 2,75× et environ 7,3 appuis/s. Un test de pied verrouillé pouvait passer malgré cette cadence peu crédible.
- L'ancienne IK reconstruisait les deux trajectoires de pied à partir d'un sinus et de la distance du corps. Elle pouvait masquer le mouvement d'un nouveau clip et son transfert de poids.
- L'esquive commune parcourait 4,2 unités en 0,28 s, avec sa vitesse maximale au premier instant, alors que la pose Lame représente plutôt un pas d'évitement.
- Choisir brutalement marche ou course au milieu de leurs vitesses natives change la cadence d'un coup. Le problème existe même si chaque clip est individuellement correct.

## Sources primaires consultées

- [Godot, AnimationTree et root motion](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html) : extraire les données de déplacement et les appliquer au corps contrôlé, synchroniser les cycles et organiser les transitions. Le même principe est applicable dans Three.js ; utiliser Godot n'est pas requis pour ce correctif.
- [Anguelov, Leblanc et Harris, GDC 2012, Animation-Driven Locomotion for Smoother Navigation](https://media.gdcvault.com/gdc2012/slides/Summit_AI/Anguelov_Bobby_AnimationDrivenLocomotion.pdf) : la cinématique des clips impose des limites aux déplacements et aux rotations ; les annotations d'appui servent à synchroniser les transitions. Le système complet décrit dans cette présentation n'est pas reproduit ici.
- [Roche et Torres-Cros, GDC 2016, Fitting the World](https://media.gdcvault.com/gdc2016/Presentations/Roche_Clifford_Fitting%20the%20World.pdf) : conserver l'intention du mouvement d'origine, détecter les contacts et limiter la correction de pied. Une ancre trop éloignée doit être relâchée plutôt que forcer une jambe en extension.
- [Autodesk Golaem, Creating a Locomotion Set](https://help.autodesk.com/cloudhelp/ENU/GOLAEM-Maya/files/tutorials/assets-conversion-0/converting-motions/glm_creating-locomotion-set.html) : cycles, phases de support et vitesse native extraite du déplacement racine. Son exigence d'une animation source avec déplacement est propre à son outil ; notre export en place conserve ce déplacement comme métadonnée.
- [Blender, IK Solver](https://docs.blender.org/manual/en/4.5/animation/constraints/tracking/ik_solver.html) et [NLA](https://docs.blender.org/manual/en/4.5/editors/nla/sidebar.html) : liens de référence pour le travail dans Blender. L'accès complet au manuel a été refusé par l'hôte pendant cette recherche ; les recommandations ci-dessus reposent sur les documents Godot, GDC et Autodesk effectivement consultés.

La provenance CC0 des clips et les décisions de retargeting sont conservées séparément dans [RETARGET-1.4.md](RETARGET-1.4.md). Une bibliothèque d'animations fournit de meilleurs gestes, pas une validation automatique de l'anatomie ou de la mise en scène.

## Contrat entre Blender et le runtime

Le GLB de la Lame porte `motionCalibration`, objet JSON ou chaîne JSON dans les extras de sa scène ou de son rig :

```json
{
  "version": 1,
  "units": "model",
  "gaits": {
    "walk": {"cycleDistance": 1.38, "contacts": {"L": [[0, 0.42]], "R": [[0.5, 1]]}},
    "run": {"cycleDistance": 5.31, "contacts": {"L": [[0, 0.2]], "R": [[0.5, 0.7]]}}
  },
  "dodge": {"distance": 1.6, "duration": 0.4},
  "attacks": {
    "attack1": {"duration": 0.93, "hitAt": 0.13, "activeEnd": 0.2, "travel": 0.5}
  }
}
```

Les valeurs de cet exemple expliquent le format ; celles du GLB et de sa provenance font foi. `cycleDistance` désigne un cycle complet avec deux appuis, mesuré sur la racine source et converti selon le rapport des longueurs de jambe. Durées et fenêtres d'attaque sont en secondes. Les distances sont en unités du modèle ; le runtime applique une seule fois l'échelle du héros (1,07 pour la Lame). Les intervalles de contact sont des fractions de cycle et peuvent franchir 1/0. `phaseOrigin` facultatif aligne le premier appui gauche.

Sans métadonnées valides, le comportement historique reste disponible. Les clips directionnels qui n'ont pas été remplacés ne sont pas présentés comme des mouvements externes retargetés.

## Application

La distance mesurée fixe le rapport entre vitesse réelle et fréquence du cycle. La vitesse du corps est limitée par le mouvement disponible plutôt que de plafonner arbitrairement le temps de lecture en laissant le corps glisser. Le clavier et le joystick utilisent le même calcul après normalisation de leur entrée.

Marche et course calibrées se mélangent selon leurs vitesses natives. Les deux couches utilisent une phase d'appui commune ; la foulée et la cadence moyennes évoluent donc continûment entre les deux clips. Le départ conserve l'anticipation du haut du corps mais active immédiatement les jambes correspondant au déplacement effectif. Arrêt et pivot restent interruptibles.

La pose des pieds vient d'abord du mélange des clips. Lorsque marche et course contribuent ensemble, un appui doit être commun aux deux mouvements : une petite contribution d'une cheville en envol ne doit pas créer un faux appui prolongé. L'ancrage attend aussi que la cheville animée soit basse et que sa vitesse réelle ait diminué. Sans ce contrôle, l'annotation source pouvait arriver pendant la fin de descente du pied retargeté et placer son ancre trop tôt.

Le modèle de production conservait aussi une marge d'origine de 2,5 cm sous les semelles au repos. Une enveloppe visuelle fixe, réservée à la Lame calibrée, retire cette marge une seule fois, à l'échelle du héros. La scène GLTF animée reste intacte ; les ancres et la hauteur de référence sont initialisées dans le même repère corrigé. Cette enveloppe ne déplace pas le collider et n'accumule aucune correction image après image. Sur un cycle complet d'idle et de garde, les vertices skinnés des semelles se trouvent désormais entre +0,27 et +0,50 cm pour le pied gauche, et entre −0,92 et −0,56 cm pour le pied droit. Il reste donc un petit écart de pose entre les pieds, mais le flottement de plusieurs centimètres est supprimé. Les mesures de contacts en marche restent identiques.

L'IK ajoute une correction bornée (au plus 14 cm et 16 % de la longueur de jambe), conserve l'orientation animée du pied et relâche l'appui si l'écart devient trop grand. Les pieds des attaques engagées, sauts et esquives ne sont pas reconstruits comme une course. Les appuis annotés produisent un compteur d'événements pour synchroniser les sons ; le nombre de sons n'est plus déterminé par une distance générique de 0,82 unité.

L'esquive Lame utilise la distance/durée du modèle et une courbe avec vitesse nulle au début et à la fin. Le choix gauche/droite est conservé pendant le geste, même si la visée change. Les esquives des autres héros conservent leur ancienne courbe.

Les attaques Lame retargetées utilisent le corps complet, y compris le bassin et les jambes, jusqu'à 0,10 s après la fin de leur fenêtre active. Le contrôleur réserve alors le déplacement à l'avancée propre au geste. Pendant la récupération, le haut termine son animation mais les jambes reprennent la locomotion si le joueur bouge ; il n'est pas nécessaire d'attendre toute la pose de récupération pour repartir. La collision utilise la lame pendant la fenêtre mesurée, plutôt qu'une seule zone large indépendante du geste. L'engagement physique et les collisions sont intégrés par le contrôleur de combat.

## Vérification et limites

`tests/lame_motion_quality.py` mesure les phases, la cadence, les positions réelles des pieds, la correction et les appuis relâchés sur le GLB chargé par Three.js, sans rendu WebGL pour la partie CPU. L'option d'intégration vérifie le jeu réel et compare clavier/joystick. Les résultats chiffrés doivent être lus avec des captures et une observation du geste en mouvement.

Mesure CPU sur le candidat retargeté du 17 novembre, à 120 Hz, après une seconde d'établissement puis huit secondes de marche droite :

| Vitesse monde | Appuis/s observés | Dérive maximale pendant l'appui | Appuis relâchés |
| --- | --- | --- | --- |
| 1,10 | 1,50 | 2,34 cm | 0 % |
| 2,475 | 1,875 | 0,19 cm | 0 % |
| 3,85 | 2,00 | 0,35 cm | 0 % |
| 5,50 | 2,125 | 2,11 cm | 1,52 % |

À 5,5, la cadence calculée est de 2,121 appuis/s ; le compteur sur une fenêtre courte est quantifié en appuis entiers. Le mélange contient 88,2 % de jog et le temps de lecture effectif du jog vaut 0,990×. La correction maximale sur les quatre essais atteint 11,48 cm, sous la limite de 14 cm. L'esquive parcourt exactement 1,712 unité monde en 0,40 s à 30, 60 et 120 Hz. Ces valeurs décrivent un sol horizontal sans collision ni rotation pendant la mesure ; elles ne remplacent pas un essai de jeu sur téléphone.

Un test qui constate une pose distincte ou l'absence d'erreur JavaScript ne prouve pas un mouvement réussi. Les points artistiques restants comprennent le style des poses, l'adaptation de la main à la longue lame, le regard, les changements brusques de direction, les raccords avec les anciens clips de pas latéraux et l'animation des autres héros. Le sol de cette version est horizontal : ce correctif n'ajoute pas une adaptation prédictive aux escaliers ou pentes.
