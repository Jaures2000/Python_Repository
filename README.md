Projet de Géolocalisation des Patrimoines – Python & Flask
🧭 Présentation du projet

Ce projet est une application web de géolocalisation développée en Python, permettant à des utilisateurs d’enregistrer et de visualiser sur une carte interactive leurs patrimoines géographiques (maisons, terrains, sites, etc.).

L’application repose sur une architecture claire combinant :

Flask pour l’interface web,

MySQL pour la persistance des données,

Folium / Leaflet pour l’affichage cartographique interactif,

une approche orientée objet (POO) pour la logique métier.

🎯 Objectifs du projet

Permettre à un utilisateur de :

s’inscrire et se connecter,

enregistrer un ou plusieurs patrimoines,

sélectionner un emplacement directement sur une carte,

visualiser uniquement ses propres patrimoines sur une carte.

Résoudre le problème d’écrasement des données lors de l’enregistrement de patrimoines ayant les mêmes coordonnées géographiques.

🧠 Problème traité : l’écrasement des données

Lors des premières versions, l’application risquait d’écraser des données lorsque plusieurs utilisateurs enregistraient des patrimoines avec les mêmes coordonnées (latitude, longitude).

✅ Solution adoptée

Le problème a été résolu par une refonte de la base de données :

Création d’une table utilisateur

Création d’une table patrimoine

Mise en place d’une relation 1 utilisateur → N patrimoines

Chaque patrimoine est lié à un utilisateur via une clé étrangère (id_user)

👉 Ainsi :

Deux utilisateurs peuvent enregistrer un patrimoine au même endroit sans conflit

Les données sont correctement contextualisées

L’écrasement est définitivement éliminé

🗄️ Base de données (MySQL)
Table utilisateur

id_user (clé primaire)

nom_utilisateur

mot_de_passe

date_creation

Table patrimoine

id_pat (clé primaire)

nom_patrimoine

latitude

longitude

id_user (clé étrangère)

date_ajout

Relation :

UTILISATEUR (1) ─────── (N) PATRIMOINE

🧱 Architecture du projet
Projet_Personnelle
│
├── app.py                  # Application Flask principale
├── config.py               # Configuration MySQL
│
├── database/
│   └── mysql_db.py         # Connexion et requêtes MySQL
│
├── models/
│   ├── utilisateur.py      # Classe Utilisateur (POO)
│   └── patrimoine.py       # Classe Patrimoine (POO)
│
├── templates/
│   ├── index.html          # Page principale
│   ├── ajouter.html        # Ajout de patrimoine
│   └── login.html          # Connexion utilisateur
│
├── maps/
│   ├── carte.html          # Carte générée (Folium)
│   └── selection.html      # Carte de sélection
│
├── static/
│   └── css/                # Styles
│
└── requirements.txt

🧑‍💻 Fonctionnalités principales

Inscription et connexion des utilisateurs

Gestion des sessions Flask

Ajout de patrimoines liés à l’utilisateur connecté

Sélection d’un emplacement par clic sur la carte (Leaflet)

Remplissage automatique latitude / longitude

Affichage cartographique filtré par utilisateur

🗺️ Cartographie

Leaflet est utilisé côté interface pour :

cliquer sur la carte

récupérer dynamiquement les coordonnées

Folium est utilisé côté serveur pour :

générer des cartes HTML

afficher les patrimoines enregistrés

▶️ Lancer le projet

Installer les dépendances :

pip install -r requirements.txt


Configurer la base MySQL dans config.py

Créer les tables MySQL

Lancer l’application :

python app.py


Accéder à :

http://localhost:5000

📌 Remarques pédagogiques

Le projet privilégie la clarté de la logique métier

Les commentaires dans le code expliquent le pourquoi, pas seulement le comment

La sécurité (hash des mots de passe) peut être améliorée mais n’était pas l’objectif principal

🏁 Conclusion

Ce projet démontre qu’avec Python, il est possible de concevoir une application complète intégrant :

base de données relationnelle,

interface web,

géolocalisation interactive,

architecture logicielle propre.

Il illustre également l’importance d’une bonne modélisation des données pour éviter des problèmes critiques comme l’écrasement des informations.

Avec Python, rien n’est impossible.