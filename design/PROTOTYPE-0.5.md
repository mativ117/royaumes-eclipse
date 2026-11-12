# La nef des serments — prototype 3D 0.5

## Deux personnages accessibles immédiatement

| Personnage | Combat | Pouvoir | PV de base | Esquive de base |
| --- | --- | --- | --- | --- |
| Dernier Rempart | Tirs à distance | Bouclier bleu 3 s et onde de choc ; recharge 9 s | 150 | 1,8 s |
| Voltigeur | Combo de trois frappes en arc | Bond de 0,75 s puis frappe au sol ; recharge 7 s | 110 | 1,15 s |

Le choix au menu change la silhouette, la tenue, les armes, les effets et les noms des commandes. Le Voltigeur possède une écharpe rouge et une lame lumineuse. Le Rempart conserve son armure et son fusil. Modèles toujours procéduraux et provisoires.

## Voltigeur

Les frappes font 44, 44 puis 66 dégâts, avant les modificateurs de serment et l’armure du boss. Le combo se réinitialise après 0,95 s sans attaque. Les coups ne touchent qu’à portée, devant le personnage et sans obstacle entre la cible et lui.

Le bond produit une vraie élévation visuelle et une frappe au sol de 95 dégâts à l’atterrissage. Il protège brièvement et peut interrompre une préparation du boss à courte portée. Le joueur peut se déplacer pendant le bond ; les murs restent infranchissables. Le cercle orange indique la zone de réception. Le pouvoir est annulé sans explosion si une transition de salle l’interrompt.

## Serments adaptés aux deux héros

- Braise : +40 PV au maximum du personnage ; impacts absorbés par le pouvoir accumulés dans la prochaine attaque, jusqu’à trois charges de +20 dégâts. L’esquive prend 0,6 s de plus à se recharger. Pour le Voltigeur, les impacts sont absorbés pendant le bond, et les charges renforcent la prochaine frappe de lame.
- Élan : -30 PV au maximum du personnage ; esquive accélérée (minimum 0,8 s) et leurre. Le Voltigeur passe donc à 80 PV ; le Rempart à 120 PV.

Le dialogue de serment affiche les chiffres et conséquences correspondant au personnage choisi. Les deux héros disposent des mêmes trois salles, du secret facultatif et des reprises après défaite. Le choix du héros est conservé lors d’une reprise de salle.

## Contrôles

PC : ZQSD/WASD/flèches ; souris pour viser ; clic pour attaquer ; Espace pour esquiver ; E pour le pouvoir ; F pour examiner/observer ; Échap pour pause.

Téléphone : joystick, visée automatique, boutons Frapper/Tirer, Esquive et Bond/Bouclier. Portrait et paysage pris en charge. L’interface est allégée sur les écrans courts ; les messages ne masquent plus le bouton d’interaction.

## Vérification

`tests/heroes.py` vérifie la sélection, les statistiques et silhouettes distinctes, le combo, les cibles devant/derrière, les obstacles, le bond, l’atterrissage unique, l’interruption du boss, les deux serments, la reprise, une victoire complète au corps à corps, le retour au Rempart et les gestes tactiles en portrait/paysage, y compris une perte de focus.

Les tests de la version précédente restent présents. `tests/publication.py` contrôle la construction et les deux modes de publication (racine avec redirection, ou directement /docs). Les tests se font dans Chromium avec WebGL logiciel et mobile simulé, pas sur Safari/iPhone physique.

## Publication et limites

Modifier les sources puis lancer `python scripts/build.py`. Le site actuel reste dans `docs/index.html`, avec le lien historique conservé. Voir [PUBLICATION.md](PUBLICATION.md).

Deux personnages, un niveau en trois salles. Les huit autres personnages ordinaires, le personnage secret complet, les deux grands niveaux suivants, les comptes, la coop, le battle et les modèles définitifs restent à développer. [Détails de la version 0.4](PROTOTYPE-0.4.md).
