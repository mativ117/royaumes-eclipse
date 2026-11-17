# Le voyage doit être compris, entendu et ressenti

## Histoire présentée dans cette version

Le soleil noir efface les noms plutôt que les vies. La Cathédrale retient encore leur mémoire ; les Souverains ont oublié ceux qu’ils protégeaient ; le colosse porte la dernière aube. Cette chaîne relie les objectifs existants sans remplacer leurs règles ou les sauvegardes.

Le menu présente le contexte du chapitre choisi. Le bouton **Récit** ouvre une chronique pendant la partie : enjeux, but du voyage et notes révélées selon l’avancement. Le temps de jeu s’arrête pendant la lecture ; Échap et le bouton Fermer rendent les commandes au joueur. Une conclusion n’est affichée dans la chronique qu’après la réussite du chapitre. Les dix héros restent accessibles et le onzième reste secret.

Le texte ne prétend pas à des dialogues doublés ni à des cinématiques : ces éléments ne sont pas présents. Les serments et les routes ont leurs conséquences de jeu existantes ; cette passe n’invente pas de fins alternatives.

## Direction musicale originale

Trois thèmes de huit mesures, composés dans `src/story-audio.js`, avec fondamentales, tempos et motifs distincts. Des voix graves, des intervalles tenus et un motif aigu accompagnent l’exploration. Le combat ajoute une pulsation et des accents. Les changements de chapitre réinitialisent le thème ; la pause, la chronique et le bouton Son atténuent les bus.

La synthèse WebAudio, la réverbération stéréo et la compression s’exécutent localement, sans téléchargement, compte ou service de musique. Ce sont des compositions synthétiques originales, pas des enregistrements orchestraux. Les réglages de volume musique et volume général sont conservés.

Les pas déclenchent une texture sonore selon le sol (bois du Convoi ou pierre). Tirs, passage de lame et impacts utilisent des transitoires filtrés distincts ; les anciens bips de ces trois gestes sont retirés. Les autres signaux d’interface et de pouvoir existants restent disponibles.

Le test `tests/story_sound.py` vérifie la navigation, la mise en pause, l’absence de révélation prématurée des fins, les changements de thème et le rendu réel en PCM stéréo. Il contrôle un signal non silencieux sans saturation dans la séquence d’essai ; cela ne remplace pas une écoute critique du mix complet.

## Cible de qualité pour les prochaines passes

La référence est un grand jeu fantastique cohérent dans notre univers. La version actuelle reste en deçà. Pour avancer, chaque passe doit se juger sur un résultat dans le jeu :

- **Combat** : anticipation compréhensible, contact net, réactions proportionnées, enchaînement sans glisse, retours visuels et sonores cohérents.
- **Niveaux** : silhouettes repérables, chemins qui s’apprennent, rencontres qui changent les décisions, moments de calme et surprises préparées.
- **Histoire** : but compris sans document extérieur, personnages qui ont des raisons d’agir, conséquences perceptibles et fins mises en scène.
- **Image** : proportions et matériaux cohérents, ombres fiables en mouvement, costumes expressifs et composition lisible sur téléphone.
- **Son** : thème reconnaissable, ambiances de lieu, plans de proximité et de distance, transitions musicales et impacts qui ne fatiguent pas.
- **Validation humaine** : durée réelle de 10–15 minutes, compréhension sans assistance et ressenti du mouvement. Les scripts contrôlés ne mesurent pas ces critères.

La prochaine amélioration de ces axes doit préserver les trois chapitres, les classes, les modes locaux, les profils et les archives. Elle ne doit pas être présentée comme une finition AAA obtenue par l’ajout de quelques effets.
