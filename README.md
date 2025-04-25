# PhilidorVitrine

**PhilidorVitrine** est un projet initié par la **bibliothèque du Centre de Musique Baroque de Versailles (CMBV)**.  
Il propose une mise en forme alternative de la base de données **Philidor 4**, conçue par le **pôle recherche** du CMBV, sous la forme d’un site web statique organisé thématiquement.

---

## Objectifs

- **Offrir une entrée simplifiée et structurée** vers les données de Philidor 4, à destination d’un public plus large, moins familier des outils de recherche avancée.
- **Mettre en valeur le contenu** de la base à travers une présentation éditoriale, claire et organisée "à la manière d’un catalogue papier".
- **Respecter l'intégrité et la richesse de la base Philidor**, en se positionnant comme un **complément** à l’interface existante, et non comme un remplacement.

---

## Fonctionnement

La vitrine statique est générée à partir d’**un fichier XML extrait de la base Philidor 4**, enrichi ponctuellement avec des données issues d’une version antérieure de la base (*Philidor*).

La transformation s’effectue via **une application web développée en local avec Flask**, installée sur un poste de la bibliothèque du CMBV.

- L'utilisateur charge le document XML et la feuille de style XSLT via l’interface.
- L’application utilise Saxon/CHE pour effectuer la transformation XSLT côté serveur.
- Le site HTML est généré automatiquement et compressé dans une archive ZIP téléchargeable.

## Technologies principales

- **Python + Flask** : interface web locale
- **Saxon/CHE** : moteur XSLT en Python (via ```saxonche```)
- **HTML statique** généré intégralement via la feuille de style XSLT
- **Dossier ```statics/```** : contient les feuilles de style CSS, images et polices respectant la charte graphique du CMBV

---

## Institution partenaire

Ce projet est porté par :

- **La bibliothèque du Centre de Musique Baroque de Versailles (CMBV)**
- En dialogue avec le **pôle recherche du CMBV**, concepteur de la base Philidor 4

---

## Licence

Le projet est diffusé sous licence CC BY-NC-SA.

---

## Remerciements

Nos remerciements chaleureux vont à l’ensemble des équipes du CMBV ayant contribué à la structuration et à l’enrichissement de la base Philidor 4.

---

## Contact

Pour toute question ou contribution : bibliotheque@cmbv.com

