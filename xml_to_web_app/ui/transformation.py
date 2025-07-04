import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Set

from PySide6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFileDialog, QPushButton, QTextEdit, 
                               QMessageBox, QProgressBar, QListWidget, QSplitter)
from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QFont

from ..core.xml_processor import XMLProcessor
from ..core.transformer_engine import TransformationWorker, XSLTTransformationEngine


class AutoTransformationWidget(QWidget):
    """Widget principal pour le workflow automatisé fusion + transformation"""
    
    # Signal pour demander l'ouverture de l'onglet Projets
    request_projects_tab = Signal(list)  # Liste des projets manquants
    
    def __init__(self):
        super().__init__()
        self.xml_processor = None
        self.xml_thread = None
        self.transformation_worker = None
        self.merged_file_path = None
        self.transformation_engine = XSLTTransformationEngine()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Titre principal
        title = QLabel("Transformation automatique XML vers Web")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Section d'avertissement
        warning_section = QLabel(
            "Ce processus automatisé effectue la fusion XML puis la transformation XSLT. "
            "Assurez-vous que tous les projets sont définis dans l'onglet 'Projets'."
        )
        warning_section.setWordWrap(True)
        warning_section.setStyleSheet("QLabel { color: #ff6b35; font-weight: bold; padding: 10px; }")
        main_layout.addWidget(warning_section)
        
        # Section de sélection de fichier
        file_group = QGroupBox("1. Sélection du fichier XML source")
        file_layout = QVBoxLayout(file_group)
        
        button_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Choisir un fichier XML")
        self.add_file_button.clicked.connect(self.open_file_dialog)
        
        self.start_process_button = QPushButton("Démarrer le processus complet")
        self.start_process_button.clicked.connect(self.start_complete_process)
        self.start_process_button.setEnabled(False)
        self.start_process_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        button_layout.addWidget(self.add_file_button)
        button_layout.addWidget(self.start_process_button)
        
        self.file_path_label = QLabel("Aucun fichier sélectionné")
        self.file_path_label.setWordWrap(True)
        
        file_layout.addLayout(button_layout)
        file_layout.addWidget(self.file_path_label)
        
        main_layout.addWidget(file_group)
        
        # Section de progression
        progress_group = QGroupBox("2. Progression du traitement")
        progress_layout = QVBoxLayout(progress_group)
        
        self.status_label = QLabel("En attente...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_group)
        
        # Section de vérification des projets
        projects_group = QGroupBox("3. Vérification des projets")
        projects_layout = QVBoxLayout(projects_group)
        
        self.projects_status = QTextEdit()
        self.projects_status.setReadOnly(True)
        self.projects_status.setMaximumHeight(150)
        self.projects_status.setPlainText("Aucune vérification effectuée")
        
        projects_layout.addWidget(self.projects_status)
        
        main_layout.addWidget(projects_group)
        
        # Section des résultats
        results_group = QGroupBox("4. Résultats de la transformation")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(120)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        self.download_button = QPushButton("Télécharger le ZIP")
        self.download_button.clicked.connect(self.download_zip)
        self.download_button.setEnabled(False)
        
        self.clear_button = QPushButton("Effacer les résultats")
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setEnabled(False)
        
        actions_layout.addWidget(self.download_button)
        actions_layout.addWidget(self.clear_button)
        
        results_layout.addWidget(self.results_text)
        results_layout.addLayout(actions_layout)
        
        main_layout.addWidget(results_group)
        
        # Variables pour stocker les résultats
        self.current_transformation_result = None
    
    def open_file_dialog(self):
        """Ouvre le dialogue de sélection de fichier"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier XML",
            ".",
            "Fichiers XML (*.xml);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(f"Fichier sélectionné : {Path(file_path).name}")
            self.selected_file_path = file_path
            self.start_process_button.setEnabled(True)
            
            # Reset des résultats précédents
            self.status_label.setText("Fichier sélectionné, prêt à démarrer le processus")
            self.projects_status.setPlainText("En attente du traitement...")
            self.results_text.clear()
            self.clear_results()
    
    def start_complete_process(self):
        """Démarre le processus complet : fusion puis transformation"""
        if not hasattr(self, 'selected_file_path'):
            QMessageBox.warning(self, "Erreur", "Aucun fichier sélectionné")
            return
        
        # Désactive le bouton pendant le traitement
        self.start_process_button.setEnabled(False)
        self.status_label.setText("Étape 1/4 : Fusion du fichier XML en cours...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Détermine les répertoires
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        resources_dir = project_root / "resources"
        
        # Démarre la fusion XML
        self.xml_thread = QThread()
        self.xml_processor = XMLProcessor(self.selected_file_path, str(resources_dir))
        self.xml_processor.moveToThread(self.xml_thread)
        
        # Connexions des signaux pour la fusion
        self.xml_thread.started.connect(self.xml_processor.process)
        self.xml_processor.progress_updated.connect(self.update_progress)
        self.xml_processor.merge_completed.connect(self.on_merge_completed)
        self.xml_processor.error_occurred.connect(self.on_error)
        self.xml_processor.merge_completed.connect(self.xml_thread.quit)
        self.xml_processor.error_occurred.connect(self.xml_thread.quit)
        self.xml_thread.finished.connect(self.xml_thread.deleteLater)
        
        self.xml_thread.start()
    
    def update_progress(self, value):
        """Met à jour la barre de progression"""
        self.progress_bar.setValue(value)
    
    def on_merge_completed(self, merged_file_path, stats_summary):
        """Appelé quand la fusion est terminée - lance la vérification des projets"""
        self.merged_file_path = merged_file_path
        self.status_label.setText("Étape 2/4 : Vérification des projets en cours...")
        self.progress_bar.setValue(25)
        
        # Vérifie les projets
        try:
            missing_projects = self.verify_projects(merged_file_path)
            
            if missing_projects:
                # Des projets manquent - affiche l'erreur et arrête le processus
                self.on_missing_projects(missing_projects)
                return
            
            # Tous les projets sont présents - continue avec la transformation
            self.projects_status.setPlainText("✓ Tous les projets requis sont présents")
            self.start_transformation()
            
        except Exception as e:
            self.on_error(f"Erreur lors de la vérification des projets : {str(e)}")
    
    def verify_projects(self, merged_file_path: str) -> List[str]:
        """Vérifie que tous les projets requis sont présents"""
        try:
            # Parse le fichier fusionné
            tree = ET.parse(merged_file_path)
            root = tree.getroot()
            
            # Récupère les projets requis depuis philidor4_data/response/item/projet
            required_projects = set()
            for item in root.findall(".//philidor4_data/response/item"):
                projet_elem = item.find("projet")
                if projet_elem is not None and projet_elem.text:
                    required_projects.add(projet_elem.text.strip())
            
            # Récupère les projets disponibles depuis projects_data/projects/project
            available_projects = set()
            for project in root.findall(".//projects_data/projects/project"):
                project_id = project.get("id")
                if project_id:
                    available_projects.add(project_id.strip())
            
            # Trouve les projets manquants
            missing_projects = required_projects - available_projects
            
            # Met à jour l'affichage
            status_text = f"Projets requis : {len(required_projects)}\n"
            status_text += f"Projets disponibles : {len(available_projects)}\n"
            
            if missing_projects:
                status_text += f"\n❌ Projets manquants ({len(missing_projects)}) :\n"
                for project in sorted(missing_projects):
                    status_text += f"  - {project}\n"
            else:
                status_text += "\n✓ Tous les projets requis sont présents"
            
            self.projects_status.setPlainText(status_text)
            
            return list(missing_projects)
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'analyse du fichier fusionné : {str(e)}")
    
    def on_missing_projects(self, missing_projects: List[str]):
        """Appelé quand des projets manquent"""
        self.progress_bar.setVisible(False)
        self.start_process_button.setEnabled(True)
        
        projects_list = "\n".join(f"• {project}" for project in missing_projects)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Projets manquants")
        msg.setText(f"Le processus ne peut pas continuer car {len(missing_projects)} projet(s) manquent :")
        msg.setDetailedText(projects_list)
        msg.setInformativeText("Veuillez d'abord définir ces projets dans l'onglet 'Projets'.")
        
        # Bouton pour ouvrir l'onglet Projets
        projects_button = msg.addButton("Ouvrir l'onglet Projets", QMessageBox.ActionRole)
        ok_button = msg.addButton(QMessageBox.Ok)
        
        msg.exec()
        
        if msg.clickedButton() == projects_button:
            # Émet le signal pour ouvrir l'onglet Projets
            self.request_projects_tab.emit(missing_projects)
        
        self.status_label.setText(f"Processus arrêté : {len(missing_projects)} projet(s) manquant(s)")
    
    def start_transformation(self):
        """Démarre la transformation XSLT"""
        self.status_label.setText("Étape 3/4 : Transformation XSLT en cours...")
        self.progress_bar.setValue(50)
        
        # Détermine le chemin du fichier XSLT
        xslt_file_path = Path(self.merged_file_path).parent.parent / "xsl" / "transform.xsl"
        
        if not xslt_file_path.exists():
            self.on_error(f"Fichier XSLT introuvable : {xslt_file_path}")
            return
        
        # Crée et lance le worker de transformation
        self.transformation_worker = TransformationWorker(
            self.transformation_engine, 
            self.merged_file_path, 
            str(xslt_file_path)
        )
        
        self.transformation_worker.finished.connect(self.on_transformation_finished)
        self.transformation_worker.error.connect(self.on_transformation_error)
        self.transformation_worker.progress.connect(self.on_transformation_progress)
        self.transformation_worker.start()
    
    def on_transformation_progress(self, message: str):
        """Met à jour le progrès de la transformation"""
        self.progress_bar.setValue(75)
    
    def on_transformation_finished(self, result: Dict[str, Any]):
        """Appelé quand la transformation est terminée"""
        self.progress_bar.setValue(100)
        
        if result['success']:
            self.current_transformation_result = result
            
            # Supprime le fichier fusionné temporaire
            try:
                if self.merged_file_path and Path(self.merged_file_path).exists():
                    os.remove(self.merged_file_path)
                    print(f"Fichier fusionné supprimé : {self.merged_file_path}")
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier fusionné : {e}")
            
            # Affiche les résultats
            info_text = f"""✓ Transformation terminée avec succès !

Durée du processus : {result['duration']:.2f} secondes
Fichiers générés : {result['file_count']}
ID de transformation : {result['transform_id'][:8]}...

Le fichier ZIP est prêt à être téléchargé."""
            
            self.results_text.setText(info_text)
            self.status_label.setText("Étape 4/4 : Processus terminé avec succès !")
            
            # Active les boutons d'action
            self.download_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            
            # Message de succès
            QMessageBox.information(
                self, 
                "Processus terminé", 
                "La transformation XML vers Web a été effectuée avec succès !\n\n"
                "Vous pouvez maintenant télécharger le fichier ZIP contenant les résultats."
            )
            
        else:
            self.on_error(f"Erreur de transformation : {result['error']}")
        
        # Réactive le bouton principal
        self.start_process_button.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def on_transformation_error(self, error_message: str):
        """Appelé en cas d'erreur de transformation"""
        self.on_error(f"Erreur de transformation : {error_message}")
    
    def on_error(self, error_message: str):
        """Appelé en cas d'erreur"""
        self.progress_bar.setVisible(False)
        self.start_process_button.setEnabled(True)
        
        QMessageBox.critical(self, "Erreur", error_message)
        self.status_label.setText(f"Erreur : {error_message}")
        
        # Supprime le fichier fusionné en cas d'erreur
        try:
            if self.merged_file_path and Path(self.merged_file_path).exists():
                os.remove(self.merged_file_path)
        except Exception:
            pass
    
    def download_zip(self):
        """Télécharge le fichier ZIP des résultats"""
        if not self.current_transformation_result:
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Sauvegarder le ZIP", 
            "transformation_results.zip", 
            "Fichiers ZIP (*.zip)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(self.current_transformation_result['zip_path'], save_path)
                QMessageBox.information(
                    self, 
                    "Succès", 
                    f"Fichier ZIP sauvegardé avec succès :\n{save_path}"
                )
                self.status_label.setText(f"ZIP sauvegardé : {Path(save_path).name}")
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Erreur", 
                    f"Erreur lors de la sauvegarde : {str(e)}"
                )
    
    def clear_results(self):
        """Efface les résultats"""
        self.results_text.clear()
        self.projects_status.setPlainText("Aucune vérification effectuée")
        self.status_label.setText("Résultats effacés")
        self.current_transformation_result = None
        self.download_button.setEnabled(False)
        self.clear_button.setEnabled(False)
    
    def closeEvent(self, event):
        """Nettoyage lors de la fermeture"""
        if self.transformation_worker and self.transformation_worker.isRunning():
            self.transformation_worker.terminate()
            self.transformation_worker.wait()
        
        self.transformation_engine.cleanup()
        event.accept()


# Widget de fusion simple (pour usage séparé si nécessaire)
class SimpleFusionWidget(QWidget):
    """Widget simplifié pour la fusion XML uniquement"""
    
    def __init__(self):
        super().__init__()
        self.xml_processor = None
        self.xml_thread = None
        self.merged_file_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Section de sélection de fichier
        file_group = QGroupBox("Fusion XML")
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
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        file_layout.addLayout(button_layout)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.progress_bar)
        
        # Section du résultat
        result_group = QGroupBox("Résultat de la fusion")
        result_layout = QVBoxLayout(result_group)
        
        self.result_label = QLabel("Aucune fusion effectuée")
        self.result_label.setWordWrap(True)
        
        self.open_temp_button = QPushButton("Ouvrir le répertoire temporaire")
        self.open_temp_button.clicked.connect(self.open_temp_directory)
        self.open_temp_button.setEnabled(False)
        
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.open_temp_button)
        
        main_layout.addWidget(file_group)
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
            self.file_path_label.setText(f"Fichier sélectionné : {Path(file_path).name}")
            self.selected_file_path = file_path
            self.process_button.setEnabled(True)
            self.result_label.setText("En attente du traitement...")
            self.open_temp_button.setEnabled(False)
    
    def process_xml(self):
        """Lance le traitement du fichier XML"""
        if not hasattr(self, 'selected_file_path'):
            QMessageBox.warning(self, "Erreur", "Aucun fichier sélectionné")
            return
        
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        resources_dir = project_root / "resources"
        
        self.xml_thread = QThread()
        self.xml_processor = XMLProcessor(self.selected_file_path, str(resources_dir))
        self.xml_processor.moveToThread(self.xml_thread)
        
        # Connexions des signaux
        self.xml_thread.started.connect(self.xml_processor.process)
        self.xml_processor.progress_updated.connect(self.update_progress)
        self.xml_processor.merge_completed.connect(self.on_merge_completed)
        self.xml_processor.error_occurred.connect(self.on_error)
        self.xml_processor.merge_completed.connect(self.xml_thread.quit)
        self.xml_processor.error_occurred.connect(self.xml_thread.quit)
        self.xml_thread.finished.connect(self.xml_thread.deleteLater)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_button.setEnabled(False)
        self.xml_thread.start()
    
    def update_progress(self, value):
        """Met à jour la barre de progression"""
        self.progress_bar.setValue(value)
    
    def on_merge_completed(self, merged_file_path, stats_summary):
        """Appelé quand la fusion est terminée"""
        self.merged_file_path = merged_file_path
        self.result_label.setText(
            f"Fusion terminée avec succès !\n"
            f"Fichier généré : {Path(merged_file_path).name}\n"
            f"Emplacement : {merged_file_path}"
        )
        self.open_temp_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        
        QMessageBox.information(
            self, 
            "Traitement terminé", 
            f"Le fichier XML a été analysé et fusionné avec succès.\n\n"
            f"Fichier de sortie : {Path(merged_file_path).name}"
        )
    
    def on_error(self, error_message):
        """Appelé en cas d'erreur"""
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        
        QMessageBox.critical(self, "Erreur", error_message)
        self.result_label.setText(f"Erreur : {error_message}")
    
    def open_temp_directory(self):
        """Ouvre le répertoire temporaire dans l'explorateur"""
        if self.merged_file_path:
            temp_dir = Path(self.merged_file_path).parent
            
            import subprocess
            import platform
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", str(temp_dir)])
                elif platform.system() == "Darwin":
                    subprocess.run(["open", str(temp_dir)])
                else:
                    subprocess.run(["xdg-open", str(temp_dir)])
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "Erreur", 
                    f"Impossible d'ouvrir le répertoire :\n{str(e)}\n\n"
                    f"Chemin : {temp_dir}"
                )
    
    def get_merged_file_path(self):
        """Retourne le chemin du fichier fusionné pour utilisation externe"""
        return self.merged_file_path