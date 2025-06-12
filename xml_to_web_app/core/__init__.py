"""
Module core - Gestionnaire

Ce module contient les classes de gestion principales :
- Project : Gère la logique métier des projets
"""

from .project_manager import (
    ProjectManager,
)

__all__ = [
    'ProjectManager'
]

# Version du module core
__version__ = '1.0.0'