"""
Interface d'édition de l'à propos de l'édition pour l'application XML to Web.
Permet l'édition du contenu HTML de la page à propos avec un éditeur WYSIWYG.

Cette interface se présente sous la forme d'une classe qui hérite de BaseEditor.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QFormLayout
from PySide6.QtCore import Qt

from .base_editor import BaseEditorWidget
from ..models.about import About, AboutValidationError, validate_about_content
from ..utils.french_date_utils import format_french_datetime

class AboutEditorWidget(BaseEditorWidget):
    """
    Fenêtre d'édition de la page à propos de l'édition avec éditeur WYSIWYG intégré.
    
    Permet l'édition du contenu HTML de la page à propos de l'édition numérique.
    Supporte la modification du contenu de la page à propos.
    
    Hérite de BaseEditor pour les fonctionnalités communes d'édition.
    """
    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Crée les métadonnées."""
        title = QLabel("Editer la page 'A propos'")
        title.setObjectName("title")
        title. setAlignment(Qt.AlignCenter)

        info_group = QGroupBox()
        info_layout = QFormLayout(info_group)

        # Informations en lecture seule (pour projets existants)
        if not self._is_new_data:
            self.updated_label = QLabel(format_french_datetime(self._data.updated_at))
            info_layout.addRow("Modifié le:", self.updated_label)
        
        parent_layout.addWidget(title)
        parent_layout.addWidget(info_group)

    def _load_data(self) -> None:
        """Charge les données de la page à propos dans l'interface."""
        if not self._data:
            return
        
        # Met à jour les informations de lecture seule
        self.updated_label.setText(format_french_datetime(self._data.updated_at))
        
        self._update_status(f"Chargement de la page à propos")
    
    def _load_initial_content(self) -> None:
        """Charge le contenu initial de l'à propos."""
        if self._data and self._data.content_html:
            self.wysiwyg_editor.load_content(self._data.content_html)
            self.html_editor.setPlainText(self._data.content_html)
            self._initial_content_loaded = True
            self._update_status(f"A propos de l'édition chargé")
        else:
            self._update_status("A propos par défaut prêt")

    def _validate_data(self) -> bool:
        """Valide le contenu HTML."""
        content = self.html_editor.toPlainText()
        try:
            validate_about_content(content)
            self.html_editor.setStyleSheet("")
            return True
        except AboutValidationError as e:
            self.html_editor.setStyleSheet("border: 2px solid #dc3545;")
            self._update_status(f"Contenu HTML invalide : {e}")
            return False

    
    def _save_data(self, content: str) -> About:
        """
        Sauvegarde l'à propos avec le contenu spécifié.
        
        Args:
            content: Contenu HTML de l'à propos
            
        Returns:
            L'à propos sauvegardé
        """
        
        try:
            # Valide le contenu HTML
            validate_about_content(content)
            
            if self._is_new_data:
                # Crée une nouvelle présentation
                about = About(content_html=content)
                self._update_status(f"Nouvel à propos créées")
                return about
            else:
                # Met à jour le projet existant
                self._data.update_content(content)
                self._update_status("A propos mis à jour")
                return self._data
                
        except AboutValidationError as e:
            raise Exception(f"Erreur de validation: {e}")
    
    def _on_data_saved_success(self, saved_data: About) -> None:
        """Met à jour l'interface après une sauvegarde réussie."""
        # Met à jour les informations affichées
        if hasattr(self, 'updated_label'):
            self.updated_label.setText(format_french_datetime(saved_data.updated_at))
    
    def _get_help_text(self) -> str:
        """Retourne le texte d'aide spécifique à l'à propos."""
        base_help = super()._get_help_text()
        
        about_specific_help = """
<h4>Spécificités de l'onglet mentions légales :</h4>
<ul>
<li><b>Modification du contenu de la page à propos</b> : Ecrase le contenu précédent au moment de la sauvegarde</li>
</ul>
        """
        
        return base_help.replace("</ul>", f"</ul>{about_specific_help}")
    
    # Méthodes publiques spécifiques aux projets
    
    def get_about(self) -> About:
        """
        Retourne l'à propos en cours d'édition.
        
        Returns:
            L'à propos actuel ou None
        """
        return self.get_data()