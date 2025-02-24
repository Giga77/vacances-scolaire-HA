# vacances-scolaire-HA
Intégration Vacances Scolaire FR pour Home Assistant

Cette intégration personnalisée pour Home Assistant permet aux utilisateurs de récupérer et d'afficher les périodes de vacances scolaires en fonction de leur localisation. Les utilisateurs peuvent configurer la localisation et l'intervalle de mise à jour directement via l'interface de Home Assistant, offrant ainsi une flexibilité maximale. L'intégration utilise des données ouvertes du ministère de l'Éducation français pour fournir des informations précises sur les vacances scolaires. Compatible avec HACS, elle facilite l'installation et la mise à jour.

## Fonctionnalités

- **Affichage des vacances scolaires** : Montre les vacances en cours ou la prochaine pour une localisation spécifique par zone et/ou ville.
- **Indicateur booléen en_vacances** : Indique si l'on est en vacances. (true ou false)
- **Localisation personnalisable** : Permet de choisir la localisation pour laquelle on souhaite obtenir les informations sur les vacances scolaires.
- **Intervalle de mise à jour configurable** : Offre la possibilité de définir la fréquence de mise à jour des données.
- **Données officielles** : Utilise l'API officielle du ministère de l'Éducation française pour des informations précises et à jour.
- **Attributs détaillés** : Fournit des informations supplémentaires telles que les dates de début et de fin des vacances.

## Installation

1. Assurez-vous que [HACS](https://hacs.xyz) est installé.

2. Ouvrez HACS.

3. Sélectionnez "Intégrations".

4. Cliquez sur les trois points en haut à droite et choisissez "Dépôts personnalisés".

5. Ajoutez le dépôt :
   - URL : 'https://github.com/Master13011/vacances-scolaire-HA'
   - Catégorie : Intégration

6. Cliquez sur "Ajouter".

7. Recherchez "Vacances Scolaires" dans les intégrations HACS et installez-la.

8. Redémarrez Home Assistant.

## Configuration

1. Allez dans Configuration > Intégrations dans Home Assistant.
2. Cliquez sur le bouton "+" pour ajouter une nouvelle intégration.
3. Recherchez "Vacances Scolaires" et sélectionnez-la.
4. Suivez les étapes de configuration :
   - Choisissez soit par la Ville, soit par la Zone
      - Ville : Choisissez la localisation (par exemple, "Aix-Marseille", "Paris", "Bordeaux", etc.)
           - Veuillez respecter le découpage des villes -> https://www.education.gouv.fr/calendrier-scolaire-100148
      - Zone : Choissisez la Zone
   - Définissez l'intervalle de mise à jour en heures

![{258E39D5-FD11-412D-BC47-4C19B6FDA5B5}](https://github.com/user-attachments/assets/3b7d0038-141d-431a-b7c7-e056ff1b0815)


## Utilisation

Une fois installée et configurée, l'intégration Vacances Scolaires ajoutera un capteur à votre instance Home Assistant. Ce capteur affichera les informations sur les vacances en cours pour la localisation spécifiée.

![{640F061F-260B-4A7D-846C-6729C9AE6583}](https://github.com/user-attachments/assets/f5737c24-8952-46e7-88d1-79caf85c2617)



Le "state" retournera :

"Zone X - Holidays" ou "Zone X - Work"

## Contribution

Les contributions à ce projet sont les bienvenues. N'hésitez pas à soumettre des pull requests ou à ouvrir des issues pour des suggestions d'amélioration ou des rapports de bugs.
