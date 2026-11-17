---
name: royaumes-quality-pass
description: Appliquer une passe de qualité ciblée au jeu Les Royaumes de l’Éclipse, avec recherche primaire, asset éditable, intégration, comparaison à vitesse normale et régressions adaptées.
---

# Passe de qualité des Royaumes de l’Éclipse

Skill local au dépôt. Il doit être lu explicitement par l’agent ; sa présence ne crée pas de connecteur et ne forme pas le modèle. Il ne modifie pas les instructions globales. Les demandes et décisions déjà autorisées par l’utilisateur prévalent ; ne pas demander à nouveau une permission pour un choix couvert par le contexte.

## Activation

Utiliser pour une amélioration de rendu, personnage, animation, combat, niveau, narration, audio ou interface dans ce projet. Lire `design/REFERENTIEL-QUALITE.md` pour l’axe concerné et `design/WORKFLOW-QUALITE.md` pour la procédure complète. Ne pas recommencer une recherche déjà documentée sans raison de version, d’erreur ou de nouvelle question.

La [cible durable de qualité](../../EXIGENCE-QUALITE.md), confirmée par l’utilisateur, s’applique au **jeu entier aussi proche que possible des meilleurs jeux AAA**. Une passe ciblée doit s’inscrire dans la couverture de tous les héros, créatures, niveaux et systèmes ; une référence réussie ne vaut pas finition de l’ensemble. Améliorer un défaut perceptible de cohérence ou de jouabilité, puis documenter l’extension restante et les preuves réelles, sans déclarer la cible atteinte à partir de tests seuls.

## Procédure

1. Définir le défaut vu par le joueur, sa séquence de référence et un critère de réussite perceptible à vitesse 1×. Préserver Web PC/téléphone, mode léger, choix sans serveur et compatibilité des sauvegardes. Le lancement 1.4 est solo : ne pas réintroduire les menus ou le code de groupes/arènes/bots dans le bundle ; conserver le module complet et les archives 1.3. Les ennemis et boss gardent leur IA locale.
2. Lire les fichiers responsables. Consulter une source primaire pertinente si le référentiel ne suffit pas ; enregistrer version, URL, date, point retenu et limite. Une source méthodologique d’un autre moteur n’autorise pas sa migration.
3. Capturer l’état réel avant modification. Mesurer le défaut approprié sans annoncer une mesure sur appareil physique à partir d’un navigateur simulé.
4. Produire une ressource source éditable et/ou un correctif ciblé. Vérifier licence/provenance des assets externes et éventuels coûts des outils avant usage. Conserver atlas, rig, durées et contacts à l’intégration ; séparer matériau, mouvement, collision et rendu dans le diagnostic.
5. Tester une référence convaincante avant d’étendre aux autres héros, créatures ou zones. Comparer depuis la caméra du jeu, à 1×, avec et sans son ; ralentir ensuite pour expliquer un défaut. Garder les concepts et les captures réelles clairement distincts.
6. Exécuter seulement les régressions pertinentes. Dans cet environnement, lancer les tests GPU séquentiellement. Vérifier erreurs, ressources, chargements et cycle sélection → jeu → menu si concerné. Mesurer p95/p99 sur matériel identifié avant de revendiquer une cadence mobile.
7. Documenter résultat, sources, fichiers, tests réellement exécutés, limitations et prochain travail. Mettre à jour les connaissances du dépôt. Pour une publication déjà autorisée, terminer build, archive, déploiement et vérification distante ; ne pas laisser une simple proposition à la place du travail.

## Points d’attention

- Un test technique réussi ne valide ni l’esthétique, ni le plaisir, ni une durée humaine de partie.
- Une augmentation de détails n’est pas un objectif sans fonction de silhouette, matière, composition ou lecture.
- Ne pas substituer une image générée au jeu réel pour prouver un progrès.
- Pour l’ancrage au sol, mesurer les vertices skinnés des semelles en repos et en mouvement dans le jeu et l’atelier. La hauteur de la cheville ne prouve pas le contact ; tenir compte de l’origine du modèle, du socle et des matrices de skin mises à jour comme au rendu.
- Pour les ombres, examiner les contacts et le mouvement. Pour les attaques, aligner intention, pose, trajectoire, dégâts, effets et son. Pour les menus, vérifier focus et méthode d’entrée autant que la disposition.
- Si une décision artistique nouvelle nécessite vraiment une réponse, poser une question précise et continuer le travail indépendant. La revue du résultat ne doit pas créer une approbation obligatoire supplémentaire pour les corrections déjà demandées.
