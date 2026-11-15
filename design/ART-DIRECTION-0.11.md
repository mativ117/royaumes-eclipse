# Direction artistique — 0.11 : le vent et les mémoires

## Direction choisie

Le 15 novembre 2026, le créateur du jeu a précisé une référence finale mêlant **Clair Obscur: Expedition 33** et **Ghost of Tsushima**. Cette direction remplace les indications plus générales de fantasy sombre ; le carillon, l’éclipse et les architectures impossibles restent propres aux Royaumes.

| Axe | Intention pour les Royaumes | Première traduction dans la 0.11 |
|---|---|---|
| Composition picturale | Grands volumes, clair-obscur, points de lumière conduisant le regard | Fenêtres monumentales, silhouettes de ruines, teintes de brume propres aux zones |
| Matières et objets | Pierre sombre, cuivre patiné, mécanismes dont on comprend l’usage | Sols plus fins, supports modelés, volant de vanne, fresque gravée, cage du noyau et armillaire |
| Nature vivante | Végétation en masses lisibles ; vent et tissus apportant le mouvement | Bosquet cuivré, herbes animées et mouvement discret de la cape |
| Guidage intégré | Assistance que le joueur appelle, sans course de flèches permanentes | Particules portées le long du chemin valide pendant la demande de repère |
| Interface | Informations essentielles près de l’action, détails consultables | Choix Épuré / Détaillé ; carte et journal conservés |

La palette visée associe obsidienne et ivoire patiné, cuivre, rouge végétal et bleus froids. Le mélange désigne une direction de composition et de matières. Ce n’est ni une reproduction des lieux ou personnages de ces jeux, ni une déclaration d’équivalence de rendu.

## Références consultées

- [Entretien avec Tom Guillermin, Sandfall Interactive — Inside the development journey of Clair Obscur: Expedition 33](https://www.unrealengine.com/developer-interviews/inside-the-development-journey-of-clair-obscur-expedition-33), 27 mars 2025. L’équipe évoque les références Belle Époque et Art déco ainsi que la composition et l’éclairage. Cette source sert de référence artistique ; le prototype des Royaumes reste un jeu Three.js pour navigateur, sans Unreal.
- [Joanna Wang, Sucker Punch — Crafting the world of Tsushima](https://blog.playstation.com/2020/07/09/crafting-the-world-of-tsushima/), 9 juillet 2020. La direction environnementale met en relation nature et constructions, palette volontaire et mouvement du vent dans le paysage. Les choix des Royaumes dans le tableau sont notre interprétation de ces principes.

Aucun modèle, image, texture ou son de ces jeux n’est intégré au projet. Les modèles et textures de cette version sont créés par les sources locales du jeu.

## Ce qui change effectivement

`src/art-direction.js` crée des supports d’objets propres à leur fonction, des portes à deux vantaux animés, un sol à dalles plus fines, un bosquet à feuillage, des herbes animées et de nouvelles silhouettes architecturales en bordure du parcours. Les acteurs reçoivent des ombres de contact simplifiées ; ce ne sont pas des ombres physiques complètes.

Le mode Épuré est activé par défaut, avec un choix Détaillé dans le menu. La préférence est locale, séparée de la sauvegarde du niveau. Les actions immédiates, les PV et les commandes restent présents ; la progression détaillée se consulte dans la carte. Il ne s’agit pas d’un mode sans interface.

Le guidage utilise toujours le chemin praticable de la 0.10. Pendant les sept secondes demandées par le joueur, des particules lentes le suivent près du personnage. Les herbes et la cape réagissent au vent. Les particules ne remplacent pas les collisions et ne révèlent pas le secret.

La vanne tourne quand elle est fermée ; les objets réagissent brièvement à l’interaction et le héros accompagne le geste. Ces animations servent de retour visuel ; elles ne retardent pas artificiellement la validation de la quête. Les sauvegardes 0.9/0.10 restent lisibles et les épreuves du niveau sont conservées.

## Coût et vérifications

Les herbes, feuilles, ombres et particules utilisent des instances. Les nouvelles portes remplacent leurs anciennes barres séparées par deux géométries partagées. Le mode Léger retire la végétation et les détails coûteux ; les objets, les interactions et le guidage restent disponibles.

`tests/art_direction.py` vérifie compilation du shader de végétation, états des portes, pose d’interaction, demande du vent, ambiances, stabilité des géométries après reprise et budget d’appels de rendu. Les suites du scénario, de guidage, de lisibilité, de multitouch et de publication complètent ces vérifications. Le mobile reste simulé dans Chromium.

## Production encore nécessaire

Cette version pose la direction dans le niveau réellement jouable. Elle ne livre pas encore les visages, costumes, décors sculptés, squelettes et animations définitifs. Le chantier artistique suivant doit approfondir une séquence représentative avec ces assets et la tester sur téléphone réel avant de généraliser le traitement aux trois grands niveaux.
