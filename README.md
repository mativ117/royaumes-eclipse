# Les Royaumes de l’Éclipse

**Version candidate 1.1-rc3 — Ambre et obsidienne.** Jeu d’action fantastique 3D pour navigateur, PC et téléphone, sans Unreal. Trois chapitres jouables jusqu’à leur conclusion, dix héros disponibles dès le départ et un onzième personnage secret.

**[Jouer](https://mativ117.github.io/royaumes-eclipse/?v=1.1-rc3)** · [Télécharger le projet complet](https://github.com/mativ117/royaumes-eclipse/raw/refs/heads/main/historique/livraisons-zip/royaumes-eclipse-1.1-rc3.zip) · [Guide de cette livraison](design/VERSION-COMPLETE.md) · [État et limites](design/SUIVI.md) · [Conception](design/CONCEPTION.md)

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

Onze modèles GLB originaux, treize clips par modèle, haut et bas du corps indépendants, appuis au sol, prise du fusil à deux mains, recul/culasse et gestes de lame. Les ennemis marcheurs disposent aussi de jambes articulées. Les modèles supplémentaires sont chargés à la sélection ; les deux premiers sont intégrés au jeu pour réduire les dépendances au démarrage.

## Modes sans serveur

- **Solo** : les trois chapitres sur PC et téléphone.
- **Coopération locale, 2–4 joueurs** : même écran et même appareil. J1/J2 peuvent partager le clavier ; J3/J4 nécessitent des manettes. Relevage des compagnons et reprise du groupe.
- **Duel d’Éclipse** : entraînement contre une IA, duel entre deux joueurs ou équipes J1/J2 contre deux IA ou J3/J4 ; trois manches gagnantes.
- **Couronne vivante** : J1/J2 contre deux IA ou J3/J4. Porter marque des points et empêche d’attaquer ; la couronne peut être passée et tombe lors d’un coup reçu. Objectif : 60 points.

Les arènes utilisent les statistiques de base, sans bonus de serment, et préservent la sauvegarde d’aventure. Coop et battle sont recommandés sur PC ou tablette avec manettes. **Il n’y a ni jeu entre appareils, ni compte e-mail/Google, ni synchronisation en ligne** dans cette livraison, conformément au choix de rester sans serveur.

## Commandes

- J1 : ZQSD/WASD ou flèches en solo ; souris ; clic pour attaquer ; Espace pour esquiver ; E pour le pouvoir ; F pour interagir ; G pour les repères ; M pour la carte ; Échap pour la pause. Incarnation : **R**.
- J2 clavier : flèches ; **J** pour attaquer ; Maj droite pour esquiver ; Ctrl droite pour le pouvoir ; Entrée pour interagir ou maintenir pour relever. Incarnation : **U**.
- Manette : stick gauche pour marcher, droit pour viser, X/gâchette pour attaquer, A pour esquiver, Y pour le pouvoir, B pour interagir, RB pour Incarnation. En solo, la première manette contrôle J1 ; en groupe, les manettes sont affectées selon le choix de commandes de J2.
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
assets/     Modèles originaux GLB et provenance
vendor/     Three.js et composants, sources et licence MIT
scripts/    Construction du site et génération Blender des personnages
tests/      Tests de parcours, classes, contrôles, rendu et publication
design/     Conception, suivi, guide et notes techniques
historique/ Anciens jeux, snapshots et ZIP de livraison
```

## Validation

Les tests couvrent les chapitres jusqu’à leur fin, tous les modèles et pouvoirs, le secret, les sauvegardes, les commandes locales, deux manettes simulées, les règles d’arène, l’animation, les collisions, les cartes et le rendu Haute/Légère en desktop/portrait/paysage. Les vérifications de mission utilisent notamment des positions et dégâts contrôlés ; elles ne constituent pas une partie humaine de 30–45 minutes. Les tests tactiles et manettes sont simulés dans Chromium, pas sur un téléphone ou une manette physiques.

Le rendu stylisé, les transitions, l’équilibrage des onze kits et le rythme des rencontres restent à réviser en parties. La physique reste au sol : pas de pentes, d’escaliers ou de corps rigides poussables. Voir [le suivi](design/SUIVI.md) pour les limites conservées et les fonctions en ligne reportées.
