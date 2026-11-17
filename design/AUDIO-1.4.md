# Audio de proximité et transport — 1.4

Cette passe garde les trois thèmes et les sons synthétiques originaux. Elle traite la direction des signaux de combat, le volume et la durée de vie des sources. Elle ne livre ni enregistrement orchestral, ni doublage, ni simulation acoustique complète.

## Sources consultées le 17 novembre 2026

- [MDN — Audio for Web games](https://developer.mozilla.org/en-US/docs/Games/Techniques/Audio_for_Web_Games) : mixer les familles de sons, conserver le contrôle utilisateur et utiliser l’information spatiale dans le jeu.
- [MDN — StereoPannerNode](https://developer.mozilla.org/en-US/docs/Web/API/StereoPannerNode) : panoramique stéréo à puissance égale. Choix adapté ici à la caméra du jeu, avec un coût inférieur à une scène HRTF complète.
- [MDN — AudioScheduledSourceNode.stop](https://developer.mozilla.org/en-US/docs/Web/API/AudioScheduledSourceNode/stop) : arrêter aussi une source dont le démarrage était planifié dans le futur.
- [MDN — AudioParam.cancelScheduledValues](https://developer.mozilla.org/en-US/docs/Web/API/AudioParam/cancelScheduledValues) : remplacer les automations de gain quand l’état ou le volume change.

Ces références décrivent les API. Les réglages de durée, de priorité et d’atténuation ci-dessous sont des choix propres à notre jeu, à évaluer à l’écoute.

## Implantation

`playWorldSound(kind, strength=1, position=null)` garde les anciens appels compatibles. Une position est un objet `{x, z}`, par exemple l’ennemi qui prépare son attaque. Sans position, le signal reste centré.

- Le personnage est l’origine d’écoute. L’axe droit de la caméra détermine la stéréo, ce qui conserve le rapport gauche/droite visible à l’écran.
- La distance réduit progressivement le gain ; les signaux au-delà de 36 unités ne créent pas de source. Le panoramique reste borné à ±0,9 pour garder une présence sur les deux oreilles.
- Les menaces (`threat`) ont une montée brève suivie d’un grondement plus long ; les impacts (`impact`) gardent une réponse courte et plus basse. Le signal de menace complète la préparation visible, sans la remplacer.
- Les pas de la Lame calibrée suivent `motionFootstepSerial`, incrémenté par ses contacts d’appui. Changer de modèle, réinitialiser son compteur ou reprendre après pause ne crée pas un faux pas. Les personnages sans ce nouveau contrat gardent leur espacement sonore précédent.
- Un bus maître applique le volume une seule fois après le limiteur, y compris aux retours de réverbération. Le réglage zéro coupe aussi les sons et les queues de salle déjà en cours.
- Les bus musique, monde et confirmations d’interface restent distincts. La pause arrête les sources musicales en cours et planifiées, les sons du monde et l’accumulation des pas ; les confirmations de choix ou de fin peuvent encore être jouées.
- Au maximum 16 événements courts sont admis simultanément. Une menace peut prendre la place d’un pas ; des appels répétés de même priorité sont abandonnés à saturation. Les petites couches de grave peuvent utiliser une seconde source par événement. Une éviction garde une extinction de 10 ms, donc ce plafond d’événements actifs n’est pas une promesse de seulement 16 nœuds AudioNode.
- Chaque source terminée déconnecte ses oscillateurs, filtres, gains et éventuel panoramique. Les voix musicales longues conservent leur propre registre et ne sont pas évincées par les tirs.

`playTone(freq, dur=.06, type='sine', volume=.025, position=null)` expose la même signature que l’ancienne fonction `tone`. Le contrôleur peut déléguer à ce helper : les confirmations passent alors par le limiteur et le volume maître, avec un nettoyage à la fin. Les paramètres d’amplitude ne doivent plus être multipliés ailleurs par le volume maître.

## Vérification

`tests/spatial_audio.py` charge uniquement le module source et utilise `OfflineAudioContext` dans Chromium avec le GPU désactivé. Il rend de vrais échantillons PCM stéréo et contrôle :

- inversion gauche/droite avec la caméra et atténuation avec la distance ;
- énergie divisée par quatre lorsque le volume est divisé par deux, pour les effets et les confirmations ;
- silence exact à zéro, y compris après le début des notes et de la réverbération ;
- signatures temporelles différentes de menace et d’impact ;
- plafond des événements, rejet à saturation, priorité et déconnexion après la fin ;
- arrêt de la file musicale, remise à zéro des pas et consommation unique des événements d’appui.

Ces mesures évitent des régressions techniques. Elles ne constituent pas une validation artistique du mix, un essai avec casque/haut-parleurs physiques ni une mesure de performance sur téléphone. Une menace doit aussi rester identifiable visuellement ; son volume et sa place dans la musique devront être revus dans une vraie rencontre à vitesse normale.

`tests/story_sound.py` passe également sur le jeu intégré : chronique, pause/reprise, changements de thème et rendu PCM avec réverbération/limiteur.

## Limites ouvertes

La spatialisation livrée est stéréo et horizontale. Elle ne simule ni occlusion par les murs, ni hauteur, ni Doppler, ni salles indépendantes. La musique reste procédurale et les sons de créature restent synthétiques. La priorité suivante est l’écoute de la rencontre de référence : préparation comprise sans ambiguïté, contact ponctuel, récupération audible et aucune fatigue due à la répétition.
