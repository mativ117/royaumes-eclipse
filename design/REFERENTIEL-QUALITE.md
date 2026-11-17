# Référentiel de qualité — Les Royaumes de l’Éclipse

Établi le 17 novembre 2026 à partir du code du projet et des sources primaires ci-dessous. Ce document conserve des connaissances consultables dans le dépôt ; il ne modifie ni n’entraîne le modèle de l’assistant. Les cibles numériques sont des **objectifs de projet à mesurer**, pas des résultats acquis ou des normes universelles de qualité.

Le jeu reste dans le navigateur, sur PC et téléphone, sans serveur. La qualité des grands jeux cités est une direction d’exigence. Elle doit être décomposée en ressources, gestes et séquences évaluables, et ne peut pas être déclarée atteinte par un changement de moteur, un nombre de polygones ou une suite de tests.

## Règle de lecture

Pour chaque axe : distinguer le défaut observable, le critère perceptible en partie, la mesure technique et le prochain travail. Les tests contrôlés vérifient la cohérence ; une revue à vitesse normale et une partie humaine vérifient la qualité vécue. Les budgets PC/mobile se déterminent sur des appareils identifiés. Le comptage des draw calls, seul, ne mesure pas la fluidité.

## 1. Personnage, costume et matière

**Constat dans le projet.** `scripts/author_lame_reference.py`, `assets/characters/LAME-PRODUCTION.json` et `src/authored-avatar.js` donnent une Lame éditable dans Blender, un squelette compatible et 23 clips. La seconde géométrie vise une adulte d’environ 7,34 longueurs de tête. La coiffure, les déformations et les drapés restent simples. Les dix autres modèles n’ont pas reçu cette refonte. Le remplacement du cuir PBR par le tissu générique dans `refineHeroMaterials` a été corrigé.

**Revue humaine.** Comparer face, profil, dos et silhouette noire à la planche approuvée, puis depuis la caméra réelle du jeu. Lire immédiatement une adulte masquée portant une arme physique, plutôt qu’une poupée ou un assemblage d’éléments. À 1×, vérifier les plis aux épaules/hanches, la prise du sabre et les traversées du manteau. Un détail invisible depuis le jeu ne doit pas coûter autant qu’un détail essentiel de silhouette.

**Mesure technique.** Enregistrer triangles après export, matériaux, os, taille GLB, dimensions des atlas et temps de chargement. Vérifier que le GLB contient UV, cartes normales/rugosité/couleur, squelette et clips attendus ; aucune carte d’auteur ne doit être remplacée silencieusement à l’intégration. Mesurer les erreurs de déformation sur les poses extrêmes et conserver des captures du moteur.

**Action actuelle / suite.** Conserver la correction du cuir et la seconde silhouette. Prochaine production : détails et déformations d’un seul héros jusqu’à une référence convaincante, puis adaptation des autres ; ne pas généraliser une faiblesse en multipliant les variantes. Les principes de matériaux/baking Blender [B1–B2] servent au pipeline, sans supposer que tous les effets Cycles sont exportables en glTF.

**Budget PC/mobile à mesurer.** Fixer le coût du héros dans une scène de combat avec plusieurs créatures, pas uniquement dans l’atelier vide. Définir ensuite un LOD et une résolution d’atlas légère. Toute réduction doit conserver masque, arme, mains et jambes lisibles ; le nombre d’objets n’est pas un critère artistique.

## 2. Mouvement, attaques et sensations

**Constat.** `src/lame-motion.js`, `src/avatar-kinematics.js`, `src/authored-avatar.js` et `src/combat-motion.js` séparent locomotion et haut du corps. Des transitions peuvent être interrompues et la phase des appuis est conservée. Le jeu déplace le personnage indépendamment des clips. Des poses correctes isolées ne garantissent donc pas des appuis crédibles, surtout en marchant pendant une attaque. La passe 1.4 ajoute un retarget de mouvements Quaternius CC0 avec métadonnées de foulée, phases de contact et fenêtres de frappe ; son intégration et la qualité vécue restent à vérifier. Le rythme et l’équilibrage doivent être revus.

**Revue humaine.** Répéter à 1× : garde → marche → course → arrêt ; demi-tour ; pas latéral ; attaque immobile puis en avançant/reculant ; interruption par esquive ; blessure ; interaction. Lire préparation, contact et récupération, une prise d’arme stable et un transfert de poids. Vérifier les départs courts, les relâchements rapides et les changements d’avis, pas seulement une marche de dix secondes.

**Mesure technique.** Relever vitesse réelle du root et vitesse/hauteur du pied durant l’appui, dérive par pas, phase des deux couches, trajectoire de lame et instant de dégâts. Pour une frappe, la fenêtre de contact du gameplay doit correspondre à la trajectoire visible. Mesurer le délai entrée → début de réponse ; ne pas confondre latence du navigateur, anticipation intentionnelle et input perdu. Les modes Sync/Immediate/At End et les filtres décrits par Godot [A1] donnent un vocabulaire de transitions ; leur usage n’exige aucune migration. L’IK doit viser des contacts crédibles, sans membres qui s’étirent [B3].

**Action actuelle / suite.** La passe 1.4 retargete marche, course, garde et trois attaques à partir des bibliothèques Standard gratuites Quaternius. Le contrôleur utilise foulées et contacts mesurés, mélange les allures, borne les corrections de pied et calibre l’esquive ; le sabre est évalué dans une fenêtre active par balayage contre une capsule. Ces intégrations sont en cours de vérification, pas une qualité artistique acquise. Garder les correctifs phase/interruptions et tester les cas courts. Ensuite revoir les raccords, les poses et le pouvoir, puis étendre seulement à partir de cette référence. Les courbes, fenêtres de cancel et déplacements doivent avoir une seule définition de référence.

**Budget PC/mobile à mesurer.** Cible de réponse et de fluidité identique sur les deux plateformes ; adapter les effets, ombres et LOD avant de réduire la fréquence des entrées ou de la simulation. Mesurer coût du skinning/IK pour le solo dans la séquence représentative ; rétablir les budgets groupe/arène si ces modes sont réintroduits. La simulation actuelle à 60 Hz ne prouve pas un affichage à 60 images/s.

**Relief et physique future.** Le [contrôleur Rapier JavaScript 0.21](https://rapier.rs/docs/user_guides/javascript/character_controller/), consulté le 17 novembre 2026, calcule une translation corrigée par les obstacles et expose pentes, marches et maintien au sol. Il ne fournit pas le style du geste ni les rotations. Il est évalué, sans ajout au runtime 1.4 : le terrain actuel reste horizontal. Voir la [décision de plateforme](OUTILS-PRODUCTION-3D.md#physique-3d--outil-évalué-pour-la-suite).

**Défaut d’origine vérifié en 1.4.** Les semelles ont été mesurées sur les vertices skinnés : le bind laissait 2,5 cm sous les bottes, et le socle de l’atelier ajoutait 1 cm. Une enveloppe visuelle fixe corrige le repère dans le jeu ; l’atelier tient compte de son propre socle. La régression contrôle les deux semelles en idle/garde et l’absence d’accumulation, avec matrices de skin mises à jour comme au rendu. Les seules positions d’os n’auraient pas révélé ce défaut.

## 3. Créatures, combat et rencontres

**Constat.** `poseEnemy` dans `src/combat-motion.js` articule des marcheurs ; `refineEnemyAppearance` dans `src/visual-world.js` leur ajoute une robe/capuche partagée. Les autres types ont des états et pouvoirs, mais leur anatomie et personnalité restent proches. La passe 1.4 donne à la famille `warden` une référence quadrupède originale, Fauche-Cendre, avec 22 os, préparation directionnelle, détente et récupération. Les groupes et boss sont dirigés par `src/campaign.js` et `src/journey.js`.

**Revue humaine.** Identifier le rôle d’une créature avant sa première attaque, sans lire un texte technique. Distinguer locomotion, perception, anticipation, impact et récupération. Une rencontre doit demander une décision de position, de cible, de timing ou de ressource ; augmenter le nombre de bots ne suffit pas. Faire suivre une épreuve intense d’un espace qui permet d’observer et de choisir.

**Mesure technique.** Capturer le taux de menaces simultanées, temps moyen entre décisions, dégâts reçus par source, morts, nombre d’attaques annulées et temps de récupération exploitable. Vérifier qu’un télégraphe est visible dans la caméra réelle et conserve une alternative de lecture à la couleur [U1]. Comparer une même rencontre avec les deux styles de base, puis avec la Lame.

**Action actuelle / suite.** Fauche-Cendre est la première application : modèle original, quatre pattes, préparation de 0,78 s, détente frontale de 2,4 unités sur 0,32 s et récupération de 1,4 s. Son télégraphe, son contact unique et son son localisé sont intégrés à une rencontre de référence ; les essais d’ensemble sont encore en cours. Les autres familles restent à produire. Ensuite revoir les compositions de groupes et fenêtres de repos. Le comportement, la silhouette et les sons doivent expliquer le rôle ensemble.

**Budget PC/mobile à mesurer.** Définir le maximum de créatures actives à partir du pire combat solo réel, du coût d’IA, d’animation et des effets. Adapter le nombre de détails hors combat, pas les règles nécessaires pour comprendre la menace. Aucun plafond numérique de créatures n’est acquis par ce document.

## 4. Niveau, navigation et narration par le décor

**Constat.** Les trois chapitres ont objectifs, branches, rencontres et conclusions. `world.regions` et les quêtes organisent une carte au sol ; `buildGuideRoute` dans `src/readability.js` trouve un chemin praticable. La narration de `src/story-audio.js` est surtout une chronique et des textes. Le monde peut encore montrer des surfaces répétées, des plates-formes abstraites ou des objets peu contextualisés. La cible de 10–15 minutes par chapitre n’est pas mesurée en partie humaine.

**Revue humaine.** À chaque arrivée, le joueur doit pouvoir répondre : où suis-je, qu’est-ce qui attire mon attention, que puis-je faire, et pourquoi cela compte. Composer premier plan, zone jouable et horizon ; donner à chaque zone une fonction et des traces de ce qui s’y est passé. Garder des zones calmes et du vide intentionnel : remplir tout espace de props dégrade aussi la lisibilité. Le repère ou la flèche aide, sans remplacer une composition compréhensible. Le décor, les réactions et les systèmes peuvent laisser le joueur reconstruire l’histoire [L1].

**Mesure technique.** Relever une partie novice avec temps actif, hésitations, demi-tours, ouvertures de carte, objectifs mal compris, décès et retours. Séparer déplacement, combat, énigme, lecture et attente. Vérifier chemins obligatoires, optionalités et objets depuis les quatre directions d’approche. Les tests de quêtes avec téléportation n’établissent ni durée ni plaisir.

**Action actuelle / suite.** Les matières et bordures de la passe 1.3 traitent une partie des défauts de surface et de contexte. Ensuite travailler une séquence continue de 2–3 minutes : arrivée, objectif visible, rencontre, découverte, retour et conséquence. Donner un sens aux Archives et à la forge à travers leur usage et leurs traces, puis appliquer la méthode aux autres zones. Faire évoluer une chronique accessible à la demande, sans imposer toute l’exposition à chaque interaction.

**Budget PC/mobile à mesurer.** Même parcours, mêmes informations essentielles. Mesurer durée de traversée et densité de détails utiles au cadrage portrait/paysage. Les éléments lointains peuvent être instanciés ou réduits ; les éléments nécessaires au choix restent lisibles. Aucune durée de parcours n’est publiée comme acquise sans essais humains.

## 5. Rendu, lumière, ombres et cohérence des matières

**Constat.** `src/presentation.js` associe environnement, PBR et composition HDR ; `src/material-surfaces.js` prépare les six cartes photographiques de la passe 1.3. Les couleurs utilisent sRGB, les normales et rugosités restent des données. Des matériaux procéduraux et photographiques coexistent. Les ombres et objets devant la caméra ont déjà produit des défauts signalés par l’utilisateur.

**Revue humaine.** Comparer trois cadrages fixes, puis marcher : silhouette lisible dans la zone claire et dans la zone sombre, contact au sol, matières distinctes, ombres qui suivent correctement les objets mobiles. Un mur, du cuir, du bois, du tissu et une roche ne doivent pas partager une texture simplement parce qu’elle est disponible. Vérifier aussi la scène sans bloom pour ne pas masquer les défauts. Les zones noires intentionnelles doivent rester compréhensibles.

**Mesure technique.** Contrôler espace colorimétrique par carte et une seule conversion d’affichage [R1]. Vérifier UV, densité des texels, répétition, coutures, normales et échelle du relief ; comparer matériaux sous une lumière neutre puis artistique. Mesurer le coût des lumières et des passes d’ombre : une source qui projette des ombres implique des rendus supplémentaires [R2]. Capturer le scintillement, l’acné et le détachement des contacts en mouvement, pas seulement en image fixe.

**Action actuelle / suite.** Préserver les atlas des personnages, attendre les cartes avant la revue et affecter des matières selon leur rôle. Ensuite établir une palette minérale/bois/métal/tissu cohérente, un éclairage de référence et une densité UV cible. Revoir les objets du plafond et la caméra avant d’ajouter davantage d’effets. Les lightmaps/bakes [B2] sont une option à étudier pour le décor statique, sans figer les ombres des personnages.

**Budget PC/mobile à mesurer.** Mesurer séparément scène, ombres et composition Haute. En Léger, prioriser contacts et silhouettes ; réduire résolution d’ombre, effets hors champ et post-traitement avant de retirer un signe utile. Tester les surfaces brillantes et les transparences à la résolution réelle. Une grande texture ne prouve pas une bonne matière.

## 6. Performance, chargement et ressources

**Constat.** Le build embarque deux héros et les matières ; les autres modèles sont chargés à la sélection. L’aperçu est une scène séparée, suspendue hors vue et libérée au jeu. Les tests `render_complete` limitent actuellement les draw calls à 650 en Haute et 400 en Léger. Ces seuils sont des garde-fous du projet, pas une preuve de débit d’images. Le WebGL logiciel des essais ne représente pas un iPhone.

**Revue humaine.** Démarrage compréhensible, retour immédiat à la sélection, pas de blocage lors d’un changement de héros, pas de saccade répétée au premier impact. Une qualité élevée qui rend les entrées instables ne satisfait pas la cible. Tester une session prolongée pour détecter échauffement et perte progressive de fluidité.

**Mesure technique.** Capturer appareils, navigateur, résolution, DPR, qualité, scène, durée et commit. Mesurer temps d’image p50/p95/p99, longs blocages, mémoire et ressources GL, octets transférés et durée jusqu’au modèle prêt. `performance.now()` [P1] mesure le temps CPU/intervalle observé ; il ne fournit pas à lui seul le temps GPU. Les meshes statiques peuvent être fusionnés ou instanciés pour réduire les appels [R3], sans perdre culling, matériaux ou collisions. Répéter sélection → jeu → menu et changement de chapitre pour détecter les ressources non libérées.

**Objectifs de départ, à éprouver.** PC Haute : viser 60 images/s, soit 16,7 ms par image, avec p95 suivi séparément. Mobile : viser 60 en Léger sur l’appareil cible ; si 30 est le compromis choisi, annoncer cette cible et viser une cadence stable à 33,3 ms. Le choix final exige des mesures matérielles et une décision de produit. Aucun score mesuré n’est actuellement donné ici.

**Action actuelle / suite.** Conserver les chargements différés et le cycle de vie de l’atelier. Profilage sur deux appareils identifiés avant d’imposer des budgets de triangles/textures/ennemis. Utiliser les régressions de ressources, puis seulement optimiser le poste dominant.

## 7. Musique, effets, espace sonore et silence

**Constat.** `src/story-audio.js` produit trois motifs synthétiques et des effets de bruit filtré. La passe 1.4 ajoute une position à `playWorldSound`, un panoramique relatif à la caméra et une atténuation par distance. Musique, effets et interface rejoignent un limiteur puis un master ; `tone` utilise désormais le même routage. Volume zéro coupe le master, la pause arrête les sons du monde et les notes actives sont nettoyées. La limite est de 16 voix d’effets actives, avec priorité aux signes importants. Les tests audio CPU ont été exécutés par le responsable du module ; la vérification d’intégration reste en cours. Une musique continue ne prouve pas un mixage abouti.

**Revue humaine.** Reconnaître pas, arme, impact, danger et interaction sans regarder le code. À casque puis en mono, sentir la distance et la direction sans perdre une information essentielle. La musique doit servir exploration, tension et résolution ; laisser du silence et de la place aux signes de gameplay. Un danger indispensable doit aussi être visible [U1]. Ne pas annoncer une bande-son enregistrée ou orchestrale pour les synthèses actuelles.

**Mesure technique.** Tester volume zéro/mute, pause, reprise, changement de chapitre, plusieurs impacts et notes actives. Vérifier le routage, les enveloppes, la libération des nœuds et les crêtes du mix. Comparer l’instant d’impact sonore à l’instant de contact visuel. Pour la spatialisation, mesurer et tester position/orientation de l’auditeur, atténuation par distance et source hors champ. `PannerNode` et `StereoPannerNode` ont des rôles distincts [S1] ; l’axe de panoramique doit correspondre à la caméra, pas arbitrairement au X du monde.

**Action actuelle / suite.** Silence à zéro, routage cohérent, nettoyage, pause et spatialisation stéréo sont implémentés dans la passe 1.4. Les pas de la Lame calibrée suivent les événements d’appui ; les autres héros conservent la solution précédente. Vérifier l’ensemble à casque et sur haut-parleur avant de considérer le mix comme abouti. Produire ensuite un jeu d’effets plus riche par arme/sol/créature, avec provenance/licence et variantes. Les sons d’interface restent indépendants de la distance. Planifier des changements de couches/phrases, plutôt qu’une bascule musicale à chaque frame.

**Budget PC/mobile à mesurer.** La limite implémentée de 16 voix d’effets est un point de départ, à vérifier dans le combat solo le plus chargé. Mesurer nombre de panners, décodage, mémoire des buffers et CPU. Réserver le calcul spatial coûteux aux sources pertinentes ; conserver contrôle utilisateur et déclenchement après interaction [S2].

## 8. Interface, entrées et accessibilité

**Constat.** Les touches solo sont configurables ; les anciennes commandes coop restent dans le module complet et les archives, hors du bundle courant. Carte et barre PC ont un décalage calculé ; les tailles et superpositions restent à vérifier dans chaque état. Le mode épuré masque plusieurs détails. La passe 1.4 ajoute `src/modal-focus.js` : entrée dans le dialogue, confinement Tab/Shift+Tab, arrière-plan inerte et retour logique du focus pour les écrans gérés, dont carte, pacte et choix de route. Les essais CPU du module sont passés ; le parcours intégré reste en cours de vérification. Le HUD contient encore du texte de 9–12 px selon les variantes.

**Revue humaine.** Commencer au clavier, à la souris, au tactile puis à la manette : choisir, comprendre, modifier, jouer, ouvrir la carte, fermer et reprendre sans action accidentelle. Lire un objectif et une interaction sans déplacer le personnage pour échapper au HUD. La carte, le récit et les réglages doivent utiliser la même logique de retour. Les boutons restent identifiables sans couleur seule, et le texte indispensable demeure lisible [U1].

**Mesure technique.** Vérifier bounding boxes et recouvrements à 390×844, 844×390, 1024, 1366 et 1920 px, avec texte long et zoom. Tests du parcours Tab/Shift+Tab/Échap, focus visible, touches remappées, conflits et persistance. Objectif de projet à éprouver : cibles tactiles d’au moins 44 CSS px bien espacées et corps de lecture de 16 CSS px ; ne pas traiter ces valeurs comme une conformité complète. Tester les indices en niveaux de gris et son coupé. La carte dessinée dans un canvas a aussi besoin de son journal textuel.

**Action actuelle / suite.** Préserver le remappage et les corrections de disposition. La gestion commune du focus est maintenant implémentée, sans changer les règles de validation. Ensuite hiérarchie des informations, taille de texte réglable, sensibilité, commandes manette des menus et alternatives aux maintiens prolongés. Le lancement 1.4 se concentre sur le solo conformément au choix confirmé par l’utilisateur, avec les autres modes conservés dans les archives. Les menus et le code de groupes/arènes/bots sont exclus du bundle courant, avec le module complet et les archives 1.3 conservés. Les créatures et boss gardent leur IA locale, sans service connecté. Une liste de réglages ne remplace pas l’essai par des personnes concernées.

**Budget PC/mobile à mesurer.** Même information utile et même fonctionnement, dispositions adaptées. Mesurer délai d’ouverture de carte et coût des mises à jour DOM. Ne pas désactiver des adaptations nécessaires pour atteindre une cible graphique. Les contrôles doivent rester accessibles pendant le chargement d’un aperçu.

## Sources primaires consultées

Les pages suivantes ont été récupérées le 17 novembre 2026. Les principes sont reformulés pour le projet ; les chiffres de budget ci-dessus sont nos propositions, pas des prescriptions attribuées à ces auteurs.

- **[L1] GDC 2010, Harvey Smith (Arkane Studios) et Matthias Worch (LucasArts), [What Happened Here? Environmental Storytelling](https://www.gdcvault.com/play/1012647/What-Happened-Here-Environmental).** Résumé officiel consulté : environnement comme dispositif narratif, interprétation active, props/textures/lumière/composition et réactions systémiques. La vidéo complète n’est pas présentée comme visionnée.
- **[R1] Three.js r160, [Color management](https://github.com/mrdoob/three.js/blob/r160/docs/manual/en/introduction/Color-management.html).** Couleur sRGB, calcul linéaire, cartes non colorimétriques et conversion de sortie. Version choisie pour correspondre au runtime 0.160.1 du projet.
- **[R2] Three.js r160, [Shadows](https://github.com/mrdoob/three.js/blob/r160/manual/en/shadows.html).** Coût des rendus d’ombre et réglage des volumes de projection.
- **[R3] Three.js r160, [Optimize Lots of Objects](https://github.com/mrdoob/three.js/blob/r160/manual/en/optimize-lots-of-objects.html).** Surcoût des objets et fusion des géométries. Les pages équivalentes `threejs.org/manual/en/...html` ont répondu 404 dans cette consultation ; le dépôt officiel de cette version a été lu.
- **[B1] Blender 4.3, [Principled BSDF](https://docs.blender.org/manual/en/4.3/render/shader_nodes/shader/principled.html).** Paramètres de matière, métal, rugosité et couches ; disponibilité/export à vérifier selon le renderer cible.
- **[B2] Blender 4.3, [Render Baking](https://docs.blender.org/manual/en/4.3/render/cycles/baking.html).** Baking des cartes pour les moteurs, UV et lightmaps.
- **[B3] Blender 4.3, [Inverse Kinematics Constraint](https://docs.blender.org/manual/en/4.3/animation/constraints/tracking/ik_solver.html).** Cible, pole target, chaîne et étirement ; l’IK est un outil de contact, pas une animation complète.
- **[A1] Godot, [Using AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html).** Couches/filtres, blend spaces et transitions synchronisées/immédiates/en fin de clip. Utilisé comme référence de conception du contrôleur existant, sans migration.
- **[S1] W3C, [Web Audio API 1.1](https://webaudio.github.io/web-audio-api/), sections `PannerNode`, `StereoPannerNode`, `AudioListener`, `GainNode` et `AudioParam`.** Définitions de spatialisation, routage et automation.
- **[S2] MDN, [Web Audio API best practices](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices).** Autoplay, contrôle utilisateur et modification des paramètres audio.
- **[U1] [Game Accessibility Guidelines — Basic](https://gameaccessibilityguidelines.com/basic/).** Remappage, taille/espacement des contrôles, même moyen d’entrée dans les menus, contraste, information non fondée uniquement sur la couleur ou le son, volumes séparés et réglages mémorisés.
- **[P1] MDN, [Performance.now](https://developer.mozilla.org/en-US/docs/Web/API/Performance/now).** Horloge monotone pour les mesures de durée ; distinguer mesure CPU et GPU.

## Application suivie dans la passe 1.4

La [matrice de prise en charge](PRISE-EN-CHARGE-1.4.md) distingue recherche, application et revue restante. Les notes spécialisées complètent ce référentiel : [retarget](RETARGET-1.4.md), [mouvement](MOUVEMENT-1.4.md), [créature](CREATURE-1.4.md), [audio](AUDIO-1.4.md) et [interface](INTERFACE-1.4.md). Elles enregistrent leurs sources et limites. Les contrôles de module ne remplacent pas les essais de toute la séquence ni une validation artistique.
