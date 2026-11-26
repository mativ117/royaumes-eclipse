# Prise en charge de la qualité — candidate 1.6

Production du 24 novembre et clôture du 26 novembre 2026. La base publiée et vérifiée est la [1.5-rc1](VALIDATION-1.5.md). La nouvelle demande vise une amélioration visible fondée sur la [comparaison aux références](COMPARAISON-AAA-1.6.md). Les ressources et modules sont intégrés dans la 1.6 ; les contrôles réellement passés figurent dans [la validation](VALIDATION-1.6.md). Les critères du tableau conservent aussi les exigences de revue humaine et matérielle encore ouvertes.

| Axe | Fabrication ou code de la passe | Preuve requise avant clôture | Extension restant à produire |
|---|---|---|---|
| Archer original | `assets/creatures/archer-thorn.glb`, source Blender et provenance ; anatomie asymétrique avec bras-arc et jambes digitigrades. | Modèle réellement chargé, matières décodées, squelette et clips finis ; canon orienté, préparation et émission au temps source, couvert et récupération. | Réactions, déformations et contre-jeu à éprouver en parties ; autres familles à traiter. |
| Raie du reflet | `assets/creatures/shade-manta.glb`, source Blender et provenance ; tête, mandibules, membrane et ailes articulées. | Silhouette distincte, phase/exposition compréhensibles, attaque réelle ; repli/volume visuel compatibles avec les obstacles et les seuils. | Rencontre, rythme, variantes et finition des ailes à éprouver. |
| Intégration des deux familles | Module dédié intégré : chargement, clone, pose, IA, réaction et nettoyage, avec conservation de Fauche-Cendre. | Pas de double IA/dégât ni d’ancien mannequin visible ; temps stables à 30/60/120 Hz, source de projectile réelle, refus des murs/portes et nettoyage des ressources. | Navigation et comportement des familles restantes et des boss. |
| Sols et architecture | `src/environment-direction-v16.js` : UV mondiales, matières par usage, incrustations sans plan coplanaire et soubassements. | Trois vues après aux mêmes conditions que [les vues avant](CAPTURES-DIRECTION-1.6-before.json), shader Haute/Léger, aire praticable et colliders inchangés, budget et cycle de vie. | Composition de toutes les zones, relief, fonctions des lieux, détours et rythme humain. |
| Identité des chapitres | Composition propre à la Cathédrale, à la Chasse et au Convoi, intégrée aux espaces existants. | Aucun ajout décoratif élevé sur un chemin ; repères utiles conservés, matériaux bois/métal/pierre cohérents et absence de plafond fantôme. | Conséquences narratives et séquences de découverte à composer dans chaque niveau. |
| Caméra de rencontre | `src/camera-direction-v16.js` : rapprochement progressif en solo et maintien du cadrage de groupe. | Séquence à 1×, stabilité de cible, entrée/sortie du combat, obstacles, UI et portrait/paysage ; pas de changement arbitraire de visée ou de déplacement. | Confort et situations limites à essayer sur appareils physiques. |
| Musique et avertissements | Module de présentation intégré : score adaptatif et sons d’arc, de révélation et d’impact. | PCM/écoute, absence de saturation, master/mute/pause et limites de voix préservés ; avertissement localisé et également visible. | Timbres, mix, répertoire des autres créatures et armes, puis écoute sur appareils. |
| Récit de rencontre | Présentation contextuelle courte intégrée, sans pause imposée ni nouveau panneau de progression. | Déclenchement pertinent, texte lisible, passage unique, effacement hors jeu et absence de chevauchement avec carte, commandes et interactions. | Dialogues, scènes incarnées et conséquences sur l’ensemble de l’histoire. |
| Héros et combat existants | Onze modèles et kits 1.5 conservés ; contacts et timing source restent la base. | Régressions appropriées de mouvement, contacts, pouvoirs et anciennes reprises ; ne pas annoncer des gestes entièrement neufs pour les héros. | Pas orientés, esquives, drapés et personnalité de mouvement propres aux onze héros. |
| Modes, sécurité et sauvegarde | Aventure, bot local et LAN expérimental 1.5 conservés ; aucune API de jeu ajoutée. | Sélection/lancement/retour, sauvegardes, secret, rôles réseau et chargements ; CSP et modèle autonome si la livraison l’inclut. | LAN natif entre téléphones et sécurité sur les appareils/réseaux visés ; hôte non considéré comme digne de confiance. |
| Mesure et publication | Sources, fabrication reproductible, captures du moteur et archives distinctes. | Build reproductible, tests réellement exécutés, intégrité des anciennes versions, paquet sous la limite retenue, publication puis vérification distante. | Mesures matérielles, compréhension novice, plaisir et cible de durée humaine. |

## Contrats de ressource et limites

Les modèles finaux doivent exposer leur orientation, les clips effectivement exportés, leurs durées et événements ainsi que les sockets utilisés par le runtime. Les métadonnées doivent correspondre aux données GLB. Une animation échantillonnée à une cadence différente de celle de l’export ne doit pas être acceptée sur la seule base du nom du clip.

Les détails visuels restent privilégiés avec un réglage Léger. Les trois chapitres, les dix héros ordinaires, le personnage secret, les profils locaux, l’import/export et les archives restent dans le périmètre. Les ajouts d’architecture ne prétendent pas produire des pentes, escaliers ou corps rigides parcourables.

Les sources 3D et sons de cette passe sont des productions originales. Les références de jeu guident la fabrication et la revue ; leurs personnages, musiques et ressources ne sont pas repris. La [comparaison](COMPARAISON-AAA-1.6.md) indique les sources primaires et la portée exacte de leur consultation.

## État des preuves

Les relevés avant et après existent pour trois vues réelles des builds 1.5 et 1.6, avec HUD masqué et qualité Légère. Les contrôles propres à la 1.6 et les limites sont consignés dans la validation. Les résultats 1.5 restent des preuves de cette base ; ils ne valident pas automatiquement les nouveaux modèles, shaders, comportements, sons ou cadrages.

Pour chaque vérification, conserver le résultat réel : réussite, défaut ou saut avec raison. Les tests GPU sont successifs dans cet environnement. Les images fixes et le WebGL logiciel ne prouvent ni la qualité d’une animation à vitesse normale, ni l’écoute, ni les performances d’un téléphone.

## Documents de continuité

- [Exigence sur l’ensemble du jeu](EXIGENCE-QUALITE.md), [suivi](SUIVI.md) et [couverture](COUVERTURE-QUALITE.md).
- [Comparaison et critères de cette passe](COMPARAISON-AAA-1.6.md).
- [Validation de la base 1.5](VALIDATION-1.5.md), [modes](MODES-1.5.md), [limites du LAN](LAN-TELEPHONES-1.5.md).
- [Référentiel](REFERENTIEL-QUALITE.md), [workflow](WORKFLOW-QUALITE.md) et [procédure locale](skills/quality-pass/SKILL.md).
