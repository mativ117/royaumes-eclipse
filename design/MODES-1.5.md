# Modes utiles — aventure, adversaire tactique et réseau local

Le choix solo de la version 1.4 reste conservé dans son archive. L’utilisateur a ensuite demandé un adversaire local avancé et une connexion entre appareils du même réseau, **y compris entre téléphones sans PC**. La livraison 1.5 présente ces trois usages dans un sélecteur unique ; les anciennes options de clavier partagé, groupes et Couronne ne sont pas réintroduites.

## Aventure et adversaire tactique

L’aventure conserve ses chapitres, ses héros, son personnage secret et ses sauvegardes. Le duel du Cercle des deux lunes se joue en trois manches gagnantes avec un adversaire calculé localement, sans appel API. Son personnage et sa difficulté sont choisis au menu. Les dix héros ordinaires sont proposés ; le personnage secret reste soumis au déblocage local.

La construction du duel ne remplace pas le point d’aventure ni les anciennes reprises. Une manche restaure les ressources des deux adversaires. Les décisions et limites du bot sont décrites dans [la note du duel et de l’IA](DUELS-1.5.md) ; son intelligence ne constitue pas une garantie de difficulté ou de plaisir sans essais humains.

## Téléphone ↔ téléphone, téléphone ↔ PC et PC ↔ PC

Le réseau local utilise un canal de données WebRTC direct. Le navigateur hôte calcule les déplacements, collisions, pouvoirs, santé et résultat. L’autre appareil envoie uniquement ses intentions et affiche des instantanés validés, avec prédiction de déplacement et réconciliation contre les obstacles. Il ne calcule pas ses propres dégâts ni sa santé.

Le transport ne configure aucun serveur STUN/TURN et n’appelle aucun service de rendez-vous. Les appareils doivent pouvoir communiquer directement sur le réseau local. Pour les relier sans serveur :

1. Ouvrir le jeu sur les deux appareils et choisir **Duel en réseau local**.
2. Le premier joueur crée une invitation et partage ou télécharge le fichier.
3. L’autre joueur ouvre ce fichier dans le jeu et renvoie la réponse préparée.
4. Le créateur ouvre la réponse. Le jeu n’indique « connecté » qu’après l’ouverture réelle du canal.
5. Chacun prépare son personnage ; l’hôte lance le duel.

Le partage natif dépend du navigateur et du système. Téléchargement et échange de code sont proposés en remplacement. Le jeu ne demande ni caméra ni micro. Les fichiers et codes restent en mémoire et sont effacés de l’interface à la connexion ou à la fermeture ; ils ne sont pas placés dans les profils, les sauvegardes ou les diagnostics. Ils expirent après dix minutes. Partager ces invitations avec son partenaire est nécessaire : elles contiennent des informations temporaires de connexion.

Un réseau invité, l’isolation Wi-Fi, une politique de navigateur ou une restriction de réseau local peut empêcher la connexion. L’interface annonce alors l’échec ; elle ne remplace pas ce canal par une fausse session ni par un relais externe. Le jeu initial et les modèles restent servis par le site web ; « sans serveur de partie » ne signifie pas que les fichiers du site sont disponibles sans premier chargement.

## Synchronisation et protections

- L’hôte et le client ont des rôles différents. Les paquets sont typés, bornés en taille et en quantité, associés à la session et munis d’une séquence monotone.
- Le client ne peut pas envoyer un instantané autoritaire. Une modification de santé locale est remplacée par le prochain état de l’hôte.
- Les entrées périmées sont neutralisées. La pause et les échanges réseau continuent d’être gérés hors de la simulation de jeu. Une déconnexion arrête le duel ; revenir au menu ferme les ressources.
- Les identifiants des attaques sont conservés entre instantanés pour ne pas recommencer une animation à chaque paquet. Les effets persistants, abris et projectiles sont reproduits sans exécuter leurs dégâts sur le client.
- Une partie sans serveur de confiance ne protège pas contre un hôte qui modifie sa propre simulation. Aucun classement ou mécanisme d’anti-triche compétitif n’est annoncé.

Voir la note de protocole et de sécurité pour les frontières exactes et les références primaires.

## Ce que les tests peuvent prouver

`tests/lan_game.py` prépare deux vrais contextes du jeu, PC et tactile simulé, reliés par un **transport en mémoire explicitement réservé au test**. Le protocole de production valide les paquets de ce pont. Ce scénario contrôle l’interface de fichiers, les rôles, le déplacement et les dégâts calculés par l’hôte, les pauses, les manches, la déconnexion, les sauvegardes et les erreurs JavaScript. Il ne prouve pas une connexion native WebRTC ni un réseau Wi-Fi physique.

`tests/lan_peer.py` contrôle séparément le transport. Le Chromium géré de cet environnement impose `WebRtcIPHandling=disable_non_proxied_udp`, ce qui empêche la collecte de candidats natifs locaux. Ce blocage doit être rapporté comme **SKIP du handshake natif**, sans changement de navigateur ou de politique pour le contourner. La compatibilité Safari/Chrome sur deux téléphones physiques et sur différents routeurs reste à vérifier.

Les tests de jeu sont préparés pour une exécution GPU séquentielle par le responsable de livraison ; cette note ne déclare pas leur réussite avant le relevé de validation.
