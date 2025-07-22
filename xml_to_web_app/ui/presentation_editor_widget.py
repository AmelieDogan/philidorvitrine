"""
Interface d'édition de la présentation de l'édition pour l'application XML to Web.
Permet l'édition du titre et du sous-titre de l'édition numérique,
ainsi que du contenu HTML de la page de présentation avec un éditeur WYSIWYG.

Cette interface se présente sous la forme d'une classe qui hérite de BaseEditor.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QGroupBox, QFormLayout
from PySide6.QtCore import Qt

from .base_editor import BaseEditorWidget
from ..models.presentation import Presentation, PresentationValidationError, validate_presentation_title, validate_presentation_subtitle, validate_presentation_content
from ..utils.french_date_utils import format_french_datetime

class PresentationEditorWidget(BaseEditorWidget):
    """
    Fenêtre d'édition de la présentation de l'édition avec éditeur WYSIWYG intégré.
    
    Permet l'édition du titre et sous-titre du site web de l'édition et de son contenu HTML.
    Supporte la modification du contenu de la page de présentation.
    
    Hérite de BaseEditorWidget pour les fonctionnalités communes d'édition.
    """
    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Crée la section pour le titre et le sous-titre + les métadonnées."""
        title = QLabel("Editer la page d'accueil de l'édition")
        title.setObjectName("title")
        title. setAlignment(Qt.AlignCenter)

        info_group = QGroupBox()
        info_layout = QFormLayout(info_group)

        # Informations en lecture seule (pour projets existants)
        if not self._is_new_data:
            self.updated_label = QLabel(format_french_datetime(self._data.updated_at))
            info_layout.addRow("Modifié le:", self.updated_label)
        
        # Champ titre
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Titre de l'édition numérique")
        self.title_edit.setMaxLength(200)
        info_layout.addRow("Titre de l'édition numérique:", self.title_edit)

        # Champ sous-titre
        self.subtitle_edit = QLineEdit()
        self.subtitle_edit.setPlaceholderText("Sous-titre de l'édition numérique")
        self.subtitle_edit.setMaxLength(300)
        info_layout.addRow("Sous-titre de l'édition numérique:", self.subtitle_edit)
        
        parent_layout.addWidget(title)
        parent_layout.addWidget(info_group)

    def _setup_specific_connections(self) -> None:
        """Configure les connexions spécifiques au projet."""
        self.title_edit.textChanged.connect(self._on_title_changed)
        self.subtitle_edit.textChanged.connect(self._on_subtitle_changed)

    def _load_data(self) -> None:
        """Charge les données du projet dans l'interface."""
        if not self._data:
            return
        
        # Charge les informations de base
        self.title_edit.setText(self._data.title)
        self.subtitle_edit.setText(self._data.subtitle)
        
        # Met à jour les informations de lecture seule
        self.updated_label.setText(format_french_datetime(self._data.updated_at))
        
        self._update_status(f"Chargement de la présentation")

    def _load_initial_content(self) -> None:
        """Charge le contenu initial de présentation."""
        if self._data and self._data.content_html:
            self.wysiwyg_editor.load_content(self._data.content_html)
            self.html_editor.setPlainText(self._data.content_html)
            self._initial_content_loaded = True
            self._update_status(f"Présentation de l'édition chargée")
        else:
            self._update_status("Présentation par défaut prête")

    def _validate_data(self) -> bool:
        """Valide les données du projet."""
        return self._validate_presentation_title() and self._validate_presentation_subtitle()

    def _validate_presentation_title(self) -> bool:
        """
        Valide le titre de l'édition numérique.
        
        Returns:
            True si le titre est valide
        """
        title = self.title_edit.text().strip()
        
        try:
            validate_presentation_title(title)
            self.title_edit.setStyleSheet("")
            return True
        except PresentationValidationError as e:
            self.title_edit.setStyleSheet("border: 2px solid #dc3545;")
            self._update_status(f"Titre invalide: {e}")
            return False
        
    def _validate_presentation_subtitle(self) -> bool:
        """
        Valide le sous-titre de l'édition numérique.
        
        Returns:
            True si le sous-titre est valide
        """
        subtitle = self.subtitle_edit.text().strip()
        
        try:
            validate_presentation_subtitle(subtitle)
            self.subtitle_edit.setStyleSheet("")
            return True
        except PresentationValidationError as e:
            self.subtitle_edit.setStyleSheet("border: 2px solid #dc3545;")
            self._update_status(f"Sous-titre invalide: {e}")
            return False

    def _save_data(self, content: str) -> Presentation:
        """
        Sauvegarde la présentation avec le contenu spécifié.
        
        Args:
            content: Contenu HTML de la présentation
            
        Returns:
            La présentation sauvegardée
        """
        title = self.title_edit.text().strip()
        subtitle = self.subtitle_edit.text().strip()
        
        try:
            # Valide le contenu HTML
            validate_presentation_content(content)
            
            if self._is_new_data:
                # Crée une nouvelle présentation
                presentation = Presentation(title=title, subtitle=subtitle, content_html=content)
                self._update_status(f"Nouvelle présentation créée")
                return presentation
            else:
                # Met à jour le projet existant
                self._data.title = title
                self._data.subtitle = subtitle
                self._data.update_content(content)
                self._update_status(f"Présentation mise à jour")
                return self._data
                
        except PresentationValidationError as e:
            raise Exception(f"Erreur de validation: {e}")

    def _on_data_saved_success(self, saved_data: Presentation) -> None:
        """Met à jour l'interface après une sauvegarde réussie."""
        # Met à jour les informations affichées pour les projets existants
        if hasattr(self, 'updated_label'):
            self.updated_label.setText(format_french_datetime(saved_data.updated_at))
    
    def _on_title_changed(self, text: str) -> None:
        """Callback appelé quand le nom du projet change."""
        self._mark_as_changed()
        self._validate_presentation_title()

    def _on_subtitle_changed(self, text: str) -> None:
        """Callback appelé quand l'identifiant du projet change."""
        self._mark_as_changed()
        self._validate_presentation_subtitle()

    def _get_help_text(self) -> str:
        """Retourne le texte d'aide spécifique à la présentation."""

        base_help = super()._get_help_text()
        return base_help + """
<h4>Spécificités de l'onglet présentation :</h4>
<ul>
<li><b>Titre de l'édition numérique</b> : Requis, utilisé dans l'entête de l'édition sur toutes les pages</li>
<li><b>Sous-titre de l'édition numérique</b> : Optionnel, s'affiche sous le titre de l'édition</li>
<li><b>Modification du contenu de la page de présentation</b> : Ecrase le contenu précédent au moment de la sauvegarde</li>
</ul>
"""
    
    def get_presentation(self) -> Presentation:
        """
        Retourne la présentation en cours d'édition.
        
        Returns:
            Le présentation actuelle ou None
        """
        return self.get_data()