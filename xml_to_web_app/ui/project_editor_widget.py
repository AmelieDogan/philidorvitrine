from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QGroupBox, QFormLayout

from .base_editor import BaseEditorWidget
from ..models.project import Project, ProjectValidationError, validate_project_name, validate_project_id, validate_html_content
from ..utils.french_date_utils import format_french_datetime

class ProjectEditorWidget(BaseEditorWidget):
    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        info_group = QGroupBox("Informations du Projet")
        info_layout = QFormLayout(info_group)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du projet (requis)")
        self.name_edit.setMaxLength(100)
        info_layout.addRow("Nom du projet:", self.name_edit)

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("Identifiant dans Philidor4 (requis)")
        self.id_edit.setMaxLength(100)
        info_layout.addRow("Identifiant Philidor4:", self.id_edit)

        if not self._is_new_data:
            self.created_label = QLabel(format_french_datetime(self._data.created_at))
            self.updated_label = QLabel(format_french_datetime(self._data.updated_at))
            info_layout.addRow("Créé le:", self.created_label)
            info_layout.addRow("Modifié le:", self.updated_label)

        parent_layout.addWidget(info_group)

    def _setup_specific_connections(self) -> None:
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.id_edit.textChanged.connect(self._on_id_changed)

    def _load_data(self) -> None:
        self.name_edit.setText(self._data.name)
        self.id_edit.setText(self._data.id)

        if hasattr(self, 'created_label'):
            self.created_label.setText(format_french_datetime(self._data.created_at))
            self.updated_label.setText(format_french_datetime(self._data.updated_at))

    def _setup_new_data(self) -> None:
        self.name_edit.setPlaceholderText("Nom du nouveau projet")
        self.name_edit.setFocus()

    def _load_initial_content(self) -> None:
        if self._data and self._data.description_html:
            self.set_content(self._data.description_html)
            self._initial_content_loaded = True

    def _validate_data(self) -> bool:
        return self._validate_name() and self._validate_id()

    def _validate_name(self) -> bool:
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
        name = self.name_edit.text().strip()
        project_id = self.id_edit.text().strip()

        validate_html_content(content)

        if self._is_new_data:
            return Project(id=project_id, name=name, description_html=content)
        else:
            self._data.name = name
            self._data.id = project_id
            self._data.update_content(content)
            return self._data

    def _on_data_saved_success(self, saved_data: Project) -> None:
        if hasattr(self, 'updated_label'):
            self.updated_label.setText(format_french_datetime(saved_data.updated_at))

    def _on_name_changed(self, text: str) -> None:
        self._mark_as_changed()
        self._validate_name()

    def _on_id_changed(self, text: str) -> None:
        self._mark_as_changed()
        self._validate_id()

    def _get_help_text(self) -> str:
        base_help = super()._get_help_text()
        return base_help + """
<h4>Spécificités des projets :</h4>
<ul>
<li><b>Nom du projet</b> : Requis, utilisé comme identifiant</li>
<li><b>Identifiant Philidor4</b> : Requis, doit être unique</li>
</ul>
"""