# Présence et rythme — 0.10

## Retour traité

Le guidage semblait changer trop vite ; le jeu gardait une présentation très sommaire. Cette version corrige des causes concrètes plutôt que de considérer la direction artistique comme terminée.

## Navigation stable

La 0.9.1 recalculait la route après 3,5 unités de déplacement ou deux secondes, et choisissait certains sous-objectifs selon leur distance à chaque appel. En outre, l’identifiant d’une vanne ou d’un ennemi pouvait remplacer celui de la quête dans la construction de son descripteur.

La quête et sa cible ont maintenant des identifiants distincts. Une vanne, un Reflet ou une chaîne reste la cible jusqu’à sa résolution. Le joueur progresse sur la route existante ; marcher le long de celle-ci ne déclenche plus une recherche. Une déviation supérieure à 2,2 unités doit durer plus de 1,1 seconde avant recalcul. Une cible mobile doit s’éloigner de plus de quatre unités, avec au moins 2,5 secondes entre mises à jour. Les changements de portes ou d’étape restent pris en compte immédiatement.

Les repères au sol sont ancrés dans le monde. Ils apparaissent sept secondes à la demande, avec G ou « Repère ». Ils ne courent plus automatiquement devant le héros. La flèche du HUD tourne progressivement. La carte conserve le chemin. Le guidage reste désactivable. Les repères suivent le sol et les obstacles ; ils ne prévoient pas les attaques temporaires.

## Mouvement et combat

Les pieds et genouillères du héros suivent désormais les jambes articulées ; ils étaient auparavant fixés au personnage pendant que les jambes bougeaient. Le rebond vertical est réduit. Les frappes de mêlée ralentissent le déplacement pendant la préparation et plantent les appuis ; un vrai coup reçu annule l’attaque en cours et rend sa charge non dépensée. Les fenêtres de dégâts restent celles de la 0.9.

La vitesse de traversée libre reste celle de la 0.9.1 : cette passe traite d’abord la stabilité du chemin et l’engagement des frappes. Elle ne prétend pas avoir validé l’allure préférée du joueur.

## Présence du monde

Les ennemis ont des corps et équipements propres à leur rôle : combattant, archer avec arc, Sentinelle blindée, lanceur au bâton et grands gardiens. Les armes suivent le bras animé. Les patrouilleurs ordinaires détectent le joueur en environ 0,7 seconde à portée et en ligne de vue ; ils restent sur une courte patrouille autrement. Un coup reçu les alerte immédiatement. Les boss et rencontres spéciales gardent leur logique dédiée.

Les Archives ont des rayonnages, la Forge des fours et conduites, les jardins des garde-corps et masses végétales. Les sols ont une palette plus sobre selon la zone. Les nouveaux décors extérieurs restent hors des chemins ; les fours utilisent les obstacles déjà présents. Géométrie et matériaux sont partagés ou regroupés en instances pour limiter les appels de rendu.

## Validation et limites

`tests/feel.py` vérifie la conservation des routes et des cibles, le délai de recalcul, l’ancrage et la demande des repères, la ligne de vue, les silhouettes, les pieds articulés et l’interruption des attaques. Les suites de mission, lisibilité, multitouch et publication restent utilisées.

Les modèles sont encore procéduraux. Les décors, squelettes et animations ne sont pas les assets définitifs. Les tests mobiles sont simulés ; le rendu et la fluidité doivent encore être évalués sur téléphone réel. La cible de 10–15 minutes reste à mesurer en partie humaine, surtout après ces changements de rythme.
