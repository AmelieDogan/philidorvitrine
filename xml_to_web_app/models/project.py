"""
Modèle de données pour un projet.
Gère la sérialisation/désérialisation XML et la validation des données.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import xml.etree.ElementTree as ET
import uuid

# Import des utilitaires XML centralisés
from ..utils.xml_utils import (
    xml_to_string, 
    validate_html_content, 
    get_text_preview,
    parse_datetime_safe,
    ValidationError
)

from ..utils.html_utils import truncate_html_safely

@dataclass
class Project:
    """
    Représente un projet avec ses métadonnées et contenu HTML.
    
    Attributes:
        uuid: Identifiant UUID unique du projet (généré automatiquement)
        id: Identifiant choisi par l'utilisateur (utilisé dans le XML)
        name: Nom du projet (nom d'affichage)
        description_html: Description au format HTML
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    id: str = ""
    name: str = ""
    description_html: str = ""
    truncated_html: str = field(default="", repr=False)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validation après initialisation."""
        if not self.name.strip():
            raise ValueError("Le nom du projet ne peut pas être vide")
        if not self.id.strip():
            raise ValueError("L'identifiant du projet ne peut pas être vide")
    
    def update_content(self, description_html: str) -> None:
        """Met à jour le contenu HTML et la date de modification."""
        self.description_html = description_html.strip()
        self.truncated_html = truncate_html_safely(self.description_html, max_chars=600)
        self.updated_at = datetime.now()
    
    def to_xml_element(self) -> ET.Element:
        """
        Convertit le projet en élément XML.
        
        Format:
        <project id="identifiant_projet" created="ISO_date" updated="ISO_date" uuid="uuid" name="nom_projet">
            <description_html>contenu HTML</description_html>
            <preview>contenu HTML tronqué</preview>
        </project>
        
        Returns:
            Element XML représentant le projet
        """
        project_elem = ET.Element("project")
        project_elem.set("id", self.id)
        project_elem.set("created", self.created_at.isoformat())
        project_elem.set("updated", self.updated_at.isoformat())
        project_elem.set("uuid", self.uuid)
        project_elem.set("name", self.name)
        
        if self.description_html:
            desc_elem = ET.SubElement(project_elem, "description_html")
            desc_elem.text = self.description_html

        if self.truncated_html:
            preview_elem = ET.SubElement(project_elem, "preview")
            preview_elem.text = self.truncated_html

        
        return project_elem
    
    def to_xml_string(self, pretty: bool = True) -> str:
        """
        Convertit le projet en chaîne XML.
        
        Args:
            pretty: Si True, formate le XML avec indentation
            
        Returns:
            Chaîne XML représentant le projet
        """
        element = self.to_xml_element()
        return xml_to_string(element, pretty=pretty)
    
    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'Project':
        """
        Crée un projet à partir d'un élément XML.
        
        Args:
            element: Élément XML représentant un projet
            
        Returns:
            Instance de Project
            
        Raises:
            ValueError: Si l'élément XML est invalide
        """
        if element.tag != "project":
            raise ValueError(f"Élément XML invalide: attendu 'project', reçu '{element.tag}'")
        
        # Récupère les attributs
        project_id = element.get("id")
        if not project_id:
            raise ValueError("Attribut 'id' manquant dans l'élément project")
        
        # Récupère le nom (peut être différent de l'ID maintenant)
        name = element.get("name", project_id)  # Utilise l'ID comme nom par défaut si pas de nom
        
        # Parse les dates avec la fonction utilitaire
        created_str = element.get("created")
        updated_str = element.get("updated")
        uuid_str = element.get("uuid")
        
        created_at = parse_datetime_safe(created_str)
        updated_at = parse_datetime_safe(updated_str)
        
        # Récupère le contenu HTML
        description_html_elem = element.find("description_html")
        description_html = description_html_elem.text if description_html_elem is not None else ""
        
        return cls(
            uuid=uuid_str or str(uuid.uuid4()),
            id=project_id,
            name=name,
            description_html=description_html,
            created_at=created_at,
            updated_at=updated_at
        )
    
    @classmethod
    def from_xml_string(cls, xml_string: str) -> 'Project':
        """
        Crée un projet à partir d'une chaîne XML.
        
        Args:
            xml_string: Chaîne XML représentant un projet
            
        Returns:
            Instance de Project
        """
        try:
            element = ET.fromstring(xml_string)
            return cls.from_xml_element(element)
        except ET.ParseError as e:
            raise ValueError(f"XML invalide: {e}")
    
    def is_empty(self) -> bool:
        """Retourne True si le projet n'a pas de contenu."""
        return not self.description_html.strip()
    
    def get_preview_text(self, max_length: int = 100) -> str:
        """
        Retourne un aperçu textuel du contenu HTML.
        
        Args:
            max_length: Longueur maximale du texte de prévisualisation
            
        Returns:
            Texte de prévisualisation sans balises HTML
        """
        return get_text_preview(self.description_html, max_length)
    
    def __str__(self) -> str:
        """Représentation textuelle du projet."""
        return f"Project(id='{self.id}', name='{self.name}', updated={self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du projet."""
        return (f"Project(uuid='{self.uuid}', id='{self.id}', name='{self.name}', "
                f"created='{self.created_at}', updated='{self.updated_at}')")


class ProjectValidationError(Exception):
    """Exception levée lors d'erreurs de validation de projet."""
    pass


def validate_project_name(name: str) -> bool:
    """
    Valide qu'un nom de projet est acceptable.
    
    Args:
        name: Nom à valider
        
    Returns:
        True si le nom est valide
        
    Raises:
        ProjectValidationError: Si le nom est invalide
    """
    if not name or not name.strip():
        raise ProjectValidationError("Le nom du projet ne peut pas être vide")
    
    if len(name.strip()) > 100:
        raise ProjectValidationError("Le nom du projet ne peut pas dépasser 100 caractères")
    
    # Vérifie les caractères interdits pour XML
    import re
    if re.search(r'[<>&"\'`]', name):
        raise ProjectValidationError("Le nom du projet contient des caractères interdits")
    
    return True


def validate_project_id(project_id: str) -> bool:
    """
    Valide qu'un identifiant de projet est acceptable.
    
    Args:
        project_id: Identifiant à valider
        
    Returns:
        True si l'identifiant est valide
        
    Raises:
        ProjectValidationError: Si l'identifiant est invalide
    """
    if not project_id or not project_id.strip():
        raise ProjectValidationError("L'identifiant du projet ne peut pas être vide")
    
    if len(project_id.strip()) > 50:
        raise ProjectValidationError("L'identifiant du projet ne peut pas dépasser 50 caractères")
    
    # Vérifie les caractères autorisés pour XML ID
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', project_id.strip()):
        raise ProjectValidationError("L'identifiant doit commencer par une lettre et ne contenir que des lettres, chiffres et underscores")
    
    return True


def validate_project_html_content(html_content: str) -> bool:
    """
    Valide le contenu HTML d'un projet.
    
    Args:
        html_content: Contenu HTML à valider
        
    Returns:
        True si le contenu est valide
        
    Raises:
        ProjectValidationError: Si le contenu est invalide
    """
    try:
        validate_html_content(html_content, max_length=50000)  # 50KB max pour les projets
        return True
    except ValidationError as e:
        raise ProjectValidationError(str(e))