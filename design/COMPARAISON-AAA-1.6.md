# Comparaison de qualité — référence AAA et passe 1.6

Point de production du 24 novembre 2026, à partir de la version publiée 1.5-rc1. L’utilisateur demande de rapprocher le jeu entier du niveau des meilleures productions de référence. La comparaison conduit à produire des créatures, une composition des lieux, une caméra et une présentation sonore cohérentes. Elle ne permet pas de déclarer une équivalence AAA obtenue.

**Ghost of Tsushima** sert de référence AAA pour la lisibilité, la réponse du combat et la continuité de l’expérience. **Clair Obscur: Expedition 33** sert de référence de qualité artistique, d’identité des lieux, de récit et de son. Il ne s’agit ni de copier leurs ressources, ni de comparer des budgets ou des moteurs comme s’ils étaient identiques. Notre jeu conserve le navigateur PC/téléphone, son univers noir/ambre, les onze héros et ses trois chapitres.

## Ce qui a réellement été examiné

- Code et ressources du jeu, suivi et [validation 1.5](VALIDATION-1.5.md).
- Trois captures du moteur en qualité Légère, avec caméra fixe et HUD masqué : [atrium](../docs/previews/r6-atrium-before.jpg), [cloître](../docs/previews/r6-cloitre-before.jpg), [chasse](../docs/previews/r6-hunt-before.jpg). Le [relevé avant](CAPTURES-DIRECTION-1.6-before.json) conserve version, empreintes et cadrages.
- Publications des développeurs indiquées ci-dessous. Leur lecture ne constitue pas une partie complète de ces jeux, ni le visionnage des conférences et vidéos associées.

Les images fixes montrent notamment une silhouette de héros dont les volumes internes se lisent peu, un pavage très régulier, des cylindres répétés dans le cloître et des garde-corps très réguliers. Dans la chasse, une grande forme sombre masque une partie du disque lumineux et reste difficile à interpréter depuis ce cadrage. Dans l’atrium, le grand disque attire davantage l’attention que les petits repères proches.

Ces constats portent sur les captures et leur résolution. Elles ne mesurent ni les mouvements, ni le son, ni les performances. Le protocole final attend le dégagement des portes et avance la simulation avant la revue fixe, afin de synchroniser contacts et visibilité. Le réglage Léger utilise les ombres de contact ; ces vues ne prouvent pas les ombres GPU de la qualité Haute. La palette noir/ambre et la monumentalité restent des choix artistiques à conserver.

## Références retenues et traduction dans notre univers

| Référence primaire | Principe retenu | Application recherchée ici |
|---|---|---|
| [Sucker Punch — Mastering the katana](https://blog.playstation.com/2020/06/23/ghost-of-tsushima-mastering-the-katana/) | Le studio relie vitesse, précision, son et réponse aux commandes ; les premières menaces doivent laisser au joueur une possibilité d’anticipation. | Donner aux attaques une préparation identifiable, un engagement, un contact et une récupération. Préserver les entrées réactives et éprouver la cohérence geste/dégât/son. |
| [Sandfall — Flying Waters](https://blog.playstation.com/2024/08/28/new-clair-obscur-expedition-33-gameplay-fighting-and-exploring-the-flying-waters-region/) | L’identité d’une région et les traces des expéditions précédentes portent la découverte ; personnages et boss ont des règles propres. | Faire reconnaître l’usage d’un lieu et la nature d’une menace. Donner aux familles de créatures une anatomie et une façon de combattre distinctes ; garder le récit lisible dans l’environnement. |
| [Sandfall / Unreal Engine — Development journey](https://www.unrealengine.com/developer-interviews/inside-the-development-journey-of-clair-obscur-expedition-33) | Le contexte musical est organisé selon les états d’expérience, dont exploration, combat et séquences narratives. | Composer des phrases et transitions adaptées au contexte. Conserver le master, le silence, la pause et la place des avertissements dans le mix. |
| [Guerrilla — The AI of Horizon Zero Dawn](https://www.guerrilla-games.com/read/the-ai-of-horizon-zero-dawn) | Le résumé officiel décrit navigation selon les gabarits, décisions d’utilité et coordination des agents. Le PDF et la conférence ne sont pas présentés comme consultés ici. | Relier gabarit visible, déplacement et couvert ; limiter les attaques simultanées et donner un comportement compréhensible à chaque famille. Aucun système Horizon reproduit n’est annoncé. |

Les valeurs de temporisation, de portée et de budget du projet restent nos choix à tester. Elles ne sont pas des prescriptions attribuées à ces studios.

## Écart observé et travail concret de la passe

La colonne « travail 1.6 » décrit les ressources et modules intégrés. Les résultats réellement obtenus figurent dans [la validation](VALIDATION-1.6.md) ; ils ne remplacent pas la revue artistique, le jeu humain ou les mesures matérielles.

| Critère | Base 1.5 et écart | Travail 1.6 | Travail encore nécessaire vers la cible |
|---|---|---|---|
| Créatures reconnaissables | Fauche-Cendre possède sa propre anatomie ; plusieurs autres familles gardent une construction commune. | Deux productions originales : archer à bras-arc et jambes digitigrades, raie du reflet avec tête, mandibules et ailes articulées ; modèles skinnés, matières, clips et sources éditables. | Autres familles, boss, variantes de silhouette et réactions à produire, puis revue de chaque rencontre. |
| Menace et réponse | Les règles existent, mais l’intention et la personnalité de plusieurs ennemis restent sommaires. | Intégration de comportements propres à l’archer et à la raie : préparation, direction engagée, émission/contact, récupération, couvert et gabarit. | Répéter les rencontres sans spam, éprouver contre-jeu, difficulté, fatigue et variété en parties humaines. |
| Composition des lieux | Grandes dalles, bordures abruptes, obstacles et arcades très répétés dominent les vues fixes. | Matières avec UV mondiales, incrustations dans la surface existante, soubassements continus et éléments de contexte propres aux chapitres dans `environment-direction-v16.js`. | Recomposer les autres séquences, la géographie, la verticalité et les transitions. Les chemins et le contrôleur plan ne deviennent pas du relief parcourable. |
| Cadrage et lecture du combat | Caméra de parcours éloignée ; héros et adversaires peuvent occuper peu de pixels. | Caméra solo rapprochée progressivement autour d’une menace, avec conservation d’une cible et maintien du cadrage de groupe dans `camera-direction-v16.js`. | Éprouver murs, piliers, menaces hors champ, portrait/paysage et confort. La capture fixe d’architecture ne prouve pas ce bénéfice dynamique. |
| Musique et effets | Trois motifs synthétiques et effets fonctionnels ; le silence, le master et la spatialisation sont déjà contrôlés. | Phrases musicales adaptatives et sons propres aux nouvelles créatures, en conservant les bus et limites de voix ; intégration sonore contrôlée en PCM. | Timbres, transitions, variantes, écoute sur appareils et mix de toutes les armes. Une synthèse originale n’est pas une bande-son orchestrale enregistrée. |
| Présentation du récit | Objectifs et chronique portent surtout l’exposition. | Courte présentation contextuelle des rencontres, sans nouveau menu ni pause imposée ; intégration contrôlée. | Dialogues incarnés, scènes, conséquences visibles et compréhension de l’histoire complète à produire. |
| Mouvement des héros | Onze kits et appuis contrôlés ; pas orientés et certaines esquives restent analytiques ou issus d’alias. | Base 1.5 préservée ; le nouveau cadrage expose davantage les gestes et leur lecture. | Animations directionnelles, raccords, expressions et drapés propres aux héros. Aucun nouveau tournage ou mocap n’est annoncé pour cette passe. |
| Technique et confort | Tests locaux et publics passés ; matériel simulé et WebGL logiciel. | Régressions de ressources, collisions, rendu, audio, campagne et modes passées sur le build intégré. | Mesurer chargement, mémoire, cadence et chauffe sur PC/téléphones identifiés. La qualité artistique exige aussi des essais humains. |

## Conditions de comparaison avant/après

Les vues d’architecture doivent conserver cadrage, résolution, qualité, position des acteurs et masquage du HUD. La caméra dynamique se juge séparément dans une séquence jouée à vitesse normale. Les tests doivent vérifier les fenêtres d’attaque, le contact, le son, les obstacles et la récupération ; un clip simplement plus long ou un ennemi plus résistant ne constitue pas une amélioration suffisante.

La revue doit inclure la Cathédrale, la Chasse et le Convoi, les onze héros, les nouvelles créatures, les familles conservées et les modes 1.5. Le LAN garde sa limite connue : protocole et synchronisation simulée contrôlés, connexion native entre téléphones encore à valider. Les sources, sauvegardes et anciennes livraisons restent à préserver.

## État de cette comparaison

Cette note établit les critères de production de la candidate 1.6 à partir de la base 1.5. Le [tableau de prise en charge](PRISE-EN-CHARGE-1.6.md) distingue la fabrication, l’intégration et les preuves encore requises. Les captures après et la validation de clôture documentent les contrôles exécutés et les limites conservées. Aucun pourcentage vers « AAA », note artistique calculée ou équivalence globale n’est déduit des tests.
