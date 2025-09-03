from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QTabWidget, QMessageBox, QScrollArea
from .welcome import WelcomeWidget
from .projects_list import ProjectsListWidget
from .presentation_editor_widget import PresentationEditorWidget
from .legal_mentions_editor_widget import LegalMentionsEditorWidget
from .about_editor_widget import AboutEditorWidget
from .transformation import AutoTransformationWidget
from .help_widget import HelpWidget

class MainWindow(QMainWindow):
    def __init__(self, project_manager, save_projects_callback, presentation, save_presentation_callback, legal_mentions, save_legal_mentions_callback, about, save_about_callback):
        super().__init__()
        self.presentation = presentation
        self.save_presentation = save_presentation_callback
        self.project_manager = project_manager
        self.save_projects = save_projects_callback
        self.legal_mentions = legal_mentions
        self.save_legal_mentions = save_legal_mentions_callback
        self.about = about
        self.save_about = save_about_callback

        self.setWindowTitle("XML to Web App")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.welcome_widget = WelcomeWidget()

        self.presentation_editor = PresentationEditorWidget(self.presentation, self)
        self.presentation_scroll_area = QScrollArea()
        self.presentation_scroll_area.setWidgetResizable(True)
        self.presentation_scroll_area.setWidget(self.presentation_editor)

        self.project_list_widget = ProjectsListWidget(self.project_manager, self.save_projects)

        self.legal_mentions_editor = LegalMentionsEditorWidget(self.legal_mentions, self)
        self.legal_mentions_scroll_area = QScrollArea()
        self.legal_mentions_scroll_area.setWidgetResizable(True)
        self.legal_mentions_scroll_area.setWidget(self.legal_mentions_editor)

        self.about_editor = AboutEditorWidget(self.about, self)
        self.about_scroll_area = QScrollArea()
        self.about_scroll_area.setWidgetResizable(True)
        self.about_scroll_area.setWidget(self.about_editor)

        self.transformation_widget = AutoTransformationWidget()

        self.help_widget = HelpWidget()

        # Premier onglet - Sert de page d'accueil, page par défaut lorsque l'application se lance
        self.tabs.addTab(self.welcome_widget, "Accueil")
        # Deuxième onglet - Permet de modifier le contenu présentant l'édition numérique
        self.tabs.addTab(self.presentation_scroll_area, "Présentation")
        # Troisième onglet - Permet d'éditer les textes contextualisant les projets,
        # ainsi que le titre de chaque projet et son identifiant dans Philidor 4
        self.tabs.addTab(self.project_list_widget, "Projets")
        # Quatrième onglet - Permet d'éditer le contenu de la page des mentions légales
        self.tabs.addTab(self.legal_mentions_scroll_area, "Mentions légales")
        # Cinquième onglet - Permet d'éditer le contenu de la page à propos
        self.tabs.addTab(self.about_scroll_area, "A propos")
        # Sixième onglet - Permet d'importer un panier de données provenant de Philidor 4,
        # vérifie que chaque projet est bien documenté grâce à l'onglet projet,
        # effectue la transformation XSLT et retourne un site web statique sous la forme d'archive web.
        self.tabs.addTab(self.transformation_widget, "Transformation")
        # Septième onglet - Donne toutes les indications d'aide
        self.tabs.addTab(self.help_widget, "Aide")

        self.presentation_editor.data_saved.connect(self._on_presentation_saved)
        self.legal_mentions_editor.data_saved.connect(self._on_legal_mentions_saved)
        self.about_editor.data_saved.connect(self._on_about_saved)

        self.connect_help(self.presentation_editor)
        self.connect_help(self.legal_mentions_editor)
        self.connect_help(self.about_editor)

        self.welcome_widget.navigate_to_tab.connect(self.tabs.setCurrentIndex)

    def create_tab(self, text):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel(text))
        return tab
    
    def connect_help(self, widget):
        widget.help_requested.connect(lambda: self._show_help_from_widget(widget))

    def _show_help_from_widget(self, widget):
        help_text = widget._get_help_text()
        QMessageBox.information(self, "Aide", help_text)
    
    def _on_presentation_saved(self, pres):
        self.presentation = pres
        self.save_presentation(pres)

    def _on_legal_mentions_saved(self, pres):
        self.legal_mentions = pres
        self.save_legal_mentions(pres)

    def _on_about_saved(self, pres):
        self.about = pres
        self.save_about(pres)

    def _show_help_from_widget(self, widget):
        help_text = widget._get_help_text()
        QMessageBox.information(self, "Aide", help_text)