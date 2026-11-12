# Les Marches de l’Éclipse — refonte 0.8

## Changement de structure

La première expédition est désormais un monde relié, sur environ 56 unités de largeur et 140 de longueur. Il se parcourt sans téléportation entre les anciennes salles. Le sol physique est composé de plateformes raccordées : le joueur ne peut ni marcher ni esquiver à travers le vide. Ce n’est pas encore le jeu final, ni les trois grands niveaux complets.

### Parcours

- **Atrium des serments** : zone d’arrivée calme, choix du héros puis du serment. Le choix ouvre les deux itinéraires.
- **Jardins suspendus** : terrasses, pont au-dessus du vide, cristaux, Sentinelle et tireur. Un détour mène à une relique qui soigne 20 PV et renforce la prochaine attaque, ainsi qu’au Reflet facultatif.
- **Cloître des cendres** : colonnade et couvertures, Oracle et Traqueur. Il offre une autre route vers la croisée.
- **Croisée des pèlerins** : jonction des itinéraires et premier refuge. Le chemin continue vers le nord.
- **Nef des marées** : passages de feu influencés par le serment, couvertures et rencontres mixtes. Il faut récupérer deux sceaux pour ouvrir le seuil.
- **Cour du Veilleur** : le combat s’active à l’entrée, la cour se ferme et la cloche reste disponible une fois. Après la victoire, le passage au nord termine l’expédition.

Les deux routes peuvent être explorées dans la même tentative. Aucune porte ne demande un nombre arbitraire d’ennemis vaincus. Les ennemis sont placés à des endroits définis ; ils ne réapparaissent pas continuellement.

## Rencontres

- **Traqueur** : avance et contourne localement les obstacles.
- **Tireur** : annonce sa direction, lance des projectiles et peut se replacer lorsqu’il est attaqué.
- **Sentinelle** : bouclier frontal, charge verrouillée et récupération vulnérable.
- **Oracle** : annonce des zones dangereuses avant de les déclencher ; ajoute une zone lorsqu’il est blessé.
- **Veilleur** : boss à deux phases. Il ne peut pas être éliminé depuis une autre zone avant le début de l’affrontement.

Les ennemis lointains attendent l’approche. Un ennemi touché est alerté. Le leurre d’Élan reste une cible possible. La navigation des ennemis utilise un contournement local, pas un planificateur de chemins général.

## Refuges et progression

Atteindre un nouveau refuge restaure les PV, recharge le pouvoir et enregistre un état de reprise pour cette tentative. Le premier se trouve à la croisée ; le second, devant le seuil, s’active après la collecte des deux sceaux.

La reprise restaure le héros et son serment, les sceaux acquis et les ennemis vaincus au moment du refuge. Les actions réalisées ensuite sont annulées. Sans refuge, la tentative reprend dans l’atrium. Recharger la page perd cette expédition : aucun compte ni synchronisation réseau n’est encore ajouté. La Marque du Reflet, distincte de l’expédition, reste sauvegardée localement si le navigateur le permet.

## Caméra, commandes et présentation

Caméra plus proche, centrée sur la position réelle dans le monde et légèrement anticipée par le mouvement. Réponse analogique progressive du joystick et freinage plus net. Les mouvements rapides sont découpés pour éviter de traverser les obstacles. Le sol et les portes utilisent la même logique physique pour les deux héros.

Le torse et les bras des héros sont moins cubiques, la démarche et l’esquive sont mieux animées. Les ennemis ont des robes et des bras plus lisibles, des réactions aux impacts et de petites barres de vie lorsqu’ils sont blessés. Les inscriptions éloignées ou déjà consommées sont masquées.

Le HUD est compact. **Carte** (ou M) ouvre un plan et suspend la simulation ; le fermer reprend l’exploration. Les refuges, objectifs et ennemis proches y apparaissent. Une mini-carte est disponible sur grand écran.

Un correctif empêche qu’un même geste tactile ouvre puis confirme automatiquement un serment : l’ouverture se fait au relâchement et la confirmation n’est activée qu’après un court délai.

## Sources et tests

- `src/world.js` : plateformes, architecture, collisions statiques et habillage.
- `src/campaign.js` : rencontres, objectifs, refuges, carte et Oracle.
- `src/game.js` : contrôles, héros, combat et interface.
- `src/template.html` : menus et disposition responsive.

`python scripts/build.py` produit la page autonome dans `docs`. Aucun téléchargement de modèle ou de moteur au lancement.

Tests actuels : `campaign.py` vérifie les routes, les portes, une traversée physique, les objectifs et les victoires des deux héros ; `systems.py` vérifie combats, reprise cohérente et secret sauvegardé ; `mobile_world.py` vérifie les gestes simultanés, la carte et les dialogues tactiles en portrait/paysage ; `publication.py` vérifie le paquet et les redirections. Les tests utilisent des états contrôlés pour certains combats et du mobile simulé ; ils ne garantissent pas la fluidité sur téléphone réel.

## Limites

Les modèles et textures restent procéduraux et stylisés ; le rendu final demandera une production d’assets et davantage d’animation. Deux héros sont présents, les autres restent à produire. Les deux autres grands niveaux, les comptes, la coopération et le battle ne sont pas encore implémentés. Les plateformes ne comportent pas encore de dénivelés parcourables ni de chute dans le vide.
