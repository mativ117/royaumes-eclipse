# Composition des environnements — passe 1.6

Cette passe applique les critères de hiérarchie spatiale, de fonction des lieux et de cohérence des matières à la géométrie jouable existante. Elle vise les trois chapitres ; elle ne change ni leurs routes, ni les objectifs, ni les volumes de collision. Elle ne constitue pas une refonte complète du level design ou une preuve de qualité AAA atteinte.

## Défauts traités

Les captures de la 1.5 montraient de grandes dalles brunes régulières, des fentes noires entre les plates-formes et des séries de colonnes/arcades très semblables. Les différences mécaniques des lieux étaient davantage portées par les indications que par leur construction visuelle.

`src/environment-direction-v16.js` ajoute une couche éditable et reproductible :

- **Cathédrale :** variations de pierre froide et passage processionnel plus clair dans le sol, lignes de métal intégrées au matériau, soubassements continus, profils sculptés dans les six empreintes de piliers du Cloître, mur extérieur et alcôves hors de ses allées. Deux drapés sur leurs mâts et des offrandes composent une trace humaine asymétrique autour de l’Atrium.
- **Jardin des noms :** terre/pierre plus végétale dans les zones latérales, chemin conservé plus clair, racines sculpturales et astrolabe dans l’eau centrale inaccessible. Les deux routes et leurs objets restent à leurs coordonnées d’origine.
- **Convoi :** vrai rôle de bois pour les cartes du pont, joints et usure intégrés au matériau, cargaisons et éléments de tension sur la coque hors des itinéraires, soubassements adaptés au chapitre. Les cargaisons ont été déplacées hors des épaules des escales : aucun nouvel accessoire traversable ne doit occuper le chemin.

Les vides délibérés restent des vides ou de l’eau. Les soubassements rendent les bords construits lisibles ; ils ne créent pas de sol praticable sur l’abîme. Les nouvelles parties décoratives ne projettent pas d’ombre de plafond. La géométrie et les informations de cheminement sont les mêmes en Haute et en Léger.

## Matières et fabrication

Les textures existantes gardent leur provenance. Les cartes photographiques Poly Haven CC0 sont créditées dans `assets/materials/LICENSE.md` ; les cartes bois/tissu procédurales restent celles du projet. Les parties sculptées et les surfaces sont produites par le module du projet, sans ressource copiée des jeux de référence.

Les UV de couleur, normale et rugosité suivent une même échelle de monde. Les faces latérales utilisent leur axe vertical : elles ne reçoivent pas la projection XZ aplatie du dessus. Les filets du sol sont calculés dans le shader plutôt qu’avec un plan superposé, pour éviter un nouveau conflit de profondeur. Le bronze garde sa réponse métallique et n’est pas recouvert de maçonnerie.

Les recettes distinguent les chapitres et restent regroupées en cinq lots décoratifs dans la Cathédrale, quatre dans le Jardin et quatre dans le Convoi. Ces chiffres sont une borne locale de dessin, pas une mesure de cadence sur téléphone.

## Intégration et cycle de vie

Appeler `initEnvironmentDirectionV16()` après `initPresentation()`, puis `updateEnvironmentDirectionV16(elapsed)` avant le rendu. `disposeEnvironmentDirectionV16()` restaure les matériaux/colonnes d’origine et libère les ressources propres au module.

Le changement de racine de chapitre, l’apparition du sol de l’escale secrète et une modification de la liste des surfaces entraînent une reconstruction propre. Le duel ne reçoit pas le décor des chapitres. Les textures originales partagées ne sont pas détruites par la suppression de cette couche.

## Contrôles effectués et limites

`python3 tests/environment_direction_v16.py` passe en CPU avec les classes Three.js réelles du dépôt :

- normales des fondations orientées vers l’extérieur et jonction sans fente flottante ; aucun mur sous un raccord de sol partagé ;
- attributs géométriques/UV finis, cartes de surface cohérentes, métal conservé, bois attribué au pont ;
- cargaisons élevées hors de l’union des régions praticables, y compris les escales ;
- empreintes de collision et données de navigation inchangées ;
- compilation des chaînes de shader contre les morceaux r160 présents, variation du carillon, reconstruction du sol secret, suppression et restauration sans destruction des cartes partagées.

Ce contrôle CPU assemble les sources de shader. À la clôture, les suites `direction_v16_integration` et `render_complete` ont aussi passé la compilation dans Chromium logiciel et les budgets Haute/Léger. Les trois captures après utilisent les mêmes cadrages que les vues avant ; les rapports conservent leurs empreintes. La lecture humaine des chemins, la qualité de la composition et la fluidité matérielle ne sont pas déduites de ce test.

Le référentiel de la comparaison reste `REFERENTIEL-QUALITE.md` : composition et récit environnemental, cohérence des surfaces et coût des objets Three.js r160. La méthode de [Sucker Punch pour le monde de Tsushima](https://blog.playstation.com/2020/07/09/crafting-the-world-of-tsushima/) guide la fonction des repères ; elle ne fournit pas les ressources de cette scène et n’autorise aucune affirmation de parité visuelle.
