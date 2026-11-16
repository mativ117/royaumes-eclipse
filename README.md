# Les Royaumes de l’Éclipse

Jeu d’action fantastique en 3D pour navigateur, sur PC et téléphone. **Expédition 0.14 — Le Carillon des Âmes** : escorte, énigme musicale, Archives du Reflet, transport du noyau, Carillonneur, Veilleur à trois phases et extraction. Deux héros, attaques animées avec contact différé et reprise locale aux refuges. Carte nommée avec obstacles, objectifs à suivre et guidage stable à la demande. Deux héros à squelette et treize animations chacun ; cour à bassin, caméra rapprochée, reflets et ombres en qualité Haute. Première partie ciblée : **10–15 minutes**, à confirmer par les essais humains.

**[Jouer](https://mativ117.github.io/royaumes-eclipse/)** · [Conception](design/CONCEPTION.md) · [Détails de la version](design/PROTOTYPE.md) · [Recherche sur la lisibilité](design/LISIBILITE.md) · [Présence et rythme 0.10](design/FEEL-0.10.md) · [Direction artistique 0.11](design/ART-DIRECTION-0.11.md) · [Cour et héros 0.12](design/SANCTUAIRE-0.12.md) · [Mouvements et ombres 0.13](design/PHYSIQUE-0.13.md) · [Dynamique 0.14](design/DYNAMIQUE-0.14.md) · [Suivi complet](design/SUIVI.md)

## Jouer

- PC : ZQSD / WASD / flèches ; souris pour viser ; clic pour tirer ; Espace pour esquiver ; E pour le bouclier ; F pour examiner ou maintenir pour observer ; G pour les repères ; M pour la carte ; Échap pour la pause.
- Téléphone : joystick et boutons tactiles ; visée automatique. Un bouton contextuel apparaît près des objets. Paysage conseillé ; qualité légère disponible.

La reprise après défaite conserve le serment et restaure l’état du dernier refuge atteint. Les actions réalisées après ce refuge sont réinitialisées. La Marque du Reflet peut être conservée sur l’appareil ; le bouton Continuer restaure le dernier refuge après rechargement. Le bilan copiable mesure le temps actif et les défaites, sans envoi réseau.

## Organisation

```text
docs/       Site publié par GitHub Pages, généré automatiquement
src/        Monde, campagne, combat, contrôles et interface éditables
assets/     Modèles originaux GLB et provenance
vendor/     Moteur et composants Three.js, sources et licence MIT
scripts/    Construction du site
tests/      Vérifications dans Chromium
design/    Conception et documentation du projet
historique/    Anciens prototypes, hors du site publié
VERSION     Version du jeu
```

## Modifier et tester

Modifier `src/game.js` ou `src/template.html`, puis lancer :

```sh
python scripts/build.py
python -m http.server 8000 --directory docs
```

Ouvrir http://localhost:8000. Le moteur est intégré à la page générée : aucun CDN ni téléchargement de modèle n’est requis au lancement.

Les tests utilisent Python Playwright et Chromium à `/usr/bin/chromium` :

```sh
python -m pip install -r tests/requirements.txt
python tests/sanctuary.py
python tests/art_direction.py
python tests/feel.py
python tests/expedition.py
python tests/readability.py
python tests/mobile_world.py
python tests/publication.py
```

Pour régénérer les modèles : `blender --background --factory-startup --python scripts/author_characters.py`, puis reconstruire la page. Le bundle des composants est reproductible avec `python scripts/prepare_three_addons.py`. Le build ordinaire ne demande ni Blender ni réseau.

[Comparer les captures 0.11 / 0.12](https://mativ117.github.io/royaumes-eclipse/docs/avant-apres.html).

Les anciennes suites de tests sont conservées dans `historique/tests-v0.7` et `historique/tests-v0.8` avec les anciens prototypes.

## Publier

Le réglage souhaité est **`main` → `/docs`**. La connexion ne peut pas changer ce réglage d’administration ; tant que Pages utilise la racine, les redirections fournies ouvrent le jeu dans `docs`. Le propriétaire peut sélectionner `/docs` une seule fois dans Settings → Pages. Après une modification, régénérer le site et envoyer sources et `docs/` dans le même commit. GitHub publie alors les pages de ce dossier. [Procédure](design/PUBLICATION.md).

Le lien historique `cathedrale-v03.html` redirige vers le jeu actuel. Pour ajouter une autre page indépendante, la placer dans `docs/` avec un nom distinct.

## Suite du projet

Les huit autres personnages du casting initial, le personnage secret complet, les deux autres grands niveaux, les comptes, la coop et le battle restent à développer. Les graphismes actuels sont provisoires. Les tests de navigateur simulé ne remplacent pas les essais de fluidité sur téléphone réel.

Three.js est sous licence MIT, conservée dans `vendor/THREE-LICENSE.txt` et dans la page générée. Aucune licence n’a encore été choisie pour les créations du jeu.
