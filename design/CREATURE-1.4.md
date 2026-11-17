# Fauche-Cendre : première famille ennemie de référence

## Sources primaires consultées le 17 novembre 2026

1. **Riot Games, bananaband1t, “Clarity in League”, 12 mars 2021** — [article du studio](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/). Le texte définit la clarté comme comprendre et pouvoir répondre, donne la priorité à la silhouette et à la direction perceptible, demande que l’attention visuelle corresponde à l’importance du danger, et que les effets correspondent aux hitboxes. Le texte et ses exemples ont été consultés, pas seulement son titre.
2. **Guerrilla, “The AI of Horizon Zero Dawn”, 17 octobre 2017** — [page du studio](https://www.guerrilla-games.com/read/the-ai-of-horizon-zero-dawn), [diapositives originales](https://www.guerrilla-games.com/media/News/Files/The-AI-of-Horizon-Zero-Dawn.pdf). Le résumé et les notes accessibles décrivent navigation pour agents de tailles différentes, combinaison HTN/utilité et coordination des groupes. Cela motive la conservation des voies d’approche et du nombre d’attaquants déjà limité dans le jeu. Il ne s’agit pas de prétendre réimplémenter leur IA.

## Application concrète

La famille `warden` devient un quadrupède bas : thorax et hanches modelés en surfaces continues, quatre pattes avec coudes/genoux, pieds, cou, mâchoire et queue articulés. Plaques dorsales et oreilles indiquent la direction ; le noir minéral distingue sa silhouette des humains armés. Une fissure sous le sternum et les yeux prennent davantage de lumière pendant l’anticipation. Les autres rôles restent intacts.

Le mouvement des pattes suit la distance réellement parcourue, pas une vitesse demandée par l’IA. Sans déplacement ni rotation, le cycle reste immobile. Les entités masquées sautent le calcul des poses et retrouvent des ancres neuves à leur retour. Les appuis se plantent dans l’espace ; les phases opposées donnent un trot diagonal. Pendant la préparation, la créature se ramasse puis relève les antérieurs avant une détente frontale courte. La récupération baisse le cou et rend la silhouette moins offensive.

La nouvelle attaque de référence est une préparation d’environ 0,8 s (0,78 s dans l’intégration), une détente frontale de 2,4 unités sur 0,32 s et une récupération de 1,4 s. Le module lit les durées réelles via `e.windupTotal`, `e.chargeDuration`, `e.recoveryTotal` et `e.timer`. Il ne déclenche aucun dégât, ne crée aucune hitbox et ne déplace pas l’entité : le télégraphe directionnel, la capsule d’attaque et les dégâts sont contrôlés par l’IA intégrée par le propriétaire du jeu. Le petit bond visuel est limité à 0,12 unité ; il ne remplace pas le déplacement physique.

## Contrat d’intégration

- Charger `src/creature-reference.js` après Three et le chargeur GLTF. `await initCreatureReference({data: base64})` accepte le GLB intégré ; à défaut, fournir `url` vers `obsidian-warden.glb`. L’erreur de chargement est remontée au propriétaire de l’écran de chargement.
- Après création complète des parties historiques : `buildCreatureReference(e)`. Renvoie `true` pour un warden prêt ; `false` pour les autres rôles ou si l’asset manque. Les autres rôles ne sont pas modifiés.
- Après `updateEnemy`, appeler `updateCreatureReference(e, dt)` ; si le retour vaut `false`, conserver `poseEnemy(e)`. La rotation visuelle est lissée comme auparavant. Les matériaux/meshes historiques du seul warden sont masqués à nouveau pour éviter leur réapparition lors d’un flash.
- Une option `{onContact(e,event)}` sert uniquement à brancher un retour d’atterrissage, jamais les dégâts. L’événement de type `landing` est émis une seule fois après une charge engagée, avec une séquence monotone. Une préparation interrompue ne produit aucun atterrissage. Les sons de touche réelle doivent provenir des contacts détectés par l’IA. L’événement peut aussi être lu dans `e.creatureReference.lastEvent`.
- Appeler `disposeCreatureReferenceRoot(o)` à l’entrée du nettoyage générique `cleanupObject(o)` : le propriétaire est retrouvé par WeakMap, y compris à la fin d’une chute. `disposeCreatureReference(e)` reste disponible pour un appel explicite. Géométrie et textures du modèle sont partagées ; squelettes et matériaux d’instance sont libérés. Ne pas disposer la géométrie partagée. `restoreLegacy:true` est prévu pour un retour explicite au visuel précédent.

La jauge de vie est abaissée à hauteur du quadrupède ; les PV, récompenses, contacts, projectiles, dangers, routes et règles d’attaque restent contrôlés par les fonctions existantes. Le volume central est bas et étroit ; tête, griffes et queue dépassent visuellement le contact circulaire existant de 0,48. La queue n’est pas une hitbox et ne peut pas bloquer un passage.

## Limites et validation

C’est une créature stylisée originale et articulée, pas une anatomie AAA ni une simulation de muscles/tissus. Les appuis supposent le sol plat actuel. Il faudra revoir le poids des contacts, l’échelle et la lisibilité sous les lumières de chaque zone, puis tester les performances sur téléphone physique. Les six clips du GLB sont des poses de revue ; le jeu emploie le mouvement procédural avec appuis.

Les tests CPU doivent couvrir remplacement limité au warden, indépendance des clones, phase basée sur déplacement réel, appuis, préparation/contact/récupération, émission unique et libération des ressources. Un rendu Blender documente la géométrie réelle ; il ne prouve pas la cadence du jeu ni la justesse des dégâts en situation.
