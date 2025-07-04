from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QTabWidget
from .projects_list import ProjectsListWidget
from .presentation_editor import PresentationEditor
from .legal_mentions_editor import LegalMentionsEditor
from .about_editor import AboutEditor
from .transformation import AutoTransformationWidget

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
        
        self.presentation_editor = PresentationEditor(self.presentation, self)
        self.project_list_widget = ProjectsListWidget(self.project_manager, self.save_projects)
        self.legal_mentions_editor = LegalMentionsEditor(self.legal_mentions, self)
        self.about_editor = AboutEditor(self.about, self)

        self.transformation_widget = AutoTransformationWidget()

        self.tabs.addTab(self.create_tab("La future page d'accueil du logiciel"), "Accueil")
        self.tabs.addTab(self.presentation_editor, "Présentation")
        self.tabs.addTab(self.project_list_widget, "Projets")
        self.tabs.addTab(self.legal_mentions_editor, "Mentions légales")
        self.tabs.addTab(self.about_editor, "A propos")
        self.tabs.addTab(self.transformation_widget, "Transformation")
        self.tabs.addTab(self.create_tab("Onglet d'aide"), "Aide")

        self.presentation_editor.data_saved.connect(self._on_presentation_saved)
        self.legal_mentions_editor.data_saved.connect(self._on_legal_mentions_saved)
        self.about_editor.data_saved.connect(self._on_about_saved)


    def create_tab(self, text):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel(text))
        return tab
    
    def _on_presentation_saved(self, pres):
        self.presentation = pres
        self.save_presentation(pres)

    def _on_legal_mentions_saved(self, pres):
        self.legal_mentions = pres
        self.save_legal_mentions(pres)

    def _on_about_saved(self, pres):
        self.about = pres
        self.save_about(pres)