"""
Utilitaires pour le traitement et la manipulation de fichiers XML.
Fonctions communes pour la validation, parsing et transformation XML.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import re
from datetime import datetime


def validate_xml_file(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Valide un fichier XML et retourne le statut avec les erreurs éventuelles.
    
    Args:
        file_path: Chemin vers le fichier XML
        
    Returns:
        Tuple (is_valid, errors_list)
    """
    errors = []
    
    try:
        path = Path(file_path)
        if not path.exists():
            errors.append(f"Fichier non trouvé: {file_path}")
            return False, errors
        
        if not path.is_file():
            errors.append(f"Le chemin ne pointe pas vers un fichier: {file_path}")
            return False, errors
        
        # Vérifie la taille du fichier
        if path.stat().st_size > 100 * 1024 * 1024:  # 100MB max
            errors.append("Fichier trop volumineux (max 100MB)")
            return False, errors
        
        # Tente de parser le XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Validations basiques
        if not root.tag:
            errors.append("Élément racine sans nom")
        
        return True, errors
        
    except ET.ParseError as e:
        errors.append(f"Erreur de parsing XML: {e}")
        return False, errors
    except PermissionError:
        errors.append(f"Permission refusée pour lire le fichier: {file_path}")
        return False, errors
    except Exception as e:
        errors.append(f"Erreur inattendue: {e}")
        return False, errors


def validate_xml_string(xml_content: str) -> Tuple[bool, List[str]]:
    """
    Valide une chaîne XML.
    
    Args:
        xml_content: Contenu XML à valider
        
    Returns:
        Tuple (is_valid, errors_list)
    """
    errors = []
    
    if not xml_content or not xml_content.strip():
        errors.append("Contenu XML vide")
        return False, errors
    
    try:
        root = ET.fromstring(xml_content)
        
        # Validations basiques
        if not root.tag:
            errors.append("Élément racine sans nom")
        
        return True, errors
        
    except ET.ParseError as e:
        errors.append(f"Erreur de parsing XML: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"Erreur inattendue: {e}")
        return False, errors


def extract_text_content(element: ET.Element, include_children: bool = True) -> str:
    """
    Extrait tout le contenu textuel d'un élément XML.
    
    Args:
        element: Élément XML
        include_children: Si True, inclut le texte des éléments enfants
        
    Returns:
        Texte extrait de l'élément
    """
    if include_children:
        return ''.join(element.itertext()).strip()
    else:
        return (element.text or '').strip()


def find_elements_by_attribute(root: ET.Element, attr_name: str, 
                              attr_value: Optional[str] = None) -> List[ET.Element]:
    """
    Trouve tous les éléments ayant un attribut spécifique.
    
    Args:
        root: Élément racine pour la recherche
        attr_name: Nom de l'attribut à chercher
        attr_value: Valeur de l'attribut (optionnel, si None cherche juste l'existence)
        
    Returns:
        Liste des éléments trouvés
    """
    found_elements = []
    
    for elem in root.iter():
        if attr_name in elem.attrib:
            if attr_value is None or elem.attrib[attr_name] == attr_value:
                found_elements.append(elem)
    
    return found_elements


def find_project_references(root: ET.Element, 
                           patterns: Optional[List[str]] = None) -> List[str]:
    """
    Trouve toutes les références de projets dans un XML.
    
    Args:
        root: Élément racine pour la recherche
        patterns: Patterns regex pour chercher les références (optionnel)
        
    Returns:
        Liste unique des références de projets trouvées
    """
    if patterns is None:
        patterns = [
            r'project[_-](\w+)',           # project_xxx ou project-xxx
            r'proj[_-](\w+)',              # proj_xxx ou proj-xxx
            r'(\w+)[_-]project',           # xxx_project ou xxx-project
            r'project["\']?\s*[:=]\s*["\']?(\w+)',  # project: xxx ou project="xxx"
        ]
    
    references = set()
    
    # Cherche dans tous les éléments
    for elem in root.iter():
        # Cherche dans les attributs
        for attr_name, attr_value in elem.attrib.items():
            if 'project' in attr_name.lower():
                references.add(attr_value)
            
            # Applique les patterns sur les valeurs d'attributs
            for pattern in patterns:
                matches = re.findall(pattern, attr_value, re.IGNORECASE)
                references.update(matches)
        
        # Cherche dans le texte
        text_content = extract_text_content(elem, include_children=False)
        if text_content:
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                references.update(matches)
    
    return sorted(list(references))


def prettify_xml(element: ET.Element, indent: str = "  ") -> None:
    """
    Ajoute l'indentation à un élément XML pour le rendre lisible.
    
    Args:
        element: Élément XML à formater
        indent: Chaîne d'indentation à utiliser
    """
    def _indent(elem, level=0):
        i = "\n" + level * indent
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + indent
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                _indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    _indent(element)


def xml_to_string(element: ET.Element, pretty: bool = True, 
                  encoding: str = 'unicode') -> str:
    """
    Convertit un élément XML en chaîne de caractères.
    
    Args:
        element: Élément XML à convertir
        pretty: Si True, formate le XML avec indentation
        encoding: Encodage à utiliser ('unicode' pour str, sinon bytes)
        
    Returns:
        Chaîne XML
    """
    if pretty:
        # Crée une copie pour ne pas modifier l'original
        import copy
        elem_copy = copy.deepcopy(element)
        prettify_xml(elem_copy)
        return ET.tostring(elem_copy, encoding=encoding, method='xml')
    else:
        return ET.tostring(element, encoding=encoding, method='xml')


def create_projects_xml(projects_data: List[Dict]) -> str:
    """
    Crée un document XML pour les projets à partir d'une liste de données.
    
    Args:
        projects_data: Liste de dictionnaires contenant les données des projets
                      Format: [{'id': 'xxx', 'name': 'xxx', 'html': 'xxx', ...}, ...]
        
    Returns:
        Document XML formaté
    """
    root = ET.Element("projects")
    root.set("generated", datetime.now().isoformat())
    root.set("count", str(len(projects_data)))
    
    for project_data in projects_data:
        project_elem = ET.SubElement(root, "project")
        
        # Attributs obligatoires
        project_elem.set("id", project_data.get('id', 'unknown'))
        
        # Attributs optionnels
        if 'name' in project_data:
            project_elem.set("name", project_data['name'])
        if 'created' in project_data:
            project_elem.set("created", project_data['created'])
        if 'updated' in project_data:
            project_elem.set("updated", project_data['updated'])
        if 'uuid' in project_data:
            project_elem.set("uuid", project_data['uuid'])
        
        # Contenu HTML
        if 'html' in project_data and project_data['html']:
            project_elem.text = project_data['html']
    
    # Formatage
    prettify_xml(root)
    
    # Génération du XML avec déclaration
    xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml_content = ET.tostring(root, encoding='unicode', method='xml')
    
    return xml_declaration + xml_content


def merge_xml_documents(base_xml: str, overlay_xml: str, 
                       merge_strategy: str = "replace") -> str:
    """
    Fusionne deux documents XML.
    
    Args:
        base_xml: XML de base
        overlay_xml: XML à fusionner
        merge_strategy: Stratégie de fusion ("replace", "append", "merge")
        
    Returns:
        Document XML fusionné
    """
    try:
        base_root = ET.fromstring(base_xml)
        overlay_root = ET.fromstring(overlay_xml)
        
        if merge_strategy == "replace":
            # Remplace complètement les éléments correspondants
            for overlay_elem in overlay_root:
                # Trouve l'élément correspondant dans la base
                base_elem = base_root.find(f".//{overlay_elem.tag}[@id='{overlay_elem.get('id')}']")
                if base_elem is not None:
                    # Remplace l'élément
                    parent = base_root.find(f".//{base_elem.tag}/..")
                    if parent is not None:
                        parent.remove(base_elem)
                        parent.append(overlay_elem)
                else:
                    # Ajoute le nouvel élément
                    base_root.append(overlay_elem)
        
        elif merge_strategy == "append":
            # Ajoute tous les éléments de overlay à base
            for overlay_elem in overlay_root:
                base_root.append(overlay_elem)
        
        elif merge_strategy == "merge":
            # Stratégie de fusion intelligente (à implémenter selon besoins)
            pass
        
        prettify_xml(base_root)
        return ET.tostring(base_root, encoding='unicode', method='xml')
        
    except ET.ParseError as e:
        raise ValueError(f"Erreur lors de la fusion XML: {e}")


def extract_xml_statistics(xml_content: str) -> Dict[str, any]:
    """
    Extrait des statistiques d'un document XML.
    
    Args:
        xml_content: Contenu XML à analyser
        
    Returns:
        Dictionnaire contenant les statistiques
    """
    try:
        root = ET.fromstring(xml_content)
        
        # Compte les éléments par type
        element_counts = {}
        for elem in root.iter():
            tag = elem.tag
            element_counts[tag] = element_counts.get(tag, 0) + 1
        
        # Statistiques générales
        stats = {
            'total_elements': len(list(root.iter())),
            'root_tag': root.tag,
            'root_attributes': dict(root.attrib),
            'element_types': len(element_counts),
            'element_counts': element_counts,
            'max_depth': _get_xml_depth(root),
            'total_text_length': len(''.join(root.itertext())),
            'has_cdata': '<![CDATA[' in xml_content,
            'xml_size_bytes': len(xml_content.encode('utf-8'))
        }
        
        # Recherche de références de projets
        project_refs = find_project_references(root)
        stats['project_references'] = project_refs
        stats['project_references_count'] = len(project_refs)
        
        return stats
        
    except ET.ParseError as e:
        return {'error': f'XML invalide: {e}'}


def _get_xml_depth(element: ET.Element, depth: int = 0) -> int:
    """
    Calcule la profondeur maximale d'un arbre XML.
    
    Args:
        element: Élément XML
        depth: Profondeur actuelle
        
    Returns:
        Profondeur maximale
    """
    if len(element) == 0:
        return depth
    
    return max(_get_xml_depth(child, depth + 1) for child in element)


def clean_xml_content(xml_content: str) -> str:
    """
    Nettoie un contenu XML en supprimant les caractères problématiques.
    
    Args:
        xml_content: Contenu XML à nettoyer
        
    Returns:
        Contenu XML nettoyé
    """
    # Supprime les caractères de contrôle non autorisés en XML
    xml_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_content)
    
    # Normalise les retours à la ligne
    xml_content = re.sub(r'\r\n|\r', '\n', xml_content)
    
    # Supprime les espaces en début et fin
    xml_content = xml_content.strip()
    
    return xml_content


def escape_xml_content(content: str) -> str:
    """
    Échappe le contenu pour inclusion sécurisée dans XML.
    
    Args:
        content: Contenu à échapper
        
    Returns:
        Contenu échappé
    """
    return (content.replace('&', '&amp;')
                  .replace('<', '&lt;')
                  .replace('>', '&gt;')
                  .replace('"', '&quot;')
                  .replace("'", '&apos;'))


# Constantes utiles
XML_DECLARATION_UTF8 = '<?xml version="1.0" encoding="utf-8"?>'
XML_DECLARATION_ISO = '<?xml version="1.0" encoding="iso-8859-1"?>'

# Patterns regex courantes pour les projets
PROJECT_PATTERNS = [
    r'project[_-](\w+)',
    r'proj[_-](\w+)', 
    r'(\w+)[_-]project',
    r'project["\']?\s*[:=]\s*["\']?(\w+)',
]

# === Fonctions spécifiques pour la validation ===

class ValidationError(Exception):
    """Exception levée lors d'erreurs de validation."""
    pass


def validate_html_content(content: str, max_length: int = 50000) -> None:
    """
    Valide le contenu HTML.
    
    Args:
        content: Contenu HTML à valider
        max_length: Taille maximale autorisée
        
    Raises:
        ValidationError: Si le contenu HTML n'est pas valide
    """
    if content is None:
        return  # Le contenu peut être vide
    
    # Vérifie la longueur du contenu
    if len(content) > max_length:
        raise ValidationError(f"Le contenu HTML ne peut pas dépasser {max_length} caractères")
    
    # Validation basique des balises HTML
    try:
        # Vérifie que les balises sont bien fermées (validation simplifiée)
        _validate_html_structure(content)
    except Exception as e:
        raise ValidationError(f"Structure HTML invalide: {e}")


def _validate_html_structure(content: str) -> None:
    """
    Validation basique de la structure HTML.
    
    Args:
        content: Contenu HTML à valider
        
    Raises:
        Exception: Si la structure n'est pas valide
    """
    # Stack pour vérifier l'imbrication des balises
    stack = []
    
    # Balises auto-fermantes
    self_closing_tags = {
        'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 
        'col', 'embed', 'source', 'track', 'wbr'
    }
    
    # Trouve toutes les balises
    tag_pattern = re.compile(r'<(/?)(\w+)(?:\s[^>]*)?\s*(/?)>')
    
    for match in tag_pattern.finditer(content):
        is_closing = match.group(1) == '/'
        tag_name = match.group(2).lower()
        is_self_closing = match.group(3) == '/' or tag_name in self_closing_tags
        
        if is_closing:
            # Balise fermante
            if not stack:
                raise Exception(f"Balise fermante '{tag_name}' sans balise ouvrante correspondante")
            if stack[-1] != tag_name:
                raise Exception(f"Balise fermante '{tag_name}' ne correspond pas à la balise ouvrante '{stack[-1]}'")
            stack.pop()
        elif not is_self_closing:
            # Balise ouvrante
            stack.append(tag_name)
    
    if stack:
        raise Exception(f"Balises non fermées: {', '.join(stack)}")


# === Fonctions helper spécifiques aux modèles ===

def clean_xml_id(id_string: str) -> str:
    """
    Nettoie un identifiant pour être utilisé comme identifiant XML.
    
    Args:
        id_string: Identifiant à nettoyer
        
    Returns:
        Identifiant XML valide
    """
    # Remplace les espaces par des underscores
    cleaned = id_string.strip().replace(" ", "_")
    # Garde seulement les caractères alphanumériques et underscores
    cleaned = re.sub(r'[^\w]', '', cleaned)
    # S'assure que ça commence par une lettre (requis pour XML)
    if cleaned and not cleaned[0].isalpha():
        cleaned = f"project_{cleaned}"
    return cleaned or "untitled_project"


def get_text_preview(html_content: str, max_length: int = 100) -> str:
    """
    Extrait un aperçu textuel du contenu HTML.
    
    Args:
        html_content: Contenu HTML
        max_length: Longueur maximale du texte de prévisualisation
        
    Returns:
        Texte de prévisualisation sans balises HTML
    """
    if not html_content:
        return "Aucune description"
    
    # Supprime les balises HTML
    text = re.sub(r'<[^>]+>', '', html_content)
    # Supprime les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def parse_datetime_safe(date_string: Optional[str], default: Optional[datetime] = None) -> datetime:
    """
    Parse une date de manière sécurisée.
    
    Args:
        date_string: Chaîne de date ISO
        default: Valeur par défaut si parsing échoue
        
    Returns:
        Objet datetime
    """
    if not date_string:
        return default or datetime.now()
    
    try:
        return datetime.fromisoformat(date_string)
    except ValueError:
        return default or datetime.now()