# Suivi courant — candidate 1.7-rc1

26 novembre 2026 : correction ciblée après critique des silhouettes et des impacts de la 1.6. Trois sculptures reprises dans leurs sources Blender ; temps, squelettes, gabarits et onze héros conservés. Contacts directionnels fondés sur la perte réelle de PV, traces de sockets en fenêtre active, petites pointes ennemies, nettoyage et effets réduits. Le LAN invité lit uniquement les PV autoritaires et affiche un accent neutre.

Huit suites finales, le contrôle des quatre appuis et le paquet déterministe passent ; captures et vidéo de coups infligeant réellement 160 PV enregistrées. Publication en cours. Les résultats sont consignés dans [VALIDATION-1.7.md](VALIDATION-1.7.md). La cible AAA globale, les autres familles/boss, les animations complètes des héros et les essais matériels restent ouverts. Les validations suivantes sont historiques.

# Suivi courant — candidate 1.6-rc1

Clôture du 26 novembre 2026 : huit suites finales et le paquet déterministe passent ; captures réelles actualisées. La 1.6 est publiée et vérifiée : HTML, onze héros, trois créatures, six captures et ZIP identiques ; aventure, atelier, duel bot et lobby LAN non appairé passent sur le site public. Le [relevé distant](PUBLICATION-1.6.json) consigne le code `c3e12a5` et le workflow réussi. La [comparaison AAA](COMPARAISON-AAA-1.6.md) motive cette passe ; la [matrice](PRISE-EN-CHARGE-1.6.md) et la [validation](VALIDATION-1.6.md) distinguent production, essais et limites.

- Deux créatures originales intégrées : Veilleur des fils et Raie du reflet, avec clips, PBR, sources Blender, comportements et collisions propres.
- Composition et matières des trois chapitres, caméra solo cadrant les deux corps et éclairage de lecture repris.
- Trois partitions synthétiques adaptatives, quatre effets de créature et présentations narratives courtes intégrés.
- Onze héros, trois chapitres, profils, anciennes reprises et duels conservés. Le LAN natif entre téléphones reste à valider ; aucune preuve en mémoire n'est annoncée comme connexion réelle.
- La cible AAA du jeu entier demeure ouverte : autres familles et boss, animation complète des héros, relief et composition détaillée, présentation narrative, timbres/mix, équilibrage et mesures physiques.

Les relevés ci-dessous restent historiques ; leurs versions et limites ne décrivent pas automatiquement la livraison courante.

# Suivi du projet — candidate 1.5-rc1

**État de reprise au 24 novembre 2026 :** candidate 1.5-rc1 publiée et vérifiée sur GitHub Pages. Contrôles locaux, captures réelles et paquet réussis. La 1.5 réunit les dix nouvelles fabrications de héros, la reprise du contrôle en combat, les portes et sols corrigés, un duel tactique sans API et un module LAN direct. Les résultats et limites figurent dans [la validation 1.5](VALIDATION-1.5.md). Le [relevé distant](PUBLICATION-1.5.json) consigne la publication du code `07a4c69`. La connexion réelle entre appareils reste à éprouver.

La [cible durable proche AAA](EXIGENCE-QUALITE.md) concerne **tout le jeu**. Les nouvelles demandes autorisent le duel contre une IA locale et le LAN, y compris téléphone ↔ téléphone sans PC ; elles complètent le choix solo de la 1.4, conservé dans ses archives. Le périmètre courant contient seulement l’aventure et ces deux usages utiles.

## Livraison courante : engagements et preuves

| Engagement | État vérifiable au point de reprise |
|---|---|
| Onze héros au même niveau de fabrication | Lame approuvée conservée ; dix modèles originaux détaillés avec sources Blender et atlas PBR. Dix exports Quaternius adaptés et provenance présents ; onze modèles contrôlés dans le jeu et l’atelier, 88 cas directionnels, onze kits et orientations des armes vérifiés. Finition et équilibrage humains encore ouverts |
| Gestes adaptés à l’arme | Profils fusil, magique, dagues, lame et lourd ; données de foulée, contacts, cadence, pouvoir et fenêtre de frappe. Pas orientés et esquives gardent des solutions analytiques héritées ; aucun mocap annoncé |
| Contrôle en combat | Déplacement tactile libre hors intention d’attaque, assistance stabilisée, préparation orientable bornée, direction active conservée, combo tamponné et récupération libérée ; CPU de contrôle/contact passé |
| Couvert et physique | Tirs contrôlés sur la trajectoire et Bastion soumis à la ligne de vue ; contrôleur au sol et sous-pas conservés. Pas de relief parcourable ou de corps rigides ajoutés |
| Grandes portes | Modules verticaux, dégagement visible lié au collider et protection d’acteur ; contrôle CPU avec vraie géométrie et collision passé. Parcours de mission et collision passés ; revue humaine de chaque seuil encore ouverte |
| Matières et ombres | Union de sols aux deux conflits identifiés sans changer les régions logiques ; contacts Léger étendus aux autres chapitres et duels. Rendu Haute/Léger, textures réellement décodées et appuis contrôlés ; finition artistique encore ouverte |
| Aventure | Trois chapitres, objectifs, boss, ancres, conclusion, secret et anciennes reprises conservés ; parcours des trois conclusions, secret et reprises passé après exports |
| Duel tactique | Bot local sans API, perception retardée, couvert, portée, récupération et pouvoirs ; tests CPU passés. Duel intégré, onze kits, manches, couverts, sauvegardes et trois relances passent |
| LAN entre appareils | Module WebRTC direct, offre/réponse manuelles, hôte autoritaire et deux joueurs. Schéma/transport/chemins d’échec contrôlés ; synchronisation du jeu passée avec pont en mémoire |
| Preuve LAN réelle | **Non acquise** : la politique Chromium gérée interdit les candidats ICE locaux. Handshake natif SKIP. Le pont de test ne valide ni DTLS réel, ni deux téléphones, ni leur routeur |
| Sauvegardes et commandes | Profils locaux, secret, import/export, remappage et manette conservés ; parcours de commandes sur les trois modes, remappage, interfaces et conservation des profils passés |
| Sécurité | Identifiants propres, caches et graphes de sauvegarde bornés ; rôles, session, séquences, tailles et débits réseau ; CSP à empreintes et referrer. Tests dédiés passés, sans prétendre à un audit de pénétration certifié |
| Publication et historique | Sources/licences/archives conservées. Projet courant vérifié et complet avec manifeste ; toutes les archives restent dans le ZIP généré par GitHub. HTML, onze modèles, créature, captures et paquet comparés à la publication ; aventure, atelier, bot et lobby LAN non appairé contrôlés sur le site public |

Les [prises en charge 1.5](PRISE-EN-CHARGE-1.5.md), l’[audit profond](AUDIT-PROFOND-1.5.md) et la [couverture du jeu entier](COUVERTURE-QUALITE.md) détaillent les critères. [Modes](MODES-1.5.md), [duel et IA](DUELS-1.5.md), [guide LAN téléphone](LAN-TELEPHONES-1.5.md), [sécurité LAN](LAN-SECURITE-1.5.md) et [portes/matières](PORTES-MATIERES-1.5.md) décrivent les règles et limites.

## Ordre de clôture

1. Contrôler les dix exports adaptés et leur provenance ; vérifier corps, mains, armes et actions dans l’atelier et le jeu, en conservant le GLB approuvé de la Lame.
2. Rejouer les onze kits, le duel, la campagne, les anciennes sauvegardes et les commandes. Garder les tests GPU séquentiels. Consigner PASS, défaut ou SKIP réel ; ne pas transformer un saut de test en succès.
3. Ajouter les captures et preuves du build courant. Les captures `r5-*-studio.jpg` doivent provenir du moteur et être accompagnées de leur relevé ; les anciens comparatifs restent datés de leur version.
4. Construire, vérifier l’intégrité des archives, puis publier et vérifier les fichiers publics. Le relevé final 1.5 est pris en charge par le responsable de livraison ; les phrases de ce suivi doivent refléter ses résultats réels.
5. Essayer ensuite deux téléphones physiques, la difficulté, la découverte des niveaux et les performances sur matériel identifié. Ces preuves ne peuvent pas être remplacées par le navigateur de développement.

## Travail qui reste à produire après cette passe

- Revue à 1× des transitions, appuis orientés, esquives, drapés, réactions et personnalité de chacun des onze héros ; aucune équivalence artistique finale n’est déduite des compteurs d’actions ou de matériaux.
- Anatomie, locomotion, langage d’attaque et présentation propres aux autres familles ennemies et aux trois boss. Le bot du duel ne remplace pas ce chantier.
- Composition des zones, fonctions des lieux, orientation, alternance des épreuves et rythme de découverte. La cible de 10–15 minutes par chapitre n’est pas une durée humaine mesurée.
- Mise en scène du récit, conséquences visibles, variantes sonores, timbres et mixage. Trois motifs synthétiques et une chronique ne constituent pas la bande-son ou la narration finales.
- Mesures PC/téléphone identifiés : chargement, mémoire, p50/p95/p99, chauffe, contrôles et écoute. Pas de revendication de FPS iPhone depuis un rendu logiciel.
- Validation native du LAN et des conditions réseau. Aucun compte distant, synchronisation cloud, classement ou anti-triche compétitif n’est livré ; un hôte modifiant sa propre simulation reste une limite du pair-à-pair.

## Historique conservé

Les notes suivantes restent un relevé daté de la 1.4 et des passes antérieures. Leurs mentions « solo uniquement », « autres héros conservés » ou « pas de réseau entre appareils » décrivent ces anciennes livraisons, pas le périmètre courant 1.5. Leurs captures et validations ne sont pas des preuves du build 1.5.

# Historique du suivi — livraison 1.4-rc1

**État de reprise :** 1.4-rc1 publiée et vérifiée sur GitHub Pages. Les 23 suites locales et les contrôles publics sont consignés dans [la validation](VALIDATION-1.4.md) et [le relevé distant](PUBLICATION-1.4.json). La [consigne globale proche AAA](EXIGENCE-QUALITE.md), confirmée ensuite par l’utilisateur, s’applique à tous les contenus et systèmes ; elle reste l’objectif de production. Les instructions de reprise sont dans [AGENTS.md](../AGENTS.md).

Les choix confirmés pour cette livraison sont : **sans serveur**, détails visuels avec réglage léger, aventure complète puis révision du résultat. La version candidate relie le contenu de jeu ; le rendu et l’équilibrage restent à éprouver en parties humaines.

| Engagement | État vérifiable |
|---|---|
| PC et téléphone | Navigateur Three.js, clavier/souris, tactile ; rendu et commandes simulés dans Chromium |
| Trois chapitres | Cathédrale, Chasse aux Souverains et Convoi de l’Impossible, avec objectifs, rencontres, boss, conclusions et reprises |
| Dix héros disponibles dès le début | Dix kits, statistiques, armes et modèles distincts ; aucune progression obligatoire pour ces dix héros |
| Onzième personnage secret | Trois étapes réparties dans les niveaux ; Éclipse incarnée, Soleil noir et Incarnation supplémentaire |
| Animation et mouvement | Lame : mouvements Quaternius CC0 retargetés, foulées/cadence/appuis mesurés, esquive calibrée et attaques engageant le corps complet ; autres héros conservés. Raccords et qualité en mouvement encore à revoir |
| Physique | Contrôleur au sol et collisions antérieures conservés ; frappe Lame par balayage du sabre contre capsule durant sa fenêtre active. Pas de pentes ni de corps rigides ajoutés |
| Solo | Voyage complet et sélection directe des chapitres |
| Coopération | Retirée du bundle et du lancement 1.4 ; code complet et archives 1.3 conservés |
| Battle | Arènes, bots et Couronne retirés du bundle et du lancement 1.4 ; code complet et archives 1.3 conservés |
| Sauvegarde | Profil local nommé, ancres, statistiques, secret, export/import ; anciens refuges conservés |
| Audio et confort | Ambiance procédurale, master/silence zéro/pause, effets stéréo selon source/caméra, priorité et limite de voix ; focus des écrans modaux. Parcours intégré vérifié ; revue du mix sur appareils physiques encore à faire |
| Direction artistique | Noir/ambre, soleil, dunes et silhouettes drapées ; matières PBR, contre-jour et composition HDR, avec mode léger. Références de mouvement Expédition 33 / Ghost of Tsushima |
| GitHub et historique | Sources, modèles, provenance, licences, tests et archives séparés ; site dans docs/ et modèles chargés à la sélection |

## Limites conservées, sans les annoncer comme terminées

- Coop et battle : hors de la candidate 1.4. Les modes locaux antérieurs restent dans les sources et archives ; aucun mode entre appareils n’est livré.
- Compte par e-mail/code ou Google, synchronisation et récupération distante : non livrés. Le profil proposé est explicitement local.
- Cible de 10–15 minutes par niveau : à confirmer en parties humaines ; aucune durée de test contrôlé n’est présentée comme une durée réelle.
- Téléphone et manettes physiques : encore à essayer. Les tests utilisent Chromium, ses entrées tactiles et des manettes simulées.
- Pentes, escaliers, corps rigides et relief parcourable : non implémentés ; le contrôleur reste au sol.
- Finition visuelle et rythme : costumes, textures, transitions, réactions et équilibrage doivent encore être revus à partir de parties. Cette livraison candidate ne clôt pas ces objectifs qualitatifs.

## Préservation du travail précédent

La Cathédrale, les serments, ses énigmes, son extraction, les archives HTML/ZIP, les modèles et les sauvegardes antérieures sont conservés. La comparaison 0.11/0.12 reste datée de ces versions, sans être présentée comme une capture de la version actuelle.

Les passes [0.13](PHYSIQUE-0.13.md), [0.14](DYNAMIQUE-0.14.md) et [0.15](ANIMATIONS-0.15.md) restent documentées. Le [guide de la livraison complète](VERSION-COMPLETE.md) décrit le résultat et ses règles. La [liste de contrôle](PRODUCTION-COMPLETE.md) suit la préparation de publication.

## Passe actuelle

La passe [Ambre et obsidienne](ESTHETIQUE-1.1.md) suit les dernières images. Les trois chapitres sont conservés. Les modes locaux de cette passe antérieure restent dans les sources et archives ; la candidate 1.4 se concentre sur le solo. Les captures de la nouvelle comparaison sont issues du moteur et restent distinctes de la comparaison historique 0.11/0.12.

La passe [Récit et son](RECIT-SON-1.1.md) ajoute le contexte dans le menu, une chronique qui suit l’avancement et trois thèmes originaux synthétiques avec couches de combat. Pas de doublage ni de bande-son orchestrale enregistrée annoncés. Les effets de pas, tirs, lames et impacts sont différenciés.

Les retours des captures ont conduit au [correctif rc3](CORRECTIFS-1.1-rc3.md). La [séquence de référence](SEQUENCE-REFERENCE.md) définit désormais les critères qualitatifs à atteindre avant d’étendre la finition. La fluidité réelle du téléphone et les clips de locomotion restent à valider.

## Revue du premier personnage

La [direction de la Lame](personnages/lame-eclipse/REVUE-01.md) est validée et sa première production 3D est intégrée avec un atelier de revue. Le niveau artistique de la planche n’est pas atteint. Les autres héros et les familles ennemies restantes sont à traiter après cette revue. Fauche-Cendre devient la première créature originale de référence dans la passe 1.4. Le navigateur est conservé pour cette étape. Les commandes solo sont configurables. Les anciennes dispositions de groupe restent dans le module conservé hors du bundle 1.4.

## Atelier et matières — 1.3-rc1

L’atelier est maintenant intégré au choix du personnage au début. Il utilise les modèles réels et conserve l’atelier séparé pour la revue. Son rendu se suspend hors vue et sa scène se libère au lancement du jeu. Les dix héros ordinaires restent disponibles ; l’aperçu ne contourne pas le secret du onzième.

La seconde production de la Lame vise une silhouette adulte : environ 7,34 longueurs de tête, épaules et extrémités affinées, masque et costume moins réguliers. Squelette et 23 clips sont conservés. Les trois attaques suivent leurs durées de clip plutôt qu’une lecture accélérée. Cela corrige le rythme de lecture, sans valider la qualité finale des gestes ou leur équilibrage.

Les matières PBR du modèle ne sont plus écrasées par le tissu générique. La [passe de finition](FINITION-1.3.md) ajoute aussi des cartes photographiques CC0 aux sols et à la maçonnerie du niveau et de l’atelier, ainsi que des bordures, supports, niches d’Archives et cheminées de forge. Les chemins et collisions ne sont pas refaits dans cette passe. Le modelage des dix autres personnages, l’anatomie des ennemis, la composition de chaque zone, le rythme et les essais sur appareil restent à poursuivre.

## Séquence, combat et créature — 1.4-rc1

La passe applique les recherches à une séquence existante : mouvements Quaternius Standard gratuits adaptés à la Lame, métadonnées de foulée/contact, IK bornée, cadence et esquive calibrées, contact du sabre pendant la fenêtre active. La géométrie du costume, ses poids et un socket de prise d’arme sont repris pour accompagner ce retarget. Il ne s’agit pas de capture de mouvement.

Fauche-Cendre remplace la famille `warden` par un quadrupède original à 22 os, avec approche, préparation directionnelle de 0,78 s, détente de 2,4 unités sur 0,32 s et récupération de 1,4 s. Le contact inflige une seule fois 22 dégâts, selon les protections/règles du jeu. Son son d’avertissement est localisé. Les autres familles ne sont pas annoncées comme refaites.

Le son utilise un master commun, le vrai silence à zéro, une pause qui nettoie les sources, un plafond de 16 voix d’effets et un panoramique relatif à la caméra. La carte, les pactes et les choix de voyage disposent d’une gestion commune du focus et d’un arrière-plan inerte. Les contrôles CPU, les parcours du jeu intégré et la publication ont passé ; leurs scénarios et limites sont consignés dans la validation 1.4.

La [matrice 1.4](PRISE-EN-CHARGE-1.4.md) montre ce qui est recherché, appliqué et encore à revoir. Le [référentiel qualité](REFERENTIEL-QUALITE.md), le [workflow](WORKFLOW-QUALITE.md) et le [skill local](skills/quality-pass/SKILL.md) conservent les connaissances dans le dépôt. Ce skill n’est ni un connecteur cloud installable ni une formation permanente du modèle.

L’utilisateur a confirmé : « Aventure solo uniquement pour l’instant ; conserver les autres dans les archives ». La candidate 1.4 se concentre donc sur le solo. Les choix d’arènes, bots et groupes sont retirés du menu et leur code est exclu du bundle via `src/local-party-solo.js`. Le module complet `src/local-party.js` et les archives 1.3 conservent le travail antérieur. Les ennemis et boss gardent leur IA locale sans service connecté. Les profils, les chapitres, les matières et la composition précédents sont conservés. La réfection complète des trois niveaux, les autres héros et créatures, le mixage final, l’équilibrage et les essais physiques restent ouverts.

## Travail restant à étendre à tout le jeu

Priorités de production à poursuivre depuis la référence actuelle : raccords, pas orientés, réactions et esquives propres à chaque héros ; drapés et prise d’arme ; anatomie et comportement des autres familles et boss ; composition et rythme des trois niveaux ; présentation du récit, timbres et mixage ; lisibilité de toute l’interface et mesures sur PC/téléphone physiques. Les éléments appliqués et les écarts restent détaillés dans la matrice. Une scène réussie ne clôt aucun contenu encore provisoire.
