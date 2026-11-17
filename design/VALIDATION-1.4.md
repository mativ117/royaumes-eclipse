# Validation 1.4-rc1 — mouvements, contacts et créature de référence

17 novembre 2026. Livraison Web PC/téléphone, sans serveur. Choix confirmé : aventure solo uniquement ; autres modes conservés dans les archives et module complet 1.3, exclus du menu et du bundle actuel.

## Modifications et vérifications exécutées

Suites passées : `retarget_assets`, `lame_motion_quality --integration`, `lame_transitions`, `stance_motion`, `blade_contacts`, `lame_attack_timing`, `predator_combat`, `creature_reference`, `reference_encounter`, `input_settings`, `hero_preview`, `hero_preview_real`, `modal_focus --integration`, `spatial_audio`, `story_sound`, `physics`, `complete_campaign`, `material_finish`, `render_complete`, `profiles`, `interaction_visibility` et `publication`.

- **Lame.** Sept actions adaptées des bibliothèques Quaternius Standard CC0 ; 23 actions conservées. Géométrie, UV et atlas PBR originaux vérifiés. Poids des pans, cape, prise et points de mesure de la lame repris. Les autres héros conservent leur production précédente.
- **Appuis.** Mélange continu marche/course, phase commune et contacts extraits des clips. Mesures sur GLB réel à 30/60/120 Hz : dérive maximale d’appui de 2,57 cm, dérive au cœur de l’appui inférieure à 1,70 cm, correction maximale de 11,48 cm. Les appuis abandonnés restent sous 1,85 %. À vitesse 5,5, environ 2,12 appuis/s ; le précédent contrôleur demandait mathématiquement 7,33 appuis/s. Ces nombres décrivent un scénario contrôlé, pas une note artistique.
- **Origine des bottes.** Un contrôle des vertices skinnés a révélé une marge de 2,5 cm sous le modèle au repos. Une enveloppe visuelle fixe corrige cette origine pour la Lame, sans modifier la racine animée ni accumuler un décalage. En garde : semelle gauche entre +0,27 et +0,50 cm, droite entre −0,92 et −0,56 cm. Le studio est ajusté séparément à son socle. Contacts de locomotion inchangés après correction.
- **Combat.** Trois attaques jouées à 1×, avec fenêtre active et balayage réel du sabre contre une capsule de corps. Un contact par cible, aucun dégât avant ou après la fenêtre, coups ratés en hauteur ou hors portée et obstacle réel vérifiés. Un intervalle trop court pour l’ancien contrôle de mur est désormais échantillonné aussi. La récupération rend les jambes au déplacement ; l’arrêt ne rejoue plus les jambes de préparation. Esquive Lame : 1,712 unité monde en 0,40 s.
- **Fauche-Cendre.** Premier quadrupède original : quatre membres articulés, 22 os, matériaux et textures intégrés. Préparation verrouillée de 0,78 s, charge de 2,4 unités sur 0,32 s et récupération de 1,4 s. Les avertissements ne causent pas de dégâts circulaires. Contact joueur unique vérifié. Le sabotage du cœur du Convoi est conservé : contact unique de 22 × 0,65 = 14,3 points d’intégrité, vérifié avec le socle et les obstacles du vrai niveau. Les ressources clonées sont libérées ; les anciennes pièces ne réapparaissent pas.
- **Son.** PCM réel : panoramique selon la caméra, atténuation par distance, master unique, silence exact à zéro, réverbération comprise. Pause et nettoyage, 16 voix courtes au maximum avec priorités, menace et impact distincts et pas liés aux appuis. La musique reste synthétique ; aucune écoute sur appareil physique ni bande-son enregistrée annoncée.
- **Interface.** Focus initial, Tab contenu, arrière-plan inerte et retour logique pour carte, pactes et choix. Carte fermable avec sa touche remappée depuis une case à cocher, sans voler la saisie ni les commandes natives. Dispositions PC et tactiles, messages près des stèles, occultations et commandes remappées vérifiés. La sélection 3D suspend/libère le rendu et se recrée au retour.
- **Contenu conservé.** Onze modèles et pouvoirs, dix héros ordinaires, secret, trois chapitres jusqu’à leur conclusion, anciennes reprises et import/export local. Matières et surfaces conservées. Rendus Haute/Légère et cartes contrôlés en desktop, portrait et paysage dans Chromium. Aucun test de durée humaine de partie déduit des parcours scriptés.

`tests/local_modes.py` annonce **SKIP** dans le bundle solo, conformément au choix utilisateur. Ce n’est pas une validation des modes archivés contre le moteur 1.4. Les snapshots 1.3 conservent leur propre moteur et leurs anciens modèles.

## Comparaison réelle

[Page de comparaison](../docs/gestes-et-creatures.html). Avant : commit `8f787ee328eb2396ee00da7067123159e22cdef5`, version 1.3-rc1. Après : candidate 1.4-rc1. Même séquence, caméra de jeu et décor existant, HUD masqué des deux côtés. Le contexte de quête, les collisions et les acteurs distants restent présents. La vidéo de créature emploie une caméra de revue trois-quarts, avec les positions et la charge réelles.

Export à 30 images/s, deux appels de simulation de 1/60 par image : les vidéos lisent le temps de jeu à 1×. Elles sont muettes et ne mesurent pas les performances d’un appareil. Les captures de l’atelier sont des rendus du modèle réel ; elles restent distinctes de la planche de conception.

Rapports : [mouvement et semelles](mesures/MOUVEMENT-1.4.json), [contacts des attaques](mesures/CONTACTS-1.4.json), [vidéos et empreintes](mesures/CAPTURES-1.4.json).

## Limites de cette validation

La cape conserve des plis rigides. Les anciens pas latéraux, les raccords brusques, la prise des doigts, les autres héros et les autres familles ennemies demandent leur propre production. La locomotion du quadrupède en jeu est procédurale avec appuis ; ses clips Blender servent à la revue. Les niveaux, leur rythme et leur narration n’ont pas été entièrement refaits. Le terrain reste horizontal ; Rapier est documenté comme piste, sans être ajouté au runtime.

Les essais Chromium avec WebGL logiciel ne valident ni les FPS, ni l’échauffement d’un téléphone physique. La cible artistique et le plaisir exigent encore des parties humaines. Cette livraison améliore une référence jouable ; elle n’est pas présentée comme une finition AAA.

## Paquet et publication

Le contrôle du paquet et le relevé distant sont consignés après leur exécution. Le ZIP conserve l’état de livraison avant l’ajout des preuves de publication.

HTML SHA-256 : `6d4a7102f33449fc16a5b5354c49336731f1e0cfeedcce13e523a492c5410085`.

Source intégrée SHA-256 : `6378000ed4fe62ffb818faaeda3c7c804e7087803bfb766d66155b4e9740d469`.

Lame GLB SHA-256 : `200c30d20d5ef4735f27871ebcd8165d95a8bedbf98a7cb3d3c23b43a72312f6`.

Fauche-Cendre GLB SHA-256 : `8e03fef66e9198fa786e567a1e5b976fb6fd5f648985d443148a84d35a9f91e7`.
