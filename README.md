# Les Royaumes de l’Éclipse

**Candidate 1.7-rc1 — Onze héros, combat et duels.** Jeu d’action fantastique 3D pour navigateur sur PC et téléphone. Trois chapitres d’aventure, dix héros disponibles dès le départ et un onzième personnage secret. [Contrôles et limites de cette livraison](design/VALIDATION-1.7.md) · [Publication vérifiée](design/PUBLICATION-1.7.json).

**[Jouer](https://mativ117.github.io/royaumes-eclipse/?v=1.7-rc1)** · [Projet courant éditable](https://github.com/mativ117/royaumes-eclipse/raw/refs/heads/main/historique/livraisons-zip/royaumes-eclipse-1.7-rc1-projet.zip) · [Toutes les sources et archives](https://github.com/mativ117/royaumes-eclipse/archive/refs/heads/main.zip) · [Suivi](design/SUIVI.md) · [Audit profond](design/AUDIT-PROFOND-1.5.md)

La cible confirmée est de rapprocher **le jeu entier de la qualité des meilleurs jeux AAA**, dans notre univers : héros, créatures, mouvements, combats, décors, récit, musiques, effets, interface et technique. Cette qualité reste un objectif de production. Les contrôles automatisés ne valident ni l’esthétique ni le plaisir. [Consigne durable](design/EXIGENCE-QUALITE.md) · [Instructions du dépôt](AGENTS.md).

## Correction 1.7 : silhouettes et coups

Trois silhouettes ennemies sont reprises : crânes moins allongés, mâchoires plus profondes, griffes courtes, masses de prédateur et matières moins brillantes. Le Veilleur porte un masque vertical fendu ; la Raie une tête spectrale avec mandibule. Les squelettes, appuis, gabarits et règles de combat sont conservés.

Les impacts suivent les PV réellement perdus et la direction du coup ; mêlée, projectile, pouvoir et garde emploient des signes distincts. Les anciennes sphères/cercles de contact et grands rubans sont remplacés par des fragments et traits courts à hauteur du corps. Les onze profils d’armes, les réglages Haute/Léger et les effets réduits sont couverts. [Comparer les captures du moteur](https://mativ117.github.io/royaumes-eclipse/docs/gestes-et-creatures.html?v=1.7-rc1) · [Technique et limites](design/COMBAT-VISUEL-1.7.md).

Les familles restantes et les boss gardent leur fabrication précédente. L’animation complète et la finition artistique restent à poursuivre ; aucun niveau AAA atteint n’est annoncé.

## Base conservée · passe 1.6

[Comparaison aux références AAA](design/COMPARAISON-AAA-1.6.md) · [Avant/après dans le moteur](https://mativ117.github.io/royaumes-eclipse/docs/gestes-et-creatures.html?v=1.7-rc1).

Deux familles deviennent des créatures originales animées : le **Veilleur des fils**, archer digitigrade à bras-arc, et la **Raie du reflet**, dont les ailes se replient près des obstacles. Préparation, tir ou charge, récupération, réaction et mort suivent leurs clips et leurs collisions. La caméra solo resserre progressivement un combat en conservant les deux corps dans le cadre ; un remplissage local aide à lire les personnages sombres.

Les trois chapitres reçoivent des matières à échelle mondiale, des soubassements et des éléments de composition propres à leurs lieux. Les routes sont conservées. Trois partitions synthétiques originales évoluent avec le combat, avec des avertissements propres aux nouvelles créatures et de courts éléments narratifs sans pause imposée. Les onze héros, sauvegardes et modes 1.5 restent conservés.

Cette passe applique des principes de fabrication des références ; elle ne constitue pas une équivalence AAA. Les autres créatures et boss, les animations directionnelles des héros, la géographie, la narration incarnée, le mix et les essais matériels restent à produire ou à éprouver.

## Base conservée · passe 1.5

[Voir deux personnages en mouvement](https://mativ117.github.io/royaumes-eclipse/docs/gestes-et-creatures.html?v=1.5-rc1) · Captures réelles à vitesse normale en qualité Légère ; comparaison historique 1.3/1.4 conservée séparément sur la même page.

Les dix autres héros reçoivent une fabrication détaillée pour rejoindre la méthode établie avec la Lame : proportions adultes, costume, armure et matières PBR, source Blender et animations Quaternius Standard CC0 adaptées à l’arme. Les profils distinguent fusil, gestes magiques, dagues, lame et arme lourde. La Lame approuvée est conservée. Les onze modèles, leurs appuis, leurs armes et leurs pouvoirs passent les contrôles du jeu et de l’atelier. Les pas orientés et esquives conservent des solutions analytiques ou alias hérités.

Le combat corrige la fuite au tactile, qui imposait auparavant de reculer lentement face à l’ennemi. La visée assistée suit l’intention de combat et stabilise sa cible. La préparation est réorientable dans une limite ; la frappe conserve ensuite sa direction. Les contacts de mêlée suivent les fenêtres calibrées et le trajet de l’arme. Les tirs contrôlent toute leur trajectoire contre les couverts minces.

Les grandes portes s’ouvrent par modules verticaux ; leur passage dépend du dégagement visible. Les sols superposés identifiés dans les chapitres II et III sont découpés sans changer les zones praticables. Les contacts d’ombre du réglage Léger sont étendus aux autres chapitres et aux duels. [Portes et matières](design/PORTES-MATIERES-1.5.md).

## Trois usages utiles, sans API de jeu

| Mode | Usage |
|---|---|
| Aventure solo | Trois chapitres, objectifs, boss, ancres, secret et sauvegardes |
| Duel tactique | Adversaire calculé localement, héros et difficulté choisis ; trois manches gagnantes |
| Duel en réseau local | Deux navigateurs du même réseau, invitation et réponse partagées manuellement ; un téléphone peut être hôte |

Le bot observe avec délai, recherche une portée favorable, utilise les couverts et ses pouvoirs, et peut punir une récupération. Il n’appelle aucun modèle distant et ne reçoit pas de bonus arbitraire de santé ou de dégâts. Difficulté et équilibrage demandent encore des parties humaines. [Duel et IA](design/DUELS-1.5.md).

Le LAN emploie WebRTC direct, sans serveur de rendez-vous, STUN ou TURN. Ouvrir le jeu sur les deux appareils, choisir le réseau local, échanger l’invitation puis la réponse et attendre l’état réellement connecté. L’hôte calcule la partie ; l’invité envoie ses commandes. Les profils d’aventure restent locaux.

**Le transfert natif entre appareils physiques reste à valider.** Le navigateur de développement bloque la collecte ICE directe. La synchronisation est testée séparément avec deux vrais contextes reliés par un transport en mémoire ; ce contrôle ne prouve pas une connexion Wi-Fi ou DTLS réelle. L’isolation d’un réseau invité ou une politique du navigateur peut empêcher la connexion. [Guide téléphone ↔ téléphone](design/LAN-TELEPHONES-1.5.md) · [Protocole et sécurité](design/LAN-SECURITE-1.5.md) · [Modes](design/MODES-1.5.md).

Les anciennes variantes clavier partagé, groupes et Couronne restent dans les sources et archives. Aucun compte e-mail/Google, synchronisation cloud ou classement compétitif n’est proposé.

## Le voyage et les héros

| Chapitre | Épreuves |
|---|---|
| La Cathédrale vivante | Serment, escorte d’une âme, carillon, Archives du Reflet, transport du noyau, Carillonneur, Veilleur et extraction |
| La Chasse aux Souverains | Traces, faiblesses à interpréter, appels du jardin, duel et terrain transformé par le Souverain |
| Le Convoi de l’Impossible | Liens à réparer, vent, choix de route, escale, défense du cœur, Mange-Aube et fin du voyage |

La cible de **10–15 minutes par chapitre** reste à mesurer en parties humaines. Les chapitres peuvent être choisis directement. Le secret des trois reflets ouvre l’Éclipse incarnée et son pouvoir supplémentaire Incarnation.

Voltigeur, Dernier Rempart, Lame d’Éclipse, Tisseuse de Failles, Porte-Cendres, Voleur d’Ombres, Bergère des Astres, Colosse de Porcelaine, Accordeur et Enfant du Néant disposent de kits distincts. Le bot utilise ces kits ; il ne remplace pas le chantier des créatures. Fauche-Cendre est la première famille entièrement produite en quadrupède ; le Veilleur et la Raie ajoutent deux anatomies propres en 1.6. Les familles restantes et les boss demandent encore cette production.

## Atelier, commandes et confort

L’atelier 3D intégré à la sélection permet de tourner le héros et d’examiner ses gestes. Le modèle choisi se charge à la demande ; le rendu de l’atelier se suspend hors vue et ses ressources se libèrent au lancement. [Atelier séparé](https://mativ117.github.io/royaumes-eclipse/docs/atelier-lame.html) · [Direction approuvée de la Lame](design/personnages/lame-eclipse/REVUE-01.md).

- **PC** : ZQSD/WASD ou flèches ; souris et clic pour attaquer ; Espace pour esquiver ; E pour le pouvoir ; F pour interagir ; G pour les repères ; M pour la carte ; Échap pour la pause ; R pour Incarnation.
- **Manette** : stick gauche pour marcher, droit pour viser ; X/gâchette pour attaquer ; A pour esquiver ; Y pour le pouvoir ; B pour interagir ; RB pour Incarnation.
- **Téléphone** : joystick, visée assistée et boutons tactiles. Paysage conseillé. Réglages Haute et Léger conservés.

Le bouton **Commandes**, au menu, en pause et en jeu, permet de remapper les touches ; les indications suivent le réglage dans les trois modes utiles. Guide, carte et chronique restent disponibles. Les musiques sont trois thèmes synthétiques originaux avec couches de combat ; pas de bande-son orchestrale enregistrée annoncée. Volume principal, silence à zéro, stéréo des effets et réduction des effets d’impact sont conservés.

Profil local nommé, statistiques, étapes du secret, chapitres et ancres restent sur cet appareil. L’export/import JSON permet de transférer le profil ; l’import remplace les données locales du jeu. Les refuges de l’ancienne Cathédrale restent compatibles. Aucun e-mail n’est collecté.

## Exécuter et modifier

Le site construit est dans `docs/`, avec les modèles dans `docs/assets/characters/`. Conserver les dossiers lors d’un transfert. GitHub Pages sert les fichiers ; il ne calcule pas les parties.

```sh
python scripts/build.py
python -m http.server 8000 --directory docs
```

Ouvrir `http://localhost:8000`. Le serveur local évite les restrictions de chargement des modèles d’un HTML ouvert directement. La construction ajoute une CSP à empreintes de scripts et une politique de référent ; elle n’autorise ni `eval` ni les gestionnaires de script dans les attributs HTML.

```text
src/        Niveaux, campagne, héros, animation, duels et interface
assets/     GLB, sources Blender, animations, matières et provenance
vendor/     Three.js et composants, sources et licence MIT
scripts/    Construction, fabrication et contrôles de publication
tests/      Parcours, classes, commandes, rendu, réseau et sécurité
design/     Conception, suivi, recherche et preuves
historique/ Anciens jeux, snapshots et ZIP conservés
```

Le ZIP des sources fourni en haut de page est généré par GitHub pour `main` et conserve les archives du dépôt. La [livraison 1.4-rc1](https://github.com/mativ117/royaumes-eclipse/raw/refs/heads/main/historique/livraisons-zip/royaumes-eclipse-1.4-rc1.zip) reste disponible séparément ; ses captures et rapports restent datés de cette version.

## Validation et limites

La [validation 1.5](design/VALIDATION-1.5.md), la [matrice](design/PRISE-EN-CHARGE-1.5.md), l’[audit](design/AUDIT-PROFOND-1.5.md) et la [couverture du jeu entier](design/COUVERTURE-QUALITE.md) distinguent correctifs, tests exécutés et travaux ouverts. Les relevés historiques, dont [la validation 1.4](design/VALIDATION-1.4.md), restent datés de leur livraison.

Les essais Chromium utilisent notamment tactile et manette simulés ; ils ne prouvent pas cadence, chauffe ou compatibilité d’un téléphone physique. Les parcours de campagne emploient des positions et dégâts contrôlés, sans mesurer une découverte humaine. La physique reste au sol : pas de pentes, escaliers ou corps rigides poussables. Raccords, pas latéraux, esquives, drapés, bestiaire, boss, composition des niveaux, histoire, mix et équilibrage restent à pousser vers la cible artistique.

## Sources et crédits

Textures Poly Haven CC0 : [pavement_01](https://polyhaven.com/a/pavement_01) et [castle_wall_slates](https://polyhaven.com/a/castle_wall_slates), Rob Tuytel. [Provenance](assets/materials/LICENSE.md).

Animations utilisées : [Universal Animation Library](https://quaternius.itch.io/universal-animation-library) et [Universal Animation Library 2](https://quaternius.itch.io/universal-animation-library-2), éditions Standard gratuites Quaternius, CC0. Pas de version payante ni de capture de mouvement annoncée. [Fichiers et licences](assets/animations/quaternius/README.md) · [Fabrication des dix autres héros](assets/characters/ROSTER-PRODUCTION.json). KayKit Free a été évalué ; sa présence dans les sources n’établit pas son utilisation dans les exports.

[Référentiel sourcé](design/REFERENTIEL-QUALITE.md) · [Workflow](design/WORKFLOW-QUALITE.md) · [Skill local](design/skills/quality-pass/SKILL.md). Ce dernier est une procédure lue dans le dépôt, pas un connecteur cloud ni une formation du modèle.
