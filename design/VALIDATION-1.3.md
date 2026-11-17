# Validation 1.3-rc1 — atelier intégré, proportions et matières

Le 17 novembre 2026. Choix conservés : accès Web PC/téléphone, sans serveur, première refonte artistique centrée sur la Lame.

## Vérifications locales

Suites passées : material_finish, hero_preview, hero_preview_real, lame_attack_timing, lame_transitions, animation_layers, stance_motion, input_settings, physics, interaction_visibility, complete_campaign, local_modes, profiles, publication, render_complete, presentation, lame_reference et package_release.

- Atelier réel intégré : changements rapides Rempart → Lame → Voltigeur → Lame, geste d’attaque, origine/source des messages, personnage secret, pause hors vue, absence de rendu parent pendant l’aperçu, destruction au lancement et recréation au retour. Galerie PC et mobile sans recouvrement ; sélection et jeu conservés dans le snapshot autonome. Identifiants hérités comme `constructor` refusés et URL invalide ramenée au Rempart.
- Atlas du vrai GLB conservés, dont Oiled leather : couleur, normales, ORM et valeurs de matériau restent identiques après leur préparation dans le jeu. Les six cartes photographiques sont décodées avant le déblocage du démarrage ; les clones reçoivent bien les images finales. Bois, tissu et métal ne reçoivent pas la maçonnerie par erreur.
- Géométrie Lame révisée, squelette et données des 23 clips conservés. Départ/arrêt/pivot interrompables, répétition des pivots, phase marche/course maintenue. Appuis des onze héros mesurés ; dérive tardive en appui inférieure à 5 cm dans le scénario contrôlé.
- Attaques Lame : durée égale aux clips, lecture à vitesse 1, aucun dégât avant le contact, un seul contact par attaque et fin de récupération. Rythme des classes ordinaires conservé. L’équilibrage humain de ce nouveau rythme reste ouvert.
- Finition de bordures, fondations, Archives, forge et abîme ; UV des surfaces fusionnées et données de collision/navigation vérifiés. Les nouvelles décorations ne changent pas les routes.
- Trois chapitres, fins, secret, onze pouvoirs/modèles, modes locaux, sauvegardes/import/export, commandes remappées et interactions conservés. Rendus Haute/Légère vérifiés en desktop, portrait et paysage dans Chromium. Budget de rendu des chapitres II/III conservé ; captures contrôlées : Atrium 510 appels, Archives 61, forge 80, jardin 116, convoi 140. Il ne s’agit pas d’une mesure de FPS sur téléphone.
- Build reproductible, anciennes URL et requêtes préservées ; archives antérieures inchangées, paquet déterministe et snapshot autonome avec onze modèles.

Les captures de `docs/previews/r3-*` sont des rendus du moteur à des positions contrôlées, sans retouche. Les essais tactiles/manettes sont simulés dans Chromium. Ils ne constituent ni une validation iPhone physique, ni une partie humaine de 10–15 minutes, ni une validation artistique du rendu demandé. La Lame reste plus simple que sa planche ; les autres héros et l’anatomie des ennemis restent provisoires.

HTML SHA-256 : `4ab2e8c99d4b57d4788347ad008c6a9038d084b30d923e8bf504bd1d77440131`.
Source intégrée SHA-256 : `0bf13149f2f0806e195a5f824c5c725b43b6fdf16e3b9333e06c0744748aced7`.
Lame GLB SHA-256 : `0df1360b65020c33ae6eebcb623070ad37e6eef5617d5bbf48822c2f2d0e1b38`.

La publication distante est relevée ensuite. Le ZIP conserve les fichiers validés avant ce relevé.

## Publication confirmée

GitHub Pages a servi le commit `d855bbdbc082664ad0e759532ff942962679a7d0`. Le HTML, les onze modèles, l’atelier, le concept, les captures et le ZIP correspondent aux fichiers de livraison. Les trois contrôles publics passent : atelier intégré et changements de héros ; atelier séparé et démarrage de la Lame ; Tisseuse et chapitre II avec récit et audio. Aucun fichier manquant ni erreur JavaScript constaté dans ces parcours.

Voir [PUBLICATION-1.3.json](PUBLICATION-1.3.json). Le relevé et les ajustements des scripts de contrôle public sont ajoutés après la livraison ; le ZIP conserve le paquet validé et son empreinte initiale.
