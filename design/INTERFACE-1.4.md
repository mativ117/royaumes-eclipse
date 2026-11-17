# Dialogues et commandes clavier — passe 1.4

La carte, le choix de serment et le choix de route/don déclaraient déjà un rôle de dialogue modal. Ils ne plaçaient pas le focus dans leur contenu et laissaient le parcours Tab atteindre des commandes situées derrière. La chronique et le panneau Commandes avaient leur propre gestion du focus ; ils sont conservés.

## Changement limité

`src/modal-focus.js` prend en charge uniquement `mapPanel`, `choicePanel` et `journeyChoice`. La sélection du dialogue actif suit l’état du jeu et les couches visibles. Le module :

- place le focus sur la première commande disponible ; le délai de confirmation du serment garde donc le bouton Revenir accessible et ne force pas le choix de Sceller ;
- contient Tab et Maj+Tab, sans modifier les flèches, Espace, Entrée ou la logique des actions ;
- ignore les commandes désactivées, cachées, sous un élément `inert` ou dans une partie repliée ;
- rend temporairement inertes les autres racines du document et restaure leur état initial à la fermeture ;
- préserve la propriété du focus d’un dialogue natif comme le guide et retrouve la dernière commande d’une couche encore ouverte ;
- restaure le déclencheur s’il existe encore et reste utilisable. Si l’interaction du monde vient de disparaître, il neutralise le focus de l’ancien dialogue sans envoyer le focus sur le canvas ;
- affiche un contour clavier visible. Aucun réglage ni mode supplémentaire n’est ajouté.

Les gestionnaires existants conservent Échap. Le garde de saisie de `input-settings.js` laisse désormais passer Échap en état carte/choix, y compris depuis une case à cocher de la carte. Son traitement du relâchement d’une touche respecte aussi les contrôles de formulaire : Espace peut réellement cocher une option de la carte. Les saisies de profil et les raccourcis configurables restent protégés.

## Intégration et vérification

Inclure le module dans la construction, puis appeler `initModalFocus()` **avant** `initInputSettings()` pour enregistrer la gestion de Tab avant le garde de saisie. Les modaux créés ensuite au démarrage sont observés sans surveiller les transformations 3D mises à jour chaque image.

`python tests/modal_focus.py` utilise les vrais fragments HTML des trois dialogues, le vrai garde de saisie et un Chromium sans GPU. Il vérifie les commandes disponibles, les boucles de focus, la fermeture par Échap depuis une case, Espace au retour au jeu, les choix dynamiques, les couches et la restauration de l’état `inert`.

`python tests/modal_focus.py --integration` ajoute un parcours sur le jeu construit ; il doit être exécuté avec le créneau GPU de validation partagé. Ces vérifications ne constituent pas une validation avec lecteur d’écran ou appareil physique.

Le scénario CPU et `tests/modal_focus.py --integration` ont passé le 17 novembre 2026 : carte réelle, pacte et choix de route, fermeture depuis une case de carte et reprise du jeu. `tests/input_settings.py` passe aussi avec touche de carte remappée, contrôles natifs conservés et disposition PC/tactile. Voir le relevé de validation de la livraison.

## Références consultées

- [W3C WAI-ARIA APG — Dialog (Modal) Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) : entrée du focus, séquence Tab contenue, arrière-plan inerte et retour vers une cible logique.
- [Game Accessibility Guidelines — Basic](https://gameaccessibilityguidelines.com/basic/) : accès à l’interface avec la même méthode d’entrée que le jeu, commandes simples et lisibilité des actions.

Consultation du 17 novembre 2026. Le comportement retenu est une adaptation de ces recommandations à la reprise directe des commandes de jeu ; aucune certification d’accessibilité n’est annoncée.
