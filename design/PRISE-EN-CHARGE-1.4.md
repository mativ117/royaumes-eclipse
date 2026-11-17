# Prise en charge de la qualité — candidate 1.4-rc1

Le but de cette passe est d’appliquer les recherches au jeu, sur une séquence et des ressources de référence. La version reste Web PC/téléphone et sans serveur, avec qualité légère. Les chapitres, profils et sauvegardes sont conservés. Les résultats d’intégration et de publication sont consignés dans [la validation](VALIDATION-1.4.md) et [le relevé distant](PUBLICATION-1.4.json) ; les tâches d’une ligne ne sont pas toutes terminées parce qu’une correction de module existe.

**RECHERCHÉ** signifie qu’une source primaire ou une recommandation spécialisée a été lue et reliée à un défaut du projet. **APPLIQUÉ** décrit les ressources et règles produites dans cette passe ou conservées d’une passe précédente. **À REVOIR** indique une limite réelle, une mesure encore manquante ou une décision ouverte. Ces états ne constituent pas une note artistique finale.

| Axe | RECHERCHÉ | APPLIQUÉ | À REVOIR |
|---|---|---|---|
| Silhouette et costume | Planche de la Lame approuvée ; Blender, matières et déformations | Proportions adultes et costume de 1.3 conservés ; retarget accompagné d’une reprise des poids et d’un socket de prise d’arme | Drapés, coiffure, mains, déformations et détails encore sous le niveau de la planche ; dix autres héros encore provisoires |
| Locomotion et appuis | AnimationTree/root motion, GDC animation-driven locomotion et contacts ; IK Blender | Marche/course/garde Quaternius Standard CC0 adaptées ; foulées et phases de contact mesurées, allures mélangées, corrections de pied bornées, départ/arrêt/pivot interruptibles | Raccords avec les anciens pas latéraux, demi-tours brusques et poids perçu à 1× ; essais physiques PC/téléphone |
| Attaques et esquive | Intention du mouvement source, synchronisation et lecture du contact | Trois attaques Lame retargetées avec corps complet ; balayage du sabre contre capsule pendant une fenêtre active ; esquive à distance/durée calibrées | Mise en scène, prise du sabre, contact visuel/sonore et équilibrage de chaque attaque ; gestes des autres héros |
| Physique et obstacles | Contrôleur Rapier JavaScript 0.21 et limites de sa translation ; volumes simples et contrôle du contact | Sous-pas au sol conservés ; gabarit du quadrupède, contact de lame en 3D et contrôle des murs renforcés | Rapier évalué seulement ; pentes, marches, plateformes et corps poussables demandent une passe dédiée |
| Créature et rencontre | Riot « Clarity in League », Guerrilla « The AI of Horizon Zero Dawn » | Fauche-Cendre, quadrupède original à 22 os ; approche, anticipation directionnelle, détente frontale, récupération et son localisé ; une rencontre de référence | Anatomie plus fine, déformations, effets et perception humaine de la menace ; autres familles ennemies et compositions de groupes |
| Level design et rythme | GDC Smith/Worch, narration par le décor ; parcours et décisions | Application du workflow à une séquence existante, objectifs et cheminements antérieurs conservés | Pas de réfection des trois niveaux dans cette passe ; durée 10–15 min à mesurer, alternance combat/exploration/lecture et orientation novice |
| Histoire et présentation | Environnement comme information à interpréter ; chronique progressive | Histoire et chronique existantes conservées ; rôle de chaque moment de la séquence pris en compte | Mise en scène narrative, personnages, réactions du monde et compréhension en partie novice ; pas de nouveau doublage |
| PBR, lumière et composition | Three r160 couleur/ombres, Blender Principled/baking | Matières Poly Haven CC0, sols/maçonnerie et composition de 1.3 conservés ; atlas des personnages préservés | Cohérence de toutes les zones, densité UV, ombres en déplacement, silhouette au soleil et dans les noirs ; pas de refonte visuelle globale annoncée |
| Musique et effets | Web Audio/W3C, contrôle utilisateur et spatialisation | Master commun, silence à zéro, arrêt des sons du monde à la pause, nettoyage, 16 voix d’effets avec priorités, atténuation et panoramique selon caméra ; pas liés aux appuis de la Lame calibrée | Mixage et timbres finaux, effets enregistrés/variantes, transitions musicales travaillées et écoute sur appareils ; les trois motifs restent synthétiques |
| Interface et accessibilité | WAI-ARIA Dialog, Game Accessibility Guidelines | Focus à l’entrée, Tab contenu, arrière-plan inerte et retour logique dans les écrans modaux ; remappage J1 et disposition de 1.3 conservés | Texte réglable, contrôle des menus à la manette, sensibilité, parcours tactile/lecteur d’écran et hiérarchie de toute l’interface |
| Performance et chargement | Three fusion/instancing, temps CPU/GPU et métriques de cadence | Chargements différés, suspension/libération de l’atelier et limites de voix conservés ou ajoutés | p50/p95/p99, mémoire et échauffement sur matériel identifié ; aucune cadence réelle sur iPhone annoncée |
| Modes et lancement | Choix utilisateur confirmé : aventure solo uniquement pour l’instant, autres modes conservés dans les archives | Lancement et bundle 1.4 solo ; menus groupes/arènes/bots retirés, module `local-party-solo.js`. Module complet et archives 1.3 conservés ; IA locale des créatures maintenue | Coop et battle hors de cette candidate ; les réintroduire uniquement avec une intention de jeu et une interface revues |
| Connaissances et procédure | Références primaires datées et limites de transposition | Référentiel, workflow et skill local de projet écrits ; provenance/licences des assets conservées | Mettre à jour à chaque mesure et nouvelle décision ; aucune formation permanente du modèle ni installation cloud de ce skill |

## Animations externes : ce qui est réellement utilisé

Les éditions **Standard gratuites** de [Universal Animation Library](https://quaternius.itch.io/universal-animation-library) et [Universal Animation Library 2](https://quaternius.itch.io/universal-animation-library-2) ont été obtenues depuis les pages officielles, avec leurs licences **CC0 1.0 Universal**. Les fichiers `_RM` conservent le déplacement racine utile à la calibration. Les variantes Pro et Source n’ont pas été téléchargées.

Une sélection de gestes est retargetée sur le squelette original de la Lame ; les poids du costume et la prise du sabre font partie de l’adaptation. Les bibliothèques ne sont pas annoncées comme des captures de mouvement. Leur disponibilité ne transforme pas automatiquement le retarget en animation finale. Fichiers d’origine, auteurs, clips et empreintes : [provenance Quaternius](../assets/animations/quaternius/PROVENANCE.json) et [note de retarget](RETARGET-1.4.md).

## Règles de la rencontre de référence

Fauche-Cendre prépare sa détente pendant **0,78 s**, avance frontalement de **2,4 unités sur 0,32 s**, puis récupère pendant **1,4 s**. Le déplacement est contrôlé par la physique du jeu et reste soumis aux obstacles ; le petit bond visuel du modèle ne le remplace pas. L’attaque ne peut infliger ses **22 dégâts de base** qu’une fois par séquence, lors d’un contact valide, avant application des protections du joueur. La queue n’est pas une hitbox.

Ces valeurs décrivent le comportement intégré, pas un équilibrage validé en parties humaines. Préparation, volume d’attaque, son et récupération doivent expliquer le danger ensemble. [Modèle et contrat d’intégration](CREATURE-1.4.md).

## Ce que la passe ne clôt pas

La recherche est appliquée à une référence jouable ; les trois niveaux n’ont pas été reconstruits, les dix autres héros n’ont pas reçu ces gestes, toutes les familles ennemies ne sont pas refaites et la musique n’est pas une bande-son orchestrale enregistrée. Le lancement 1.4 est épuré au solo conformément au choix confirmé par l’utilisateur. Le code des modes locaux et les archives 1.3 restent conservés hors du bundle courant. Le rendu final et le plaisir doivent être jugés sur le résultat à vitesse normale et lors d’essais humains.

Les contrôles CPU, les parcours d’intégration, le paquet et les vérifications publiques ont passé ; le [relevé de validation](VALIDATION-1.4.md) précise les scénarios et limites. Ils ne constituent ni une validation artistique AAA, ni un essai sur téléphone physique.

## Connaissances conservées

- [Référentiel qualité](REFERENTIEL-QUALITE.md) : défauts actuels, critères de revue, mesures et sources.
- [Workflow](WORKFLOW-QUALITE.md) : recherche → audit → asset → intégration → comparaison 1× → régression → livraison.
- [Skill local de projet](skills/quality-pass/SKILL.md) : procédure réutilisable lorsqu’un agent la lit dans ce dépôt ; ce fichier n’est pas un plugin cloud installable et ne forme pas le modèle.
- Notes spécialisées : [mouvement](MOUVEMENT-1.4.md), [retarget](RETARGET-1.4.md), [créature](CREATURE-1.4.md), [audio](AUDIO-1.4.md), [interface](INTERFACE-1.4.md).

## Périmètre de lancement épuré

`src/local-party-solo.js` fournit les raccords nécessaires à l’aventure sans inclure le code des arènes, bots et groupes du module complet. Le menu de cette candidate ne propose plus ces modes. Ce retrait de périmètre n’est pas une suppression de l’IA des ennemis : les créatures et boss continuent de fonctionner localement dans le navigateur, sans connexion à un service d’IA.

La démarche conserve le travail réversible dans `src/local-party.js` et dans les archives 1.3. L’utilisateur a confirmé l’aventure solo uniquement pour l’instant, avec conservation des autres modes dans les archives. Le module complet conservé permet de réexaminer ce périmètre plus tard sans perdre le travail antérieur.
