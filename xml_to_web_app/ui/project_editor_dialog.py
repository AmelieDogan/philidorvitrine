# project_editor_dialog.py

from typing import Optional
from PySide6.QtWidgets import QWidget
from .base_editor import BaseEditorDialog
from .project_editor_widget import ProjectEditorWidget
from ..models.project import Project

class ProjectEditorDialog(BaseEditorDialog):
    def __init__(self, project: Optional[Project] = None, parent: Optional[QWidget] = None):
        super().__init__(
            editor_widget_class=ProjectEditorWidget,
            data=project,
            parent=parent,
            window_title="Éditeur de Projet",
            dialog_size=(1000, 700)
        )

    def get_project(self) -> Optional[Project]:
        return self.get_editor_widget().get_data()