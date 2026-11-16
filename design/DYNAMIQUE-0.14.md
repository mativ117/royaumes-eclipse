# Dynamique des affrontements — 0.14

## Changements jouables

- **Esquive** : 4,2 m sur 0,28 s avec départ vif et décélération, intégrée dans le temps pour conserver la distance à différentes fréquences. Les collisions restent actives. Une pression clavier ou tactile jusqu’à 0,16 s avant la disponibilité est retenue ; au-delà elle expire. Invulnérabilité de 0,28 s conservée.
- **Mêlée** : les deux premières frappes avancent de 0,6 m, la troisième de 0,95 m, pendant la préparation. L’avancée reste dans la direction engagée ; elle s’arrête avant le corps d’une cible ou un obstacle. Portée, préparation, fenêtre de contact et dommages existants sont conservés.
- **Espacement** : séparation progressive des adversaires proches et du joueur. Les masses du Veilleur et du porteur sont plus importantes. Les ennemis engagés dans une préparation ou une charge ne sont pas déplacés par la séparation entre ennemis ; le joueur peut traverser leur enveloppe pendant une esquive ou un bond. Ombres et ancrages magiques restent intangibles.
- **Approches** : les gardiens de mêlée utilisent des approches latérales alternées. Deux gardiens au maximum peuvent préparer simultanément une attaque à proximité du joueur ; les autres se replacent autour. Cette règle ne limite pas les archers, les oracles ou les attaques des boss.
- **Ombres** : suppression des projections des arcs, nervures, rayons et du monolithe suspendus du parvis. Les éléments restent visibles, et les ombres des acteurs, socles et piliers sont conservées. La stabilisation de la 0.13 reste active.

## Vérifications

`tests/dynamics.py` compare la distance d’esquive à 30 et 120 pas/s, vérifie la décélération, la mémoire de commande et son expiration, l’avancée de mêlée, la séparation et les places d’attaque, ainsi que l’exclusion des ornements suspendus des ombres. Les autres suites couvrent les collisions, la mission complète, les sauvegardes, l’animation, le guidage, l’affichage et les commandes tactiles.

## Limites conservées

Cette passe modifie la sensation et le placement du combat, sans ajouter une nouvelle zone. L’équilibrage doit encore être éprouvé en parties humaines sur PC et téléphone. Les ombres en qualité Légère restent des contacts simplifiés. La physique reste au sol et la navigation ennemie locale : pas encore de navigation volumique, de pentes, d’escaliers ni de corps rigides poussables. Les transitions et variantes d’animation, les réactions directionnelles et la profondeur des rencontres restent à développer ; le rendu et la dynamique finaux visés ne sont pas atteints.
