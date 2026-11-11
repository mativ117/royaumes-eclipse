# Publication GitHub Pages

- Dépôt : `mativ117/royaumes-eclipse`.
- Source Pages souhaitée : branche `main`, dossier `/docs`.
- État lors de l’envoi : branche `main`, racine `/`. La connexion GitHub autorise le code mais refuse ce réglage d’administration (403). Deux redirections à la racine permettent donc de jouer immédiatement, tout en gardant le jeu dans `docs`.
- Pour ne publier que `docs`, le propriétaire peut choisir Settings → Pages → main → /docs → Save. Les redirections à la racine seront alors simplement ignorées.
- Adresse principale : https://mativ117.github.io/royaumes-eclipse/
- Ancien lien conservé : https://mativ117.github.io/royaumes-eclipse/cathedrale-v03.html

## Mise à jour du jeu

1. Modifier `src/game.js` ou `src/template.html`.
2. Lancer `python scripts/build.py`.
3. Vérifier le site localement et exécuter les tests utiles.
4. Envoyer les sources et les pages générées dans le même commit sur `main`.
5. Vérifier le déploiement GitHub Pages puis la version publiée dans `version.json`.

Ne pas éditer directement `docs/index.html` : une prochaine construction remplacerait ces modifications. Le script ne touche pas aux autres pages indépendantes ajoutées dans `docs`.

## Ajouter une page indépendante

Un fichier `docs/exemple.html` devient accessible à `https://mativ117.github.io/royaumes-eclipse/exemple.html`. Aucun changement du réglage Pages n’est nécessaire.

Tout ce qui est dans `docs` est destiné à être public. Les sources, documents de conception et anciennes versions sont rangés à l’extérieur. Ne jamais mettre de secret ou de donnée personnelle dans le dépôt.

## Archives

`historique/` conserve les fichiers du dépôt avant cette réorganisation. Le fichier vide nommé `historique` a été remplacé par un véritable dossier. `design/GITHUB-INITIAL.md` conserve les anciennes instructions de création ; utiliser cette page pour la publication actuelle.
