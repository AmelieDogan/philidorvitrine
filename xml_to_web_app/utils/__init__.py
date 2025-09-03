"""
Module utils - Utilitaires pour l'application de transformation XML.

Ce module contient les fonctions utilitaires pour :
- Manipulation et validation XML
- Traitement de fichiers
- Fonctions communes
"""

from .xml_utils import (
    validate_xml_file,
    validate_xml_string,
    extract_text_content,
    find_elements_by_attribute,
    find_project_references,
    prettify_xml,
    create_projects_xml,
    merge_xml_documents,
    extract_xml_statistics,
    clean_xml_content,
    escape_xml_content,
    XML_DECLARATION_UTF8,
    XML_DECLARATION_ISO,
    PROJECT_PATTERNS
)

__all__ = [
    'validate_xml_file',
    'validate_xml_string', 
    'extract_text_content',
    'find_elements_by_attribute',
    'find_project_references',
    'prettify_xml',
    'create_projects_xml',
    'merge_xml_documents',
    'extract_xml_statistics',
    'clean_xml_content',
    'escape_xml_content',
    'create_cdata_section',
    'XML_DECLARATION_UTF8',
    'XML_DECLARATION_ISO',
    'PROJECT_PATTERNS'
]

# Version du module utils
__version__ = '1.0.0'