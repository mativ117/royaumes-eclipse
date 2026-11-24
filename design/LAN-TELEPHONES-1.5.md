# Duel sur le même réseau, y compris entre téléphones

Le module vise deux appareils qui ouvrent le jeu dans leur navigateur, sur un réseau personnel autorisé à faire communiquer ses clients. Le téléphone qui crée l’invitation peut héberger le duel : un PC n’est pas nécessaire. Le jeu ne contacte aucun service de rendez-vous ni API d’IA pour cette connexion.

## Appairage prévu

1. Ouvrir le lien **HTTPS** du jeu sur les deux appareils et choisir « Réseau local » ainsi que son personnage.
2. Sur le premier appareil, créer une invitation et la transmettre à l’autre personne avec le partage de fichiers du téléphone, un téléchargement ou le texte proposé par l’interface.
3. Sur le second, importer l’invitation ; il prépare une réponse. Renvoyer cette réponse au premier appareil.
4. Sur le premier, importer la réponse. Attendre l’état de connexion réelle, puis confirmer les joueurs prêts et démarrer le duel.

Le partage de fichiers utilise les fonctions disponibles sur l’appareil. Il ne choisit pas automatiquement un destinataire et ne publie pas les invitations. Le fichier n’est pas une sauvegarde du jeu : il contient des paramètres de connexion temporaires, notamment des informations de réseau et une empreinte publique. Le partager uniquement avec l’autre joueur et ne pas le publier. Une invitation expire après dix minutes et ne sert qu’à cet appairage.

Il n’y a pas de découverte automatique de tous les appareils Wi-Fi. Le navigateur a besoin d’échanger l’offre et la réponse avant de relier les appareils ; le partage manuel remplace ici un serveur de rendez-vous. Le transport ne demande ni compte, ni micro, ni caméra.

## Pendant la partie

L’hôte calcule le duel et l’autre appareil envoie ses commandes. Les métadonnées de progression et les sauvegardes restent locales. Garder les pages au premier plan : le système peut suspendre une page ou son réseau lorsqu’on change d’application. Une connexion perdue doit arrêter le duel plutôt que laisser un personnage avancer seul. Une nouvelle connexion est nécessaire après une rupture définitive ou un changement de réseau.

Le réglage Léger reste disponible sur téléphone. Aucune cadence sur iPhone ou Android physique n’est annoncée à partir des essais du navigateur de développement.

## Si la connexion échoue

Vérifier que les deux appareils sont sur le même réseau et que celui-ci autorise les échanges entre ses clients. Un réseau invité, une isolation Wi-Fi, une politique de navigateur, une autorisation d’accès au réseau local ou un filtrage mDNS peuvent empêcher l’appairage. Une invitation ancienne ou une réponse venant d’une autre invitation est refusée : recréer un appairage complet.

Le mode ne tente pas de contourner ces restrictions par une ouverture automatique de ports, une demande d’accès au micro, un serveur externe ou une modification des politiques de l’appareil. Les interfaces ne présentant que des adresses publiques, sans candidat local ou mDNS utilisable, ne sont pas prises en charge par ce transport volontairement local.

## État de validation

Les schémas de données, les limites et le cycle du module sont testés. Le navigateur géré de cet environnement interdit les candidats directs non proxifiés ; il n’a fourni aucun candidat ICE local. L’échec et le nettoyage sont vérifiés, mais le **transfert réel entre deux appareils reste à valider**, notamment Safari iOS ↔ Chrome Android. Un test du jeu avec un canal simulé ne remplace pas cette étape. [Détails de sécurité et résultats](LAN-SECURITE-1.5.md).

