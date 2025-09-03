from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QScrollArea, QPushButton, QGridLayout)
from PySide6.QtCore import Qt, Signal

class HelpWidget(QWidget):
    """Widget de page d'accueil pour l'application XML to Web App"""
    
    # Signal émis lorsque l'utilisateur souhaite naviguer vers un onglet spécifique
    navigate_to_tab = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Zone de défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Titre principal
        title = QLabel("Aide")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)
        
        # Guide de démarrage rapide
        self.create_quick_start_guide(content_layout)
        
        # Informations sur le flux de travail
        self.create_workflow_info(content_layout)
        
        # Espacement final
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_header(self, layout):
        """Crée l'en-tête de bienvenue"""
        header_frame = QFrame()
        header_frame.setObjectName("welcome-header")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(20, 30, 20, 30)
        
        # Titre principal
        title_label = QLabel("Bienvenue dans XML to Web App")
        title_label.setObjectName("main-title")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Sous-titre
        subtitle_label = QLabel("Transformez vos données XML Philidor 4 en site web statique")
        subtitle_label.setObjectName("main-subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        
        # Version ou info supplémentaire
        version_label = QLabel("Interface intuitive • Génération automatique • Résultat professionnel")
        version_label.setObjectName("version-info")
        version_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(version_label)
        
        layout.addWidget(header_frame)
    
    def create_quick_start_guide(self, layout):
        """Crée le guide de démarrage rapide"""
        guide_frame = QFrame()
        guide_frame.setObjectName("guide-section")
        guide_layout = QVBoxLayout(guide_frame)
        guide_layout.setSpacing(15)
        guide_layout.setContentsMargins(20, 20, 20, 20)
        
        guide_title = QLabel("Guide de démarrage rapide")
        guide_title.setObjectName("section-title")
        
        # Utilisation d'un layout pour les étapes
        steps_layout = QVBoxLayout()
        steps_layout.setSpacing(10)
        
        steps = [
            ("1", "Présentation", "Configurez le contenu de présentation de votre édition numérique"),
            ("2", "Projets", "Ajoutez vos projets et définissez leurs identifiants Philidor 4"),
            ("3", "Pages légales", "Personnalisez les mentions légales et la page 'À propos'"),
            ("4", "Import de données", "Importez votre panier de données XML depuis Philidor 4"),
            ("5", "Génération", "Lancez la transformation XSLT et téléchargez votre site web")
        ]
        
        for step_num, step_title, step_desc in steps:
            step_frame = self.create_step_item(step_num, step_title, step_desc)
            steps_layout.addWidget(step_frame)
        
        guide_layout.addWidget(guide_title)
        guide_layout.addLayout(steps_layout)
        
        layout.addWidget(guide_frame)
    
    def create_step_item(self, number, title, description):
        """Crée un élément d'étape du guide"""
        step_frame = QFrame()
        step_frame.setObjectName("step-item")
        step_layout = QHBoxLayout(step_frame)
        step_layout.setSpacing(15)
        step_layout.setContentsMargins(15, 10, 15, 10)
        
        # Numéro de l'étape
        number_label = QLabel(number)
        number_label.setObjectName("step-number")
        number_label.setAlignment(Qt.AlignCenter)
        number_label.setFixedSize(30, 30)
        
        # Contenu de l'étape
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setObjectName("step-title")
        
        desc_label = QLabel(description)
        desc_label.setObjectName("step-description")
        desc_label.setWordWrap(True)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        
        step_layout.addWidget(number_label)
        step_layout.addLayout(content_layout)
        
        return step_frame
    
    def create_workflow_info(self, layout):
        """Crée les informations sur le flux de travail"""
        workflow_frame = QFrame()
        workflow_frame.setObjectName("workflow-section")
        workflow_layout = QVBoxLayout(workflow_frame)
        workflow_layout.setSpacing(15)
        workflow_layout.setContentsMargins(20, 20, 20, 20)
        
        workflow_title = QLabel("💡 Conseils d'utilisation")
        workflow_title.setObjectName("section-title")
        
        tips = [
            "Suivez l'ordre des onglets de gauche à droite pour un flux optimal",
            "Sauvegardez régulièrement vos modifications avec Ctrl+S",
            "Vérifiez que tous vos projets sont bien configurés avant la transformation",
            "Consultez l'onglet 'Aide' pour des informations détaillées sur chaque fonction"
        ]
        
        tips_layout = QVBoxLayout()
        tips_layout.setSpacing(8)
        
        for tip in tips:
            tip_label = QLabel(f"• {tip}")
            tip_label.setObjectName("tip-item")
            tip_label.setWordWrap(True)
            tips_layout.addWidget(tip_label)
        
        workflow_layout.addWidget(workflow_title)
        workflow_layout.addLayout(tips_layout)
        
        layout.addWidget(workflow_frame)