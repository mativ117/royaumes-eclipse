# Réseau local — frontières de confiance et contrôles 1.5

Le périmètre est un duel entre deux navigateurs, dont téléphone ↔ téléphone sans PC obligatoire. Les appareils échangent une invitation et une réponse manuellement ; aucun serveur de rendez-vous, STUN, TURN, compte ou appel à une IA distante n’est configuré. Le site et les modèles restent téléchargés depuis leur hébergement habituel : cela ne constitue pas une promesse de jeu entièrement hors ligne.

## Architecture et confiance

`src/lan-peer.js` emploie le `RTCDataChannel` du navigateur. La configuration est `iceServers: []`, avec un canal ordonné fiable nommé `eclipse-lan-v1`, protocole `eclipse/1`. Le navigateur assure le transport DTLS lorsqu’une connexion aboutit. Les empreintes publiques DTLS sont incluses dans les descriptions échangées ; le programme n’implémente pas sa propre cryptographie et ne réclame ni microphone ni caméra.

L’appareil qui crée l’invitation calcule la simulation. L’invité transmet uniquement ses intentions ; les positions, dégâts, santé, pouvoirs et résultats viennent de l’hôte. Cette autorité limite les falsifications de l’invité ; elle ne rend pas l’hôte digne de confiance par magie. Un propriétaire de navigateur peut modifier son propre code. Aucun anti-triche compétitif ni authentification d’identité distante n’est annoncé. L’appairage est destiné à des personnes qui se connaissent et choisissent de partager leurs invitations.

Le rôle est attaché à l’objet de connexion, pas à une propriété envoyée par l’autre joueur. Le protocole, indépendant du rendu et de la simulation, est dans `src/lan-protocol.js`.

## Contrôles appliqués

| Frontière | Contrôle |
|---|---|
| Page exécutée | Contexte sécurisé requis ; lien HTTPS du jeu ou origine locale considérée fiable par le navigateur. Aucun contournement des politiques du navigateur. |
| Invitation/réponse | Format et version explicites, identifiant de session aléatoire de 256 bits, type attendu, expiration à dix minutes, horloges bornées et réponse liée à l’invitation en attente. Une seule réponse est acceptée. |
| Description de connexion | SDP ASCII de 32 Kio maximum, nombre et longueur des lignes bornés, un seul média `application`, empreinte SHA-256 et paramètres ICE requis. Pas de piste audio/vidéo. |
| Destinations ICE | Candidats `host` sur adresses privées, lien local, boucle locale ou noms mDNS `.local` seulement ; aucune adresse de serveur externe, candidat réflexif ou relais accepté. Les destinations publiques sont retirées de la description locale et refusées à l’import. |
| Messages | JSON texte de 64 Kio maximum avant désérialisation ; clés et types autorisés, nombres finis bornés, listes limitées, clés de prototype, getters, symboles et propriétés supplémentaires refusés. Ni `eval`, ni interprétation de HTML provenant du pair. |
| Actions autorisées | L’hôte reçoit `hello`, `ready`, `input`, `request`, `ping`, `bye`. L’invité reçoit `hello`, `start`, `pause`, `snapshot`, `ping`, `bye`. Un paquet d’état reçu d’un invité provoque l’arrêt de la connexion. |
| Entrées | Axes dans `[-1,1]`, angle normalisé et boutons booléens. Aucun champ de position, santé, dégâts, identité de slot ou téléportation n’est accepté dans `input`. |
| États et visuels | Exactement deux slots distincts ; onze identifiants de héros et leurs PV maximums vérifiés contre le roster. Au plus 64 projectiles, 24 effets et trois volumes par abri. Un portail exige une sortie finie complète. Les durées et identifiants d’animation sont bornés. |
| Rejeu et débit | Session épinglée, séquence strictement croissante ; plafond global de 80 messages/s avec rafale bornée, entrées 40/s, états 30/s et pings 2/s. Les valeurs sont des limites du protocole, pas des objectifs d’envoi. |
| File d’envoi | Envoi refusé si le tampon dépasserait 128 Kio ; un état abandonné n’est pas conservé dans une deuxième file applicative. |
| Connexion perdue | Battement hors de la boucle du jeu ; après huit secondes sans réception, arrêt lorsque les timers du navigateur sont exécutés. Les pauses longues de l’OS peuvent suspendre ces timers. |
| Nettoyage et confidentialité | Fermeture du canal et du pair, annulation des timers et effacement de l’identifiant de session de l’objet. Diagnostics limités à des compteurs et états, sans SDP, empreinte, adresse ou jeton. Aucun stockage de SDP ou de sauvegarde dans ces deux modules. |

L’alias et le héros choisis sont les métadonnées de présentation utiles. Les sauvegardes, courriels, statistiques du profil et données de progression ne font pas partie du protocole. La couche d’interface doit également vider ses fichiers et champs d’appairage à la fermeture ; les fichiers explicitement téléchargés ou partagés restent sous le contrôle de la personne.

## Vérifications du 23 novembre 2026

- `python tests/lan_protocol.py` : **PASS CPU**. Onze héros et PV cohérents ; invitations expirées/étrangères, candidats publics, types illégitimes, NaN/Infini, dépassements, objets de prototype et accesseurs, coordonnées de portail absentes, autorité, séquences et rafales testés.
- `python tests/lan_peer.py` : **PASS des tests de module**, avec un double RTC déterministe. Appairage, exigence HTTPS, rôles, refus de rejouage et de messages trop grands, file d’envoi, expiration, battement et nettoyage sont contrôlés. Ce double ne simule pas la cryptographie DTLS.
- Le même script démarre Chromium sans GPU et sonde la collecte ICE native. Dans cet environnement, **zéro candidat natif** est fourni. La politique gérée `WebRtcIPHandling=disable_non_proxied_udp` est présente. La préparation d’invitation échoue proprement, ne prétend pas être connectée et libère les ressources : **PASS du chemin d’échec**. Aucun appel à une API ou à la capture média n’est effectué.
- **SKIP du transfert WebRTC réel et du test entre téléphones physiques.** La politique gérée n’a été ni désactivée ni contournée par des flags, un autre navigateur ou un serveur de relais. Rapport local : `/tmp/royaumes-lan-transport-report.json`. L’option `--require-direct` fait échouer le contrôle si la connexion directe n’est pas vérifiable ; l’exécution standard signale explicitement le SKIP.

La vérification de la synchronisation du jeu est distincte de celle du transport réseau. Un test de simulation avec un canal en mémoire ne prouve ni un échange DTLS réel, ni la compatibilité du routeur ou d’iOS/Android. Les deux doivent rester identifiables dans le relevé de livraison.

## Références primaires

Consultées le 23 novembre 2026 :

- [MDN — WebRTC connectivity](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity) : descriptions de session, offre/réponse et canal de signalisation. Ici, le partage manuel tient ce rôle.
- [MDN — Using WebRTC data channels](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels) : canal, négociation et DTLS assuré par le navigateur.
- [MDN — `RTCDataChannel.bufferedAmount`](https://developer.mozilla.org/en-US/docs/Web/API/RTCDataChannel/bufferedAmount) : observation de la file avant envoi.
- [OWASP — WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html) : validation, autorisation par message, rejeu, quotas et journalisation minimale. Ces principes sont transposés au DataChannel ; aucun serveur WebSocket n’est ajouté au jeu.
- [WebKit — bug 174500](https://bugs.webkit.org/show_bug.cgi?id=174500), **RESOLVED FIXED** : historique de la restriction des connexions directes sans capture et prise en charge mDNS. Ce cas historique ne justifie pas de demander un accès au micro pour jouer. Il ne prouve pas que toutes les versions de Safari et tous les réseaux ont été testés ici.
- [Chrome Enterprise — liste des politiques](https://chromeenterprise.google/policies/#WebRtcIPHandling) : contexte des restrictions d’administration du navigateur.

