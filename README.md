# vacances-scolaire-HA
Intégration Vacances Scolaire FR pour Home Assistant

Cette intégration personnalisée pour Home Assistant permet aux utilisateurs de récupérer et d'afficher les périodes de vacances scolaires en fonction de leur localisation. Les utilisateurs peuvent configurer la localisation et l'intervalle de mise à jour directement via l'interface de Home Assistant, offrant ainsi une flexibilité maximale. L'intégration utilise des données ouvertes du ministère de l'Éducation français pour fournir des informations précises sur les vacances scolaires. Compatible avec HACS, elle facilite l'installation et la mise à jour.

## Fonctionnalités

- **Affichage des vacances scolaires** : Montre les prochaines vacances scolaires ou les vacances en cours pour une localisation spécifique.
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
   - Choisissez la localisation (par exemple, "Nice", "Paris", "Bordeaux", etc.)
   - Définissez l'intervalle de mise à jour en heures


## Utilisation

Une fois installée et configurée, l'intégration Vacances Scolaires ajoutera un capteur à votre instance Home Assistant. Ce capteur affichera les informations sur les prochaines vacances scolaires ou les vacances en cours pour la localisation spécifiée.



## Contribution

Les contributions à ce projet sont les bienvenues. N'hésitez pas à soumettre des pull requests ou à ouvrir des issues pour des suggestions d'amélioration ou des rapports de bugs.
