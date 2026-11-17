# Suivi du projet — version candidate 1.4-rc1

Les choix confirmés pour cette livraison sont : **sans serveur**, détails visuels avec réglage léger, aventure complète puis révision du résultat. La version candidate relie le contenu de jeu ; le rendu et l’équilibrage restent à éprouver en parties humaines.

| Engagement | État vérifiable |
|---|---|
| PC et téléphone, sans Unreal | Navigateur Three.js, clavier/souris, tactile ; rendu et commandes simulés dans Chromium |
| Trois chapitres | Cathédrale, Chasse aux Souverains et Convoi de l’Impossible, avec objectifs, rencontres, boss, conclusions et reprises |
| Dix héros disponibles dès le début | Dix kits, statistiques, armes et modèles distincts ; aucune progression obligatoire pour ces dix héros |
| Onzième personnage secret | Trois étapes réparties dans les niveaux ; Éclipse incarnée, Soleil noir et Incarnation supplémentaire |
| Animation et mouvement | Lame : mouvements Quaternius CC0 retargetés, foulées/cadence/appuis mesurés, esquive calibrée et attaques engageant le corps complet ; autres héros conservés. Raccords et qualité en mouvement encore à revoir |
| Physique | Contrôleur au sol et collisions antérieures conservés ; frappe Lame par balayage du sabre contre capsule durant sa fenêtre active. Pas de pentes ni de corps rigides ajoutés |
| Solo | Voyage complet et sélection directe des chapitres |
| Coopération | Retirée du bundle et du lancement 1.4 ; code complet et archives 1.3 conservés |
| Battle | Arènes, bots et Couronne retirés du bundle et du lancement 1.4 ; code complet et archives 1.3 conservés |
| Sauvegarde | Profil local nommé, ancres, statistiques, secret, export/import ; anciens refuges conservés |
| Audio et confort | Ambiance procédurale, master/silence zéro/pause, effets stéréo selon source/caméra, priorité et limite de voix ; focus des écrans modaux. Revue du mix et parcours intégré encore à confirmer |
| Direction artistique | Noir/ambre, soleil, dunes et silhouettes drapées ; matières PBR, contre-jour et composition HDR, avec mode léger. Références de mouvement Expédition 33 / Ghost of Tsushima |
| GitHub et historique | Sources, modèles, provenance, licences, tests et archives séparés ; site dans docs/ et modèles chargés à la sélection |

## Limites conservées, sans les annoncer comme terminées

- Coop et battle : hors de la candidate 1.4. Les modes locaux antérieurs restent dans les sources et archives ; aucun mode entre appareils n’est livré.
- Compte par e-mail/code ou Google, synchronisation et récupération distante : non livrés. Le profil proposé est explicitement local.
- Cible de 10–15 minutes par niveau : à confirmer en parties humaines ; aucune durée de test contrôlé n’est présentée comme une durée réelle.
- Téléphone et manettes physiques : encore à essayer. Les tests utilisent Chromium, ses entrées tactiles et des manettes simulées.
- Pentes, escaliers, corps rigides et relief parcourable : non implémentés ; le contrôleur reste au sol.
- Finition visuelle et rythme : costumes, textures, transitions, réactions et équilibrage doivent encore être revus à partir de parties. Cette livraison candidate ne clôt pas ces objectifs qualitatifs.

## Préservation du travail précédent

La Cathédrale, les serments, ses énigmes, son extraction, les archives HTML/ZIP, les modèles et les sauvegardes antérieures sont conservés. La comparaison 0.11/0.12 reste datée de ces versions, sans être présentée comme une capture de la version actuelle.

Les passes [0.13](PHYSIQUE-0.13.md), [0.14](DYNAMIQUE-0.14.md) et [0.15](ANIMATIONS-0.15.md) restent documentées. Le [guide de la livraison complète](VERSION-COMPLETE.md) décrit le résultat et ses règles. La [liste de contrôle](PRODUCTION-COMPLETE.md) suit la préparation de publication.

## Passe actuelle

La passe [Ambre et obsidienne](ESTHETIQUE-1.1.md) suit les dernières images. Les trois chapitres sont conservés. Les modes locaux de cette passe antérieure restent dans les sources et archives ; la candidate 1.4 se concentre sur le solo. Les captures de la nouvelle comparaison sont issues du moteur et restent distinctes de la comparaison historique 0.11/0.12.

La passe [Récit et son](RECIT-SON-1.1.md) ajoute le contexte dans le menu, une chronique qui suit l’avancement et trois thèmes originaux synthétiques avec couches de combat. Pas de doublage ni de bande-son orchestrale enregistrée annoncés. Les effets de pas, tirs, lames et impacts sont différenciés.

Les retours des captures ont conduit au [correctif rc3](CORRECTIFS-1.1-rc3.md). La [séquence de référence](SEQUENCE-REFERENCE.md) définit désormais les critères qualitatifs à atteindre avant d’étendre la finition. La fluidité réelle du téléphone et les clips de locomotion restent à valider.

## Revue du premier personnage

La [direction de la Lame](personnages/lame-eclipse/REVUE-01.md) est validée et sa première production 3D est intégrée avec un atelier de revue. Le niveau artistique de la planche n’est pas atteint. Les autres héros et les familles ennemies restantes sont à traiter après cette revue. Fauche-Cendre devient la première créature originale de référence dans la passe 1.4. Le navigateur est conservé pour cette étape. Les commandes solo sont configurables. Les anciennes dispositions de groupe restent dans le module conservé hors du bundle 1.4.

## Atelier et matières — 1.3-rc1

L’atelier est maintenant intégré au choix du personnage au début. Il utilise les modèles réels et conserve l’atelier séparé pour la revue. Son rendu se suspend hors vue et sa scène se libère au lancement du jeu. Les dix héros ordinaires restent disponibles ; l’aperçu ne contourne pas le secret du onzième.

La seconde production de la Lame vise une silhouette adulte : environ 7,34 longueurs de tête, épaules et extrémités affinées, masque et costume moins réguliers. Squelette et 23 clips sont conservés. Les trois attaques suivent leurs durées de clip plutôt qu’une lecture accélérée. Cela corrige le rythme de lecture, sans valider la qualité finale des gestes ou leur équilibrage.

Les matières PBR du modèle ne sont plus écrasées par le tissu générique. La [passe de finition](FINITION-1.3.md) ajoute aussi des cartes photographiques CC0 aux sols et à la maçonnerie du niveau et de l’atelier, ainsi que des bordures, supports, niches d’Archives et cheminées de forge. Les chemins et collisions ne sont pas refaits dans cette passe. Le modelage des dix autres personnages, l’anatomie des ennemis, la composition de chaque zone, le rythme et les essais sur appareil restent à poursuivre.

## Séquence, combat et créature — 1.4-rc1

La passe applique les recherches à une séquence existante : mouvements Quaternius Standard gratuits adaptés à la Lame, métadonnées de foulée/contact, IK bornée, cadence et esquive calibrées, contact du sabre pendant la fenêtre active. La géométrie du costume, ses poids et un socket de prise d’arme sont repris pour accompagner ce retarget. Il ne s’agit pas de capture de mouvement.

Fauche-Cendre remplace la famille `warden` par un quadrupède original à 22 os, avec approche, préparation directionnelle de 0,78 s, détente de 2,4 unités sur 0,32 s et récupération de 1,4 s. Le contact inflige une seule fois 22 dégâts, selon les protections/règles du jeu. Son son d’avertissement est localisé. Les autres familles ne sont pas annoncées comme refaites.

Le son utilise un master commun, le vrai silence à zéro, une pause qui nettoie les sources, un plafond de 16 voix d’effets et un panoramique relatif à la caméra. La carte, les pactes et les choix de voyage disposent d’une gestion commune du focus et d’un arrière-plan inerte. Les contrôles CPU de ces modules ont été exécutés par leurs responsables ; les essais du jeu intégré et la publication sont consignés séparément après leur exécution.

La [matrice 1.4](PRISE-EN-CHARGE-1.4.md) montre ce qui est recherché, appliqué et encore à revoir. Le [référentiel qualité](REFERENTIEL-QUALITE.md), le [workflow](WORKFLOW-QUALITE.md) et le [skill local](skills/quality-pass/SKILL.md) conservent les connaissances dans le dépôt. Ce skill n’est ni un connecteur cloud installable ni une formation permanente du modèle.

L’utilisateur a confirmé : « Aventure solo uniquement pour l’instant ; conserver les autres dans les archives ». La candidate 1.4 se concentre donc sur le solo. Les choix d’arènes, bots et groupes sont retirés du menu et leur code est exclu du bundle via `src/local-party-solo.js`. Le module complet `src/local-party.js` et les archives 1.3 conservent le travail antérieur. Les ennemis et boss gardent leur IA locale sans service connecté. Les profils, les chapitres, les matières et la composition précédents sont conservés. La réfection complète des trois niveaux, les autres héros et créatures, le mixage final, l’équilibrage et les essais physiques restent ouverts.
