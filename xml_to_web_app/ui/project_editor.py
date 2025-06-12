"""
Interface d'édition de projet pour l'application XML to Web.
Permet l'édition du nom et du contenu HTML d'un projet avec un éditeur WYSIWYG.
Version refactorisée héritant de BaseEditor.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QGroupBox, QFormLayout, QWidget
)

from ..utils.french_date_utils import format_french_datetime
from .base_editor import BaseEditor
from ..models.project import Project, ProjectValidationError, validate_project_name, validate_project_id, validate_html_content


class ProjectEditor(BaseEditor):
    """
    Fenêtre d'édition de projet avec éditeur WYSIWYG intégré.
    
    Permet l'édition du nom du projet et de son contenu HTML.
    Supporte la création de nouveaux projets et la modification de projets existants.
    
    Hérite de BaseEditor pour les fonctionnalités communes d'édition.
    """
    
    def __init__(self, project: Optional[Project] = None, parent: Optional[QWidget] = None):
        """
        Initialise l'éditeur de projet.
        
        Args:
            project: Projet à éditer (None pour créer un nouveau projet)
            parent: Widget parent
        """
        super().__init__(
            data=project,
            parent=parent,
            window_title="Éditeur de Projet",
            dialog_size=(1000, 700)
        )
    
    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Crée la section d'informations du projet."""
        info_group = QGroupBox("Informations du Projet")
        info_layout = QFormLayout(info_group)
        
        # Champ nom du projet
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du projet (requis)")
        self.name_edit.setMaxLength(100)
        info_layout.addRow("Nom du projet:", self.name_edit)

        # Champ identifiant Philidor4 du projet
        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("Identifiant dans Philidor4 (requis)")
        self.id_edit.setMaxLength(100)
        info_layout.addRow("Identifiant Philidor4:", self.id_edit)
        
        # Informations en lecture seule (pour projets existants)
        if not self._is_new_data:
            self.created_label = QLabel(format_french_datetime(self._data.created_at))
            self.updated_label = QLabel(format_french_datetime(self._data.updated_at))
            info_layout.addRow("Créé le:", self.created_label)
            info_layout.addRow("Modifié le:", self.updated_label)
        
        parent_layout.addWidget(info_group)
    
    def _setup_specific_connections(self) -> None:
        """Configure les connexions spécifiques au projet."""
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.id_edit.textChanged.connect(self._on_id_changed)
    
    def _load_data(self) -> None:
        """Charge les données du projet dans l'interface."""
        if not self._data:
            return
        
        # Charge les informations de base
        self.name_edit.setText(self._data.name)
        self.id_edit.setText(self._data.id)
        
        # Met à jour les informations de lecture seule
        if hasattr(self, 'created_label'):
            self.created_label.setText(format_french_datetime(self._data.created_at))
            self.updated_label.setText(format_french_datetime(self._data.updated_at))
        
        self._update_status(f"Chargement du projet: {self._data.name}")
    
    def _setup_new_data(self) -> None:
        """Configure l'interface pour un nouveau projet."""
        self.name_edit.setPlaceholderText("Nom du nouveau projet")
        self.name_edit.setFocus()
        self._update_status("Nouveau projet - Saisissez le nom du projet")
    
    def _load_initial_content(self) -> None:
        """Charge le contenu initial du projet."""
        if self._data and self._data.description_html:
            self.wysiwyg_editor.load_content(self._data.description_html)
            self.html_editor.setPlainText(self._data.description_html)
            self._initial_content_loaded = True
            self._update_status(f"Projet chargé: {self._data.name}")
        else:
            self._update_status("Nouveau projet prêt")
    
    def _validate_data(self) -> bool:
        """Valide les données du projet."""
        return self._validate_name() and self._validate_id()
    
    def _validate_name(self) -> bool:
        """
        Valide le nom du projet.
        
        Returns:
            True si le nom est valide
        """
        name = self.name_edit.text().strip()
        
        try:
            validate_project_name(name)
            self.name_edit.setStyleSheet("")
            return True
        except ProjectValidationError as e:
            self.name_edit.setStyleSheet("border: 2px solid #dc3545;")
            self._update_status(f"Nom invalide: {e}")
            return False
        
    def _validate_id(self) -> bool:
        """
        Valide l'identifiant du projet.
        
        Returns:
            True si l'identifiant est valide
        """
        project_id = self.id_edit.text().strip()
        
        try:
            validate_project_id(project_id)
            self.id_edit.setStyleSheet("")
            return True
        except ProjectValidationError as e:
            self.id_edit.setStyleSheet("border: 2px solid #dc3545;")
            self._update_status(f"Identifiant invalide: {e}")
            return False
    
    def _save_data(self, content: str) -> Project:
        """
        Sauvegarde le projet avec le contenu spécifié.
        
        Args:
            content: Contenu HTML du projet
            
        Returns:
            Le projet sauvegardé
        """
        name = self.name_edit.text().strip()
        project_id = self.id_edit.text().strip()
        
        try:
            # Valide le contenu HTML
            validate_html_content(content)
            
            if self._is_new_data:
                # Crée un nouveau projet
                project = Project(id=project_id, name=name, description_html=content)
                self._update_status(f"Nouveau projet créé: {name}")
                return project
            else:
                # Met à jour le projet existant
                self._data.name = name
                self._data.id = project_id
                self._data.update_content(content)
                self._update_status(f"Projet mis à jour: {name}")
                return self._data
                
        except ProjectValidationError as e:
            raise Exception(f"Erreur de validation: {e}")
    
    def _on_data_saved_success(self, saved_data: Project) -> None:
        """Met à jour l'interface après une sauvegarde réussie."""
        # Met à jour les informations affichées pour les projets existants
        if hasattr(self, 'updated_label'):
            self.updated_label.setText(format_french_datetime(saved_data.updated_at))
    
    def _on_name_changed(self, text: str) -> None:
        """Callback appelé quand le nom du projet change."""
        self._mark_as_changed()
        self._validate_name()

    def _on_id_changed(self, text: str) -> None:
        """Callback appelé quand l'identifiant du projet change."""
        self._mark_as_changed()
        self._validate_id()
    
    def _get_help_text(self) -> str:
        """Retourne le texte d'aide spécifique aux projets."""
        base_help = super()._get_help_text()
        
        project_specific_help = """
<h4>Spécificités des projets :</h4>
<ul>
<li><b>Nom du projet</b> : Requis, utilisé comme identifiant</li>
<li><b>Identifiant Philidor4</b> : Requis, doit être unique</li>
<li><b>Création vs Modification</b> : Interface adaptée selon le contexte</li>
</ul>
        """
        
        return base_help.replace("</ul>", f"</ul>{project_specific_help}")
    
    # Méthodes publiques spécifiques aux projets
    
    def get_project(self) -> Optional[Project]:
        """
        Retourne le projet en cours d'édition.
        
        Returns:
            Le projet actuel ou None
        """
        return self.get_data()