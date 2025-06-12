"""
Modèle de données pour les fichiers XML importés depuis la base de données.
Gère l'analyse et la validation des données XML d'entrée.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import xml.etree.ElementTree as ET
from pathlib import Path
import re


@dataclass
class XMLData:
    """
    Encapsule les données XML importées de la base de données.
    
    Attributes:
        file_path: Chemin vers le fichier XML original
        raw_xml: Contenu XML brut
        parsed_data: Arbre XML parsé
        root_element: Élément racine du XML
        projects_referenced: Liste des identifiants de projets référencés
        encoding: Encodage du fichier XML
        is_valid: Indique si le XML est valide
        validation_errors: Liste des erreurs de validation
    """
    
    file_path: Optional[Path] = None
    raw_xml: str = ""
    parsed_data: Optional[ET.ElementTree] = None
    root_element: Optional[ET.Element] = None
    projects_referenced: List[str] = field(default_factory=list)
    encoding: str = "utf-8"
    is_valid: bool = False
    validation_errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialise les données après création."""
        if self.raw_xml:
            self.parse_xml()
    
    @classmethod
    def from_file(cls, file_path: str | Path) -> 'XMLData':
        """
        Crée une instance XMLData à partir d'un fichier.
        
        Args:
            file_path: Chemin vers le fichier XML
            
        Returns:
            Instance XMLData
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le fichier ne peut pas être lu
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Le chemin ne pointe pas vers un fichier: {file_path}")
        
        # Détecte l'encodage
        encoding = cls._detect_encoding(path)
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback sur utf-8 avec gestion d'erreurs
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            encoding = 'utf-8'
        
        return cls(
            file_path=path,
            raw_xml=content,
            encoding=encoding
        )
    
    @classmethod
    def from_string(cls, xml_content: str) -> 'XMLData':
        """
        Crée une instance XMLData à partir d'une chaîne XML.
        
        Args:
            xml_content: Contenu XML
            
        Returns:
            Instance XMLData
        """
        return cls(raw_xml=xml_content)
    
    @staticmethod
    def _detect_encoding(file_path: Path) -> str:
        """
        Détecte l'encodage d'un fichier XML.
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            Encodage détecté (par défaut utf-8)
        """
        try:
            # Lit les premiers octets pour détecter l'encodage dans la déclaration XML
            with open(file_path, 'rb') as f:
                first_line = f.readline().decode('utf-8', errors='ignore')
                
            # Cherche la déclaration d'encodage
            encoding_match = re.search(r'encoding=["\']([^"\']+)["\']', first_line)
            if encoding_match:
                return encoding_match.group(1).lower()
        except Exception:
            # En cas d'erreur, on utilise utf-8 par défaut
            pass
        
        return 'utf-8'
    
    def parse_xml(self) -> bool:
        """
        Parse le contenu XML et extrait les informations.
        
        Returns:
            True si le parsing s'est bien passé, False sinon
        """
        self.validation_errors.clear()
        
        if not self.raw_xml.strip():
            self.validation_errors.append("Contenu XML vide")
            self.is_valid = False
            return False
        
        try:
            # Parse le XML
            self.parsed_data = ET.ElementTree(ET.fromstring(self.raw_xml))
            self.root_element = self.parsed_data.getroot()
            
            # Extrait les références de projets
            self._extract_project_references()
            
            # Valide la structure
            self._validate_structure()
            
            self.is_valid = len(self.validation_errors) == 0
            return self.is_valid
            
        except ET.ParseError as e:
            self.validation_errors.append(f"Erreur de parsing XML: {e}")
            self.is_valid = False
            return False
        except Exception as e:
            self.validation_errors.append(f"Erreur inattendue: {e}")
            self.is_valid = False
            return False
    
    def _extract_project_references(self) -> None:
        """
        Extrait tous les identifiants de projets référencés dans le XML.
        Cherche dans les attributs et le contenu textuel.
        """
        if not self.root_element:
            return
        
        project_ids = set()
        
        # Cherche dans tous les éléments et leurs attributs
        for elem in self.root_element.iter():
            # Cherche dans les attributs qui pourraient contenir des références
            for attr_name, attr_value in elem.attrib.items():
                if 'project' in attr_name.lower():
                    project_ids.add(attr_value)
            
            # Cherche dans le texte des éléments
            if elem.text:
                # Utilise une regex pour trouver des références de projets
                # Format supposé: project_xxx ou des mots-clés spécifiques
                project_refs = re.findall(r'project[_-](\w+)', elem.text, re.IGNORECASE)
                project_ids.update(project_refs)
        
        self.projects_referenced = sorted(list(project_ids))
    
    def _validate_structure(self) -> None:
        """Valide la structure basique du XML."""
        if not self.root_element:
            self.validation_errors.append("Pas d'élément racine trouvé")
            return
        
        # Validation basique de la structure
        if len(list(self.root_element)) == 0:
            self.validation_errors.append("Le XML ne contient aucun élément enfant")
        
        # Vérifie que le XML n'est pas trop volumineux
        if len(self.raw_xml) > 10 * 1024 * 1024:  # 10MB max
            self.validation_errors.append("Fichier XML trop volumineux (max 10MB)")
    
    def get_project_references(self) -> List[str]:
        """
        Retourne la liste des identifiants de projets référencés.
        
        Returns:
            Liste des identifiants de projets
        """
        return self.projects_referenced.copy()
    
    def has_project_reference(self, project_id: str) -> bool:
        """
        Vérifie si un projet spécifique est référencé.
        
        Args:
            project_id: Identifiant du projet à chercher
            
        Returns:
            True si le projet est référencé
        """
        return project_id in self.projects_referenced
    
    def get_missing_projects(self, available_projects: List[str]) -> List[str]:
        """
        Retourne la liste des projets référencés mais non disponibles.
        
        Args:
            available_projects: Liste des projets disponibles
            
        Returns:
            Liste des projets manquants
        """
        available_set = set(available_projects)
        referenced_set = set(self.projects_referenced)
        return sorted(list(referenced_set - available_set))
    
    def get_unused_projects(self, available_projects: List[str]) -> List[str]:
        """
        Retourne la liste des projets disponibles mais non référencés.
        
        Args:
            available_projects: Liste des projets disponibles
            
        Returns:
            Liste des projets non utilisés
        """
        available_set = set(available_projects)
        referenced_set = set(self.projects_referenced)
        return sorted(list(available_set - referenced_set))
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Retourne des statistiques sur les données XML.
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        stats = {
            'file_size_bytes': len(self.raw_xml),
            'file_size_kb': len(self.raw_xml) / 1024,
            'element_count': 0,
            'projects_referenced_count': len(self.projects_referenced),
            'projects_referenced': self.projects_referenced,
            'is_valid': self.is_valid,
            'validation_errors_count': len(self.validation_errors),
            'encoding': self.encoding
        }
        
        if self.root_element:
            stats['element_count'] = len(list(self.root_element.iter()))
            stats['root_tag'] = self.root_element.tag
            stats['root_attributes'] = dict(self.root_element.attrib)
        
        return stats
    
    def save_to_file(self, file_path: str | Path, pretty: bool = True) -> None:
        """
        Sauvegarde les données XML dans un fichier.
        
        Args:
            file_path: Chemin de destination
            pretty: Si True, formate le XML avec indentation
        """
        if not self.parsed_data:
            raise ValueError("Aucune donnée XML à sauvegarder")
        
        path = Path(file_path)
        
        if pretty and self.root_element:
            self._indent_xml(self.root_element)
        
        # Sauvegarde avec déclaration XML
        with open(path, 'w', encoding=self.encoding) as f:
            f.write(f'<?xml version="1.0" encoding="{self.encoding}"?>\n')
            self.parsed_data.write(f, encoding='unicode', xml_declaration=False)
    
    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Ajoute l'indentation au XML pour le rendre lisible."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def validate(self) -> bool:
        """
        Valide complètement les données XML.
        
        Returns:
            True si valide, False sinon
        """
        if not self.is_valid:
            self.parse_xml()
        
        return self.is_valid
    
    def get_validation_report(self) -> str:
        """
        Génère un rapport de validation.
        
        Returns:
            Rapport de validation formaté
        """
        report = []
        report.append("=== RAPPORT DE VALIDATION XML ===")
        
        if self.file_path:
            report.append(f"Fichier: {self.file_path}")
        
        report.append(f"Statut: {'✓ VALIDE' if self.is_valid else '✗ INVALIDE'}")
        report.append(f"Encodage: {self.encoding}")
        report.append(f"Taille: {len(self.raw_xml)} caractères")
        
        if self.validation_errors:
            report.append("\nERREURS:")
            for i, error in enumerate(self.validation_errors, 1):
                report.append(f"  {i}. {error}")
        
        if self.projects_referenced:
            report.append(f"\nPROJETS RÉFÉRENCÉS ({len(self.projects_referenced)}):")
            for project in self.projects_referenced:
                report.append(f"  - {project}")
        else:
            report.append("\nAucun projet référencé trouvé")
        
        return "\n".join(report)
    
    def __str__(self) -> str:
        """Représentation textuelle des données XML."""
        status = "✓" if self.is_valid else "✗"
        return f"XMLData({status}, {len(self.projects_referenced)} projets référencés)"
    
    def __repr__(self) -> str:
        """Représentation détaillée des données XML."""
        return (f"XMLData(file_path={self.file_path}, "
                f"is_valid={self.is_valid}, "
                f"projects_count={len(self.projects_referenced)})")


class XMLDataError(Exception):
    """Exception levée lors d'erreurs de traitement des données XML."""
    pass