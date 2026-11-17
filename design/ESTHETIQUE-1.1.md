# Ambre et obsidienne — 1.1-rc2

Les images transmises deviennent la référence principale : aplats noirs, dunes striées, soleil immense, silhouettes drapées et échelle monumentale. Expédition 33 et Ghost of Tsushima restent des références de sensation et de mouvement ; le paysage et la palette suivent désormais cette direction fantastique désertique.

## Changements présents dans le moteur

- Ciel dégradé sombre et disque solaire texturé, silhouette serpentine lointaine, dunes de fond avec relief et stries. Ces formes ne sont pas des créatures interactives ni du terrain parcourable.
- Éclairage en contre-jour, environnement réfléchi précalculé, ombres projetées conservées et stabilisées autour du joueur.
- Pierre, bois, sable et textile avec couleur, normales et rugosité procédurales. La Cathédrale conserve son bassin ; les sols de la Chasse et les ponts du Convoi gardent des matières distinctes.
- Rendu intermédiaire HDR lorsque disponible, halo des hautes lumières, composition et traitement des contours. Le réglage Léger utilise le rendu direct et conserve le choix antérieur de désactiver les ombres projetées et le miroir.
- Onze modèles régénérés avec UV et capes plus longues, plis plus nombreux et animation des extrémités. Inclinaison du buste lors des accélérations ; maintien de la marche pendant les réactions aux coups ; prise du fusil calée sur la direction réelle de l’attaque.
- Manteaux et yeux bleus pour les gardiens, sans supprimer les armes ni les indices des rôles. Chute et disparition progressive après une défaite ; matériaux temporaires libérés.

## Cohérence et limites

Le joueur doit distinguer les ennemis, les objets, les passages et les annonces de danger. Les couleurs cyan/violet et les contours d’interaction sont donc conservés malgré la dominante ambre. Les références sont traduites en géométrie et en lumière dans le jeu ; aucune image de concept ne remplace le niveau.

Les captures comparatives sont issues du moteur, avec le même héros, la même position et la même caméra. Les annonces temporaires sont masquées pour la comparaison. Elles se trouvent sur `docs/ambre-obsidienne.html`. Le script `scripts/capture_presentation.py` permet de les reproduire.

Cette passe n’atteint pas encore le détail des images ni une finition AAA. Les personnages restent des modèles stylisés procéduraux, le tissu n’a pas de simulation physique, le relief des dunes est décoratif et les appuis sont adaptés à un sol plat. Les animations, les proportions du décor et la qualité réelle sur téléphone restent à revoir en parties humaines.

## Contenu conservé

Trois chapitres complets, dix héros et le secret, coopération et battle locaux, profils locaux et export/import, reprise aux ancres et archives précédentes. Aucun serveur, compte distant ou mode réseau ajouté. La durée de 10–15 minutes reste une cible à mesurer.
