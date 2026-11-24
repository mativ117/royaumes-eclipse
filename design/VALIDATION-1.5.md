# Validation de la candidate 1.5-rc1

Contrôles réalisés les 23 et 24 novembre 2026. Cette page consigne les résultats locaux ; la vérification de la publication est enregistrée séparément dans `PUBLICATION-1.5.json`. La cible proche AAA reste une exigence de production, pas une certification obtenue par ces tests.

## Environnement et portée

Python, Node, Blender 4.3.2, Playwright 1.62 et Chromium avec WebGL logiciel. Les essais graphiques sont exécutés successivement, avec des dispositions PC, portrait et paysage. Les entrées tactiles et manettes sont simulées. Aucune cadence, chauffe ou latence sur appareil physique n'est déduite de ces mesures. Les parcours de campagne utilisent des positions et dégâts contrôlés ; ils ne mesurent pas une découverte humaine de 10–15 minutes.

## Contrôles réussis

| Axe | Suites et résultat observé |
|---|---|
| Sols et portes | `ground_layout`, `doors_materials --integration` : union sans double surface, aire et navigation préservées ; neuf seuils réels, modules limités, dégagement visible lié à la collision, anti-écrasement et ouverture à 30/60/120 Hz |
| Couvert et contacts | `combat_control`, `blade_contacts`, `lame_attack_timing` : balayage des tirs, direction préparatoire bornée, une frappe par corps dans la fenêtre source, obstacles et ratés horizontaux/verticaux |
| Ressources et animation | `retarget_assets`, `roster_motion`, `lame_motion_quality`, `stance_motion` : onze modèles réels, données finies, poids des armes secondaires, contacts de semelle, cadence, trois frappes, esquives et 88 cas directionnels |
| Campagne et physique | `expedition`, `complete_campaign`, `physics` : trois conclusions, escorte, énigmes, routes, boss, reprise, île secrète, Incarnation, déplacement contre obstacles et stabilité des ombres |
| Rendu et atelier | `render_complete`, `material_finish`, `hero_preview_real`, `presentation` : matériaux et textures réellement décodés, sols et UV, Haute/Léger, interfaces PC/téléphone, cycle sélection → atelier → jeu → menu et libération du rendu de l'atelier |
| Lisibilité, profils et son | `interaction_visibility`, `profiles`, `story_sound`, `spatial_audio`, `modal_focus` : lecture des stèles depuis quatre approches, cible proche, indice persistant, anciennes reprises, import refusé sans perte, focus, silence réel, pause et stéréo |
| IA locale | `tactical_bot` : perception retardée, mémoire limitée, contournement d'un couvert, réaction aux projectiles, ressources propres et décisions déterministes sans appel réseau |
| Frontières de confiance | `hero_validation`, `lan_protocol`, `security_headers` : identifiants propres, graphes et paquets bornés, rôles, séquences, expiration, débit ; scripts injectés refusés, scripts autorisés et textures embarquées fonctionnels |
| Transport LAN | `lan_peer` : module avec double RTC déterministe et échec réel sans candidat ICE, délais et nettoyage vérifiés. **Transfert WebRTC natif : SKIP**, voir ci-dessous |

`session_actors` passe : vrai duel contre le bot sur quatorze secondes, couvert, manches, contacts de la Lame, tirs réels, parité des onze kits et de la surchauffe, axes des deux fusils identiques pour joueur et adversaire, trois relances avec une seule action par touche et conservation de l'aventure. `lan_game` vérifie séparément la synchronisation simulée décrite ci-dessous. `input_settings` et `publication` passent également : trois modes, touches remappées, tactile, absence de superposition carte/menu, ancien lien et racine du dépôt, choix de serment et construction reproductible. `package_release` passe : anciens fichiers inchangés, ZIP déterministe inférieur à 95 Mo avec manifeste et sources éditables, onze modèles complets, snapshot autonome sans requête de modèle. Le snapshot HTML conserve le jeu ; l’atelier séparé est fourni avec le projet complet.

## Mesures de mouvement

Les dix nouveaux exports possèdent 24 actions chacun ; la Lame approuvée conserve ses 23 actions et son empreinte `200c30d20d5ef4735f27871ebcd8165d95a8bedbf98a7cb3d3c23b43a72312f6`.

Le contrôle CPU des onze vrais modèles évalue leurs sommets après skinning : pénétration maximale des semelles d'environ 0,50 mm dans ses scénarios. La mesure directionnelle couvre 88 cas, avec une dérive maximale d'appui de 1,22 cm et aucun relâchement d'appui fort. Les relâchements des portions faibles d'entrée/sortie sont conservés dans le diagnostic ; ils ne sont pas effacés pour annoncer un contact permanent. Le budget IK reste borné à 14 cm.

Les pas arrière et latéraux utilisant des alias de marche déclenchent le contrôleur analytique adapté. Ils ne sont pas présentés comme des animations directionnelles nouvellement produites. Les rapports détaillés sont [PERSONNAGES-MOUVEMENT-1.5.json](PERSONNAGES-MOUVEMENT-1.5.json) et [APPUIS-DIRECTIONNELS-1.5.json](APPUIS-DIRECTIONNELS-1.5.json).

## LAN : limites de la preuve

`lan_game` contrôle deux vrais contextes du jeu reliés par un pont **en mémoire réservé au test**, avec le protocole de production : intentions, santé autoritaire, dégâts, pauses, manches, déconnexion et sauvegardes. Cela ne valide ni le Wi-Fi ni DTLS.

La politique du navigateur géré (`disable_non_proxied_udp`) ne produit aucun candidat ICE local. Elle n'a pas été contournée. Le transfert natif et le parcours entre deux téléphones restent à essayer sur appareils physiques. Le jeu utilise WebRTC direct avec invitations manuelles, sans PC obligatoire, API, STUN/TURN ou serveur de rendez-vous. Un hôte peut modifier sa propre simulation ; aucun anti-triche compétitif n'est annoncé.

## Correctifs révélés par les contrôles

- Le durcissement CSP bloquait le `fetch(blob:)` interne du décodeur de textures GLB : autorisation des objets locaux ajoutée, sans origine d'API externe ; décodage et refus des scripts injectés vérifiés ensemble.
- Des pistes constantes optimisées ne réinitialisaient pas certains os : la pose animée est restaurée avant chaque évaluation pour empêcher l'accumulation d'inclinaison et d'IK.
- Les alias de marche arrière/latérale recevaient des contacts de marche avant : sélection des appuis analytiques corrigée, semelles contrôlées après IK.
- Un quaternion cloné pouvait être représenté par plusieurs rotations Euler équivalentes : orientation complète de la racine fixée, au lieu de modifier seulement son axe Y.
- Le canon pouvait créer un projectile au-delà d'un couvert proche : contrôle du segment corps → canon ajouté aux deux combattants. Le test avec ancre de canon allongée est explicitement contrôlé ; les tirs du modèle réel sont également vérifiés contre le pilier de l'arène.

## Captures et limites conservées

Les images de l'atelier viennent du moteur, avec textures chargées et cadrage selon les dimensions réelles. Les vidéos sont exportées à vitesse normale avec deux pas de simulation à 60 Hz par image à 30 Hz ; elles utilisent le véritable réglage Léger et ne mesurent pas les FPS d'un appareil. Les vidéos historiques 1.3/1.4 restent distinctes.

Les preuves sont dans `CAPTURES-PERSONNAGES-1.5.json` et `CAPTURES-MOUVEMENT-1.5.json`. Les raccords, esquives propres aux héros, drapés, autres créatures et boss, composition des lieux, mise en scène narrative, timbres, mix et équilibrage humain restent à poursuivre. Le contrôleur demeure plan : pas de pentes, escaliers ou corps rigides annoncés.
