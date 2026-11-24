# Audit profond du jeu — base 1.4 et intégration 1.5

Point de contrôle du 23 novembre 2026. Objectif confirmé : rapprocher **l’ensemble du jeu** de la qualité des meilleurs jeux AAA dans notre univers, en conservant l’accès Web PC/téléphone. Les nouvelles demandes couvrent les onze héros, les duels contre une IA locale sans API et le réseau local entre téléphones sans PC obligatoire.

Cet audit relie les retours aux ressources et règles effectives. Il ne certifie pas l’absence de tout bug. Le dernier état public connu au début du travail est [1.4-rc1](VALIDATION-1.4.md) ; les modifications 1.5 sont encore à réunir et à vérifier dans le jeu. Les états ci-dessous décrivent ce point de contrôle, pas une publication finale déjà réussie.

**Clôture locale du 24 novembre :** la [validation 1.5](VALIDATION-1.5.md) complète ce point initial avec les résultats des onze personnages, des appuis, de la campagne, des duels, du rendu et de la sécurité. Elle consigne aussi les défauts de décodage des textures, d’accumulation de pose, de contacts directionnels et de rotation des clones révélés pendant les contrôles. Le LAN natif et les essais physiques restent explicitement ouverts.

## Méthode et limites des preuves

Lecture du code des scènes, du contrôleur, de l’animation, des pouvoirs, du rendu, de l’audio, de l’interface, de la sauvegarde et des nouveaux modes. Inspection de métadonnées GLB et de la fabrication des dix nouveaux héros. Les captures `r3-jardin.jpg` et `r3-convoi.jpg` ont servi à constater les compositions historiques ; elles sont étiquetées comme anciennes, sans être présentées comme des captures 1.5.

Les tests CPU `doors_materials --integration`, `ground_layout`, `combat_control` et `hero_validation` ont été exécutés et passent. Aucun test de jeu WebGL nouveau, aucune partie novice et aucun essai sur téléphone physique n’ont été lancés par l’auteur de cet audit. Les responsables d’intégration consignent ces parcours séparément. Les tests GPU restent séquentiels dans cet environnement.

**P0** : incohérence de règles, frontière de confiance ou défaut bloquant à résoudre avant de présenter le mode concerné comme fonctionnel. **P1** : défaut majeur de sensation, lisibilité ou production. **P2** : travail de finition ou couverture à compléter. Ces priorités sont propres au projet ; elles ne sont pas un score de qualité artistique.

## Défauts concrets et état au point de contrôle

| ID / priorité | Déclencheur et cause vérifiable | Effet pour le joueur | État et critère de fermeture |
|---|---|---|---|
| A01 · P0 | [world.js](../src/world.js), seuils de 19–48 unités ; ancien `sculptGates` construisait deux feuilles de 9,5–24 unités | À l’ouverture, une feuille pouvait traverser ou recouvrir les passages voisins | Modules verticaux dans [art-direction.js](../src/art-direction.js). CPU réel passé sur neuf seuils et collision. Revue en mouvement depuis les deux côtés à ajouter |
| A02 · P0 | [journey.js](../src/journey.js), traces/Gué et île secrète : plusieurs boîtes de sol au même Y sur la même surface | Scintillement et conflits de textures, avec des dalles qui semblaient changer selon la caméra | Union des rectangles dans [ground-layout.js](../src/ground-layout.js), régions logiques conservées. CPU passé ; confirmer les deux lieux au rendu |
| A03 · P0 | Ancienne boucle de projectiles dans [game.js](../src/game.js) ne vérifiait le mur qu’au nouvel endpoint ; un tir à 32 unités/s avance de 0,533 unité à 60 Hz | Des tirs pouvaient franchir un couvert mince malgré le contrôleur de déplacement valide | Sous-échantillonnage de la trajectoire dans `projectileBlockedAlong`, [combat-control.js](../src/combat-control.js). CPU passé ; duels et pouvoirs à rejouer |
| A04 · P0 | `HERO_DEFS[id]` était utilisé sans propriété propre aux frontières d’import/reprise/cache | Des identifiants hérités comme `constructor` pouvaient être acceptés et casser un chargement ou une reprise | `isHeroId`, caches sans prototype et bornage du graphe de sauvegarde. [hero_validation.py](../tests/hero_validation.py) passe sans requête pour les identifiants invalides |
| A05 · P1 | Visée tactile permanente vers la cible la plus proche, combinée à une vraie vitesse de recul limitée | Fuir devenait un recul lent ; changer légèrement de cible pouvait faire pivoter le corps pendant le combat | Le déplacement libre reprend son orientation, l’assistance suit l’intention de combat et conserve une cible avec hystérésis. Rejouer chaque profil à une main sur téléphone |
| A06 · P1 | Préparation et récupération verrouillées, pas orientés hérités et cadres d’entrée étroits | Direction difficile à corriger, enchaînements peu accessibles et impression de glissement | Préparation orientable dans une limite, trajectoire active conservée, jambes libérées en récupération et buffer d’entrée. Contrôler visuellement pieds, arme et dégâts à 1× |
| A07 · P1 | Dix héros étaient encore des ressources antérieures à la Lame détaillée ; les rôles ne disposaient pas tous de mouvements adaptés | Écart de qualité de modèle, de prise d’arme et de personnalité gestuelle | Dix sources d’art et exports adaptés sont présents, avec métadonnées/provenance concordantes. Les contrôles finaux atelier/jeu restent à joindre. La [couverture](COUVERTURE-QUALITE.md) distingue fabrication présente et héros validé |
| A08 · P1 | [staging.js](../src/staging.js) conserve une construction de corps commune à de nombreuses familles ; les boss ajoutent surtout échelle et ornements | La distinction mécanique existe mais l’anatomie, les réactions et la mise en scène restent sommaires | Fauche-Cendre est une première référence seulement. Prévoir une production propre des autres familles et de chacun des boss |
| A09 · P1 | Les contacts Léger historiques étaient enfants du monde de la Cathédrale, et `updateArtDirection` s’arrêtait dans les autres chapitres | Les ennemis et adversaires des chapitres II/III pouvaient perdre leur ancrage quand les ombres GPU étaient coupées | [contact-shadows.js](../src/contact-shadows.js) ajoute une couche dans la scène, indépendante du premier monde. Source présente ; vérifier Haute/Léger dans les trois chapitres et duels |
| A10 · P1 | Les règles d’entrée J1 et la manette filtraient strictement le mode solo | Un nouveau mode pouvait perdre les touches remappées ou le pad | `inputSolo` couvre les trois modes utiles et `getGamepads` est protégé contre les exceptions de permission. Les parcours de sélection, pause, carte et retour doivent passer dans chaque mode |
| A11 · P0 pour le LAN | Nouveau flux distant : invitations, commandes, snapshots et événements de fermeture | Un paquet malformé, trop fréquent, ancien ou de mauvais rôle ne doit ni modifier l’autorité ni bloquer le navigateur | Schémas bornés, session, séquences, débit, rôles et DTLS dans les modules LAN. Les validations du protocole et du transport, puis le jeu à deux, doivent être relevés ; ne pas annoncer le LAN depuis une seule page locale |
| A12 · P1 | La simulation et les contrôles sont suspendus par la pause et l’arrière-plan | Des entrées réseau pourraient rester actives ou une session se figer sans état compréhensible | Le transport et ses délais vivent hors `update`, les entrées périmées deviennent neutres et la déconnexion est explicite. Tester onglet caché, perte de réseau et hôte interrompu |
| A13 · P1 | [journey.js](../src/journey.js) construit de grandes zones planes, de nombreux éléments en séries et des transitions peu mises en scène | Les épreuves sont variées, mais le parcours et le monde peuvent encore paraître abstraits et répétitifs | Revoir composition, fonctions des lieux, rythme, détours et compréhension novice par zone ; pas de reconstruction totale ni de durée humaine validée annoncée |
| A14 · P1 | [story-audio.js](../src/story-audio.js) utilise trois motifs synthétiques et une chronique textuelle progressive | Les règles se comprennent, mais le récit, la tension et l’identité sonore ne sont pas au niveau de la cible finale | Mise en scène narrative, motifs/transitions, effets et variantes, écoute du mix et conséquences dans le monde à produire |
| A15 · P1 | Nouveaux modèles, atlas et scènes ; cache de modèles et cibles de composition conservent des ressources | Le niveau de détail peut coûter au chargement et à la mémoire sans qu’un budget de dessin le révèle | Mesurer temps de chargement, textures/mémoire, cycles de sélection et p95/p99 sur matériel identifié. Les captures exportées ne sont pas une mesure de FPS |
| A16 · P2 | La physique reste un plan avec volumes simples, et tous les objets décoratifs n’ont pas une fonction de collision explicite | Risque de confusion entre décor, couvert et objet solide ; les pentes ou plateformes attendues n’existent pas encore | Cartographier les accessoires sur les chemins et leur intention. Rapier est étudié, pas intégré ; ne pas prétendre livrer du relief parcourable |

## Lecture de la production par domaine

### Personnages, déformations et armes

Le critère final concerne tous les héros et le secret : silhouette, adulte crédible dans son intention, matières, corps continu, articulations, tenue de l’arme, pieds et gestes adaptés au kit. Les dix fabrications d’art ont entre 18 170 et 23 984 sommets et neuf matériaux au point de l’audit ; cela ne prouve pas une équivalence avec la Lame. Les dix exports adaptés et leur provenance sont ensuite présents dans `assets/characters/`, avec profils fusil, magique, dagues, lame, lourd, ombre et ultime. Leur revue intégrée reste à consigner. Ces profils doivent différer par leur geste et leur rythme, pas uniquement par couleur ou vitesse ; les solutions héritées pour pas orientés et esquives restent une limite.

Conserver les sources Blender, les licences et la provenance des animations. Les bibliothèques [Quaternius Standard](https://quaternius.itch.io/universal-animation-library) et [KayKit Character Animations Free 1.1](https://kaylousberg.itch.io/kaykit-character-animations) sont documentées dans les ressources ; seule la sélection réellement obtenue sous CC0 doit être créditée comme utilisée. Aucune capture de mouvement ni version payante n’est supposée.

### Combat et rencontres

La séquence complète doit aligner intention, anticipation, déplacement, trajectoire, collision, impact, son et récupération. Les pieds doivent suivre la vitesse réelle ; accélérer une animation de marche pour cacher un recul trop lent ne suffit pas. La direction doit pouvoir être corrigée pendant une préparation bornée, tout en restant lisible pendant la fenêtre active. Une esquive et une interruption doivent annuler proprement le contact et libérer les entrées.

Le duel tactique local est évalué sur ses décisions observables : perception et réaction finies, couvert et contournement, portée, ouverture de récupération, ressources propres et absence de lecture instantanée des touches adverses. Une difficulté supérieure ne doit pas signifier dégâts arbitrairement gonflés ou esquive parfaite de chaque tir. Le bestiaire et les boss restent un chantier séparé.

### Niveaux, matériaux, lumière et récit

Les chapitres comportent déjà des décisions et épreuves différentes : escorte, mémoire, transport, traces, terrain de boss, vent, route et défense du cœur. L’écart se situe surtout dans leur réalisation spatiale et leur présentation. Les grandes nappes de sol et séries d’arches ne racontent pas encore suffisamment la fonction et l’histoire de chaque lieu.

La revue doit distinguer vide intentionnel, espace de respiration, décor hors parcours et surface accidentellement absente. Vérifier les transitions de matières et UV depuis la caméra du jeu, sans bloom puis avec la composition normale. Les ombres demandent des séquences en mouvement, avec le contact au sol et les objets du plafond, et non seulement une image fixe.

### Interface, son et accessibilité

Le remappage, le focus et le contexte des messages sont des bases à préserver. La nouvelle sélection de modes, les invitations et leurs réponses doivent rester compréhensibles sans vocabulaire réseau. Les états « préparation », « invitation prête », « attente », « connecté », « pause » et « connexion perdue » sont distincts. Une invitation générée ne vaut pas une connexion établie.

Vérifier les boutons, la carte, les messages d’interaction, les textes longs et les retours au menu dans les dispositions PC, portrait et paysage. Les informations essentielles doivent être données autrement que par la couleur ou le son seul. La musique actuelle et les effets synthétiques doivent encore recevoir une écoute critique sur casque et haut-parleurs ; les tests PCM ne jugent pas leur qualité artistique.

### Sécurité et confiance

Le navigateur hôte calcule les règles et les points de vie ; l’autre appareil transmet des intentions bornées. Les sauvegardes restent locales. L’appairage manuel et DTLS évitent un service de rendez-vous, mais ne donnent ni identité de compte vérifiée ni protection compétitive contre un hôte qui modifie son propre jeu. Cette limite doit être présentée clairement, sans prétendre à un serveur anti-triche.

Le transport doit refuser les paquets inattendus, anciens, trop gros et trop fréquents ; les adresses privées d’invitation ne doivent pas se retrouver dans les journaux ou le stockage persistant. Le fonctionnement entre deux téléphones physiques dépend aussi du réseau, du navigateur et des permissions locales. Pas de découverte automatique des appareils, de STUN/TURN ni d’appel API ne sont ajoutés par une simple sélection de mode.

Le durcissement de construction par [html_security.py](../scripts/html_security.py) ajoute des empreintes des scripts inline, interdit les attributs de script, objets et base externes, et fixe le référent à `no-referrer`. Il doit être testé avec le jeu et l’atelier générés ; une CSP mal appliquée pourrait les casser. Une CSP livrée en balise meta ne constitue pas un en-tête `frame-ancestors` ni un remplacement du contrôle des paquets.

## Critères de sortie de la passe

1. Les ressources finales de chaque héros existent, sont chargées par le jeu et l’atelier, et passent la séquence de leur arme, déplacement, esquive et pouvoir.
2. Les neuf seuils conservent leurs routes et se voient depuis les deux côtés sans feuille démesurée, plafond fantôme, collision anticipée ou écrasement.
3. Les lieux de sols superposés sont revus au rendu ; le correctif ne retire pas de zone praticable et ne masque pas le défaut par un décalage aléatoire de hauteur.
4. L’IA locale joue effectivement un duel avec des décisions justes. Le LAN passe un vrai échange entre deux navigateurs, puis fait l’objet d’un essai sur les appareils visés ; les deux niveaux de preuve restent séparés.
5. Anciennes sauvegardes, secret, trois chapitres, touches, atelier et mode Léger restent couverts par les régressions pertinentes.
6. La livraison enregistre ce qui est vérifié, ce qui reste simulé, les captures réelles, les limites et les prochains contenus à produire. Le statut « AAA atteint » n’est pas utilisé.

## Sources primaires et recommandations réutilisées

Les sources détaillées et leurs versions figurent dans le [référentiel](REFERENTIEL-QUALITE.md). Cet audit réutilise les recherches documentées au lieu de prétendre avoir visionné toutes les conférences.

- [GDC — Animation-Driven Locomotion for Smoother Navigation](https://www.gdcvault.com/play/1015387/Animation-Driven-Locomotion-for-Smoother) : rapport entre intention de déplacement, animation et navigation.
- [Riot Games — Clarity in League](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/) : lisibilité des silhouettes, direction des attaques et signes utiles.
- [Guerrilla — The AI of Horizon Zero Dawn](https://www.guerrilla-games.com/read/the-ai-of-horizon-zero-dawn) : perception, coordination et lecture des comportements, sans annoncer une reproduction de leur système.
- [GDC — What Happened Here? Environmental Storytelling](https://www.gdcvault.com/play/1012647/What-Happened-Here-Environmental) : résumé officiel consulté dans la recherche antérieure, pas vidéo complète annoncée comme visionnée.
- [Sucker Punch — Crafting the World of Tsushima](https://blog.playstation.com/2020/07/09/crafting-the-world-of-tsushima/) : fonction de la composition et de l’orientation naturelle.
- Three.js r160 : [couleurs](https://github.com/mrdoob/three.js/blob/r160/docs/manual/en/introduction/Color-management.html), [ombres](https://github.com/mrdoob/three.js/blob/r160/manual/en/shadows.html), [nombreux objets](https://github.com/mrdoob/three.js/blob/r160/manual/en/optimize-lots-of-objects.html).
- [W3C — WebRTC Security Architecture](https://www.w3.org/TR/webrtc/) et [MDN — WebRTC data channels](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels) : transport et cadre de sécurité ; validation et autorité du jeu restent à construire autour.
- [OWASP — Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) et [HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) : liste de valeurs admises, frontières de confiance et stockage ; les recommandations de session sont adaptées au pair-à-pair, sans inventer un serveur WebSocket.
- [W3C APG — Modal Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) et [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/basic/) : navigation, focus, entrées et lisibilité.

Le [tableau de couverture](COUVERTURE-QUALITE.md) conserve les héros, familles, zones et systèmes qui restent à traiter. La [note portes et matières](PORTES-MATIERES-1.5.md) détaille le correctif mécanique et les contrôles exécutés.
