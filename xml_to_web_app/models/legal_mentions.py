"""
Modèle de données pour les mentions légales de l'édition numérique.
Gère les informations de titre, sous-titre et contenu de présentation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET
import uuid
import html

# Import des utilitaires XML centralisés
from ..utils.xml_utils import (
    xml_to_string, 
    validate_html_content, 
    get_text_preview,
    parse_datetime_safe,
    ValidationError
)


@dataclass
class LegalMentions:
    """
    Représente le contenu HTML de la page des mentions légales avec ses métadonnées.
    
    Attributes:
        uuid: Identifiant UUID unique des mentions légales (généré automatiquement)
        content_html: Contenu HTML de la page mentions légales
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
        Convertit les mentions légales en élément XML.
        
        Format:
        <legal_mentions uuid="uuid" created="ISO_date" updated="ISO_date">
            <content><![CDATA[contenu HTML]]></content>
            <metadata>
                <meta key="key" value="value"/>
            </metadata>
        </legal_mentions>
        
        Returns:
            Element XML représentant les mentions légales
        """
        legal_mentions_elem = ET.Element("legal_mentions")
        legal_mentions_elem.set("uuid", self.uuid)
        legal_mentions_elem.set("created", self.created_at.isoformat())
        legal_mentions_elem.set("updated", self.updated_at.isoformat())
        
        # Contenu HTML avec CDATA
        if self.content_html:
            content_elem = ET.SubElement(legal_mentions_elem, "content")
            content_elem.text = self.content_html
        
        # Métadonnées
        if self.metadata:
            metadata_elem = ET.SubElement(legal_mentions_elem, "metadata")
            for key, value in self.metadata.items():
                meta_elem = ET.SubElement(metadata_elem, "meta")
                meta_elem.set("key", str(key))
                meta_elem.set("value", str(value))
        
        return legal_mentions_elem
    
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
    def from_xml_element(cls, element: ET.Element) -> 'LegalMentions':
        """
        Crée des mentions légales à partir d'un élément XML.
        
        Args:
            element: Élément XML représentant des mentions légales
            
        Returns:
            Instance de LegalMentions
            
        Raises:
            ValueError: Si l'élément XML est invalide
        """
        if element.tag != "legal_mentions":
            raise ValueError(f"Élément XML invalide: attendu 'legal_mentions', reçu '{element.tag}'")
        
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
    def from_xml_string(cls, xml_string: str) -> 'LegalMentions':
        """
        Crée des mentions légales à partir d'une chaîne XML.
        
        Args:
            xml_string: Chaîne XML représentant des mentions légales
            
        Returns:
            Instance de LegalMentions
        """
        try:
            element = ET.fromstring(xml_string)
            return cls.from_xml_element(element)
        except ET.ParseError as e:
            raise ValueError(f"XML invalide: {e}")
    
    def is_empty(self) -> bool:
        """Retourne True si les mentions légales n'ont pas de contenu."""
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


def create_default_legal_mentions() -> LegalMentions:
    """
    Crée des mentions légales par défaut.
    
    Returns:
        Présentation avec des valeurs par défaut
    """
    return LegalMentions(
        content_html="""
<h2>Mentions l&eacute;gales</h2>
<h4>INFORMATION &Eacute;DITEUR</h4>
<p>Le site www.cmbv.fr est &eacute;dit&eacute; par<br>Centre de musique baroque de Versailles<br>H&ocirc;tel des Menus-Plaisirs<br>22 avenue de Paris<br>CS 70353, 78035 Versailles cedex<br>T&eacute;l : +33 (0)1 39 20 78 10<br>Fax : +33 (0)1 39 20 78 01<br><a href="mailto:contact@cmbv.com">Nous contacter</a></p>
<p>Association loi 1901 dont la mission nationale, confi&eacute;e par le minist&egrave;re de la culture,&nbsp;est de valoriser le patrimoine musical fran&ccedil;ais des XVII<sup>e</sup> et XVIII<sup>e</sup>&nbsp;si&egrave;cles.</p>
<p>Num&eacute;ros de licence d&rsquo;entrepreneur du spectacle :<br>&ndash; Licence 2 / n&deg; : 2- 1112910<br>&ndash; Licence 3 / n&deg; : 3- 1112911</p>
<p>Directeur de la publication<br>Nicolas Bucher</p>
<h4><strong>R&Eacute;ALISATION</strong></h4>
<p>La pr&eacute;sente &eacute;dition num&eacute;rique est r&eacute;alis&eacute;e gr&acirc;ce &agrave; un logiciel d&eacute;velopp&eacute; par Am&eacute;lie Dogan, stagiaire au CMBV de avril &agrave; juillet 2025 pour l'obtention de son master. Les donn&eacute;es pr&eacute;sent&eacute;es proviennent de la base de donn&eacute;es Philidor4 tandis que les informations &eacute;ditoriales sont ajout&eacute;es gr&acirc;ce &agrave; l'interface graphique du logiciel.</p>
<h4>H&Eacute;BERGEMENT</h4>
<p><strong>GANDI S.A.S </strong><br>63-65 boulevard Massena &agrave; Paris<br>75013&nbsp;PARIS<br><a href="http://www.gandi.net" target="_blank" rel="noopener noreferrer">www.gandi.net</a></p>
<h4>PROPRI&Eacute;T&Eacute; INTELLECTUELLE</h4>
<p>Conform&eacute;ment au code de la Propri&eacute;t&eacute; Intellectuelle et plus g&eacute;n&eacute;ralement &agrave; tous les accords comportant des dispositions relatives au droit d'auteur, la reproduction partielle ou totale de textes, d'images ou d'illustrations non destin&eacute;es explicitement &agrave; &ecirc;tre t&eacute;l&eacute;charg&eacute;es par les visiteurs, sont interdites sans autorisation pr&eacute;alable de l'&eacute;diteur ou de tout ayant-droit.</p>
<h4>DONN&Eacute;ES PERSONNELLES / DONN&Eacute;ES ENTR&Eacute;ES PAR L'UTILISATEUR</h4>
<p>Au cours de votre visite sur le site www.cmbv.fr, il pourra vous &ecirc;tre demand&eacute; de saisir des informations personnelles nominatives vous concernant (nom, pr&eacute;nom, e-mail, etc.). Les donn&eacute;es re&ccedil;ues de votre part sont reprises dans les fichiers du Centre de musique baroque de Versailles et servent uniquement &agrave; r&eacute;pondre &agrave; la demande d'informations que vous avez introduite, sous r&eacute;serve des dispositions l&eacute;gales applicables et notamment de la Loi " Informatique et Libert&eacute;s " modifi&eacute;e par la loi du 6 ao&ucirc;t 2004.&nbsp;Les donn&eacute;es personnelles et confidentielles collect&eacute;es ne sont &agrave; aucun moment destin&eacute;es &agrave; &ecirc;tre vendues, commercialis&eacute;es ou lou&eacute;es &agrave; un tiers. Elles pourront toutefois &ecirc;tre utilis&eacute;es par le Centre de musique baroque de Versailles pour envoyer une enqu&ecirc;te de satisfaction annuelle. Conform&eacute;ment &agrave; l'article 39 de la Loi " Informatique et Libert&eacute;s " n&deg;78-17 du 6 janvier 1978, vous disposez d'un droit d'acc&egrave;s et de rectification des donn&eacute;es vous concernant en &eacute;crivant au Centre de musique baroque de Versailles.&nbsp;<br><a href="mailto:contact@cmbv.com">Contactez-nous</a></p>
<h4>HYPERLIENS</h4>
<p>Le site http://www.cmbv.fr peut contenir des liens hypertextes menant &agrave; d'autres sites Internet totalement ind&eacute;pendants du site www.cmbv.fr. Le Centre de musique baroque de Versailles ne suppose aucunement, ni ne garantit que les informations contenues dans de tels liens hypertextes ou dans tout autre site Internet soient exactes, compl&egrave;tes ou v&eacute;ridiques. D&egrave;s lors, tout acc&egrave;s &agrave; un autre site Internet li&eacute; au site http://www.cmbv.fr s&rsquo;effectue sous la propre responsabilit&eacute;, pleine et enti&egrave;re, de l'utilisateur.</p>
<h4>RESPONSABILIT&Eacute;S</h4>
<p>L'utilisation des informations contenues sur le pr&eacute;sent site rel&egrave;ve de la seule responsabilit&eacute; de son utilisateur.</p>
<p>Toutes les ressources contenues dans ce site, textes, visuels et illustrations (sch&eacute;mas, dessins, plans, photographies et animations informatiques) sont communiqu&eacute;s &agrave; titre purement informatif et ne peuvent en rien engager la responsabilit&eacute; de l'&eacute;diteur.</p>
<p>En effet, malgr&eacute; le souhait de l'&eacute;diteur d&rsquo;apporter les informations les plus exactes possibles et d&rsquo;assurer une mise &agrave; jour r&eacute;guli&egrave;re du site Internet, celui&ndash;ci n&rsquo;est pas responsable d&rsquo;impr&eacute;cisions, d&rsquo;inexactitudes, d&rsquo;erreurs ou de possibles omissions portant sur des informations contenues sur le site ni des r&eacute;sultats obtenus par l&rsquo;utilisation et la pratique des informations d&eacute;livr&eacute;es sur ce support de communication.</p>
<h4>EXERCICE DU DROIT D'ACC&Egrave;S</h4>
<p>Conform&eacute;ment &agrave; l&rsquo;article 34 de la loi "Informatique et Libert&eacute;s", vous disposez d&rsquo;un droit d'acc&egrave;s, de modification, de rectification et de suppression des donn&eacute;es vous concernant. Pour exercer ce droit d'acc&egrave;s, adressez&ndash;vous &agrave; l'&eacute;diteur.</p>
<p>Pour plus d&rsquo;informations sur la loi &laquo; Informatique et Libert&eacute;s &raquo;, vous pouvez consulter le site Internet de la&nbsp;<a href="http://www.cnil.fr/" target="_blank" rel="noopener noreferrer">CNIL</a>.</p>
        """.strip()
    )


class LegalMentionsValidationError(Exception):
    """Exception levée lors d'erreurs de validation des mentions légales."""
    pass


def validate_legal_mentions_content(content_html: str) -> bool:
    """
    Valide le contenu HTML des mentions légales.
    
    Args:
        content_html: Contenu HTML à valider
        
    Returns:
        True si le contenu est valide
        
    Raises:
        LegalMentionsValidationError: Si le contenu est invalide
    """
    try:
        validate_html_content(content_html, max_length=200000)  # 100KB max pour les présentations
        return True
    except ValidationError as e:
        raise LegalMentionsValidationError(str(e))
