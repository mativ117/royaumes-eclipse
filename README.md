# Les Royaumes de l’Éclipse

**Version candidate 1.4-rc1 — Mouvement, combat et créature de référence.** Jeu d’action fantastique 3D pour navigateur, PC et téléphone. Trois chapitres jouables jusqu’à leur conclusion, dix héros disponibles dès le départ et un onzième personnage secret.

**[Jouer](https://mativ117.github.io/royaumes-eclipse/?v=1.4-rc1)** · [Télécharger le projet complet](https://github.com/mativ117/royaumes-eclipse/raw/refs/heads/main/historique/livraisons-zip/royaumes-eclipse-1.4-rc1.zip) · [Guide de cette livraison](design/VERSION-COMPLETE.md) · [État et limites](design/SUIVI.md) · [Conception](design/CONCEPTION.md)

## Passe de référence 1.4

**[Comparer les mouvements avant/après](https://mativ117.github.io/royaumes-eclipse/docs/gestes-et-creatures.html)** · Captures du jeu à vitesse normale.

La Lame reçoit des mouvements adaptés des bibliothèques gratuites **Quaternius Universal Animation Library 1 et 2 Standard**, sous CC0 : marche, course, garde et trois attaques. Ce sont des animations réalisées par des animateurs, retargetées sur notre personnage ; aucune capture de mouvement n’est annoncée. Foulées, cadence, appuis et distance d’esquive sont calibrés à partir des clips. Le contact du sabre suit sa trajectoire pendant une fenêtre active, au lieu d’une zone large déclenchée indépendamment du geste.

Une première famille ennemie devient une créature complète : **Fauche-Cendre**, prédateur quadrupède original. Sa préparation, sa détente frontale et sa récupération sont distinctes, avec un avertissement visible et un son localisé. Les autres familles gardent leur production précédente.

Le son passe par un volume principal commun, avec vrai silence à zéro, nettoyage à la pause, priorités et spatialisation stéréo des effets du monde. Les écrans modaux gèrent le focus pour que Tab reste dans le panneau et que la fermeture rende une cible logique aux commandes.

Cette candidate travaille une séquence existante ; elle ne refait pas les trois niveaux ni tous les personnages. Les matières et la composition de la passe précédente sont conservées. [Prise en charge de chaque axe et limites](design/PRISE-EN-CHARGE-1.4.md) · [Référentiel sourcé](design/REFERENTIEL-QUALITE.md) · [Workflow et connaissances du projet](design/WORKFLOW-QUALITE.md).

## Atelier au choix du personnage

L’atelier 3D est intégré à la sélection de départ : le modèle du personnage choisi peut être tourné et ses gestes examinés avant de jouer. Il se charge à l’approche de la zone, suspend son rendu hors vue et se libère au lancement de la partie. La refonte détaillée concerne la Lame ; les dix autres modèles restent provisoires.

La passe 1.3 a donné à la Lame des proportions adultes plus élancées, des épaules et des extrémités affinées, un masque céramique retravaillé et un costume moins régulier. Son squelette et les actions compatibles sont conservés. Départ, arrêt et pivots peuvent être interrompus ; marche et course conservent leur phase. La passe 1.4 reprend les clips et leurs métadonnées de déplacement/contact, ce qui demande encore une revue des raccords et de l’équilibrage.

Les textures de cuir intégrées au modèle sont conservées au lieu d’être remplacées par une matière de tissu. Sols et maçonnerie du jeu et de l’atelier utilisent six cartes PBR photographiques Poly Haven. Des bordures et supports encadrent les plates-formes de la Cathédrale ; les Archives et la forge gagnent du contexte. [Détail de la passe et limites](design/FINITION-1.3.md).

**[Essayer la Lame](https://mativ117.github.io/royaumes-eclipse/?hero=lame&v=1.4-rc1)** · [Ouvrir l’atelier séparément](https://mativ117.github.io/royaumes-eclipse/docs/atelier-lame.html?v=1.4-rc1) · [Fiche et planche validées](design/personnages/lame-eclipse/REVUE-01.md) · [Outils gratuits et plateforme](design/OUTILS-PRODUCTION-3D.md)

La mini-carte suit la barre de menu sur PC. Le bouton **Commandes**, accessible au menu, en pause et en jeu, permet de modifier les touches du héros. Elles restent sur cet appareil ; les indications du guide et des boutons suivent les réglages.

## Dernier correctif et méthode de finition

La version rc3 corrige le message masqué pendant une interaction, la sélection d’objets proches, la visibilité autour des stèles/colonnes et une partie du glissement des pieds. [Détail du correctif](design/CORRECTIFS-1.1-rc3.md). Ce correctif ne constitue pas une transformation graphique.

Pour obtenir un vrai saut de qualité, le travail doit se concentrer sur une [séquence de référence](design/SEQUENCE-REFERENCE.md) de deux à trois minutes : personnage, animations, scène composée et validation sur appareil physique.

## La nouvelle direction visuelle

Noir profond, soleil ambré, dunes lointaines et silhouettes drapées : cette passe reprend les nouvelles références transmises. Matières avec relief et rugosité, lumière en contre-jour, composition HDR, capes retravaillées et réactions de mouvement. Une chronique présente les enjeux et suit la progression ; trois thèmes musicaux originaux évoluent en combat, avec des effets de pas et d’armes distincts. [Récit et son](design/RECIT-SON-1.1.md). Le réglage Léger est conservé. Le rendu reste stylisé et ne constitue pas encore une finition AAA.

[Captures comparatives du jeu](https://mativ117.github.io/royaumes-eclipse/docs/ambre-obsidienne.html) · [Détails et limites de la passe](design/ESTHETIQUE-1.1.md)

## Le voyage

| Chapitre | Défis |
|---|---|
| La Cathédrale vivante | Serment, escorte d’une âme, carillon, Archives du Reflet, noyau à transporter, Carillonneur, Veilleur et extraction |
| La Chasse aux Souverains | Deux traces à retrouver, faiblesses à interpréter, appels du jardin, duel, terrain qui change avec les phases du Souverain |
| Le Convoi de l’Impossible | Liens du colosse à réparer, rafales, route du couchant ou de l’orage, don d’escale, cœur à défendre, Mange-Aube et fin du voyage |

Les serments accompagnent l’aventure. Chaque niveau dispose d’ancres de reprise, d’une carte et d’objectifs suivis. La cible de conception reste **10–15 minutes par chapitre** ; elle n’est pas une durée mesurée en parties humaines. Les chapitres peuvent aussi être choisis directement pour les essayer.

## Héros et animation

Voltigeur, Dernier Rempart, Lame d’Éclipse, Tisseuse de Failles, Porte-Cendres, Voleur d’Ombres, Bergère des Astres, Colosse de Porcelaine, Accordeur et Enfant du Néant : armes, silhouettes, statistiques et pouvoirs distincts. Le secret des trois reflets ouvre l’Éclipse incarnée et son pouvoir supplémentaire Incarnation.

Onze modèles de personnages GLB originaux, treize clips de base et les actions compatibles de la Lame, dont une sélection de mouvements Quaternius CC0 adaptés. Haut et bas du corps indépendants pour la locomotion ; les attaques retargetées de la Lame engagent le corps complet. Appuis, prise du fusil à deux mains et recul/culasse restent présents. La famille Fauche-Cendre dispose d’un modèle original à 22 os ; les autres ennemis marcheurs gardent leurs jambes articulées. Les modèles supplémentaires sont chargés à la sélection ; les deux premiers sont intégrés au jeu pour réduire les dépendances au démarrage.

## Aventure solo sans serveur

Le choix confirmé est l’aventure solo uniquement pour l’instant, avec les autres modes conservés dans les archives. La version 1.4 présente donc uniquement l’aventure solo sur PC et téléphone. Les choix d’arène, d’adversaires bots et de groupes sont retirés du lancement ; leur code n’est pas inclus dans le bundle de cette candidate. Le jeu conserve ses créatures, leurs comportements locaux et les boss : cette IA ne demande aucune connexion à un service.

Les modes coopératifs et compétitifs locaux précédents restent dans `src/local-party.js` et les [archives de la version 1.3](https://github.com/mativ117/royaumes-eclipse/raw/refs/heads/main/historique/livraisons-zip/royaumes-eclipse-1.3-rc1.zip). Ils ne sont pas proposés dans cette candidate. Les profils et sauvegardes d’aventure restent conservés. **Il n’y a ni jeu entre appareils, ni compte e-mail/Google, ni synchronisation en ligne**, conformément au choix sans serveur.

## Commandes

- Clavier et souris : ZQSD/WASD ou flèches ; souris ; clic pour attaquer ; Espace pour esquiver ; E pour le pouvoir ; F pour interagir ; G pour les repères ; M pour la carte ; Échap pour la pause. Incarnation : **R**.
- Manette : stick gauche pour marcher, droit pour viser, X/gâchette pour attaquer, A pour esquiver, Y pour le pouvoir, B pour interagir, RB pour Incarnation. La première manette contrôle le héros.
- Téléphone : joystick, visée automatique et boutons tactiles. Paysage conseillé. Qualité Haute ou variante Légère.

## Sauvegarde et réglages

Profil local nommé, statistiques, chapitres terminés, étapes du secret et ancres de reprise sont conservés sur cet appareil. Les refuges de l’ancienne Cathédrale restent compatibles. Export/import JSON permet de conserver ou transférer le profil ; l’import remplace les données du jeu sur cet appareil. Aucun e-mail n’est collecté.

Guide intégré, carte, chronique avec le bouton Récit, choix de présentation, trois thèmes musicaux synthétiques, volumes et réduction des effets d’impact. Le son démarre après une action volontaire.

## Exécuter et modifier

Le site généré est dans `docs/`, avec ses modèles dans `docs/assets/characters/`. **Conserver les dossiers** lors d’un transfert.

```sh
python scripts/build.py
python -m http.server 8000 --directory docs
```

Ouvrir `http://localhost:8000`. Le serveur local évite les restrictions des navigateurs sur le chargement de modèles depuis un fichier HTML ouvert directement. GitHub Pages sert les mêmes fichiers sans serveur applicatif.

```text
src/        Niveaux, campagne, héros, animation, modes locaux et interface
assets/     Modèles GLB, source Blender, matières et provenance
vendor/     Three.js et composants, sources et licence MIT
scripts/    Construction du site et génération Blender des personnages
tests/      Tests de parcours, classes, contrôles, rendu et publication
design/     Conception, suivi, guide et notes techniques
historique/ Anciens jeux, snapshots et ZIP de livraison
```

## Validation

[Relevé détaillé de la livraison 1.4](design/VALIDATION-1.4.md) · mesures, parcours exécutés et limites.

La base de tests couvre les chapitres jusqu’à leur fin, modèles et pouvoirs, secret, sauvegardes, animation, collisions, cartes et rendu Haute/Légère en desktop/portrait/paysage. Les contrôles de modes locaux des versions antérieures restent dans les sources ; ils ne prouvent pas leur présence dans le bundle solo 1.4. Les vérifications de mission utilisent notamment des positions et dégâts contrôlés ; elles ne constituent pas une partie humaine de 30–45 minutes. Les tests tactiles et manettes sont simulés dans Chromium, pas sur un téléphone ou une manette physiques.

Le rendu stylisé, les transitions, l’équilibrage des onze kits et le rythme des rencontres restent à réviser en parties. La physique reste au sol : pas de pentes, d’escaliers ou de corps rigides poussables. Voir [le suivi](design/SUIVI.md) pour les limites conservées et les fonctions en ligne reportées.

## Crédits des nouvelles matières

Textures [pavement_01](https://polyhaven.com/a/pavement_01), Rob Tuytel, et [castle_wall_slates](https://polyhaven.com/a/castle_wall_slates), Rob Tuytel, distribuées par Poly Haven sous CC0. Les cartes de couleur, normale et rugosité sont adaptées en 512 × 512 et intégrées au site. [Licence et provenance](assets/materials/LICENSE.md).

Animations source : [Universal Animation Library](https://quaternius.itch.io/universal-animation-library) et [Universal Animation Library 2](https://quaternius.itch.io/universal-animation-library-2), éditions Standard gratuites, Quaternius, CC0. [Licences, fichiers d’origine et provenance](assets/animations/quaternius/README.md). Les éditions Pro/Source n’ont pas été utilisées.
