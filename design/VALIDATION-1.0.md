# Validation — version candidate 1.0-rc1

Contrôles terminés le 16 novembre 2026. Client et paquet de livraison : commit `861a664`. Ce relevé et la fermeture de la liste de contrôle sont ajoutés après publication ; le ZIP est conservé comme artefact de cette livraison.

## Publication réelle

- HTML servi par GitHub Pages identique au fichier généré. SHA-256 : `f43cad53992587d6442910408d8118fdba7b05ea855a2f7765c57198013746a1`.
- Les onze modèles servis ont été téléchargés et comparés aux empreintes de `docs/version.json`.
- ZIP public identique au paquet validé de 10 179 864 octets. SHA-256 : `7433cfd8c1807163711456d7e1972d978d4ea9133e3851cc8a230eeed43eeba0`.
- Navigation sur le site public : redirection de l’accueil, choix de la Tisseuse, chargement de son modèle distant, démarrage du chapitre II et rendu WebGL, sans erreur JavaScript.

## Vérifications locales

Les suites couvrent profils, chapitres complets, modes locaux, animation, physique, dynamique, Cathédrale, guidage, art, ombres, cartes, tactile, rendu des nouveaux niveaux, construction et paquet. Les scénarios contrôlent notamment les conditions de fin, les boss et le secret ; ils ne remplacent pas des parties humaines chronométrées.

Le battle humain à quatre est vérifié par affectation des équipes et entrées de manettes simulées. Les reprises coop, règles de duel, protection de la sauvegarde d’aventure, absence de bonus de serment et règles de couronne sont contrôlées. Le rendu Haute/Légère est exécuté en desktop, portrait et paysage.

Les archives antérieures ont été comparées à leur inventaire ; aucune ancienne livraison n’est supprimée. Le ZIP est reproductible à contenu de checkout identique, et le snapshot historique courant intègre les onze modèles pour fonctionner sans téléchargement de modèle.

## À éprouver en parties

Performances sur téléphone réel, matériel de manette réel, durée et rythme des chapitres, équilibre des onze kits, lisibilité en groupe et qualité artistique. Les limites physiques et les fonctions réseau reportées sont détaillées dans [SUIVI.md](SUIVI.md).

## Incident après ces vérifications

Lors de l’envoi du relevé final, GitHub a répondu : « Repository mativ117/royaumes-eclipse is disabled. Please ask the owner to check their account. » (403). Un contrôle ultérieur a confirmé que le dépôt et GitHub Pages renvoient 404. Le ZIP brut restait accessible lors du dernier contrôle, mais ne constitue pas une garantie de disponibilité future.

Les sources, modèles, archives et versions autonomes sont conservés dans le workspace. Une copie du ZIP et du HTML autonome est livrée dans `/workspace/shared/livraison-royaumes-eclipse/`, avec une notice locale. Le commit de documentation reste local, en attente du rétablissement des accès GitHub.
