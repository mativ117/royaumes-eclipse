# Retours des captures — 1.1-rc3

## Message masqué devant une stèle

Cause reproduite : `body.has-interaction #notice { display:none!important }` cachait le texte tant que le bouton d’interaction restait affiché. Le joueur devait quitter sa zone pour lire le message. La règle est supprimée. Les messages sont placés sous l’interface supérieure ; en paysage, ils évitent la zone centrale du personnage. L’indice de la fresque reste visible à proximité après lecture.

Quand les zones de deux objets se chevauchent, l’objet le plus proche est choisi, et l’anneau de la fresque/lanterne suit cette cible.

## Décor qui cache le joueur

Les stèles et autres objets interactifs participent désormais à l’atténuation du premier plan. Les six colonnes du parvis sont traitées séparément pour ne pas rendre tout un ensemble transparent. Quatre visées couvrent bas du corps, épaules et tête. Les matériaux propres aux objets remplacés sont libérés avec leur salle ; la liste d’occlusion évite les références à ces objets supprimés.

## Appuis

La destination du pied au début du balancement est rééquilibrée de 0,65 à 0,725 foulée. Cela réduit le dépassement de portée en fin d’appui. Le test porte sur onze héros, deux vitesses et quatre directions. Ce correctif ne fournit pas de nouveaux clips de départ/arrêt/pivot et ne démontre pas une fréquence d’images fluide sur iPhone.

La stratégie de finition est décrite dans [SEQUENCE-REFERENCE.md](SEQUENCE-REFERENCE.md). Cette version est un correctif de lisibilité et d’appuis, sans annonce de saut graphique majeur.
