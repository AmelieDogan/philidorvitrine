"""
Superclasse pour les interfaces d'édition de l'application XML to Web.
Fournit les fonctionnalités communes pour l'édition de contenu avec éditeur WYSIWYG.
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import Optional, Callable, Any
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QTabWidget, QWidget,
    QMessageBox, QGroupBox, QStatusBar, QFrame,
    QProgressBar, QSizePolicy
)
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from .wysiwyg_editor import WysiwygEditor

class MetaQWidgetABC(type(QWidget), ABCMeta):
    """Métaclasse combinée pour résoudre le conflit entre QDialog et ABC."""
    pass

class BaseEditorWidget(QWidget, metaclass=MetaQWidgetABC):
    """
    Widget de base pour les interfaces d'édition avec éditeur WYSIWYG.
    
    Fournit les fonctionnalités communes :
    - Éditeur WYSIWYG avec onglets (visuel/HTML)
    - Gestion des modifications non sauvegardées
    - Barre de statut et indicateurs
    - Raccourcis clavier standardisés
    - Synchronisation entre éditeurs
    
    Les classes filles doivent implémenter :
    - _create_info_section() : Section d'informations spécifiques
    - _validate_data() : Validation des données
    - _save_data() : Logique de sauvegarde
    - _load_data() : Chargement des données
    
    Signals:
        data_saved: Émis quand les données sont sauvegardées (Any)
        editing_cancelled: Émis quand l'édition est annulée
        help_requested: Émis quand l'aide est demandée
    """
    
    # Signaux Qt communs
    data_saved = Signal(object)  # Type générique pour les données sauvegardées
    editing_cancelled = Signal()
    help_requested = Signal()
    
    def __init__(self, data: Optional[Any] = None, parent: Optional[QWidget] = None,
                 show_action_buttons: bool = True):
        """
        Initialise l'éditeur de base.
        
        Args:
            data: Données à éditer (None pour création)
            parent: Widget parent
            show_action_buttons: Afficher les boutons d'action (Sauvegarder/Annuler)
        """
        super().__init__(parent)
        
        self._logger = logging.getLogger(self.__class__.__name__)
        self._data = data
        self._is_new_data = data is None
        self._has_unsaved_changes = False
        self._auto_save_enabled = True
        self._content_change_callback: Optional[Callable[[str], None]] = None
        self._show_action_buttons = show_action_buttons
        
        # État de l'éditeur
        self._editor_ready = False
        self._initial_content_loaded = False
        
        self._setup_ui()
        self._setup_connections()
        self._setup_shortcuts()
        
        # Initialisation des données spécifiques
        self._initialize_data()

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.adjustSize()
        
        self._logger.info(f"{self.__class__.__name__} initialisé - {'Nouvelles données' if self._is_new_data else 'Données existantes'}")
    
    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur commune."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Section d'informations spécifiques (implémentée par les classes filles)
        self._create_info_section(main_layout)
        
        # Section éditeur commune
        self._create_editor_section(main_layout)
        
        # Barre de statut commune
        self._create_status_section(main_layout)
        
        # Boutons d'action communs (optionnels)
        if self._show_action_buttons:
            self._create_action_buttons(main_layout)
    
    @abstractmethod
    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        """
        Crée la section d'informations spécifiques.
        À implémenter dans les classes filles.
        
        Args:
            parent_layout: Layout parent où ajouter la section
        """
        pass
    
    def _create_editor_section(self, parent_layout: QVBoxLayout) -> None:
        """Crée la section d'éditeur commune avec onglets."""
        editor_group = QGroupBox("Contenu de la page")
        editor_layout = QVBoxLayout(editor_group)
        
        # Onglets pour différents modes d'édition
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("editor")
        
        # Onglet éditeur WYSIWYG
        self._create_wysiwyg_tab()
        
        # Onglet éditeur HTML brut
        self._create_html_tab()
        
        editor_layout.addWidget(self.tab_widget)
        parent_layout.addWidget(editor_group)
    
    def _create_wysiwyg_tab(self) -> None:
        """Crée l'onglet de l'éditeur WYSIWYG."""
        wysiwyg_widget = QWidget()
        wysiwyg_layout = QVBoxLayout(wysiwyg_widget)
        wysiwyg_layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils pour l'éditeur WYSIWYG
        toolbar_frame = QFrame()
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Boutons de l'éditeur
        self.wysiwyg_status_label = QLabel("Initialisation de l'éditeur...")
        self.wysiwyg_status_label.setStyleSheet("color: #666; font-style: italic;")
        toolbar_layout.addWidget(self.wysiwyg_status_label)
        
        toolbar_layout.addStretch()
        
        # Bouton de synchronisation
        self.sync_button = QPushButton("Synchroniser avec HTML")
        self.sync_button.setEnabled(False)
        self.sync_button.clicked.connect(self._sync_to_html_tab)
        toolbar_layout.addWidget(self.sync_button)
        
        wysiwyg_layout.addWidget(toolbar_frame)
        
        # Éditeur WYSIWYG
        self.wysiwyg_editor = WysiwygEditor()
        self.wysiwyg_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.wysiwyg_editor.setMinimumHeight(500)  # ou une valeur raisonnable

        wysiwyg_layout.addWidget(self.wysiwyg_editor)
        
        self.tab_widget.addTab(wysiwyg_widget, "Éditeur Visuel")
    
    def _create_html_tab(self) -> None:
        """Crée l'onglet de l'éditeur HTML brut."""
        html_widget = QWidget()
        html_layout = QVBoxLayout(html_widget)
        html_layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils pour l'éditeur HTML
        html_toolbar_frame = QFrame()
        html_toolbar_layout = QHBoxLayout(html_toolbar_frame)
        html_toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Informations
        html_info_label = QLabel("Édition HTML directe")
        html_info_label.setStyleSheet("color: #666; font-style: italic;")
        html_toolbar_layout.addWidget(html_info_label)
        
        html_toolbar_layout.addStretch()
        
        # Bouton de synchronisation
        self.sync_from_html_button = QPushButton("Synchroniser vers l'éditeur visuel")
        self.sync_from_html_button.clicked.connect(self._sync_from_html_tab)
        html_toolbar_layout.addWidget(self.sync_from_html_button)
        
        # Bouton de validation HTML
        self.validate_html_button = QPushButton("Valider HTML")
        self.validate_html_button.clicked.connect(self._validate_html_content)
        html_toolbar_layout.addWidget(self.validate_html_button)
        
        html_layout.addWidget(html_toolbar_frame)
        
        # Éditeur HTML brut
        self.html_editor = QTextEdit()
        self.html_editor.setPlaceholderText("Saisissez votre contenu HTML ici...")
        
        # Police monospace pour le HTML
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.html_editor.setFont(font)
        
        html_layout.addWidget(self.html_editor)
        
        self.tab_widget.addTab(html_widget, "Code HTML")
    
    def _create_status_section(self, parent_layout: QVBoxLayout) -> None:
        """Crée la barre de statut commune."""
        self.status_bar = QStatusBar()
        
        # Indicateur de changements non sauvegardés
        self.unsaved_label = QLabel()
        self.status_bar.addPermanentWidget(self.unsaved_label)
        
        # Barre de progression pour les opérations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        parent_layout.addWidget(self.status_bar)
        
        self._update_status("Prêt")
    
    def _create_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Crée les boutons d'action communs."""
        button_layout = QHBoxLayout()
        
        # Bouton d'aide
        self.help_button = QPushButton("Aide")
        self.help_button.clicked.connect(self._show_help)
        button_layout.addWidget(self.help_button)
        
        button_layout.addStretch()
        
        # Boutons principaux
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self._cancel_editing)
        self.cancel_button.setObjectName("secondary")
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton(self._get_save_button_text())
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self._save_data_wrapper)
        self.save_button.setObjectName("primary")
        button_layout.addWidget(self.save_button)
        
        parent_layout.addLayout(button_layout)
    
    def _setup_connections(self) -> None:
        """Configure les connexions de signaux communes."""
        # Connexions pour l'éditeur WYSIWYG
        self.wysiwyg_editor.editor_ready.connect(self._on_wysiwyg_ready)
        self.wysiwyg_editor.content_changed.connect(self._on_wysiwyg_content_changed)
        self.wysiwyg_editor.save_requested.connect(self._on_save_requested)
        
        # Connexions pour l'éditeur HTML
        self.html_editor.textChanged.connect(self._on_html_editor_changed)
        
        # Connexions pour les onglets
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Connexions spécifiques (à surcharger si nécessaire)
        self._setup_specific_connections()
    
    def _setup_specific_connections(self) -> None:
        """
        Configure les connexions spécifiques aux classes filles.
        Méthode vide par défaut, à surcharger si nécessaire.
        """
        pass
    
    def _setup_shortcuts(self) -> None:
        """Configure les raccourcis clavier communs."""
        # Ctrl+S pour sauvegarder
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self._save_data_wrapper)
        
        # Ctrl+Q pour annuler
        cancel_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        cancel_shortcut.activated.connect(self._cancel_editing)
        
        # F1 pour l'aide
        help_shortcut = QShortcut(QKeySequence.StandardKey.HelpContents, self)
        help_shortcut.activated.connect(self._show_help)
    
    def _initialize_data(self) -> None:
        """Initialise les données (charge ou crée)."""
        if self._data:
            self._load_data()
        else:
            self._setup_new_data()
    
    @abstractmethod
    def _load_data(self) -> None:
        """
        Charge les données existantes dans l'interface.
        À implémenter dans les classes filles.
        """
        pass
    
    @abstractmethod
    def _setup_new_data(self) -> None:
        """
        Configure l'interface pour de nouvelles données.
        À implémenter dans les classes filles.
        """
        pass
    
    def _on_wysiwyg_ready(self) -> None:
        """Callback appelé quand l'éditeur WYSIWYG est prêt."""
        self._editor_ready = True
        self.wysiwyg_status_label.setText("Éditeur prêt")
        self.wysiwyg_status_label.setStyleSheet("color: #28a745;")
        self.sync_button.setEnabled(True)
        
        # Charge le contenu initial si des données existent
        if self._data and not self._initial_content_loaded:
            self._load_initial_content()
        
        self._logger.info("Éditeur WYSIWYG prêt")
    
    @abstractmethod
    def _load_initial_content(self) -> None:
        """
        Charge le contenu initial dans l'éditeur.
        À implémenter dans les classes filles.
        """
        pass
    
    def _on_wysiwyg_content_changed(self, content: str) -> None:
        """Callback appelé quand le contenu WYSIWYG change."""
        self._mark_as_changed()
        
        if self._content_change_callback:
            self._content_change_callback(content)
    
    def _on_html_editor_changed(self) -> None:
        """Callback appelé quand le contenu HTML brut change."""
        self._mark_as_changed()
    
    def _on_tab_changed(self, index: int) -> None:
        """Callback appelé quand l'onglet actif change."""
        if index == 0:  # Onglet WYSIWYG
            self._update_status("Éditeur visuel actif")
        elif index == 1:  # Onglet HTML
            self._update_status("Éditeur HTML actif")
    
    def _on_save_requested(self) -> None:
        """Callback appelé quand une sauvegarde est demandée."""
        if self._auto_save_enabled:
            self._save_data_wrapper()
    
    def _mark_as_changed(self) -> None:
        """Marque les données comme ayant des changements non sauvegardés."""
        if not self._has_unsaved_changes:
            self._has_unsaved_changes = True
            self._update_unsaved_indicator()
    
    def _update_unsaved_indicator(self) -> None:
        """Met à jour l'indicateur de changements non sauvegardés."""
        if self._has_unsaved_changes:
            self.unsaved_label.setText("● Modifications non sauvegardées")
            self.unsaved_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        else:
            self.unsaved_label.setText("✓ Sauvegardé")
            self.unsaved_label.setStyleSheet("color: #28a745;")
    
    @abstractmethod
    def _validate_data(self) -> bool:
        """
        Valide les données saisies.
        À implémenter dans les classes filles.
        
        Returns:
            True si les données sont valides
        """
        pass
    
    def _validate_html_content(self) -> None:
        """Valide le contenu HTML."""
        html_content = self.html_editor.toPlainText()
        
        try:
            # Validation basique - à adapter selon vos besoins
            if not html_content.strip():
                raise ValueError("Le contenu HTML ne peut pas être vide")
            
            QMessageBox.information(self, "Validation HTML", "Le code HTML est valide.")
            self.html_editor.setStyleSheet("")
        except Exception as e:
            QMessageBox.warning(self, "HTML Invalide", f"Erreur de validation HTML:\n{e}")
            self.html_editor.setStyleSheet("border: 2px solid #dc3545;")
    
    def _sync_to_html_tab(self) -> None:
        """Synchronise le contenu WYSIWYG vers l'onglet HTML."""
        if self._editor_ready:
            self.wysiwyg_editor.get_content(self._on_content_for_sync)
    
    def _on_content_for_sync(self, content: str) -> None:
        """Callback pour la synchronisation vers HTML."""
        self.html_editor.setPlainText(content)
        self._update_status("Contenu synchronisé vers HTML")
    
    def _sync_from_html_tab(self) -> None:
        """Synchronise le contenu HTML vers l'éditeur WYSIWYG."""
        if self._editor_ready:
            html_content = self.html_editor.toPlainText()
            self.wysiwyg_editor.load_content(html_content)
            self._update_status("Contenu synchronisé vers l'éditeur visuel")
    
    def _save_data_wrapper(self) -> None:
        """Méthode wrapper pour la sauvegarde."""
        if not self._validate_data():
            return
        
        # Récupère le contenu depuis l'éditeur actif
        if self.tab_widget.currentIndex() == 0:  # WYSIWYG
            if self._editor_ready:
                self.wysiwyg_editor.get_content(self._on_content_for_save)
            else:
                self._show_error("L'éditeur n'est pas encore prêt")
        else:  # HTML
            content = self.html_editor.toPlainText()
            self._save_with_content(content)
    
    def _on_content_for_save(self, content: str) -> None:
        """Callback pour la sauvegarde avec contenu."""
        self._save_with_content(content)
    
    def _save_with_content(self, content: str) -> None:
        """Sauvegarde avec le contenu spécifié."""
        try:
            # Appelle la méthode de sauvegarde spécifique
            saved_data = self._save_data(content)
            
            if saved_data:
                # Marque comme sauvegardé
                self._has_unsaved_changes = False
                self._update_unsaved_indicator()
                
                # Émet le signal de sauvegarde
                self.data_saved.emit(saved_data)
                
                # Met à jour les données internes
                self._data = saved_data
                self._is_new_data = False
                
                self._on_data_saved_success(saved_data)
                
                self._logger.info(f"Données sauvegardées avec succès")
            
        except Exception as e:
            self._show_error(f"Erreur lors de la sauvegarde: {e}")
    
    @abstractmethod
    def _save_data(self, content: str) -> Any:
        """
        Sauvegarde les données avec le contenu spécifié.
        À implémenter dans les classes filles.
        
        Args:
            content: Contenu HTML à sauvegarder
            
        Returns:
            Les données sauvegardées
        """
        pass
    
    def _on_data_saved_success(self, saved_data: Any) -> None:
        """
        Callback appelé après une sauvegarde réussie.
        Méthode vide par défaut, à surcharger si nécessaire.
        
        Args:
            saved_data: Les données qui ont été sauvegardées
        """
        pass
    
    def _get_save_button_text(self) -> str:
        """
        Retourne le texte du bouton de sauvegarde.
        Peut être surchargé dans les classes filles.
        
        Returns:
            Texte du bouton
        """
        return "Mettre à jour" if not self._is_new_data else "Enregistrer"
    
    def _cancel_editing(self) -> None:
        """Annule les modifications en fonction du contexte (QDialog ou non)."""
        if self._has_unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Annuler les modifications",
                "Toutes les modifications non sauvegardées seront perdues.\nSouhaitez-vous continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Cas 1 : si dans un QDialog → émettre signal pour fermeture
        top_level = self.window()
        from PySide6.QtWidgets import QDialog
        if isinstance(top_level, QDialog):
            self.editing_cancelled.emit()
            return

        # Cas 2 : sinon → recharger les données
        self._has_unsaved_changes = False
        self._update_unsaved_indicator()
        self._load_initial_content()
        self._update_status("Modifications annulées.")

    def _show_error(self, message: str) -> None:
        """Affiche un message d'erreur."""
        QMessageBox.critical(self, "Erreur", message)
        self._logger.error(message)
    
    def _show_help(self) -> None:
        """Affiche l'aide générique."""
        self.help_requested.emit()
    
    def _get_help_text(self) -> str:
        """
        Retourne le texte d'aide.
        Peut être surchargé dans les classes filles pour ajouter des informations spécifiques.
        
        Returns:
            Texte d'aide HTML
        """
        return """
<h3>Aide - Éditeur</h3>

<h4>Raccourcis clavier :</h4>
<ul>
<li><b>Ctrl+S</b> : Sauvegarder</li>
<li><b>Ctrl+Q</b> : Annuler</li>
<li><b>F1</b> : Afficher cette aide</li>
</ul>

<h4>Utilisation :</h4>
<ul>
<li><b>Éditeur Visuel</b> : Édition WYSIWYG avec formatage</li>
<li><b>Code HTML</b> : Édition directe du code HTML</li>
<li><b>Synchronisation</b> : Utilisez les boutons pour synchroniser entre les deux modes</li>
</ul>

<h4>Validation :</h4>
<ul>
<li>Le contenu HTML est validé automatiquement</li>
<li>Les changements non sauvegardés sont indiqués</li>
</ul>
        """
    
    def _update_status(self, message: str) -> None:
        """Met à jour le message de statut."""
        self.status_bar.showMessage(message)
    
    # Méthodes publiques pour l'interaction
    
    def get_data(self) -> Optional[Any]:
        """
        Retourne les données en cours d'édition.
        
        Returns:
            Les données actuelles ou None
        """
        return self._data
    
    def has_unsaved_changes(self) -> bool:
        """
        Vérifie si des modifications non sauvegardées existent.
        
        Returns:
            True si des modifications non sauvegardées existent
        """
        return self._has_unsaved_changes
    
    def save(self) -> bool:
        """
        Sauvegarde les données de manière programmatique.
        
        Returns:
            True si la sauvegarde a réussi
        """
        if self._validate_data():
            self._save_data_wrapper()
            return not self._has_unsaved_changes
        return False
    
    def set_content_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Définit un callback pour les changements de contenu.
        
        Args:
            callback: Fonction appelée lors des changements
        """
        self._content_change_callback = callback
    
    def enable_auto_save(self, enabled: bool = True) -> None:
        """
        Active ou désactive la sauvegarde automatique.
        
        Args:
            enabled: True pour activer la sauvegarde automatique
        """
        self._auto_save_enabled = enabled
        if hasattr(self, 'wysiwyg_editor'):
            self.wysiwyg_editor.enable_auto_save(enabled)
    
    def get_current_content(self, callback: Callable[[str], None]) -> None:
        """
        Récupère le contenu actuel de l'éditeur actif.
        
        Args:
            callback: Fonction appelée avec le contenu
        """
        if self.tab_widget.currentIndex() == 0:  # WYSIWYG
            if self._editor_ready:
                self.wysiwyg_editor.get_content(callback)
            else:
                callback("")
        else:  # HTML
            callback(self.html_editor.toPlainText())
    
    def set_content(self, content: str) -> None:
        """
        Définit le contenu de l'éditeur.
        
        Args:
            content: Contenu HTML à charger
        """
        if self._editor_ready:
            self.wysiwyg_editor.load_content(content)
        self.html_editor.setPlainText(content)


class MetaQDialogABC(type(QDialog), ABCMeta):
    """Métaclasse combinée pour résoudre le conflit entre QDialog et ABC."""
    pass


class BaseEditorDialog(QDialog, metaclass=MetaQDialogABC):
    """
    Classe de dialogue pour les interfaces d'édition avec éditeur WYSIWYG.
    
    Encapsule BaseEditorWidget dans un QDialog pour une utilisation en tant que fenêtre modale.
    Gère automatiquement la fermeture avec vérification des modifications non sauvegardées.
    
    Signals:
        data_saved: Émis quand les données sont sauvegardées (Any)
        editing_cancelled: Émis quand l'édition est annulée
    """
    
    # Signaux Qt
    data_saved = Signal(object)
    editing_cancelled = Signal()
    
    def __init__(self, editor_widget_class: type, data: Optional[Any] = None, 
                 parent: Optional[QWidget] = None, window_title: str = "Éditeur", 
                 dialog_size: tuple = (1000, 700)):
        """
        Initialise le dialogue d'éditeur.
        
        Args:
            editor_widget_class: Classe du widget d'éditeur à utiliser
            data: Données à éditer (None pour création)
            parent: Widget parent
            window_title: Titre de la fenêtre
            dialog_size: Taille de la fenêtre (largeur, hauteur)
        """
        super().__init__(parent)
        
        self._window_title = window_title
        
        # Configuration de la fenêtre
        self.setWindowTitle(window_title)
        self.setModal(True)
        self.resize(*dialog_size)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget d'éditeur intégré
        self.editor_widget = editor_widget_class(data, self, show_action_buttons=True)
        layout.addWidget(self.editor_widget)
        
        # Connexions
        self.editor_widget.data_saved.connect(self._on_data_saved)
        self.editor_widget.editing_cancelled.connect(self._on_editing_cancelled)
        self.editor_widget.help_requested.connect(self._on_help_requested)
    
    def _on_data_saved(self, data: Any) -> None:
        """Callback appelé quand les données sont sauvegardées."""
        self.data_saved.emit(data)
        self.accept()
    
    def _on_editing_cancelled(self) -> None:
        """Callback appelé quand l'édition est annulée."""
        self.editing_cancelled.emit()
        self.reject()
    
    def _on_help_requested(self) -> None:
        """Callback appelé quand l'aide est demandée."""
        help_text = self.editor_widget._get_help_text()
        QMessageBox.information(self, "Aide", help_text)
    
    def closeEvent(self, event) -> None:
        """Gère la fermeture de la fenêtre."""
        if self.editor_widget.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Vous avez des modifications non sauvegardées. Voulez-vous vraiment fermer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def get_editor_widget(self) -> BaseEditorWidget:
        """
        Retourne l'instance du widget éditeur.
        
        Returns:
            Le widget éditeur utilisé dans ce QDialog
        """
        return self.editor_widget