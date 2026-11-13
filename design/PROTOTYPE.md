# Le Carillon des Âmes — expédition 0.9

Un premier niveau complet dans le monde relié des Marches : début calme, quatre épreuves liées, rituel, gardien intermédiaire, boss final et retour. Les deux autres grands niveaux restent à produire.

## Présence et rythme 0.10

Guidage stabilisé, repères au sol à la demande, cibles conservées, pieds articulés et frappes plus engagées. Silhouettes ennemies différenciées et architecture propre aux ailes. [Détails et limites](FEEL-0.10.md).

## Lisibilité 0.9.1

La carte nomme les zones et montre les obstacles, portes et objectifs. Un journal permet de choisir l’objectif suivi ; son chemin praticable peut être désactivé. Les objets de quête ont des formes propres, leur état reste consultable et les libellés proches remplacent les grandes étiquettes distantes. Les sauvegardes 0.9 sont conservées. [Recherche et détails](LISIBILITE.md).

## Fil conducteur

La cathédrale a perdu sa voix. Le joueur libère une âme, retrouve un accord et réunit lumière et énergie pour réveiller le Carillonneur. L’âme secourue au début devient l’ancre qui permet de sortir à la fin.

| Étape | Décision ou défi | Cible de rythme, découverte |
|---|---|---|
| Atrium | Choisir héros et serment avec contrepartie | 30–60 s |
| Jardins | Guider une âme, disperser deux embuscades, explorer le détour secret | 90–120 s |
| Cloître | Lire une mélodie variable, accorder trois lanternes sous menace | 60–90 s |
| Archives | Affronter trois Reflets qui alternent absence et matérialisation ; le pouvoir les révèle | 75–120 s |
| Forge | Fermer trois vannes, éviter les jets, transporter un noyau jusqu’au refuge | 90–120 s |
| Nef | Charger deux sceaux, détruire les chaînes et battre le Carillonneur | 60–90 s |
| Cour | Veilleur à trois phases, cloche interruptive à usage unique, renforts | 90–150 s |
| Retour | Rejoindre l’âme sauvée, avant la fermeture de la faille | jusqu’à 70 s |

Ces budgets servent à viser une première partie de 10–15 minutes. Ils ne sont pas un résultat mesuré : le temps varie avec l’exploration, le héros et les défaites. Aucun chronomètre minimum ne bloque artificiellement l’avancée. Les deux premières épreuves et les deux ailes peuvent être traitées dans l’ordre choisi. Les 23 adversaires sont placés et finis, sans génération continue de vagues.

## Combat

La lame a trois coups : préparation visible, contact unique à 0,16 s (0,25 s au troisième coup), récupération. Les dégâts sont de 44 / 44 / 72 ; le troisième coup repousse davantage. Le fusil part après une préparation de 0,07 s. Les armes suivent le bras, le torse tourne, les ennemis arment leurs attaques, les impacts produisent étincelles et une courte suspension de 25 ms. Esquive et pouvoir interrompent l’attaque ; une charge non dépensée est rendue.

Le noyau ralentit le déplacement et occupe les bras. Attaquer, esquiver ou subir un coup le pose au sol : on peut dégager le chemin puis le reprendre. Le bouclier du Rempart permet de protéger son transport. Les Reflets demandent de choisir une fenêtre de vulnérabilité. Le Carillonneur reste protégé tant que ses chaînes subsistent. Le Veilleur change de phase à 65 % et 30 % de vie.

## Refuges et suivi

Les refuges restaurent les PV et le pouvoir et sauvegardent localement le héros, le serment, les épreuves et les ennemis vaincus. « Continuer » recharge le dernier refuge même après fermeture de la page. Le retour final possède son propre point de reprise ; le boss reste vaincu après une défaite lors de l’extraction. Une nouvelle expédition remplace la sauvegarde au prochain refuge. La victoire la supprime.

Un compteur mesure le temps actif réel : menus, pause et carte sont exclus. Le bilan copiable contient durée, défaites, héros et premiers passages dans les zones pour les essais d’équilibrage. Il reste local, sans compte ni envoi de données. La Marque du Reflet utilise une sauvegarde distincte.

## Sources et validation

`world.js` décrit les plateformes et obstacles ; `campaign.js` les rencontres et refuges ; `expedition.js` les épreuves et la sauvegarde ; `combat-motion.js` les contacts et poses ; `game.js` les contrôles, simulation et IA ; `template.html` l’interface. `scripts/build.py` génère une page autonome sans CDN.

`tests/expedition.py` vérifie toutes les transitions, l’escorte sur son vrai trajet, l’accessibilité physique des objectifs, les immunités, le transport, la reprise après rechargement, les contacts différés, les trois phases et la sortie. Certains états et dégâts sont contrôlés : ce test ne constitue pas un playtest de durée ou de difficulté. Les suites mobile et publication vérifient les gestes simultanés et les adresses du site. Les anciennes suites restent archivées.

## Limites actuelles

Deux héros ; modèles, animations et textures procéduraux. Pas encore d’assets finaux, de comptes, de coop, de battle ni de dénivelés parcourables. Les essais Chromium avec mobile simulé ne garantissent pas la fluidité sur iPhone réel. La durée cible nécessite les premiers bilans de parties humaines pour équilibrer les ennemis et déplacements.
