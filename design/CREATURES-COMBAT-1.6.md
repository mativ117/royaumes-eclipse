# Créatures et combat — intégration 1.6

Cette passe traite deux familles fréquentes de l'aventure. Elle ne refait pas les autres familles ni les boss. Les principes de lecture, préparation, engagement et récupération suivent la comparaison de qualité du projet ; leur application n'est pas présentée comme une équivalence artistique AAA.

## Deux anatomies et deux comportements

Le **Veilleur des fils** remplace l'archer géométrique : corps digitigrade, bras-arc asymétrique, squelette et surface PBR originaux. Sa préparation de 1,1 seconde est accompagnée par le corps, l'émission lumineuse et un trait au sol. La direction ne suit plus le joueur pendant la seconde moitié de ce signe. La flèche sort du socket réel au deuxième pas de 30 Hz du clip de libération, puis l'acteur récupère pendant 1,1 seconde. Hors vue directe, il recherche un angle au lieu de tirer à travers le couvert. Les dégâts et la vitesse de l'ancien projectile restent inchangés.

La **Raie du reflet** remplace le Reflet humanoïde : membrane articulée, mandibules et queue segmentée, avec sa propre nage et son exposition. Elle se déplace pour chercher un angle, devient attaquable pendant sa préparation de 0,9 seconde, s'engage dans une direction annoncée puis récupère pendant 1,3 seconde. Sa course de 4,4 mètres sur 0,4 seconde intègre la même distance à 30, 60 et 120 Hz. Chaque victime peut recevoir une seule fois les 18 dégâts de cet engagement. Le signe au sol n'inflige pas de dégâts.

Un impact visible est borné dans le temps ; une frappe suffisante pendant une préparation l'interrompt. Les interruptions déjà demandées par les pouvoirs du jeu restent respectées. Un clip de mort prend en charge le corps ; le fondu et la libération des ressources restent gérés par le jeu.

## Matières, poses et contacts

Les deux GLB chargent leurs atlas embarqués. Les modèles sont clonés avec squelettes et matériaux indépendants ; les géométries et textures de production restent partagées. La racine est définie par une rotation complète `(0, 0, 0)`, les exports regardant déjà vers `−Z`. Les poses de liaison sont restaurées avant chaque évaluation pour éviter une accumulation de corrections. Les jambes de l'archer utilisent le solveur IK existant pendant la locomotion ; la créature flottante ne revendique pas de contact de pied.

Les ailes de la Raie se replient immédiatement près d'un obstacle. Le pli mesuré sur les vrais sommets utilise un angle local X positif de 1,2 radian pour les deux ailes et 0,66 pour leurs extrémités. Le repli prend priorité sur le battement du clip afin de préserver sa largeur étroite. Le rayon de contact du corps reste 0,55 mètre. Des sondes orientées et rapprochées protègent aussi le bec et la queue longue : le mouvement et la rotation ne vérifient pas seulement le centre. Aucun saut de position ne traverse une porte scellée.

Les corrections ne constituent pas une simulation de tissus ou de corps rigides. Les sondes sont une approximation conservatrice d'anatomie ; la lecture et les passages doivent aussi être revus dans les scènes réelles.

## Intégration et cycle de vie

`src/enemy-direction-v16.js` fournit les hooks : `initEnemyDirectionV16`, `buildEnemyDirectionV16`, `updateEnemyDirectionV16`, `poseEnemyDirectionV16`, `enemyDirectionV16Hit`, `poseEnemyDirectionV16Fallen`, `refreshEnemyDirectionV16FallMaterials` et `disposeEnemyDirectionV16Root`.

Le marqueur d'instance est `e.authoredEnemy`, distinct de `creatureReference` utilisé par le Fauche-Cendre. Le chargement normal est différé depuis les fichiers du site ; le paquet HTML peut fournir `ROYAUMES_ENEMY_DIRECTION_DATA`. Aucune API ni source externe n'est consultée pendant une partie. Les modèles antérieurs sont masqués seulement après l'installation réussie du modèle chargé.

Après la duplication des matériaux de mort, le hook `refreshEnemyDirectionV16FallMaterials(e, copies)` met à jour les références. Le nettoyage enlève les modèles avant le parcours générique, libère une fois les squelettes et matériaux d'instance, et conserve les ressources des templates pour une rencontre suivante.

## Contrôles exécutés

`python3 tests/enemy_direction_v16.py` : **PASS CPU**, sur le comportement et les deux vrais GLB. Le contrôle couvre la chronologie source, l'angle verrouillé, le contournement d'un couvert, les trois cadences de simulation, le contact unique et les seuils solides, les sondes de queue et de rotation, le pli à côté d'un pilier mince, les sommets animés, les os indépendants, l'interruption externe, les références de matériaux de mort et le nettoyage idempotent. Rapport : `/tmp/enemy-direction-v16-report.json`.

`tests/creature_assets_v16.py` contrôle séparément l'anatomie, les cartes embarquées, les poids et les durées de production. Les sources, empreintes et mesures figurent dans `assets/creatures/ENEMIES-PRODUCTION-1.6.json`. Ces contrôles CPU ne remplacent pas la revue WebGL, l'écoute, une partie humaine ou une mesure de performance sur téléphone physique.
