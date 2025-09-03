# XML to WEB App

![Python](https://img.shields.io/badge/Python-70.3%25-3776AB?style=flat-square&logo=python&logoColor=white)
![XSLT](https://img.shields.io/badge/XSLT-21.4%25-555555?style=flat-square)
![CSS](https://img.shields.io/badge/CSS-5.0%25-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-2.4%25-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![HTML](https://img.shields.io/badge/HTML-0.9%25-E34F26?style=flat-square&logo=html5&logoColor=white)

XML to WEB App est une application de bureau conçue pour le Centre de Musique Baroque de Versailles (CMBV). Son objectif est de faciliter l'édition et la publication de Philidor Vitrine, une édition numérique basée sur les données XML de la base de données PHILIDOR4.

Cette application permet aux utilisateurs de gérer le contenu éditorial (présentation, mentions légales, etc.) et de le transformer en un site web statique complet et stylisé, prêt pour la mise en ligne.

## Philidor Vitrine : objectifs

- **Offrir une entrée simplifiée et structurée** vers les données de Philidor 4, à destination d’un public plus large, moins familier des outils de recherche avancée.
- **Mettre en valeur le contenu** de la base à travers une présentation éditoriale, claire et organisée "à la manière d’un catalogue papier".
- **Respecter l'intégrité et la richesse de la base Philidor**, en se positionnant comme un **complément** à l’interface existante, et non comme un remplacement.

## Fonctionnalités

La vitrine statique est le résultat d'une transformation XSLT qui s’effectue via **un logiciel développé en Python**, ce dernier peut-être installé sur n'importe quel poste.

La vitrine statique est générée à partir d’**un fichier XML extrait de la base Philidor 4**, enrichi ponctuellement avec des données saisies directement dans le logiciel et le plus souvent issues d’une version antérieure de la base (*Philidor*).

- L'utilisateur complète l'ensemble des données éditoriales dans le logiciel.
- L'utilisateur charge le document XML via l'interface.
- L’application utilise la bibliothèque 
saxonche
 pour effectuer la transformation XSLT.
- Le site HTML est généré automatiquement et compressé dans une archive ZIP téléchargeable.

## Technologies utilisées

- **Python 3.x** : Le langage de programmation principal de l'application.
- **PySide6** : Framework utilisé pour la création de l'interface graphique du bureau.
- **XSLT 2.0** : Langage de transformation pour convertir les données XML en fichiers HTML.
- **XML** : Format pour le stockage des données structurées.
- **CSS** : Pour le stylisme de l'édition numérique générée, en respectant la charte graphique du CMBV.

## Installation et utilisation

Prérequis : Assurez-vous d'avoir **Python 3.x** installé sur votre système.

### Clonage du repository :

```bash
git clone https://github.com/bibliotheque-cmbv/philidorvitrine.git
cd philidorvitrine
```

### Installation des dépendances :

```bash
pip install -r requirements.txt
Lancement de l'application :

```bash
python -m main
```

Utilisation : L'application s'ouvrira avec une interface graphique. Vous pourrez naviguer entre les onglets pour éditer le contenu et lancer la transformation qui générera les fichiers du site web dans le dossier output.

## Attribution

Ce projet a été développé par Amélie Dogan pour le CMBV dans le cadre de son stage de master 2 "Technologies numériques appliquées à l'histoire" à Ecole nationale des chartes.

Ce projet est porté par :

- **La bibliothèque du Centre de Musique Baroque de Versailles (CMBV)**
- En dialogue avec le **pôle recherche du CMBV**, concepteur de la base Philidor 4

## Remerciements

Nos remerciements chaleureux vont à l’ensemble des équipes du CMBV ayant contribué à la structuration et à l’enrichissement de la base Philidor 4.
