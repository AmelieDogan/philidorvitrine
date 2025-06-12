from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox,
    QPushButton, QTextEdit, QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from .project_editor import ProjectEditor
from ..utils.french_date_utils import format_french_datetime

class ProjectsListWidget(QWidget):
    def __init__(self, project_manager, save_callback):
        super().__init__()
        self.project_manager = project_manager
        self.save_callback = save_callback

        # Layout comprenant le main_layout et les bouttons
        global_layout = QVBoxLayout(self)

        self.title_widget = QLabel("Liste des projets")
        global_layout.addWidget(self.title_widget)

        self.main_widget = QGroupBox()

        # Layout principal contenant la liste des projets à gauche
        # et la prévisualisation des informations du projet à droite
        self.main_layout = QHBoxLayout()

        # Widget de gauche
        self.list_widget = QListWidget()

        # widget de droite 
        self.prewiew_widget = QGroupBox()
        self.prewiew_widget.setTitle("Prévisualisation du projet sélectionné")

        # Layout contenant le widget avec les métadonnées
        # et le widget avec la prévisualisation HTML 
        self.preview_layout = QVBoxLayout()

        # Widget pour les métadonnées
        self.info_group = QGroupBox("Métadonnées du Projet")
        self.info_layout = QFormLayout(self.info_group)

        self.id_label = QLabel(str(""))
        self.created_label = QLabel(str(""))
        self.updated_label = QLabel(str(""))

        self.info_layout.addRow("Identifiant Philidor4 :", self.id_label)
        self.info_layout.addRow("Créé le :", self.created_label)
        self.info_layout.addRow("Modifié le :", self.updated_label)
        
        self.preview_layout.addWidget(self.info_group)

        # Widget pour la prévisualisation HTML
        self.html_preview_title = QLabel("Description du projet")
        self.html_preview = QTextEdit()
        self.html_preview.setReadOnly(True)

        self.preview_layout.addWidget(self.html_preview_title)
        self.preview_layout.addWidget(self.html_preview)

        self.prewiew_widget.setLayout(self.preview_layout)

        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addWidget(self.prewiew_widget)

        self.main_widget.setLayout(self.main_layout)

        global_layout.addWidget(self.main_widget)

        # Ajout des boutons pour créer et modifier des projets
        self.edit_button = QPushButton("Modifier le projet")
        self.edit_button.clicked.connect(self.edit_selected_project)
        global_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Supprimer le projet")
        self.delete_button.clicked.connect(self.delete_selected_project)
        global_layout.addWidget(self.delete_button)

        self.new_button = QPushButton("Nouveau projet")
        self.new_button.clicked.connect(self.create_new_project)
        global_layout.addWidget(self.new_button)

        self.refresh_project_list()

    def refresh_project_list(self):
        """Met à jour la liste des projets enregistrés"""
        self.list_widget.clear()
        for project in self.project_manager.list_projects():
            item = QListWidgetItem(project.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, project.uuid)
            self.list_widget.addItem(item)

        self.list_widget.itemChanged.connect(self.update_preview)

    def update_preview(self, item):
        """Met à jour la prévisualisation de la présentation d'un projet"""
        if item.checkState() == Qt.Checked:

            # Déconnecter temporairement le signal
            self.list_widget.itemChanged.disconnect()
            
            # Parcourir tous les éléments et décocher les autres
            for i in range(self.list_widget.count()):
                other_item = self.list_widget.item(i)
                if other_item != item:  # Ne pas toucher à l'élément actuellement coché
                    other_item.setCheckState(Qt.Unchecked)
            
            # Reconnecter le signal
            self.list_widget.itemChanged.connect(self.update_preview)

            project_uuid = item.data(Qt.UserRole)
            project = self.project_manager.get_project(project_uuid)
            self.html_preview.setHtml(project.description_html or "<i>Aucune description</i>")
            self.id_label.setText(str(project.id))
            self.created_label.setText(format_french_datetime(project.created_at))
            self.updated_label.setText(format_french_datetime(project.updated_at))
        else:
            self.html_preview.clear()
            self.id_label.setText(str(""))
            self.created_label.setText(str(""))
            self.updated_label.setText(str(""))

    def edit_selected_project(self):
        """Edite le projet sélectionné"""
        selected_items = [item for item in self.list_widget.findItems("", Qt.MatchContains)
                          if item.checkState() == Qt.Checked]
        if not selected_items:
            QMessageBox.information(self, "Aucun projet sélectionné", "Cochez un projet pour le modifier.")
            return

        project_uuid = selected_items[0].data(Qt.UserRole)
        project = self.project_manager.get_project(project_uuid)

        editor = ProjectEditor(project, self)
        editor.data_saved.connect(lambda p: self._finalize_project_edit(editor, p))
        editor.exec()

    def delete_selected_project(self):
        """Supprime le projet sélectionné après confirmation"""
        # Trouver le projet coché
        selected_items = [item for item in self.list_widget.findItems("", Qt.MatchContains)
                        if item.checkState() == Qt.Checked]
        
        if not selected_items:
            QMessageBox.information(self, "Aucun projet sélectionné", 
                                "Cochez un projet pour le supprimer.")
            return

        project_uuid = selected_items[0].data(Qt.UserRole)
        project = self.project_manager.get_project(project_uuid)
        
        # Dialog de confirmation
        reply = QMessageBox.question(
            self, 
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le projet :\n\n"
            f"Nom : {project.name}\n"
            f"ID : {project.id}\n\n"
            f"Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Bouton par défaut
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.project_manager.delete_project(project_uuid)
                if success:
                    self.save_callback()  # Sauvegarder les changements
                    self.refresh_project_list()  # Rafraîchir la liste
                    self.html_preview.clear()  # Vider la prévisualisation
                    QMessageBox.information(self, "Suppression réussie", 
                                        f"Le projet '{project.name}' a été supprimé.")
                else:
                    QMessageBox.warning(self, "Erreur", "Le projet n'a pas pu être supprimé.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", 
                                f"Erreur lors de la suppression :\n{e}")

    def create_new_project(self):
        """Crée un nouveau projet"""
        editor = ProjectEditor(parent=self)
        editor.data_saved.connect(lambda p: self._finalize_project_edit(editor, p))
        editor.exec()

    def _finalize_project_edit(self, editor, project):
        try:
            if self.project_manager.get_project_by_uuid(project.uuid):
                # Projet existant → mise à jour
                self.project_manager.update_project(
                    project.uuid,
                    project.name,
                    project.id,
                    project.description_html
                )
            else:
                # Nouveau projet → création
                self.project_manager.create_project(
                    name=project.name,
                    description_html=project.description_html,
                    project_id=project.id,
                    project_uuid=project.uuid
                )

            self.save_callback()
            self.refresh_project_list()
            self.html_preview.clear()
            editor.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement du projet :\n{e}")
