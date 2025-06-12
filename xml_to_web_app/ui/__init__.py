"""
Module ui - Interface graphique.

Ce module contient les classes de données principales :
- MainWindow : Fenêtre principale
- ProjectsListWidget : Widget avec la liste des projets et l'aperçu des
  informations sur chaque projet.
"""

from .main_window import (
    MainWindow,
)

__all__ = [
    'MainWindow',
]

# Version du module models
__version__ = '1.0.0'