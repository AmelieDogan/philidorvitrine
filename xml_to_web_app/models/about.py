"""
Modèle de données pour la section à propos de l'édition numérique.
Gère les informations de titre, sous-titre et contenu de présentation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
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


@dataclass
class About:
    """
    Représente le contenu HTML de la page à propos avec ses métadonnées.
    
    Attributes:
        uuid: Identifiant UUID unique de l'à propos (généré automatiquement)
        content_html: Contenu HTML de la page à propos
        created_at: Date de création
        updated_at: Date de dernière modification
        metadata: Métadonnées additionnelles
    """
    
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_html: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_content(self, content_html: str) -> None:
        """Met à jour le contenu HTML et la date de modification."""
        self.content_html = content_html.strip()
        self.updated_at = datetime.now()
    
    def to_xml_element(self) -> ET.Element:
        """
        Convertit l'à propos en élément XML.
        
        Format:
        <about uuid="uuid" created="ISO_date" updated="ISO_date">
            <content><![CDATA[contenu HTML]]></content>
            <metadata>
                <meta key="key" value="value"/>
            </metadata>
        </about>
        
        Returns:
            Element XML représentant l'à propos
        """
        about_elem = ET.Element("about")
        about_elem.set("uuid", self.uuid)
        about_elem.set("created", self.created_at.isoformat())
        about_elem.set("updated", self.updated_at.isoformat())
        
        # Contenu HTML avec CDATA
        if self.content_html:
            content_elem = ET.SubElement(about_elem, "content")
            content_elem.text = self.content_html
        
        # Métadonnées
        if self.metadata:
            metadata_elem = ET.SubElement(about_elem, "metadata")
            for key, value in self.metadata.items():
                meta_elem = ET.SubElement(metadata_elem, "meta")
                meta_elem.set("key", str(key))
                meta_elem.set("value", str(value))
        
        return about_elem
    
    def to_xml_string(self, pretty: bool = True) -> str:
        """
        Convertit les mentions légales en chaîne XML.
        
        Args:
            pretty: Si True, formate le XML avec indentation
            
        Returns:
            Chaîne XML représentant les mentions légales
        """
        element = self.to_xml_element()
        return xml_to_string(element, pretty=pretty)
    
    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'About':
        """
        Crée l'à propos à partir d'un élément XML.
        
        Args:
            element: Élément XML représentant l'à propos
            
        Returns:
            Instance de About
            
        Raises:
            ValueError: Si l'élément XML est invalide
        """
        if element.tag != "about":
            raise ValueError(f"Élément XML invalide: attendu 'about', reçu '{element.tag}'")
        
        # Récupère les attributs
        uuid_str = element.get("uuid")
        created_str = element.get("created")
        updated_str = element.get("updated")
        
        created_at = parse_datetime_safe(created_str)
        updated_at = parse_datetime_safe(updated_str)
        
        # Récupère le contenu HTML       
        content_elem = element.find("content")
        content_html = content_elem.text if content_elem is not None else ""
        
        # Récupère les métadonnées
        metadata = {}
        metadata_elem = element.find("metadata")
        if metadata_elem is not None:
            for meta_elem in metadata_elem.findall("meta"):
                key = meta_elem.get("key")
                value = meta_elem.get("value")
                if key:
                    metadata[key] = value
        
        return cls(
            uuid=uuid_str or str(uuid.uuid4()),
            content_html=content_html or "",
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata
        )
    
    @classmethod
    def from_xml_string(cls, xml_string: str) -> 'About':
        """
        Crée l'à propos à partir d'une chaîne XML.
        
        Args:
            xml_string: Chaîne XML représentant l'à propos
            
        Returns:
            Instance de About
        """
        try:
            element = ET.fromstring(xml_string)
            return cls.from_xml_element(element)
        except ET.ParseError as e:
            raise ValueError(f"XML invalide: {e}")
    
    def is_empty(self) -> bool:
        """Retourne True si l'à propos n'a pas de contenu."""
        return not self.content_html.strip()
    
    def get_preview_text(self, max_length: int = 200) -> str:
        """
        Retourne un aperçu textuel du contenu HTML.
        
        Args:
            max_length: Longueur maximale du texte de prévisualisation
            
        Returns:
            Texte de prévisualisation sans balises HTML
        """
        return get_text_preview(self.content_html, max_length)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Définit une métadonnée."""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Récupère une métadonnée."""
        return self.metadata.get(key, default)


def create_default_about() -> About:
    """
    Crée une section à propos par défaut.
    
    Returns:
        Présentation avec des valeurs par défaut
    """
    return About(
        content_html="""
<p>Bonjour, il faudrait penser à me compléter...</p>
        """.strip()
    )


class AboutValidationError(Exception):
    """Exception levée lors d'erreurs de validation de l'à propos."""
    pass


def validate_about_content(content_html: str) -> bool:
    """
    Valide le contenu HTML de l'à propos.
    
    Args:
        content_html: Contenu HTML à valider
        
    Returns:
        True si le contenu est valide
        
    Raises:
        AboutValidationError: Si le contenu est invalide
    """
    try:
        validate_html_content(content_html, max_length=200000)  # 100KB max pour les présentations
        return True
    except ValidationError as e:
        raise AboutValidationError(str(e))
