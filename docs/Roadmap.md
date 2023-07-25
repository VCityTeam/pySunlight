## Version 0.1 (30/06/2023) - Isoler le plugin vers Sunlight
  - Extraire le code minimal pour faire tourner `Sunlight` (3DUSE, libcityGML, openGL...).
    - Sauvegarder dans un nouveau [repository](https://github.com/VCityTeam/Sunlight).
  - Refactoring du projet.
    - Supprimer tout usage des classes de la librairie Qt (QDir, Qstring...).
    - Usage d'une librairie de [log](https://github.com/gabime/spdlog) (au lieu de code ad-hoc).
  - Vérifier que les résultats d'ensoleillement calculés de Sunlight sont identiques à ceux calculés avec 3DUSE.
  - Design notes du pipeline cible de production.
  - Benchmark des performances.

## Version 0.2 (14/07/2023) - Ajout du parser 3DTiles dans pySunlight
  - Fixer l'API de Sunlight et la wrapper en Python dans `pySunlight`.
  - Demander d'effectuer des calculs de Sunlight depuis pySunlight.
  - Parser des 3DTiles à l'aide de py3DTiler `TileReader` afin d'obtenir une liste de triangles.
  - Porter le main de Sunlight vers pySunlight puisqu'il dépend du parsing de fichier.
    - Transformer les 3DTiles en des 3DTiles avec des features en niveau de triangles afin de 
    d'associer des résultats à chaque triangle.
    - Convertir une listes de triangles par pySunlight en une liste de triangles avec des identifiants associés utilisable Sunlight.
  - Supprimer le code du parser libcityGML de Sunlight.
  - Portage du build de Sunlight en CMake afin de faciliter la fabrication du wrapper.
  - Benchmark des performances.

## Version 0.3 (28/07/2023) - Exporter les résultats de Sunlight par pySunlight
  - Gestion des résultats de Sunlight
    - Collecter les résultats de Sunlight dans pySunlight pour un time stamp donné.
    - Supprimer le code d'écriture des fichiers de résultats de Sunlight.
    - Générer un 3DTiles Sunlight contenant la géométrie ET les résultats de Sunlight 
    dans une batch table.
  - Ajout du triangle occultant dans le résultat.
  - Déploiement de la brique pySunlight.
    - Dockerisation pySunlight (le conteneur pySunlight ET le docker-compose
    pour son usage).

## Version 0.4 (11/08/2023) - Afficher les résultats dans Ud-Viz
  - Chargement d'un 3DTiles Sunlight produit par pySunlight.
  - Affichage des géométries des batiments (format 3DTiles) coloré par
    les résultat de Sunlight (à partir d'une date)
    - Le lien entre les triangles visualisés dans UD-Viz et les valeurs 
      dans la base est fait grâce aux identifiants de la batch table.
    - Coloration des triangles selon l'ensoleillement.
  - Création des aggrégats par bâtiment par jour et par heure.
  - UI de sélection des dates de début et de fin.
  - Timelapse de l'ensoleillement sur la ville.

## Version 0.5 (18/08/2023) - Lancer un précalcul de pySunlight
  - Création de la requête utilisateur (CLI)
    - Saisie des paramètres : 3DTiles, date de début, date de fin, fichiers 
    du chemin du Soleil selon la date
    - Formatage des entrées ([argparse](https://docs.python.org/3/library/argparse.html))
  - Usage de pySunlight dans un contexte docker (difficulté: comment passer
    des arguments de CLI a un runtime docker-compose).
  - Documentation utilisateur

## Version 0.6 (25/08/2023) - Polissage et Performances
  - Optimisation de Sunlight (librairies de raytracing...)
  - Corrections de bugs
  - Validation et retouches documentations (Développeur + Utilisateur)
  - Générer la doc Doxygen
  - Rendre le dépôt public
    - Écriture du Readme.md
    - Choix de la licence de droit
---

# Glossary
Sunlight : Code extrait du plugin Sunlight de 3DUSE et stocké dans son propre dépôt.  
pySunlight : Wrapper python effectuant le parsing et l'écriture des 3DTiles. Il demande à Sunlight de faire les calculs.  
3DTiles Sunlight : 3DTiles contenant la géométrie et une batch table hierarchy des résultats.