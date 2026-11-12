# La nef des serments — prototype 3D 0.6

Deux héros, trois salles et désormais des adversaires qui demandent de lire une direction plutôt que de tirer continuellement.

## Sentinelle

La Sentinelle a 160 PV et un bouclier frontal. Hors récupération, un impact venant de l’avant ne lui inflige que 15 % des dégâts normaux. Le flanc et l’arrière restent vulnérables. Les projectiles sont évalués selon leur direction d’arrivée ; les attaques de zone des pouvoirs ignorent le bouclier.

Elle tourne progressivement en garde. Avant une charge, elle annonce une direction puis la verrouille. La charge suit cette ligne, respecte les murs et obstacles et inflige 25 dégâts au contact. Une charge terminée ou bloquée laisse 2,6 secondes de récupération, bouclier abaissé. Les dégâts de contact ne se répètent pas sans respecter l’invulnérabilité normale du joueur.

Une Sentinelle remplace le gardien de la première salle, et une autre remplace un tireur dans la nef. Pas d’apparition infinie : les rencontres restent limitées et peuvent être contournées. Leur leurre cible les ombres d’Élan comme les autres ennemis.

## Cloche du Silence

Dans l’arène du Veilleur, une cloche se trouve sur le chemin d’entrée. En s’approchant, utiliser F ou le bouton contextuel. Elle annule les zones dangereuses et les projectiles ennemis présents, puis force une récupération de quatre secondes du boss. C’est une ouverture à utiliser au moment choisi, une seule fois par tentative de cette salle.

La cloche ne donne pas de dégâts gratuits et ne se réactive pas en appuyant plusieurs fois. Elle est réinitialisée avec la salle après une défaite. Son mouvement et son onde dorée signalent son activation.

## Contrôles, héros et limites

Les contrôles de la 0.5, les deux personnages, les serments, le secret et les points de reprise sont conservés. [Détails des héros](PROTOTYPE-0.5.md). Les graphismes restent des modèles procéduraux provisoires. Les autres niveaux, héros, comptes et modes réseau restent à développer.

## Vérifications

`tests/tactics.py` vérifie le bouclier directionnel, le flanc, la récupération, la direction verrouillée, l’arrêt sur obstacle, l’usage unique de la cloche, l’annulation des dangers et sa réinitialisation au point de reprise. Il teste aussi l’interaction de la cloche avec le Voltigeur en portrait et paysage, sans régression de pause sur une perte de focus.

`tests/heroes.py` vérifie les deux kits et la progression au corps à corps. `tests/publication.py` contrôle le paquet réellement publié et ses redirections. Vérifications dans Chromium avec mobile simulé ; le confort sur iPhone réel reste à confirmer.
