# Guide du contenu jouable — versions candidates 1.0 et 1.1

La passe visuelle 1.1 est décrite dans [Ambre et obsidienne](ESTHETIQUE-1.1.md). Le contenu et les règles ci-dessous sont conservés.

## Ce qui est livré

Le voyage relie trois chapitres avec introductions, objectifs, ancres, boss et conclusions. La galerie propose dix héros ordinaires immédiatement et un héros secret. La direction détaillée est conservée avec une variante Légère ; les nouveaux lieux possèdent leur propre géographie, ciel, décor, signalétique et habillage.

| Héros | Arme / pouvoir |
|---|---|
| Dernier Rempart | Fusil de cuivre ; Bastion bloque, interrompt et repousse |
| Voltigeur | Lame des vents ; bond et frappe au sol |
| Lame d’Éclipse | Long sabre ; protection brève et traversée offensive |
| Tisseuse de Failles | Bâton ; deux passages pour corps et projectiles, sans franchir un seuil de quête scellé |
| Porte-Cendres | Canon ; chauffe, surchauffe ralentissante et libération en zone persistante |
| Voleur d’Ombres | Dagues ; double qui répète une frappe et échange de position |
| Bergère des Astres | Sceptre ; astre mobile, attraction, soin et protection partagée à proximité |
| Colosse de Porcelaine | Marteau ; frappe puissante et abri matériel temporaire |
| Accordeur | Diapason ; pulsations qui interrompent, bonus de tir près de la pulsation |
| Enfant du Néant | Croissant ; ombre combattante et métamorphose temporaire |
| Éclipse incarnée | Fracture et Soleil noir ; Incarnation supplémentaire, suivie de fragilité |

Les effets sont mécaniques, pas seulement des changements de couleur. Les corps et projectiles suivent les collisions ; le tir ne remplace plus le cycle des jambes. Les transformations modifient aussi le rendu du personnage concerné, sans modifier les matériaux des compagnons.

## Déroulement et reprise

La Cathédrale conserve ses anciennes épreuves et refuges. Après sa conclusion, le bouton de chapitre poursuit vers la Chasse, puis le Convoi. Le menu permet aussi d’essayer directement un chapitre.

La Chasse alterne découverte des traces, interprétation de faiblesses, appels de l’observatoire, duel et Souverain à trois phases. Les piliers du terrain se lèvent pendant le boss. Le Convoi alterne réparation, traversée exposée aux rafales, choix d’horizon, escale, défense du cœur et affrontement final. La route change les adversaires de l’escale et la protection du cœur.

Une ancre restaure la santé et enregistre la progression. Après défaite, la reprise reconstruit les rencontres depuis l’ancre. Les parties locales partagent la progression ; en coopération, un compagnon relève un allié à terre en maintenant son interaction à proximité pendant 2,5 secondes. J1 mène les interactions de la Cathédrale. Les participants peuvent interagir dans les deux autres chapitres. Le groupe partage une caméra et reste proche du meneur.

## Secret

Les trois étapes prévues sont réalisées : reflet de la Cathédrale, réponse au geste du Souverain, escale invisible et combat contre l’ombre. Elles sont accessibles avec chacun des dix kits et conservées dans le profil local. Le héros secret apparaît ensuite dans les sélections. Incarnation utilise une jauge remplie au combat, dure huit secondes et laisse quatre secondes de fragilité. R pour J1, U pour J2 clavier ou RB à la manette ; bouton supplémentaire sur téléphone.

## Arènes locales

Le Duel d’Éclipse se conclut en trois manches gagnantes. La Couronne vivante demande 60 points de possession : attaquer est interdit au porteur, un coup reçu la fait tomber et l’interaction permet de la passer ou de la poser. Les bots utilisent les déplacements, armes et pouvoirs du roster. Les tirs des deux camps voyagent comme des projectiles, avec visée, couvert et esquive.

L’entrée dans l’arène conserve le point d’aventure, retire les bonus de serment et réinitialise les ressources de manche. Aucun classement en ligne ni avantage lié au profil n’est présent. Deux humains peuvent partager le clavier ; les équipes peuvent affronter deux IA ou J3/J4 avec les manettes nécessaires. Les manettes physiques restent à essayer ; la validation utilise des entrées simulées.

## Profil et confort

Le profil reste sur l’appareil : nom, statistiques, étapes du secret, chapitres et ancres. Export/import JSON inclut aussi un éventuel refuge de l’ancien format. Les données sont validées avant remplacement, et le nom est affiché comme texte. Sans serveur, aucune connexion e-mail/Google ou récupération distante n’est proposée.

Qualités Haute/Légère, musique procédurale originale, volume, réduction des effets, guide, carte et objectifs suivis sont intégrés. La touche Q reste disponible pour ZQSD ; Incarnation utilise R afin de ne pas entrer en conflit avec le déplacement.

## Validation et limites

Voir `tests/complete_campaign.py`, `tests/local_modes.py`, `tests/profiles.py`, `tests/render_complete.py`, puis les suites d’animation, de physique, de Cathédrale et de publication. Les parcours sont contrôlés ; les durées humaines, l’équilibrage et les performances matérielles ne sont pas déduits de ces tests.

Les scènes restent stylisées et procédurales, les appuis sont calculés sur un plan et une correction de portée peut produire du glissement lors des changements brusques de direction. Il reste du travail de production sur les costumes, les textures, les transitions, les réactions et la variété des rencontres pour pousser les références visuelles. Le jeu réseau et les comptes nécessiteront une autre livraison avec une infrastructure choisie explicitement.
