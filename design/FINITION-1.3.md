# Atelier, silhouette et matières — 1.3-rc1

Cette passe répond aux proportions de poupée et aux zones vides ou sans textures signalées dans le jeu et dans l’atelier. Elle conserve les trois chapitres, les profils, les modes locaux et le choix Web PC/téléphone sans serveur. La qualité visuelle finale demandée reste l’objectif de production.

## Sélection des personnages

L’atelier est intégré au menu de sélection. Le personnage choisi apparaît dans une scène 3D réelle, avec rotation, choix d’un geste et réglage graphique. Le chargement est différé jusqu’à l’approche de l’aperçu. Le rendu d’arrière-plan du jeu est suspendu pendant la consultation ; l’atelier se suspend hors vue et se libère au début de la partie. L’adresse séparée de l’atelier est conservée.

Les modèles réels des classes sont utilisés. La Lame est la première refonte détaillée ; les dix autres gardent leurs modèles provisoires. L’aperçu respecte le déverrouillage local du personnage secret. Les profils locaux et l’export/import restent indépendants de cet aperçu.

## Seconde production de la Lame

Les proportions visent une adulte élancée : environ 7,34 longueurs de tête, tête plus petite, épaules moins gonflées, mains et bottes affinées, pans de vêtement plus longs et moins réguliers. Le masque minéral, les mèches et le col sont retravaillés. Le costume reste sombre et asymétrique. La géométrie change ; le squelette et les 23 clips sont conservés.

Départ, arrêt et pivots peuvent être interrompus lorsque le déplacement réel change. Marche, course et pas orientés conservent leur phase. Les attaques de la Lame utilisent la durée de leurs clips, environ 0,65/0,65/0,90 seconde, plutôt que la lecture accélérée précédente. Les contacts gardent leurs fractions de progression. Les autres héros gardent leur rythme antérieur ; l’équilibrage de la Lame demande une nouvelle revue en partie.

Un défaut de matériau est corrigé : la carte de cuir intégrée au GLB était remplacée par le tissu générique. Les cartes PBR déjà présentes sur le modèle sont désormais préservées. La silhouette, les vêtements, la coiffure et les déformations restent plus simples que la planche approuvée.

## Matières et composition du décor

Deux matières photographiques [Poly Haven](https://polyhaven.com/) sont adaptées en six cartes 512 × 512 : couleur, normale et rugosité pour les dalles du sol et la maçonnerie. Elles sont embarquées dans le site, avec leurs auteurs et empreintes dans [PROVENANCE.json](../assets/materials/PROVENANCE.json). Les teintes propres aux zones de la Cathédrale sont conservées. Le bois et les bannières gardent leurs familles de matières. Les surfaces du jeu et de l’atelier attendent leur préparation avant l’affichage du modèle. Les surfaces fusionnées qui n’avaient pas d’UV en reçoivent une projection.

Dans la Cathédrale, des bordures et supports encadrent les bords exposés des plates-formes. Des niches et tablettes composent le fond des Archives ; des cheminées et colliers complètent les fours de la forge. Ces ajouts occupent les limites extérieures ou les empreintes déjà solides des fours. Les chemins, objectifs et collisions ne sont pas modifiés par cette passe.

Dans l’atelier, un socle dallé, une bordure métallique et une maçonnerie en retrait donnent un contexte au personnage. Les deux réglages graphiques restent disponibles. Cette composition ne représente pas un nouveau niveau de jeu.

## Outils et suite

Blender 4.3 est déjà utilisable ici. Poly Haven fournit ces matières sous CC0. Mixamo reste une option de fichiers FBX exportés depuis un compte Adobe gratuit, sans connecteur direct vérifié ; aucun clip Mixamo n’est livré dans cette passe. Voir [les outils et leurs limites](OUTILS-PRODUCTION-3D.md).

La refonte des dix autres héros, l’anatomie des créatures, les contacts et transitions de combat, la composition de toutes les zones, le rythme des rencontres et les essais sur téléphone physique restent ouverts. La cible de 10–15 minutes par chapitre et la qualité finale doivent être évaluées en parties humaines. Les résultats des tests et de la publication sont consignés séparément après leur exécution.

## Captures de cette passe

Ces images viennent du moteur réel à des positions contrôlées, sans retouche. Elles servent à la revue de la silhouette et des matières ; elles ne prouvent pas le rythme d’une partie.

- [Sélection avec l’atelier intégré](../docs/previews/r3-selection.jpg) et [atelier séparé](../docs/previews/r3-lame-atelier.jpg).
- [Atrium](../docs/previews/r3-atrium.jpg), [Archives](../docs/previews/r3-archives.jpg), [forge](../docs/previews/r3-forge.jpg), [jardin](../docs/previews/r3-jardin.jpg), [convoi](../docs/previews/r3-convoi.jpg).
