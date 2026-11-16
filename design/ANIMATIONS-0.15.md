# Appuis et armes — 0.15

## Problème traité

Le tir remplaçait l’animation du corps entier : les jambes revenaient à une pose fixe alors que le contrôleur continuait de déplacer le héros. La même concurrence existait avec le bouclier et le transport. Le personnage pouvait ainsi sembler glisser ou flotter.

## Changements

- Les treize clips de chaque modèle sont séparés en canaux disjoints : racine/bassin/jambes et colonne/tête/bras/arme. Les jambes conservent leur marche pendant le tir, le bouclier et le transport. Esquive, bond et réaction à un impact gardent la priorité sur les deux parties du corps.
- La cadence des pas utilise le déplacement réel, y compris l’avancée des frappes. Les transitions marche/course préservent la phase. L’animation d’attaque ne redémarre pas le cycle des jambes.
- Une correction cinématique à deux segments place les pieds : phase d’appui, levée et trajectoire vers un prochain appui anticipé. Un appui reste fixe dans le monde tant que la jambe peut l’atteindre. Les chevilles restent à hauteur du sol ; les genoux se plient aussi pendant les pas latéraux et arrière. Le système se désactive pendant bond et esquive et se réinitialise aux reprises/sélections.
- Le fusil utilise une prise à deux mains : la main droite guide l’arme et la gauche rejoint un point de soutien solidaire de celle-ci. Le recul déplace légèrement l’arme et les poignets, avec une réponse de la colonne, du torse et du cou. La garde est conservée brièvement entre les tirs.
- Les modèles GLB ont été régénérés : point de soutien, culasse animée et gestes de lame révisés. Le flash du canon est bref et lumineux ; il suit le marqueur de bouche du canon.
- Les frappes de lame alternent les côtés puis utilisent un geste plus vertical ; préparation, passage rapide de la lame et retour en garde impliquent torse, colonne, tête, bras libre et poignet. Le passage de la lame est aligné sur les temps de contact existants : aucun changement de dommages ou de cadence de combat.

## Références consultées

- [Three.js — découper les pistes d’un clip](https://discourse.threejs.org/t/split-whole-model-animation-into-sub-model-animations-control-them-independently/62983) : animation indépendante de parties du corps, sans superposition de pistes concurrentes.
- [Three.js — système d’animation](https://threejs.org/manual/pages/animation-system.html) : pistes, clips, mixeur et transitions.
- [EA/DICE — animer Anakin dans Battlefront II](https://www.ea.com/en-gb/games/starwars/battlefront/news/anakin-skywalker-animations-interview) : intention, posture, appuis et personnalité du geste, plutôt qu’accumulation d’acrobaties. Les modèles et animations ici restent originaux.
- [GDC — Physical Animation in Star Wars Jedi: Fallen Order](https://www.gdcvault.com/play/1026848/Physical-Animation-in-Star-Wars) : résumé public consulté sur le mélange d’animation créée et de corrections physiques pour les transitions. Le système physique Unreal/PhysX de cette conférence n’est pas reproduit dans ce jeu Three.js.

## Vérification et limites

`tests/animation_layers.py` vérifie les canaux disjoints, les jambes actives pendant le tir en déplacement, la hauteur des appuis, leur stabilité, la prise à deux mains, la culasse, la priorité de l’esquive, le balayage réel de la lame et les réinitialisations. Les suites existantes couvrent le niveau complet, les pouvoirs, les refuges, les contrôles et la publication.

Le sol reste horizontal. Il ne s’agit pas encore d’une adaptation à des escaliers ou à un terrain accidenté, ni de capture de mouvement. Si un appui dépasse la portée de la jambe, sa position est rapprochée pour conserver le pied au sol : un glissement résiduel est possible aux changements brusques de direction ou lors des poussées entre acteurs. Les variantes de départ/arrêt, les réactions directionnelles des ennemis et les interactions avec le relief restent à développer. Fluidité sur téléphone réel à confirmer ; les contrôles tactiles sont vérifiés dans Chromium simulé.
