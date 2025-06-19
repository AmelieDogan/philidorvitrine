from pathlib import Path
from PySide6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFileDialog, QPushButton, QTextEdit, 
                               QMessageBox, QProgressBar)
from PySide6.QtCore import QThread

from ..core.xml_processor import XMLProcessor

class TransformationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.xml_processor = None
        self.xml_thread = None
        self.merged_file_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Section d'avertissement
        self.warning_section = QLabel(
            "Rappel : les onglets précédents doivent être complétés pour que "
            "les pages correspondantes s'affichent comme souhaité."
        )
        self.warning_section.setWordWrap(True)
        self.warning_section.setStyleSheet("QLabel { color: #ff6b35; font-weight: bold; }")
        
        # Section de sélection de fichier
        file_group = QGroupBox("Sélection du fichier XML")
        file_layout = QVBoxLayout(file_group)
        
        button_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Choisir un fichier XML")
        self.add_file_button.clicked.connect(self.open_file_dialog)
        
        self.process_button = QPushButton("Analyser et fusionner")
        self.process_button.clicked.connect(self.process_xml)
        self.process_button.setEnabled(False)
        
        button_layout.addWidget(self.add_file_button)
        button_layout.addWidget(self.process_button)
        
        self.file_path_label = QLabel("Aucun fichier sélectionné")
        self.file_path_label.setWordWrap(True)
        
        # Barre de progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        file_layout.addLayout(button_layout)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.progress_bar)
        
        # Section des statistiques
        stats_group = QGroupBox("Statistiques du fichier XML")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(200)
        self.stats_display.setPlainText("Aucune analyse effectuée")
        
        stats_layout.addWidget(self.stats_display)
        
        # Section du fichier fusionné
        result_group = QGroupBox("Résultat de la fusion")
        result_layout = QVBoxLayout(result_group)
        
        self.result_label = QLabel("Aucune fusion effectuée")
        self.result_label.setWordWrap(True)
        
        self.open_temp_button = QPushButton("Ouvrir le répertoire temporaire")
        self.open_temp_button.clicked.connect(self.open_temp_directory)
        self.open_temp_button.setEnabled(False)
        
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.open_temp_button)
        
        # Assemblage final
        main_layout.addWidget(self.warning_section)
        main_layout.addWidget(file_group)
        main_layout.addWidget(stats_group)
        main_layout.addWidget(result_group)
        main_layout.addStretch()
    
    def open_file_dialog(self):
        """Ouvre le dialogue de sélection de fichier"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier XML",
            ".",
            "Fichiers XML (*.xml);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(f"Fichier sélectionné :\n{file_path}")
            self.selected_file_path = file_path
            self.process_button.setEnabled(True)
            
            # Reset des résultats précédents
            self.stats_display.setPlainText("Fichier sélectionné, cliquez sur 'Analyser et fusionner'")
            self.result_label.setText("En attente du traitement...")
            self.open_temp_button.setEnabled(False)
    
    def process_xml(self):
        """Lance le traitement du fichier XML"""
        if not hasattr(self, 'selected_file_path'):
            QMessageBox.warning(self, "Erreur", "Aucun fichier sélectionné")
            return
        
        # Détermine le répertoire resources basé sur la structure de votre projet
        # Le script est dans core/, resources/ est au même niveau que core/
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent  # Remonte de core/ vers la racine
        resources_dir = project_root / "resources"
        
        # Vérification et message de debug
        print(f"Script actuel: {current_file}")
        print(f"Racine du projet: {project_root}")
        print(f"Répertoire resources: {resources_dir}")
        
        # Crée le worker thread
        self.xml_thread = QThread()
        self.xml_processor = XMLProcessor(self.selected_file_path, str(resources_dir))
        self.xml_processor.moveToThread(self.xml_thread)
        
        # Connexions des signaux
        self.xml_thread.started.connect(self.xml_processor.process)
        self.xml_processor.progress_updated.connect(self.update_progress)
        self.xml_processor.stats_ready.connect(self.display_stats)
        self.xml_processor.merge_completed.connect(self.on_merge_completed)
        self.xml_processor.error_occurred.connect(self.on_error)
        self.xml_processor.merge_completed.connect(self.xml_thread.quit)
        self.xml_processor.error_occurred.connect(self.xml_thread.quit)
        self.xml_thread.finished.connect(self.xml_thread.deleteLater)
        
        # Démarre le traitement
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_button.setEnabled(False)
        self.xml_thread.start()
    
    def update_progress(self, value):
        """Met à jour la barre de progression"""
        self.progress_bar.setValue(value)
    
    def display_stats(self, stats):
        """Affiche les statistiques du fichier XML"""
        processor = self.sender()
        if processor:
            summary = processor._create_stats_summary(stats)
            self.stats_display.setPlainText(summary)
    
    def on_merge_completed(self, merged_file_path, stats_summary):
        """Appelé quand la fusion est terminée"""
        self.merged_file_path = merged_file_path
        self.result_label.setText(
            f"Fusion terminée avec succès !\n"
            f"Fichier généré: {Path(merged_file_path).name}\n"
            f"Emplacement: {merged_file_path}"
        )
        self.open_temp_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        
        QMessageBox.information(
            self, 
            "Traitement terminé", 
            f"Le fichier XML a été analysé et fusionné avec succès.\n\n"
            f"Fichier de sortie: {Path(merged_file_path).name}"
        )
    
    def on_error(self, error_message):
        """Appelé en cas d'erreur"""
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        
        QMessageBox.critical(self, "Erreur", error_message)
        
        self.result_label.setText(f"Erreur: {error_message}")
        self.stats_display.setPlainText(f"Erreur lors de l'analyse: {error_message}")
    
    def open_temp_directory(self):
        """Ouvre le répertoire temporaire dans l'explorateur"""
        if self.merged_file_path:
            temp_dir = Path(self.merged_file_path).parent
            
            # Ouvre le répertoire selon l'OS
            import subprocess
            import platform
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", str(temp_dir)])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(temp_dir)])
                else:  # Linux
                    subprocess.run(["xdg-open", str(temp_dir)])
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "Erreur", 
                    f"Impossible d'ouvrir le répertoire:\n{str(e)}\n\n"
                    f"Chemin: {temp_dir}"
                )
    
    def get_merged_file_path(self):
        """Retourne le chemin du fichier fusionné pour utilisation externe"""
        return self.merged_file_path