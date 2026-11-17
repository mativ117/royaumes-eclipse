# Suivi du projet — version candidate 1.2-rc1

Les choix confirmés pour cette livraison sont : **sans serveur**, détails visuels avec réglage léger, aventure complète puis révision du résultat. La version livrée relie le contenu de jeu ; le rendu et l’équilibrage restent à éprouver en parties humaines.

| Engagement | État vérifiable |
|---|---|
| PC et téléphone, sans Unreal | Navigateur Three.js, clavier/souris, tactile ; rendu et commandes simulés dans Chromium |
| Trois chapitres | Cathédrale, Chasse aux Souverains et Convoi de l’Impossible, avec objectifs, rencontres, boss, conclusions et reprises |
| Dix héros disponibles dès le début | Dix kits, statistiques, armes et modèles distincts ; aucune progression obligatoire pour ces dix héros |
| Onzième personnage secret | Trois étapes réparties dans les niveaux ; Éclipse incarnée, Soleil noir et Incarnation supplémentaire |
| Animation et mouvement | Treize clips par héros, corps séparé en couches, appuis, prise à deux mains, recul/culasse, gestes de lame ; ennemis marcheurs articulés |
| Physique | Contrôleur au sol, contacts/glissement, socles et décors solides, couvert temporaire et garde-fous des capacités aux seuils de quête |
| Solo | Voyage complet et sélection directe des chapitres |
| Coopération | Locale 2–4, même écran/appareil, clavier et manettes, relevage et reprise du groupe |
| Battle | Duel local ou contre IA, équipes contre deux IA ou J3/J4 et Couronne vivante ; manches/score et conclusion |
| Sauvegarde | Profil local nommé, ancres, statistiques, secret, export/import ; anciens refuges conservés |
| Audio et confort | Ambiance procédurale, volume, réduction des effets, guide, carte, repères et deux qualités graphiques |
| Direction artistique | Noir/ambre, soleil, dunes et silhouettes drapées ; matières PBR, contre-jour et composition HDR, avec mode léger. Références de mouvement Expédition 33 / Ghost of Tsushima |
| GitHub et historique | Sources, modèles, provenance, licences, tests et archives séparés ; site dans docs/ et modèles chargés à la sélection |

## Limites conservées, sans les annoncer comme terminées

- Coop et battle **entre appareils** : non livrés. Le choix de rester sans serveur conduit ici à des modes locaux.
- Compte par e-mail/code ou Google, synchronisation et récupération distante : non livrés. Le profil proposé est explicitement local.
- Cible de 10–15 minutes par niveau : à confirmer en parties humaines ; aucune durée de test contrôlé n’est présentée comme une durée réelle.
- Téléphone et manettes physiques : encore à essayer. Les tests utilisent Chromium, ses entrées tactiles et des manettes simulées.
- Pentes, escaliers, corps rigides et relief parcourable : non implémentés ; le contrôleur reste au sol.
- Finition visuelle et rythme : costumes, textures, transitions, réactions et équilibrage doivent encore être revus à partir de parties. Cette livraison candidate ne clôt pas ces objectifs qualitatifs.

## Préservation du travail précédent

La Cathédrale, les serments, ses énigmes, son extraction, les archives HTML/ZIP, les modèles et les sauvegardes antérieures sont conservés. La comparaison 0.11/0.12 reste datée de ces versions, sans être présentée comme une capture de la version actuelle.

Les passes [0.13](PHYSIQUE-0.13.md), [0.14](DYNAMIQUE-0.14.md) et [0.15](ANIMATIONS-0.15.md) restent documentées. Le [guide de la livraison complète](VERSION-COMPLETE.md) décrit le résultat et ses règles. La [liste de contrôle](PRODUCTION-COMPLETE.md) suit la préparation de publication.

## Passe actuelle

La passe [Ambre et obsidienne](ESTHETIQUE-1.1.md) suit les dernières images. Les trois chapitres et les modes sont conservés. Les captures de la nouvelle comparaison sont issues du moteur et restent distinctes de la comparaison historique 0.11/0.12.

La passe [Récit et son](RECIT-SON-1.1.md) ajoute le contexte dans le menu, une chronique qui suit l’avancement et trois thèmes originaux synthétiques avec couches de combat. Pas de doublage ni de bande-son orchestrale enregistrée annoncés. Les effets de pas, tirs, lames et impacts sont différenciés.

Les retours des captures ont conduit au [correctif rc3](CORRECTIFS-1.1-rc3.md). La [séquence de référence](SEQUENCE-REFERENCE.md) définit désormais les critères qualitatifs à atteindre avant d’étendre la finition. La fluidité réelle du téléphone et les clips de locomotion restent à valider.

## Revue du premier personnage

La [direction de la Lame](personnages/lame-eclipse/REVUE-01.md) est validée et sa première production 3D est intégrée avec un atelier de revue. Le niveau artistique de la planche n’est pas atteint. Les autres héros et la refonte anatomique des créatures restent à traiter après cette revue. Le navigateur est conservé pour cette étape. Les commandes J1 solo sont configurables ; les dispositions fixes coop/manettes restent inchangées.
