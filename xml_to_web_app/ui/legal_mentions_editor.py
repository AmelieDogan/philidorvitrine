"""
Interface d'édition des mentions légales de l'édition pour l'application XML to Web.
Permet l'édition du contenu HTML des mentions légales avec un éditeur WYSIWYG.

Cette interface se présente sous la forme d'une classe qui hérite de BaseEditor.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QGroupBox, QFormLayout, QWidget
)

from ..utils.french_date_utils import format_french_datetime
from .base_editor import BaseEditor
from ..models.legal_mentions import LegalMentions, LegalMentionsValidationError, validate_legal_mentions_content


class LegalMentionsEditor(BaseEditor):
    """
    Fenêtre d'édition des mentions légales de l'édition avec éditeur WYSIWYG intégré.
    
    Permet l'édition du contenu HTML d ela page des mentios légales.
    Supporte la modification du contenu de la page mentions légales.
    
    Hérite de BaseEditor pour les fonctionnalités communes d'édition.
    """
    
    def __init__(self, legal_mentions: Optional[LegalMentions] = None, parent: Optional[QWidget] = None):
        """
        Initialise l'éditeur des mentions légales de l'édition.
        
        Args:
            legal_mentions: Mentions légales à éditer
            parent: Widget parent
        """
        super().__init__(
            data=legal_mentions,
            parent=parent,
            window_title="Éditeur des mentions légales de l'édition",
            dialog_size=(1000, 700)
        )
    
    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Crée les métadonnées."""
        info_group = QGroupBox()
        info_layout = QFormLayout(info_group)

        # Informations en lecture seule (pour projets existants)
        if not self._is_new_data:
            self.updated_label = QLabel(format_french_datetime(self._data.updated_at))
            info_layout.addRow("Modifié le:", self.updated_label)
        
        parent_layout.addWidget(info_group)
    
    def _load_data(self) -> None:
        """Charge les données des mentions légales dans l'interface."""
        if not self._data:
            return
        
        # Met à jour les informations de lecture seule
        self.updated_label.setText(format_french_datetime(self._data.updated_at))
        
        self._update_status(f"Chargement des mentions légales")
    
    def _load_initial_content(self) -> None:
        """Charge le contenu initial des mentions légales."""
        if self._data and self._data.content_html:
            self.wysiwyg_editor.load_content(self._data.content_html)
            self.html_editor.setPlainText(self._data.content_html)
            self._initial_content_loaded = True
            self._update_status(f"Mentions légales de l'édition chargées")
        else:
            self._update_status("Mentions légales par défaut prêtes")

    def _validate_data(self) -> bool:
        """Valide le contenu HTML."""
        content = self.html_editor.toPlainText()
        try:
            validate_legal_mentions_content(content)
            self.html_editor.setStyleSheet("")
            return True
        except LegalMentionsValidationError as e:
            self.html_editor.setStyleSheet("border: 2px solid #dc3545;")
            self._update_status(f"Contenu HTML invalide : {e}")
            return False

    
    def _save_data(self, content: str) -> LegalMentions:
        """
        Sauvegarde les mentions légales avec le contenu spécifié.
        
        Args:
            content: Contenu HTML des mentions légales
            
        Returns:
            Les mentions légales sauvegardées
        """
        
        try:
            # Valide le contenu HTML
            validate_legal_mentions_content(content)
            
            if self._is_new_data:
                # Crée une nouvelle présentation
                legal_mentions = LegalMentions(content_html=content)
                self._update_status(f"Nouvelles mentions légales créées")
                return legal_mentions
            else:
                # Met à jour le projet existant
                self._data.update_content(content)
                self._update_status("Mentions légales mises à jour")
                return self._data
                
        except LegalMentionsValidationError as e:
            raise Exception(f"Erreur de validation: {e}")
    
    def _on_data_saved_success(self, saved_data: LegalMentions) -> None:
        """Met à jour l'interface après une sauvegarde réussie."""
        # Met à jour les informations affichées
        if hasattr(self, 'updated_label'):
            self.updated_label.setText(format_french_datetime(saved_data.updated_at))
    
    def _get_help_text(self) -> str:
        """Retourne le texte d'aide spécifique aux mentions légales."""
        base_help = super()._get_help_text()
        
        legal_mentions_specific_help = """
<h4>Spécificités de l'onglet mentions légales :</h4>
<ul>
<li><b>Modification du contenu de la page de mentions légales</b> : Ecrase le contenu précédent au moment de la sauvegarde</li>
</ul>
        """
        
        return base_help.replace("</ul>", f"</ul>{legal_mentions_specific_help}")
    
    # Méthodes publiques spécifiques aux projets
    
    def get_legal_mentions(self) -> Optional[LegalMentions]:
        """
        Retourne les mentions légales en cours d'édition.
        
        Returns:
            Les mentions légales actuelles ou None
        """
        return self.get_data()