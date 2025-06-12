"""
Module models - Modèles de données pour l'application de transformation XML.

Ce module contient les classes de données principales :
- Project : Représente un projet avec son contenu HTML
- XMLData : Encapsule les données XML importées de la base de données
"""

from .project import (
    Project,
    ProjectValidationError,
    validate_project_name,
    validate_html_content
)

from .xml_data import (
    XMLData,
    XMLDataError
)

__all__ = [
    'Project',
    'ProjectValidationError',
    'validate_project_name', 
    'validate_html_content',
    'XMLData',
    'XMLDataError'
]

# Version du module models
__version__ = '1.0.0'