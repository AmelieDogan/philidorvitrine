from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QScrollArea, QPushButton, QGridLayout)
from PySide6.QtCore import Qt, Signal

class WelcomeWidget(QWidget):
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
        
        # En-tête de bienvenue
        self.create_header(content_layout)

        # Description de l'application
        self.create_description(content_layout)
        
        # Cartes de navigation rapide
        self.create_navigation_cards(content_layout)
        
        # Guide de démarrage rapide
        self.create_quick_start_guide(content_layout)
        
        # Informations sur le flux de travail
        self.create_workflow_info(content_layout)
        
        # Section d'aide rapide
        self.create_help_section(content_layout)
        
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
    
    def create_navigation_cards(self, layout):
        """Crée les cartes de navigation rapide vers les onglets"""
        nav_title = QLabel("Accès rapide")
        nav_title.setObjectName("section-title")
        layout.addWidget(nav_title)
        
        # Container pour les cartes
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # Définition des cartes d'onglets
        tab_cards = [
            {
                "title": "Présentation",
                "description": "Configurez le contenu de présentation de votre édition numérique",
                "tab_index": 1,
                "icon": "📝"
            },
            {
                "title": "Projets", 
                "description": "Gérez vos projets et leurs identifiants Philidor 4",
                "tab_index": 2,
                "icon": "📁"
            },
            {
                "title": "Mentions légales",
                "description": "Éditez le contenu des mentions légales",
                "tab_index": 3,
                "icon": "⚖️"
            },
            {
                "title": "À propos",
                "description": "Personnalisez votre page à propos",
                "tab_index": 4,
                "icon": "ℹ️"
            },
            {
                "title": "Transformation",
                "description": "Importez vos données et générez votre site web",
                "tab_index": 5,
                "icon": "🔄"
            },
            {
                "title": "Aide",
                "description": "Consultez la documentation et l'assistance",
                "tab_index": 6,
                "icon": "❓"
            }
        ]
        
        # Création des cartes (2 colonnes)
        for i, card_info in enumerate(tab_cards):
            card = self.create_navigation_card(card_info)
            row = i // 2
            col = i % 2
            cards_layout.addWidget(card, row, col)
        
        layout.addWidget(cards_frame)
    
    def create_navigation_card(self, card_info):
        """Crée une carte de navigation individuelle"""
        card = QFrame()
        card.setObjectName("nav-card")
        card.setFrameShape(QFrame.Box)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        # En-tête avec icône et titre
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(card_info["icon"])
        icon_label.setObjectName("card-icon")
        
        title_label = QLabel(card_info["title"])
        title_label.setObjectName("card-title")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Description
        desc_label = QLabel(card_info["description"])
        desc_label.setObjectName("card-description")
        desc_label.setWordWrap(True)
        
        # Bouton d'action
        action_btn = QPushButton("Accéder")
        action_btn.setObjectName("card-button")
        action_btn.clicked.connect(lambda: self.navigate_to_tab.emit(card_info["tab_index"]))
        
        card_layout.addLayout(header_layout)
        card_layout.addWidget(desc_label)
        card_layout.addStretch()
        card_layout.addWidget(action_btn)
        
        return card
    
    def create_description(self, layout):
        """Crée la section de description"""
        desc_frame = QFrame()
        desc_frame.setObjectName("description-section")
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setSpacing(15)
        desc_layout.setContentsMargins(20, 20, 20, 20)
        
        desc_title = QLabel("À propos de cette application")
        desc_title.setObjectName("section-title")
        
        desc_text = QLabel(
            "Cette application vous accompagne dans la création de sites web statiques "
            "à partir de vos données XML provenant de Philidor 4. Grâce à son interface "
            "intuitive et son processus guidé, vous pouvez facilement configurer le contenu "
            "de votre site, gérer vos projets, et générer automatiquement un site web "
            "professionnel prêt à être déployé."
        )
        desc_text.setWordWrap(True)
        desc_text.setObjectName("description-text")
        
        desc_layout.addWidget(desc_title)
        desc_layout.addWidget(desc_text)
        
        layout.addWidget(desc_frame)
    
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
    
    def create_help_section(self, layout):
        """Crée la section d'aide rapide"""
        help_frame = QFrame()
        help_frame.setObjectName("help-section")
        help_layout = QVBoxLayout(help_frame)
        help_layout.setSpacing(15)
        help_layout.setContentsMargins(20, 20, 20, 20)
        
        help_title = QLabel("Besoin d'aide ?")
        help_title.setObjectName("section-title")
        
        help_text = QLabel(
            "Si vous rencontrez des difficultés ou avez des questions, consultez l'onglet "
            "'Aide' qui contient une documentation complète sur l'utilisation de l'application."
        )
        help_text.setWordWrap(True)
        help_text.setObjectName("help-text")
        
        help_button = QPushButton("Ouvrir l'aide")
        help_button.setObjectName("help-button")
        help_button.clicked.connect(lambda: self.navigate_to_tab.emit(6))
        
        help_layout.addWidget(help_title)
        help_layout.addWidget(help_text)
        help_layout.addWidget(help_button)
        
        layout.addWidget(help_frame)