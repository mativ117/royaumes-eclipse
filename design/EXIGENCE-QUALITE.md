# Exigence durable — viser la qualité des meilleurs jeux sur l’ensemble du jeu

**Priorité explicitement confirmée par l’utilisateur le 17 novembre 2026 : pousser le jeu entier aussi près que possible de la qualité des meilleurs jeux AAA, dans notre univers.** Cette demande guide la production à venir et les arbitrages de chaque passe. Elle ne constitue ni une description du rendu actuel, ni une promesse commerciale, ni une qualité acquise par la réussite des tests.

La cible porte sur la cohérence de l’expérience complète : ce que le joueur voit, entend, comprend et ressent lorsqu’il explore, choisit, se déplace et combat. Une scène spectaculaire isolée ne suffit pas si les autres personnages, zones ou systèmes restent sommaires. La Lame et Fauche-Cendre sont des premières références de travail ; elles n’épuisent pas le périmètre final.

## Périmètre de l’exigence

| Domaine | Qualité recherchée sur tout le contenu |
|---|---|
| Tous les héros, y compris le secret | Silhouettes adultes et crédibles dans leur intention, costume et matières cohérents, déformations propres, prise d’arme plausible, personnalité gestuelle et pouvoirs distincts. Éviter les proportions de poupée et les simples variantes du même mannequin. |
| Toutes les familles ennemies et les boss | Créatures à l’anatomie et au comportement compréhensibles, locomotion propre, préparation et récupération lisibles, réactions au joueur, rencontres construites plutôt qu’accumulation de bots. |
| Mouvement et animation | Appuis et transfert de poids crédibles, accélération/freinage, virages, pas orientés et transitions réactives. L’attaque en déplacement doit conserver les contacts et la prise d’arme ; une correction technique ne doit pas masquer une cadence ou une pose peu naturelle. |
| Combat et sensations | Préparation, trajectoire, déplacement, collision, dégâts, effets et son alignés ; impacts et récupérations perceptibles, esquives et pouvoirs différenciés, décisions tactiques et équilibrage à éprouver en partie. |
| Trois niveaux et tous les environnements | Géographie et fonction des lieux, chemins compréhensibles, exploration et défis variés, progression et rythme. Composer chaque zone et ses transitions ; corriger les vides ou surfaces sans finition accidentels sans remplir systématiquement tous les espaces. |
| Rendu, matériaux, lumière et ombres | Échelle et densité des textures cohérentes, matières distinctes, contacts au sol, silhouettes lisibles, ombres stables qui suivent les objets mobiles, décor qui n’occulte pas les informations importantes. Revoir le résultat en mouvement et dans les deux qualités. |
| Histoire et mise en scène | Enjeux, motivations et conséquences présentés clairement, scènes et découvertes qui ont un sens dans notre univers, narration portée aussi par les lieux et les réactions. Les textes de chronique seuls ne constituent pas une mise en scène finale. |
| Musiques et effets sonores | Identité sonore, tension et respiration, transitions musicales, timbres et variantes adaptés aux armes, sols et créatures, mix intelligible, contacts synchronisés, espace et distance perceptibles, contrôle utilisateur fiable. |
| Interface et accessibilité | Lecture immédiate sur PC et téléphone, panneaux et carte sans chevauchement, commandes expliquées et modifiables, focus et retours cohérents, menus utilisables avec les entrées prévues, information essentielle non limitée à une couleur ou un son. |
| Physique et interactions | Objets solides respectés, contacts et glissement cohérents, volumes d’attaque conformes au geste, interactions accessibles sans décalage artificiel. Ne pas prétendre disposer de relief parcourable ou de corps rigides tant qu’ils ne sont pas produits. |
| Technique et performances | Chargement, stabilité, cadence et mémoire maîtrisés dans les scènes réellement jouées ; mesurer sur PC et téléphone physiques. Le réglage Léger doit préserver les règles, signes et sensations essentiels. |
| Cohérence d’ensemble | Les personnages, créatures, niveaux, sons et interfaces doivent sembler appartenir au même jeu. La finition d’une seule ressource ne doit pas servir à annoncer celle de tout le produit. |

## Décisions produit conservées

Le jeu reste accessible par lien, dans le navigateur, sur PC et téléphone. Le choix sans serveur est conservé. Le périmètre courant conserve l’aventure solo, les duels contre une IA tactique locale et le module LAN direct demandé ensuite, y compris téléphone ↔ téléphone sans PC obligatoire. Le transfert natif du LAN reste à éprouver. Les anciens modes inutiles restent dans les archives. Les créatures et boss conservent leur IA locale, sans service connecté.

Les détails visuels sont privilégiés avec un réglage Léger. Les trois chapitres, les dix héros disponibles dès le début, le onzième personnage secret, les profils locaux, l’export/import, les anciennes reprises et l’historique restent à préserver. La direction de la Lame déjà approuvée est une base de production ; elle ne demande pas une nouvelle validation pour chaque correction déjà autorisée.

La direction artistique reste originale : noir et ambre, espaces monumentaux, silhouettes et tissus, avec les références transmises par l’utilisateur. Le rapprochement avec les jeux de référence concerne l’exigence de fabrication et de sensation ; il ne justifie pas d’en copier les ressources.

## Méthode pour atteindre cette cible

1. **Reprendre l’état réel.** Consulter la version, le [suivi](SUIVI.md), la matrice de prise en charge courante et son relevé de validation ; vérifier le code et les ressources. Distinguer ce qui est produit, ce qui a été testé et ce qui reste artistiquement ou matériellement à évaluer.
2. **Choisir un défaut perceptible et une référence.** Utiliser le [référentiel sourcé](REFERENTIEL-QUALITE.md) et le [workflow](WORKFLOW-QUALITE.md). Donner à la passe un bénéfice concret : poids du mouvement, lecture d’une menace, compréhension d’un lieu, qualité d’un contact ou absence de gêne d’interface.
3. **Produire et intégrer.** Travailler l’asset éditable, le contrôleur et sa présentation ensemble lorsque nécessaire. Vérifier les matériaux, le squelette, les déformations, les contacts et le son dans le runtime ; une ressource bien rendue hors jeu peut encore être dégradée à l’intégration.
4. **Comparer à 1×.** Enregistrer le résultat réel avant/après dans les mêmes conditions de caméra, résolution et qualité. Regarder et écouter à vitesse normale avant de ralentir pour diagnostiquer. Les images générées restent des concepts, clairement séparés des captures du jeu.
5. **Vérifier puis étendre.** Exécuter les régressions pertinentes et mesurer les postes concernés. Une première référence réussie sert ensuite aux autres héros, créatures et zones ; elle ne clôt pas leur travail. Faire des essais humains pour la navigation, le plaisir, le récit, l’équilibrage et la durée.
6. **Conserver les résultats.** Mettre à jour la couverture de tout le jeu, les sources, les preuves, les limites et la prochaine passe. Les connaissances restent dans le dépôt et les assets ; elles ne constituent pas une formation permanente du modèle.

Cette méthode n’ajoute pas une approbation obligatoire entre chaque correction. Les choix déjà confirmés et les travaux nécessaires à leur réalisation restent autorisés. Une question est utile lorsqu’un nouveau choix important ne peut pas être résolu avec le contexte ; les tâches indépendantes continuent pendant ce temps.

## Critère de progrès et suivi durable

Chaque livraison doit permettre de répondre aux questions suivantes :

- Quel défaut du jeu a réellement changé pour le joueur, et dans quels héros, familles ennemies, zones et états d’interface ?
- Quelle comparaison issue du moteur, à vitesse normale, montre ce changement ? Le bénéfice reste-t-il perceptible avec le son et les contrôles réels ?
- Quelles mesures et régressions ont été exécutées, sur quel commit, appareil, navigateur, résolution et qualité ? Quelles vérifications restent simulées ?
- Quel contenu demeure provisoire ou incohérent avec la nouvelle référence ? Quelle prochaine passe permet d’étendre le progrès à l’ensemble du jeu ?

Le suivi doit garder une couverture explicite : tous les héros et le secret, toutes les familles ennemies et boss, les trois chapitres et leurs zones, les gestes et contacts, la présentation du récit, l’audio, l’interface, la physique et les deux qualités graphiques. Un axe peut avoir des éléments appliqués tout en restant à revoir ailleurs. « Testé » ne signifie pas « fini ».

Les captures du moteur, séquences à 1×, provenance des ressources et résultats de tests constituent les preuves techniques du travail. La cadence doit être relevée sur des appareils physiques identifiés, avec p50/p95/p99, durée, résolution et réglage ; les cibles à établir et les compromis appartiennent au référentiel, pas à un label AAA. L’esthétique, le plaisir et la compréhension doivent aussi être évalués en partie humaine.

Une augmentation de particules, de polygones, de taille des textures ou de quantité d’assets n’est pas un progrès suffisant en soi. La priorité reste la cohérence, la lisibilité, la jouabilité et la sensation d’un jeu abouti sur son ensemble.

## Documents qui portent cette exigence

- [AGENTS.md](../AGENTS.md) : consigne d’entrée pour les agents travaillant dans le dépôt.
- [Suivi du projet](SUIVI.md) et matrice de la livraison courante : état et couverture du contenu ; la matrice 1.4 reste un relevé de cette étape, pas la définition du périmètre final.
- [Référentiel qualité](REFERENTIEL-QUALITE.md) : sources, constats, critères de revue, mesures et limites.
- [Workflow](WORKFLOW-QUALITE.md) et [skill local](skills/quality-pass/SKILL.md) : procédure réutilisable de recherche, production, intégration, comparaison et vérification.

Cette exigence est une cible durable de production pour tout le jeu. Aucun document, score de test ou nom de version ne doit la transformer en déclaration prématurée de qualité atteinte.
