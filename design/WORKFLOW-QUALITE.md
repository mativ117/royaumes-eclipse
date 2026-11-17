# Workflow de qualité du projet

Ce workflow transforme les références en modifications vérifiables. Il conserve les connaissances dans le dépôt et accompagne [le référentiel](REFERENTIEL-QUALITE.md). Il ne constitue pas une formation permanente du modèle. Le [skill local du projet](skills/quality-pass/SKILL.md) décrit la procédure réutilisable par un agent qui le lit.

## 1. Définir une séquence et un défaut

Choisir une séquence représentative de deux à trois minutes, un personnage et une rencontre. Noter le commit, les appareils visés, le cadrage et le problème vu par le joueur : glissement, menace illisible, orientation perdue, interface masquée, matériau incohérent, impact sans poids. Séparer ce défaut d’une demande générale de « plus de détails ».

Conserver les contraintes déjà décidées : navigateur PC/téléphone, absence de serveur, réglage léger, dix héros disponibles et un secret, sauvegardes compatibles. La direction approuvée de la Lame reste la référence du premier personnage ; une nouvelle question n’est utile que si un choix réellement nouveau ne peut pas être résolu avec le contexte disponible.

## 2. Chercher la source qui répond au défaut

Prioriser documentation officielle de la version utilisée, conférence de praticien ou recommandation spécialisée accessible. Lire la partie utile, consigner titre, auteur/version, URL, date, point retenu et limite d’application. Distinguer un résumé officiel d’une conférence visionnée. Ne pas recopier une recette de moteur comme si elle s’appliquait sans adaptation à Three.js.

Pour un asset externe, enregistrer sa source, licence, auteur, modifications et empreinte. Pour un outil distant, vérifier disponibilité, capacité, confidentialité et éventuel coût avant de le considérer comme utilisé. Le pipeline actuel peut déjà produire avec Blender et des ressources CC0 ; un abonnement ou une migration n’est pas implicite.

## 3. Auditer dans le code et capturer avant

Relier chaque défaut à son propriétaire : asset Blender/GLB, contrôleur, collision, caméra, matériau, rendu, son ou DOM. Les corrections d’un shader ne réparent pas une silhouette ; une texture de briques ne convient pas à tous les objets.

Capturer une pose et une courte séquence réelle, depuis le moteur, à vitesse 1× et avec entrées identiques. Noter résolution, qualité et version. Les concepts générés restent étiquetés comme concepts ; ne pas les substituer à une preuve du rendu réel. Mesurer seulement ce qui aide à juger le défaut : dérive du pied, fenêtre de contact, superposition, crête audio, temps d’image ou ressource non libérée.

## 4. Produire puis intégrer une référence

Modifier une ressource ou un système avec une hypothèse claire. Pour un personnage : silhouette → pose → UV/matières → rig/déformations → locomotion → contact de combat → effets/son. Pour un niveau : fonction → parcours → séquence d’événements → composition → matières/lumière → signes et rythme. Pour le son : rôle → timbre → contact → distance → mix et contrôle utilisateur.

Conserver une source éditable et un export reproductible. Vérifier l’asset avant son intégration, puis dans le jeu : les cartes, axes, durées, échelles et prises peuvent être altérés par le runtime. Tester solo et acteur cloné si les deux chemins sont concernés. Éviter de multiplier les héros ou créatures à partir d’une référence encore faible.

## 5. Comparer à vitesse normale

Refaire exactement la séquence. Examiner d’abord à 1×, puis ralentir seulement pour diagnostiquer. Comparer avant/après dans la caméra de jeu, avec le son normal et une passe son coupé ; consulter aussi l’atelier sous lumière de revue. Vérifier que le gain reste lisible sur téléphone et n’ajoute pas un autre défaut.

La revue humaine répond à des questions concrètes : « le pied accroche-t-il ? », « le joueur voit-il l’ouverture ? », « cette zone raconte-t-elle son usage ? », « l’impact arrive-t-il au contact ? ». Une capture séduisante ou une note technique ne clôt pas cette revue. Une partie novice est nécessaire pour navigation, compréhension, rythme et durée de niveau.

## 6. Vérifier les invariants et le budget

Exécuter les contrôles appropriés au changement : textures/rig/clips, interactions/collisions, profils et anciennes reprises, quêtes, entrées, UI modale, chargement/libération, rendu Haute/Léger. Une correction purement documentaire ne demande pas une nouvelle campagne de tests GPU. Ne pas ajouter de tests qui ne font que recopier une constante de l’implémentation.

Le lancement 1.4 est solo. Vérifier que le menu et le bundle n’incluent pas les groupes/arènes/bots retirés ; garder le module complet et les archives 1.3. Les ennemis et boss conservent leur IA locale. Les tests historiques des modes locaux ne sont pertinents que si leur code est modifié ou réintroduit, et ne doivent pas les faire réapparaître par accident dans le produit courant.

Les tests navigateur GPU sont séquentiels dans cet environnement. Capturer les erreurs JavaScript, fichiers absents et ressources GL. Répéter les cycles concernés jusqu’à stabilisation des ressources ; ne pas confondre un cache initial qui se remplit avec une fuite. Pour la fluidité finale, profiler un PC et un téléphone identifiés, avec durée, échauffement, résolution et p95/p99. Les essais Chromium simulés ne prouvent pas un débit sur iPhone.

## 7. Livrer et conserver les connaissances

Consigner problème, changement, sources, artefacts, tests réellement passés et limites restantes. Mettre à jour le référentiel si une règle a été invalidée par la mesure. Préserver les archives antérieures ; construire la nouvelle version, son snapshot et son ZIP, puis contrôler la version effectivement servie en ligne lorsque la publication est autorisée.

Le rapport final sépare : **amélioration produite**, **vérification technique**, **revue artistique ou appareil encore à faire**. Ne pas qualifier le rendu de final ou de niveau AAA tant que cette appréciation n’est pas établie. L’objectif est un résultat qui progresse dans le jeu, avec des preuves, pas une accumulation de recommandations.

## Fiche courte à utiliser pour chaque passe

```text
Défaut observé / séquence :
Commit et appareil(s) / résolution / qualité :
Source consultée / version / date / limite :
Hypothèse et fichiers responsables :
Critère perceptible à 1× :
Mesure technique et budget à vérifier :
Asset source / export / licence / empreinte :
Comparaison avant-après réelle :
Régressions exécutées et résultats :
Limites et prochain défaut prioritaire :
```
