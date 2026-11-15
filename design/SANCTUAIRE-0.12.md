# Le parvis et les héros — 0.12

## Problème traité

Les changements précédents laissaient visibles le même sol quadrillé, le petit personnage assemblé et un cadrage éloigné. Cette passe reconstruit la zone d’arrivée et remplace les deux personnages par des modèles articulés. Elle se concentre sur une séquence représentative ; elle ne prétend pas que les autres zones ont reçu le même traitement architectural.

## Modèles et mouvement

`scripts/author_characters.py`, exécuté avec Blender 4.3.2, crée les modèles originaux Rempart et Voltigeur. Aucun personnage ou animation d’un autre jeu n’est utilisé. Les GLB sont conservés dans `assets/characters` avec leur provenance et embarqués dans la page publiée.

Chaque héros possède un squelette de 22 os, une tenue, un manteau articulé et une arme séparée. Treize actions sont exportées : repos, marche, course, trois frappes, tir, esquive, bond, protection, interaction, portage et réaction au coup. `AnimationMixer` les joue avec transitions et ajustement à la vitesse de déplacement ou à la durée de l’attaque. Les modèles sont stylisés et ne sont pas les costumes finaux du casting complet.

La vitesse libre passe de 6 à 4,9 pour le Rempart et de 7,4 à 6,1 pour le Voltigeur. La portée de base de mêlée passe de 3,5 à 2,7 pour mieux correspondre à la lame et au corps ; les dégâts et fenêtres de contact restent conservés. Une traînée suit la lame, le tir part du canon et l’arme est masquée pendant le portage. Les fenêtres physiques du combat continuent d’être pilotées par la simulation ; l’animation ne décide pas seule des dégâts.

## Cour et caméra

Le bassin occupe le centre de la cour. Il bloque les déplacements mais laisse passer les tirs et la ligne de vue. Ses dimensions sont utilisées par le moteur de collision et la carte ; le guidage propose des chemins autour. Les colonnes nouvelles reprennent les empreintes des anciens obstacles et les structures de bordure restent hors du sol praticable.

La mosaïque radiale, les voûtes, les colonnes et le monument cadrent la vue. La caméra se rapproche et s’abaisse tout en gardant une orientation stable. Sur téléphone, la sélection automatique des ennemis tient compte du champ de vision. Les obstacles solides situés devant le héros s’atténuent progressivement pour le laisser visible ; leur collision reste active.

## Rendu et coût

Les composants GLTFLoader, BufferGeometryUtils et Reflector viennent des sources officielles Three.js r160, sous licence MIT. Les originaux, leur empreinte et le générateur de bundle sont conservés dans `vendor/three-r160-upstream` et `scripts/prepare_three_addons.py`.

La qualité Haute ajoute un reflet planaire du bassin en 512 × 512 et une ombre directionnelle 1024 × 1024 suivant le héros. La réflexion cesse d’être rendue quand on quitte la cour. Les vues de pause, carte et choix figées arrêtent les rendus répétés jusqu’à leur fermeture ou un redimensionnement. Elle ajoute une passe réelle de rendu : le budget de test standard passe à 650 appels, la variante Légère reste sous 400. Ce sont des budgets de validation, pas une garantie de fréquence d’images sur téléphone.

Le tactile démarre en qualité Légère pour limiter le coût de compilation et de rendu initial ; le réglage Haute reste sélectionnable. La qualité Légère conserve la cour et les modèles mais remplace le miroir par une surface d’eau stylisée à rides animées, sans reflet de scène, et les ombres physiques par les ombres de contact. La page reste autonome, sans CDN ni récupération de modèle au lancement. Sa taille augmente à environ 2,3 Mo avant compression HTTP.

## Vérification et comparaison

`tests/sanctuary.py` vérifie les modèles skinnés, les clips et os en mouvement, le portage, les frappes, le canon, le parcours physique autour du bassin, l’occultation, les variantes de rendu et les erreurs JavaScript/shader. Les suites du scénario, guidage, lisibilité, multitouch et publication restent conservées. Les sauvegardes locales utilisant le protocole 0.9 restent compatibles.

`scripts/capture_comparison.py` capture les vues réellement exécutées des versions 0.11 et 0.12 au même point de départ. La page `docs/avant-apres.html` permet de les comparer. Le cadrage propre à chaque version est conservé ; aucune image générée ou retouchée ne remplace les captures. Le téléphone est simulé dans Chromium.

Les objectifs complets du projet et leur état sont réunis dans [SUIVI.md](SUIVI.md). La durée de 10–15 minutes et la fluidité réelle sur téléphone restent à confirmer par des parties humaines.
