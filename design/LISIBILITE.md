# Lisibilité : recherche et application 0.9.1

Recherche effectuée le 12 novembre 2026. Ces références sont des recommandations de conception, pas une certification de conformité du prototype.

## Références retenues

- [Xbox Accessibility Guideline 109 — Objective clarity](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109) : garder objectifs, progression et prochaines actions consultables ; proposer des repères désactivables. Application : objectif suivi, journal de carte, états des objets de quête et rappel de la mélodie apprise.
- [Xbox Accessibility Guideline 103 — Additional channels](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/103) : doubler la couleur par des symboles, formes et mots. Application : silhouettes propres aux objets, flèche du joueur, croix des refuges, triangles des menaces et libellés explicites.
- [Xbox Accessibility Guideline 102 — Contrast](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/102) : contraste suffisant entre information et fond, notamment pour les textes de petite taille. Application : panneaux sombres presque opaques, textes clairs, bords de chemin séparés du vide. Le contraste des principaux couples de couleurs est vérifié ; une évaluation complète de toute la scène reste à faire.
- [Game Accessibility Guidelines — Interactive elements](https://gameaccessibilityguidelines.com/give-a-clear-indication-that-interactive-elements-are-interactive/) : rendre l’interactivité perceptible et cohérente. Application : halo de proximité, action contextuelle explicite, objets consommés atténués et étiquettes proches seulement.
- [Riot Games — Clarity in League](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/) : hiérarchie visuelle, silhouettes reconnaissables et limitation du bruit. Application : moins de grandes étiquettes simultanées ; un objectif suivi prioritaire ; indications de navigation distinctes des dangers. Le combat n’a pas été rééquilibré dans cette version.

## Diagnostic de la 0.9

La carte représentait principalement le sol, des points colorés et une légende sommaire. Les murs et portes étaient absents. Beaucoup d’objets de quête utilisaient le même cristal sur le même socle. Les actions immédiates étaient noyées dans la progression générale ; plusieurs aides contextuelles étaient calculées mais masquées par la feuille de style. La mini-carte était trop petite pour porter seule la navigation, notamment sur téléphone.

## Changements livrés

- Carte orientée au nord, noms des huit zones, murs/obstacles, portes actuellement fermées, flèche du joueur, repères typés et légende.
- Journal donnant les prochaines actions disponibles, avec choix de l’objectif suivi. Les quêtes terminées sont consultables dans la progression.
- États textuels des empreintes, de la lentille et du noyau. La mélodie n’est affichée qu’après lecture de la fresque.
- Guidage facultatif : chemin sur la carte et quatre repères au sol. Il suit le sol praticable et respecte les portes, avec marge autour des obstacles. Les dangers temporaires ne sont pas inclus : le joueur doit toujours lire les attaques.
- Silhouettes : volant pour les vannes, plaque pour la fresque, anneau pour la lentille, polyèdre pour le noyau, arche pour le rituel, balise pour le refuge. La couleur complète ces formes.
- Libellés 3D limités à courte portée ; objets terminés atténués ; anneau près de l’objet que le joueur approche.
- HUD recentré sur un objectif et sa prochaine action. Les détails moins urgents restent dans la carte sur téléphone.

Les sauvegardes 0.9 restent compatibles. Le choix de guidage est une préférence locale séparée ; il ne modifie ni les épreuves ni les combats.

## Vérification et prochaines étapes

`tests/readability.py` couvre chemins praticables, portes, sélection et mise à jour des objectifs, états d’objets, formes distinctes et carte défilable sur mobile. Les suites de mission, multitouch et publication restent utilisées. Les essais de téléphone sont simulés dans Chromium.

Pour le look final, poursuivre la différenciation des ennemis par silhouette, les décors propres à chaque zone, l’accord entre effets et zones de dégâts et des réglages de taille du texte. Une partie observée sur téléphone réel doit mesurer les hésitations : où le joueur s’arrête, quel objet il confond, et s’il comprend la prochaine action sans assistance orale. Le pourcentage d’avancement artistique reste une appréciation, pas une mesure vérifiée.
