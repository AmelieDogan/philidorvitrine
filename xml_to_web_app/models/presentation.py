"""
Modèle de données pour la présentation de l'édition numérique.
Gère les informations de titre, sous-titre et contenu de présentation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET
import uuid
import html
import re

# Import des utilitaires XML centralisés
from ..utils.xml_utils import (
    xml_to_string, 
    validate_html_content, 
    get_text_preview,
    parse_datetime_safe,
    ValidationError
)


@dataclass
class Presentation:
    """
    Représente une présentation d'édition numérique avec ses métadonnées et contenu HTML.
    
    Attributes:
        uuid: Identifiant UUID unique de la présentation (généré automatiquement)
        title: Titre principal de l'édition numérique
        subtitle: Sous-titre de l'édition numérique (optionnel)
        content_html: Contenu HTML de présentation
        created_at: Date de création
        updated_at: Date de dernière modification
        metadata: Métadonnées additionnelles
    """
    
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    subtitle: Optional[str] = None
    content_html: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validation après initialisation."""
        if not self.title.strip():
            raise ValueError("Le titre de la présentation ne peut pas être vide")
    
    def update_content(self, content_html: str) -> None:
        """Met à jour le contenu HTML et la date de modification."""
        self.content_html = content_html.strip()
        self.updated_at = datetime.now()
    
    def update_title(self, title: str) -> None:
        """Met à jour le titre de la présentation."""
        if not title.strip():
            raise ValueError("Le titre ne peut pas être vide")
        self.title = title.strip()
        self.updated_at = datetime.now()
    
    def update_subtitle(self, subtitle: Optional[str]) -> None:
        """Met à jour le sous-titre de la présentation."""
        self.subtitle = subtitle.strip() if subtitle else None
        self.updated_at = datetime.now()
    
    def to_xml_element(self) -> ET.Element:
        """
        Convertit la présentation en élément XML.
        
        Format:
        <presentation uuid="uuid" created="ISO_date" updated="ISO_date">
            <title>titre</title>
            <subtitle>sous-titre</subtitle>
            <content><![CDATA[contenu HTML]]></content>
            <metadata>
                <meta key="key" value="value"/>
            </metadata>
        </presentation>
        
        Returns:
            Element XML représentant la présentation
        """
        presentation_elem = ET.Element("presentation")
        presentation_elem.set("uuid", self.uuid)
        presentation_elem.set("created", self.created_at.isoformat())
        presentation_elem.set("updated", self.updated_at.isoformat())
        
        # Titre (obligatoire)
        title_elem = ET.SubElement(presentation_elem, "title")
        title_elem.text = self.title
        
        # Sous-titre (optionnel)
        if self.subtitle:
            subtitle_elem = ET.SubElement(presentation_elem, "subtitle")
            subtitle_elem.text = self.subtitle
        
        # Contenu HTML avec CDATA
        if self.content_html:
            content_elem = ET.SubElement(presentation_elem, "content")
            content_elem.text = self.content_html
        
        # Métadonnées
        if self.metadata:
            metadata_elem = ET.SubElement(presentation_elem, "metadata")
            for key, value in self.metadata.items():
                meta_elem = ET.SubElement(metadata_elem, "meta")
                meta_elem.set("key", str(key))
                meta_elem.set("value", str(value))
        
        return presentation_elem
    
    def to_xml_string(self, pretty: bool = True) -> str:
        """
        Convertit la présentation en chaîne XML.
        
        Args:
            pretty: Si True, formate le XML avec indentation
            
        Returns:
            Chaîne XML représentant la présentation
        """
        element = self.to_xml_element()
        return xml_to_string(element, pretty=pretty)
    
    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'Presentation':
        """
        Crée une présentation à partir d'un élément XML.
        
        Args:
            element: Élément XML représentant une présentation
            
        Returns:
            Instance de Presentation
            
        Raises:
            ValueError: Si l'élément XML est invalide
        """
        if element.tag != "presentation":
            raise ValueError(f"Élément XML invalide: attendu 'presentation', reçu '{element.tag}'")
        
        # Récupère les attributs
        uuid_str = element.get("uuid")
        created_str = element.get("created")
        updated_str = element.get("updated")
        
        created_at = parse_datetime_safe(created_str)
        updated_at = parse_datetime_safe(updated_str)
        
        # Récupère les éléments texte
        title_elem = element.find("title")
        title = title_elem.text if title_elem is not None else ""
        
        subtitle_elem = element.find("subtitle")
        subtitle = subtitle_elem.text if subtitle_elem is not None else None
        
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
            title=title,
            subtitle=subtitle,
            content_html=content_html or "",
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata
        )
    
    @classmethod
    def from_xml_string(cls, xml_string: str) -> 'Presentation':
        """
        Crée une présentation à partir d'une chaîne XML.
        
        Args:
            xml_string: Chaîne XML représentant une présentation
            
        Returns:
            Instance de Presentation
        """
        try:
            element = ET.fromstring(xml_string)
            return cls.from_xml_element(element)
        except ET.ParseError as e:
            raise ValueError(f"XML invalide: {e}")
    
    def is_empty(self) -> bool:
        """Retourne True si la présentation n'a pas de contenu."""
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
    
    def get_header_info(self) -> Dict[str, Optional[str]]:
        """
        Retourne les informations pour le header du site.
        
        Returns:
            Dictionnaire contenant titre et sous-titre
        """
        return {
            'title': self.title,
            'subtitle': self.subtitle
        }
    
    def get_escaped_title(self) -> str:
        """Retourne le titre échappé pour l'HTML."""
        return html.escape(self.title)
    
    def get_escaped_subtitle(self) -> Optional[str]:
        """Retourne le sous-titre échappé pour l'HTML."""
        return html.escape(self.subtitle) if self.subtitle else None
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Définit une métadonnée."""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Récupère une métadonnée."""
        return self.metadata.get(key, default)
    
    def copy(self) -> 'Presentation':
        """Crée une copie de la présentation avec un nouvel UUID."""
        return Presentation(
            title=f"{self.title} (Copie)",
            subtitle=self.subtitle,
            content_html=self.content_html,
            metadata=self.metadata.copy()
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de la présentation."""
        subtitle_info = f" - {self.subtitle}" if self.subtitle else ""
        return f"Presentation(title='{self.title}{subtitle_info}', updated={self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    def __repr__(self) -> str:
        """Représentation détaillée de la présentation."""
        return (f"Presentation(uuid='{self.uuid}', title='{self.title}', subtitle='{self.subtitle}', "
                f"created='{self.created_at}', updated='{self.updated_at}')")


def create_default_presentation() -> Presentation:
    """
    Crée une présentation par défaut.
    
    Returns:
        Présentation avec des valeurs par défaut
    """
    return Presentation(
        title="Philidor Vitrine",
        subtitle="Une édition numérique de la base Philidor4",
        content_html="""
    <h2>Bienvenue dans cette édition numérique</h2>
    <p>Cette édition numérique présente une collection d'œuvres organisées par projets. 
    Vous pouvez naviguer à travers les différentes œuvres et découvrir leur contenu.</p>
    
    <h3>Comment naviguer</h3>
    <ul>
        <li>Explorez les projets dans le menu principal</li>
        <li>Consultez les œuvres individuelles</li>
    </ul>
    
    <p>Bonne découverte !</p>
        """.strip()
    )


class PresentationValidationError(Exception):
    """Exception levée lors d'erreurs de validation de présentation."""
    pass


def validate_presentation_title(title: str) -> bool:
    """
    Valide qu'un titre de présentation est acceptable.
    
    Args:
        title: Titre à valider
        
    Returns:
        True si le titre est valide
        
    Raises:
        PresentationValidationError: Si le titre est invalide
    """
    if not title or not title.strip():
        raise PresentationValidationError("Le titre ne peut pas être vide")
    
    if len(title.strip()) < 2:
        raise PresentationValidationError("Le titre doit contenir au moins 2 caractères")
    
    if len(title.strip()) > 200:
        raise PresentationValidationError("Le titre ne peut pas dépasser 200 caractères")
    
    # Vérifie les caractères interdits pour XML
    import re
    if re.search(r'[<>&"\'`]', title):
        raise PresentationValidationError("Le titre contient des caractères interdits")
    
    return True


def validate_presentation_subtitle(subtitle: Optional[str]) -> bool:
    """
    Valide qu'un sous-titre de présentation est acceptable.
    
    Args:
        subtitle: Sous-titre à valider (peut être None)
        
    Returns:
        True si le sous-titre est valide
        
    Raises:
        PresentationValidationError: Si le sous-titre est invalide
    """
    if subtitle is None or subtitle.strip() == "":
        return True  # Le sous-titre est optionnel
    
    if len(subtitle.strip()) > 300:
        raise PresentationValidationError("Le sous-titre ne peut pas dépasser 300 caractères")
    
    # Vérifie les caractères interdits pour XML
    import re
    if re.search(r'[<>&"\'`]', subtitle):
        raise PresentationValidationError("Le sous-titre contient des caractères interdits")
    
    return True


def validate_presentation_content(content_html: str) -> bool:
    """
    Valide le contenu HTML d'une présentation.
    
    Args:
        content_html: Contenu HTML à valider
        
    Returns:
        True si le contenu est valide
        
    Raises:
        PresentationValidationError: Si le contenu est invalide
    """
    try:
        validate_html_content(content_html, max_length=100000)  # 100KB max pour les présentations
        return True
    except ValidationError as e:
        raise PresentationValidationError(str(e))
