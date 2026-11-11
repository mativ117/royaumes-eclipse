# Document de conception

## Identité

Titre : Les Royaumes de l’Éclipse. Dépôt : `royaumes-eclipse`.

Jeu navigateur sans Unreal, destiné aux PC et téléphones, avec jeu entre appareils comme objectif. Fantastique étrange : architectures monumentales, eau noire, brume orange, éclipses, silhouettes encapuchonnées et armes lumineuses. Les personnages auront des noms, histoires et visuels originaux.

Vue proposée : dessus légèrement incliné. Cette proposition reste à vérifier dans la première version jouable. Les images de référence donnent une direction artistique ; leur fidélité graphique n’est pas encore démontrée par le prototype.

## Structure d’une expédition

Trois niveaux successifs, chacun avec sa mécanique :

1. **La Cathédrale vivante** : exploration de salles changeantes, énigmes, pactes et choix de chemins pour trouver la sortie.
2. **La Chasse aux Souverains** : traque, découverte des faiblesses et affrontement d’un gardien qui transforme le terrain.
3. **Le Convoi de l’Impossible** : traversée sur une créature colossale, défense, escales et choix d’itinéraire.

Les choix d’un niveau influencent les suivants. Cible proposée : 8 à 12 minutes par niveau, à ajuster après essais. Sauvegarde entre niveaux en solo ; reprise de groupe en coop à concevoir.

## Combat

Mélange d’action rapide et de lecture tactique. Trois actions principales : attaque, esquive, pouvoir spécial. Variantes : hordes, duels, chasses, combats à règle spéciale, affrontements en mouvement et boss à plusieurs phases. Alterner avec exploration et rencontres.

Les dangers doivent être annoncés visuellement et par le son. Les mécanismes obligatoires restent réalisables seul, quel que soit le personnage. La coopération permet des combinaisons de pouvoirs sans imposer une composition d’équipe.

## Personnages

Les dix personnages sont disponibles dès le début, sans achat ni déblocage.

| Personnage | Identité de gameplay |
| --- | --- |
| Le Voltigeur | Bonds, rebonds et frappe au sol |
| Le Dernier Rempart | Tirs précis, bouclier frontal et charge |
| La Lame d’Éclipse | Parade, charge de lame et traversée offensive |
| La Tisseuse de Failles | Passages pour joueurs, ennemis et projectiles |
| Le Porte-Cendres | Accumulation de chaleur et libération contrôlée |
| Le Voleur d’Ombres | Double reproduisant une attaque et échange de position |
| La Bergère des Astres | Astre mobile de protection, attaque et attraction |
| Le Colosse de Porcelaine | Terrain transformé en marteau ou abri |
| L’Accordeur | Pulsations, rythme et interruptions |
| L’Enfant du Néant | Ombre combattante et transformation temporaire |

Les kits exacts et leurs commandes restent à détailler et équilibrer.

### Onzième personnage secret

**L’Éclipse incarnée** : armure noire fissurée d’or, cape de brume, couronne flottante et soleil noir. Attaque Fracture, esquive Passage obscur, pouvoir Soleil noir. Capacité supplémentaire **Incarnation**, alimentée par une jauge, avec transformation temporaire suivie de vulnérabilité. En battle, annonces et possibilités de contre doivent maintenir un équilibre avec les autres personnages.

Déblocage secret sauvegardé en trois étapes : suivre un reflet indépendant dans la Cathédrale ; comprendre et répondre au geste d’un Souverain ; découvrir une escale invisible du Convoi et affronter son ombre. Réalisable avec chacun des dix personnages, seul ou en coop. Chaque participant qui termine une étape la valide pour son compte.

## Modes

- Solo : aventure complète, progression et secrets.
- Coopération : 2 à 4 joueurs, salons privés et complémentarité des pouvoirs.
- Battle : 1 contre 1 et 2 contre 2, salons privés par code pour commencer.

Règles de battle proposées, à tester : Duel d’Éclipse en trois manches gagnantes ; Couronne vivante où conserver une couronne rapporte des points, empêche d’attaquer et permet des passes entre partenaires. La progression ne donne aucun bonus de vie ou de dégâts.

## Comptes et progression

Pseudo public modifiable, adresse e-mail privée, connexion par code temporaire envoyé par e-mail et option Google. Mode invité avec sauvegarde locale et transfert lors de la création du compte. Liaison des méthodes de connexion, déconnexion et suppression du compte à prévoir.

Le compte conserve apparences, avancement, statistiques, étapes du secret et accès au personnage secret. Les dix personnages ordinaires sont toujours accessibles. Les pouvoirs extraordinaires d’expédition restent temporaires.

Solo et coop privée accessibles en invité comme cible. Le classement éventuel nécessiterait un compte ; un battle classé ne fait pas partie de la première version.

Les données personnelles et les secrets serveur ne doivent jamais être placés dans le dépôt. Le fournisseur d’authentification, la base de données et l’architecture réseau restent à choisir.

## Réalisation par étapes

1. Vérifier le plaisir de jeu dans une salle : deux personnages, ennemis, collisions, clavier/souris et commandes tactiles.
2. Construire une courte séquence de la Cathédrale avec un combat à règle spéciale.
3. Ajouter les autres personnages, puis les deux autres niveaux et le secret.
4. Développer et valider la coopération entre PC et téléphone.
5. Ajouter comptes, sauvegardes et transfert de progression invité.
6. Développer les deux formats de battle et les équilibrer.
7. Finaliser tutoriel, réglages, audio, accessibilité, performances et publication.

Cette séquence est une proposition de production, pas une liste de fonctionnalités déjà réalisées. Les étapes peuvent évoluer selon les résultats des essais.
