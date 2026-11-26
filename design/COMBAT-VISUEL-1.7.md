# Contacts et trajectoires — passe 1.7

26 novembre 2026, base publiée 1.6-rc1. La critique concerne la lecture visuelle des coups et des dégâts. Le code précédent superposait cercles au sol, boules lumineuses et étincelles omnidirectionnelles, sans exprimer clairement le matériau touché. Le critère de cette passe est un contact bref à hauteur du corps, orienté par le coup, distinct d'une attaque ratée ou bloquée, lisible à vitesse normale depuis la caméra du jeu.

`src/combat-feedback-v17.js` est une source originale éditable, sans ressource externe. Elle ne change ni dégâts, durée, portée, collision, déplacement ni protocole réseau.

- Un contact demande les PV **avant** application et lit les PV réels après application. PV identiques, hausse de PV et nombres invalides refusent tout effet. Les branches de bouclier/plaque emploient un signe angulaire séparé ; aucune prédiction de collision ne produit des dégâts visuels.
- La mêlée laisse une incision courte et une trace étroite issue des sockets réels. Leur fenêtre reprend `hitAt` et `activeEnd`, avec refus des discontinuités. Le contact utilise le segment de lame courant lorsqu'il est proche de la victime ; les signes ne dessinent aucune portée supplémentaire.
- Les tirs laissent des segments dans la portion réellement parcourue, arrêtée au mur par la simulation existante. Les anciennes sphères ennemies deviennent des pointes triangulaires partagées, longues de 34 cm, orientées selon leur vitesse ; leur matériau d'alerte demeure conservé.
- Pouvoir, projectile, lame et blocage ont des formes distinctes. Métal : traits fins clairs ; pierre/porcelaine : éclats mats ; tissu/créature : éclats courts de cuivre ; ombre : fragments sombres. Les onze héros possèdent des réglages de largeur, durée et teinte dans une palette ambre/os/noir.

Deux géométries dynamiques réutilisées regroupent lueurs et éclats mats : au plus deux appels de dessin supplémentaires, sans lumière ni texture. La petite pointe des projectiles réutilise leurs objets existants. Les traces facultatives réservent au moins 30 % du batch aux contacts et peuvent céder leur place à un vrai impact.

| Réglage | Lueurs / éclats simultanés | Événements / traces par pas |
|---|---:|---:|
| Haute | 72 / 24 | 8 / 24 |
| Léger | 36 / 12 | 5 / 14 |
| Effets réduits | 20 / 6 | 3 / 8, traces désactivées |

En effets réduits, le contact reste local et fixe, sans particules projetées. Changer de réglage applique immédiatement le plafond inférieur. Tous les effets expirent en moins de 0,34 s de simulation ; un nettoyage vide les buffers et les historiques de sockets. La destruction complète libère les deux matériaux, les deux buffers et la géométrie de pointe. Aucun timer, téléchargement, `eval` ou nouvelle permission CSP.

## Points d'intégration

1. Charger le module dans le bundle. Après la baisse de PV effective dans `game.damage`, `game.hurt` et le `partyHurt` de `session-modes.js`, appeler `combatFeedbackContactV17(victime, beforeHP, source)`. Annoter la source avec `feedbackKind: 'melee' | 'projectile' | 'power'`. Ne pas répéter le contact dans les appelants de dégâts.
2. Dans les seules branches réellement bloquées, appeler `combatFeedbackBlockV17(victime, source)`. Les grands signes de zone et télégraphes utiles conservent leur rôle.
3. Dans `authored-avatar.updateBladeTrail` et `session-modes.updateDuelBladeTrail`, déléguer à `combatFeedbackWeaponV17(actor, avatar, heroId, dt)` après pose/kinématiques, en masquant et vidant l'ancien ruban.
4. Après déplacement et résolution de mur d'une balle, appeler `combatFeedbackProjectileV17(b, oldX, oldZ, oldY)`. Après tous les contacts/poses du pas, appeler une fois `updateCombatFeedbackV17(dt)` pour remplir les buffers avant le rendu.
5. Appeler `clearCombatFeedbackV17()` depuis `clearFX` et `resetAvatarPose` : nouvelle salle, nouvelle manche et retour au menu ne gardent aucun effet. `disposeCombatFeedbackV17()` est idempotent pour une destruction complète.

Le LAN invité peut réagir à une baisse de PV reçue dans `lanPatchActor` : conserver les PV précédents seulement si `_lanInitialized` était déjà vrai ; comparer après application du snapshot. Le type de coup n'est pas transporté : `kind: 'contact'` reste un accent neutre, sans inventer mêlée ou pouvoir. Une nouvelle manche remet déjà `_lanInitialized` à faux. Poses et traces sont purement visuelles, sans recalcul de collision. Cette proposition d'intégration ne vaut pas validation du LAN.

## Vérification et limites

`python tests/combat_feedback_v17.py` : **PASS CPU** avec Three.js réel, sans navigateur/GPU. Couvre refus des faux contacts, invariance des données de jeu, onze profils/sockets et fenêtres actives, trajectoires réellement parcourues et refus des téléportations, petite pointe ennemie orientée, réserves/plafonds sous saturation, changement Haute/Léger, effets réduits fixes, expiration et destruction idempotente. Ce test ne valide ni esthétique, ni intégration réseau, ni cadence sur appareil physique.

La comparaison réelle avant/après et les régressions du build intégré relèvent du relevé de livraison. Aucune nouvelle capture ni revue humaine à vitesse normale n'est annoncée par ce contrôle CPU. La finition des animations des onze héros, des réactions des ennemis et du mix reste ouverte ; cette passe ciblée ne constitue pas une qualité AAA acquise.

Références méthodologiques réutilisées : [référentiel, mouvement/combat](REFERENTIEL-QUALITE.md#2-mouvement-attaques-et-sensations), [comparaison primaire Sucker Punch/Sandfall](COMPARAISON-AAA-1.6.md#références-retenues-et-traduction-dans-notre-univers), [procédure locale](skills/quality-pass/SKILL.md). Elles guident l'alignement intention/pose/contact/effets ; les valeurs et ressources de ce module sont originales.
