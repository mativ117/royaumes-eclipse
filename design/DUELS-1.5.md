# Duel et IA tactique locale — 1.5

Le **Cercle des deux lunes** ajoute un usage court aux héros existants. Le même cadre de combat sert à l’adversaire local et au duel LAN : collisions, contacts, protections, pouvoirs, dégâts et santé. Les dix héros ordinaires sont disponibles ; l’Éclipse incarnée dépend toujours du secret local. Entrer dans l’arène ne remplace ni le point d’aventure ni ses anciennes reprises.

## Règles et commandes

Le duel se conclut en **trois manches gagnantes**. Une manche dure au maximum 90 secondes. Santé et ressources sont rétablies entre les manches. Le héros, le personnage adverse et la difficulté se choisissent avant le lancement. Les commandes remappées, la manette et le tactile servent au même joueur dans tous les modes. Au terme d’une manche, le joueur ou l’hôte peut continuer ; l’invité attend la décision de l’hôte.

Le bot n’est pas un appel à une IA générative. `src/tactical-bot.js` calcule les décisions dans le navigateur, avec un générateur déterministe initialisé par une graine. Il ne contacte aucun service et ne modifie ni les points de vie, ni les dégâts, ni les délais de récupération pour se donner un avantage.

## Observation et décisions

Le bot utilise une perception retardée des signes publics : position visible, déplacement, protection et phase d’attaque. Le couvert et la portée limitent l’observation. Sa mémoire de dernière position est courte ; il peut rechercher l’adversaire au lieu de continuer à connaître sa position exacte derrière un obstacle. Ses propres ressources lui permettent de choisir un pouvoir utile, sans lire les touches adverses.

Les décisions sont recalculées à 10 Hz, avec engagement et hystérésis pour éviter une alternance à chaque image. Le planificateur peut approcher, garder une distance, contourner un obstacle, rechercher un couvert, se désengager, exploiter une récupération ou répondre à un projectile observé. Le déplacement reste soumis au contrôleur du jeu. Les attaques et esquives conservent leurs fenêtres et coûts ; une décision ne téléporte pas l’acteur, hors pouvoirs dont la permutation ou le franchissement est la règle explicite.

| Profil | Réaction perceptive | Mémoire | Intention |
|---|---|---|---|
| Vétéran | 0,24 s | 1,25 s | Visée moins précise et engagements plus longs |
| Tacticien | 0,16 s | 1,40 s | Ajustements de portée et de visée plus rapides, avec erreur et vitesse de rotation encore bornées |

Ces valeurs décrivent le code, sans garantir une difficulté adaptée à tous les héros. Le rythme de décision peut ajouter du délai à la réaction perceptive. La réponse n’est pas instantanée et le bot ne dispose pas d’une esquive parfaite de tous les tirs. Une difficulté équitable demande encore des parties humaines avec les onze kits.

## Différence avec les ennemis d’aventure

L’adversaire tactique utilise les héros et leurs capacités. Il n’ajoute pas une anatomie ou un nouveau comportement à toutes les créatures de campagne. Fauche-Cendre reste la première famille produite comme créature originale ; les autres familles et boss conservent leur chantier artistique et leurs limites, suivis dans [la couverture globale](COUVERTURE-QUALITE.md).

## Vérification et limites

`tests/tactical_bot.py` a passé les contrôles CPU de délai à plusieurs cadences, déterminisme, géométrie de couvert, réaction et absence d’appel réseau. Le test intégré `tests/session_actors.py` est écrit pour vérifier le vrai lancement, un déplacement prolongé, contacts/impacts et couverts, onze kits, manches, commandes répétées et retour à l’aventure. Sa réussite ne doit être annoncée que dans le relevé final après exécution.

Le [guide des modes](MODES-1.5.md) et les [frontières de confiance LAN](LAN-SECURITE-1.5.md) décrivent les variantes entre appareils. L’échange WebRTC réel et les téléphones physiques restent une validation distincte de l’IA et du pont de test en mémoire.
