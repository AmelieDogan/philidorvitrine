"""
Gestionnaire de projets pour l'application XML to Web.
Gère la logique métier des projets : CRUD, validation, et sérialisation XML.
"""

from typing import List, Dict, Optional, Any
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

from ..models.project import Project, ProjectValidationError, validate_project_name, validate_project_id, validate_html_content


class ProjectManager:
    """
    Gère la logique métier des projets.
    
    Fonctionnalités :
    - CRUD des projets (Create, Read, Update, Delete)
    - Validation des données
    - Sauvegarde/chargement XML des projets
    - Gestion de la cohérence des données
    """
    
    def __init__(self):
        """Initialise le gestionnaire de projets."""
        self._projects: Dict[str, Project] = {}  # Clé = UUID du projet
        self._projects_by_id: Dict[str, Project] = {}  # Clé = ID utilisateur du projet
        self._logger = logging.getLogger(__name__)
        self._logger.info("ProjectManager initialisé")
    
    def create_project(self, project_id: str, name: str, description_html: str = "", project_uuid: Optional[str] = None) -> Project:
        """
        Crée un nouveau projet.
        
        Args:
            project_id: Identifiant choisi par l'utilisateur pour le projet
            name: Nom du projet
            description_html: Description HTML du projet (optionnel)
            project_uuid: Identifent unique du projet pour la gestion interne (optionnel), si non importé, créé lors de la création du projet
            
        Returns:
            Le projet créé
            
        Raises:
            ProjectValidationError: Si les données sont invalides
            ValueError: Si un projet avec cet identifiant existe déjà
        """
        # Validation des données
        validate_project_id(project_id)
        validate_project_name(name)
        if description_html:
            validate_html_content(description_html)
        
        # Vérifie l'unicité de l'identifiant
        if self._id_exists(project_id):
            raise ValueError(f"Un projet avec l'identifiant '{project_id}' existe déjà")
        
        try:
            # Crée le projet
            project = Project(
                id=project_id,
                name=name,
                description_html=description_html.strip()
            )
            
            # Stocke le projet avec les deux clés
            self._projects[project.uuid] = project
            self._projects_by_id[project.id] = project
            
            self._logger.info(f"Projet créé: {project.name} (ID: {project.id}, UUID: {project.uuid})")
            return project
            
        except Exception as e:
            self._logger.error(f"Erreur lors de la création du projet '{name}': {e}")
            raise ProjectValidationError(f"Impossible de créer le projet: {e}")
    
    def update_project(self, project_uuid: str, name: str = None, project_id: str = None, description_html: str = None) -> Project:
        """
        Met à jour un projet existant.
        
        Args:
            project_uuid: UUID du projet à mettre à jour
            name: Nouveau nom (optionnel)
            project_id: Nouvel identifiant (optionnel)
            description_html: Nouveau contenu HTML (optionnel)
            
        Returns:
            Le projet mis à jour
            
        Raises:
            ValueError: Si le projet n'existe pas
            ProjectValidationError: Si les nouvelles données sont invalides
        """
        if project_uuid not in self._projects:
            raise ValueError(f"Projet non trouvé: {project_uuid}")
        
        project = self._projects[project_uuid]
        old_id = project.id
        
        # Validation des nouvelles données
        if name is not None:
            validate_project_name(name)
            project.name = name
            
        if project_id is not None:
            validate_project_id(project_id)
            
            # Vérifier l'unicité seulement si l'ID a changé
            if project_id != old_id and self._id_exists(project_id):
                raise ValueError(f"Un projet avec l'identifiant '{project_id}' existe déjà")
            
            # Mettre à jour les index
            if old_id != project_id:
                del self._projects_by_id[old_id]
                self._projects_by_id[project_id] = project
                project.id = project_id
                
        if description_html is not None:
            if description_html.strip():
                validate_html_content(description_html)
            project.description_html = description_html.strip()
        
        # Mettre à jour la date de modification
        project.updated_at = datetime.now()
        
        self._logger.info(f"Projet mis à jour: {project.name} (ID: {project.id}, UUID: {project.uuid})")
        return project

    
    def delete_project(self, project_uuid: str) -> bool:
        """
        Supprime un projet.
        
        Args:
            project_uuid: UUID du projet à supprimer
            
        Returns:
            True si le projet a été supprimé, False s'il n'existait pas
        """
        if project_uuid in self._projects:
            project = self._projects[project_uuid]
            project_name = project.name
            project_id = project.id
            
            # Supprime des deux dictionnaires
            del self._projects[project_uuid]
            del self._projects_by_id[project_id]
            
            self._logger.info(f"Projet supprimé: {project_name} (ID: {project_id}, UUID: {project_uuid})")
            return True
        
        self._logger.warning(f"Tentative de suppression d'un projet inexistant: {project_uuid}")
        return False
    
    def get_project(self, project_uuid: str) -> Project:
        """
        Récupère un projet par son UUID, avec erreur.
        
        Args:
            project_uuid: UUID du projet
            
        Returns:
            Le projet correspondant
            
        Raises:
            ValueError: Si le projet n'existe pas
        """
        if project_uuid not in self._projects:
            raise ValueError(f"Projet non trouvé: {project_uuid}")
        
        return self._projects[project_uuid]
    
    def get_project_by_uuid(self, uuid: str) -> Optional[Project]:
        """
        Récupère un projet par son uuid sans erreur.
        
        Args:
            uuid : identifiant unique du projet
            
        Returns:
            Le projet correspondant ou None si non trouvé
        """
        for project in self._projects.values():
            if project.uuid == uuid:
                return project
        return None
    
    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Récupère un projet par son identifiant utilisateur.
        
        Args:
            project_id: Identifiant du projet (version nettoyée ou originale)
            
        Returns:
            Le projet correspondant ou None si non trouvé
        """
        return self._find_project_by_id(project_id)
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """
        Récupère un projet par son nom.
        
        Args:
            name: Nom du projet
            
        Returns:
            Le projet correspondant ou None si non trouvé
        """
        for project in self._projects.values():
            if project.name == name:
                return project
        return None
    
    def list_projects(self) -> List[Project]:
        """
        Retourne la liste de tous les projets.
        
        Returns:
            Liste des projets triée par date de mise à jour (plus récent en premier)
        """
        projects = list(self._projects.values())
        return sorted(projects, key=lambda p: p.updated_at, reverse=True)
    
    def list_project_uuids(self) -> List[str]:
        """Retourne la liste des UUIDs des projets."""
        return list(self._projects.keys())
    
    def list_project_ids(self) -> List[str]:
        """Retourne la liste des identifiants utilisateur des projets."""
        return list(self._projects_by_id.keys())
    
    def get_project_count(self) -> int:
        """
        Retourne le nombre de projets.
        
        Returns:
            Nombre de projets
        """
        return len(self._projects)
    
    def clear_all_projects(self) -> None:
        """Supprime tous les projets."""
        count = len(self._projects)
        self._projects.clear()
        self._projects_by_id.clear()
        self._logger.info(f"Tous les projets supprimés ({count} projets)")
    
    def get_projects_xml(self, pretty: bool = True) -> str:
        """
        Génère le XML contenant tous les projets.
        
        Args:
            pretty: Si True, formate le XML avec indentation
            
        Returns:
            Chaîne XML contenant tous les projets
        """
        # Crée l'élément racine
        root = ET.Element("projects")
        root.set("count", str(len(self._projects)))
        root.set("generated", datetime.now().isoformat())
        
        # Ajoute chaque projet
        for project in self.list_projects():
            project_elem = project.to_xml_element()
            root.append(project_elem)
        
        # Formate si demandé
        if pretty:
            self._indent_xml(root)
        
        # Génère le XML complet avec déclaration
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
    
    def load_from_xml(self, xml_content: str) -> int:
        """
        Charge les projets depuis un contenu XML.
        
        Args:
            xml_content: Contenu XML contenant les projets
            
        Returns:
            Nombre de projets chargés
            
        Raises:
            ValueError: Si le XML est invalide ou mal formaté
        """
        try:
            # Parse le XML
            root = ET.fromstring(xml_content)
            
            if root.tag != "projects":
                # Essaie de traiter comme un seul projet
                if root.tag == "project":
                    project = Project.from_xml_element(root)
                    
                    # Vérifie les conflits d'identifiant
                    if self._id_exists(project.id):
                        raise ValueError(f"Projet avec l'identifiant '{project.id}' existe déjà")
                    
                    self._projects[project.uuid] = project
                    self._projects_by_id[project.id] = project
                    self._logger.info(f"Projet unique chargé: {project.name}")
                    return 1
                else:
                    raise ValueError(f"Élément racine invalide: attendu 'projects' ou 'project', reçu '{root.tag}'")
            
            # Charge tous les projets
            loaded_count = 0
            conflicts = []
            
            for project_elem in root.findall("project"):
                try:
                    project = Project.from_xml_element(project_elem)
                    
                    # Vérifie les conflits d'identifiant
                    existing = self._find_project_by_id(project.id)
                    if existing:
                        conflicts.append(f"Projet avec l'identifiant '{project.id}' existe déjà")
                        continue
                    
                    self._projects[project.uuid] = project
                    self._projects_by_id[project.id] = project
                    loaded_count += 1
                    
                except Exception as e:
                    self._logger.warning(f"Erreur lors du chargement d'un projet: {e}")
                    conflicts.append(f"Projet invalide ignoré: {e}")
            
            self._logger.info(f"{loaded_count} projets chargés depuis XML")
            
            if conflicts:
                conflict_msg = "\n".join(conflicts)
                raise ValueError(f"Certains projets n'ont pas pu être chargés:\n{conflict_msg}")
            
            return loaded_count
            
        except ET.ParseError as e:
            raise ValueError(f"XML invalide: {e}")
        except Exception as e:
            self._logger.error(f"Erreur lors du chargement XML: {e}")
            raise ValueError(f"Impossible de charger les projets: {e}")
    
    def export_project_xml(self, project_uuid: str) -> str:
        """
        Exporte un seul projet au format XML.
        
        Args:
            project_uuid: UUID du projet à exporter
            
        Returns:
            Chaîne XML du projet
            
        Raises:
            ValueError: Si le projet n'existe pas
        """
        project = self.get_project(project_uuid)
        xml_str = project.to_xml_string(pretty=True)
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
    
    def validate_all_projects(self) -> List[str]:
        """
        Valide tous les projets et retourne la liste des erreurs.
        
        Returns:
            Liste des erreurs de validation (vide si tout est valide)
        """
        errors = []
        
        for project in self._projects.values():
            try:
                validate_project_id(project.id)
                validate_project_name(project.name)
                if project.description_html:
                    validate_html_content(project.description_html)
            except ProjectValidationError as e:
                errors.append(f"Projet '{project.name}' (ID: {project.id}): {e}")
        
        return errors
    
    def get_project_stats(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur les projets.
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        projects = list(self._projects.values())
        
        if not projects:
            return {
                "total": 0,
                "empty": 0,
                "with_content": 0,
                "oldest": None,
                "newest": None,
                "avg_content_length": 0
            }
        
        empty_count = sum(1 for p in projects if p.is_empty())
        content_lengths = [len(p.description_html) for p in projects if p.description_html]
        
        return {
            "total": len(projects),
            "empty": empty_count,
            "with_content": len(projects) - empty_count,
            "oldest": min(projects, key=lambda p: p.created_at),
            "newest": max(projects, key=lambda p: p.created_at),
            "avg_content_length": sum(content_lengths) / len(content_lengths) if content_lengths else 0
        }
    
    def is_id_available(self, project_id: str) -> bool:
        """
        Vérifie si un identifiant est disponible.
        
        Args:
            project_id: Identifiant à vérifier
            
        Returns:
            True si l'identifiant est disponible
        """
        return not self._id_exists(project_id)
    
    # Méthodes privées
    
    def _id_exists(self, project_id: str) -> bool:
        """Vérifie si un identifiant nettoyé existe déjà."""
        return project_id in self._projects_by_id
    
    def _find_project_by_id(self, project_id: str) -> Optional[Project]:
        """Trouve un projet par son identifiant nettoyé."""
        return self._projects_by_id.get(project_id)
    
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


class ProjectManagerError(Exception):
    """Exception de base pour les erreurs du ProjectManager."""
    pass


class ProjectNotFoundError(ProjectManagerError):
    """Exception levée quand un projet demandé n'est pas trouvé."""
    pass


class ProjectIdConflictError(ProjectManagerError):
    """Exception levée quand il y a un conflit d'identifiant de projet."""
    pass