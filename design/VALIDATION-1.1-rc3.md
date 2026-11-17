# Validation du correctif 1.1-rc3

Contrôles du 17 novembre 2026. Suites passées : interaction_visibility, stance_motion, animation_layers, physics, sanctuary, complete_campaign et publication. Les tests du message et de l’interface ont aussi été rendus en portrait et paysage après correction.

- Lecture de la fresque par vrai tap depuis quatre approches ; message visible malgré la présence du bouton.
- Lanterne la plus proche et anneau de cible cohérents ; indice conservé à proximité après lecture.
- Atténuation des objets/colonnes qui cachent le héros ; nettoyage de la liste lors des nouvelles parties.
- Onze modèles, deux vitesses et quatre directions : dérive d’appui inférieure à 5 cm dans le test contrôlé. Il reste jusqu’à environ 4,4 cm sur le Néant ; le correctif n’est pas une validation qualitative de l’animation.
- Collisions, couches de tir/marche, prise de l’arme, progression des chapitres et publication compatibles.

Aucun résultat de test n’est présenté comme une mesure de fluidité sur téléphone physique. Le but qualitatif reste décrit dans [SEQUENCE-REFERENCE.md](SEQUENCE-REFERENCE.md).

HTML SHA-256 : `be114355da93ceded6b0ed100601c00b2782d0bcdd0295ab54a1679d5fd1b7a6`.
Sources intégrées SHA-256 : `c765eb3808ec907fd5c20da34143b1221bd8670019fda47a69993800871d7745`.

L’archive complète est produite et vérifiée par package_release. La publication distante est contrôlée ensuite par verify_live et smoke_live.
