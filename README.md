# Les Royaumes de l’Éclipse

Jeu d’action fantastique en 3D pour navigateur, sur PC et téléphone. **Prototype solo 0.7** : le Dernier Rempart et le Voltigeur, trois salles de la Cathédrale, deux serments avec contreparties, des Sentinelles à contourner, une cloche tactique, un secret facultatif et un boss à deux phases. Architecture gothique, fenêtres orangées, pierre texturée et brume légère.

**[Jouer](https://mativ117.github.io/royaumes-eclipse/)** · [Conception](design/CONCEPTION.md) · [Détails de la version](design/PROTOTYPE.md)

## Jouer

- PC : ZQSD / WASD / flèches ; souris pour viser ; clic pour tirer ; Espace pour esquiver ; E pour le bouclier ; F pour examiner ou maintenir pour observer ; Échap pour la pause.
- Téléphone : joystick et boutons tactiles ; visée automatique. Un bouton contextuel apparaît près des objets. Paysage conseillé ; qualité légère disponible.

La reprise après défaite conserve le serment et recommence la salle. La Marque du Reflet peut être conservée sur l’appareil ; les expéditions ne sont pas sauvegardées au rechargement.

## Organisation

```text
docs/       Site publié par GitHub Pages, généré automatiquement
src/        Logique du jeu et interface éditables
vendor/     Moteur Three.js et licence MIT
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
python tests/art.py
python tests/tactics.py
python tests/heroes.py
python tests/smoke.py
python tests/design.py
python tests/input_regression.py
```

## Publier

Le réglage souhaité est **`main` → `/docs`**. La connexion ne peut pas changer ce réglage d’administration ; tant que Pages utilise la racine, les redirections fournies ouvrent le jeu dans `docs`. Le propriétaire peut sélectionner `/docs` une seule fois dans Settings → Pages. Après une modification, régénérer le site et envoyer sources et `docs/` dans le même commit. GitHub publie alors les pages de ce dossier. [Procédure](design/PUBLICATION.md).

Le lien historique `cathedrale-v03.html` redirige vers le jeu actuel. Pour ajouter une autre page indépendante, la placer dans `docs/` avec un nom distinct.

## Suite du projet

Les huit autres personnages du casting initial, le personnage secret complet, les deux autres grands niveaux, les comptes, la coop et le battle restent à développer. Les graphismes actuels sont provisoires. Les tests de navigateur simulé ne remplacent pas les essais de fluidité sur téléphone réel.

Three.js est sous licence MIT, conservée dans `vendor/THREE-LICENSE.txt` et dans la page générée. Aucune licence n’a encore été choisie pour les créations du jeu.
