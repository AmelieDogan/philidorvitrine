import sys
from xml.etree import ElementTree as ET
from pathlib import Path
from PySide6 import QtWidgets
from .ui import MainWindow
from .core.project_manager import ProjectManager
from .models.presentation import Presentation, create_default_presentation
from .models.legal_mentions import LegalMentions, create_default_legal_mentions
from .models.about import About, create_default_about

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "resources" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_XML_PATH = DATA_DIR / "projects.xml"
PRESENTATION_XML_PATH = DATA_DIR / "presentation.xml"
LEGAL_MENTIONS_XML_PATH = DATA_DIR / "legal_mentions.xml"
ABOUT_XML_PATH = DATA_DIR / "about.xml"


# ---------------- Gestion des projets ---------------- #

project_manager = ProjectManager()

def load_projects():
    """Charge les projets s'il y en a."""
    try:
        with open(PROJECTS_XML_PATH, "r", encoding="utf-8") as f:
            xml_content = f.read()
            project_manager.load_from_xml(xml_content)
    except FileNotFoundError:
        print("Aucun fichier de projets trouvé, démarrage avec une base vide.")
    except Exception as e:
        print(f"Erreur lors du chargement des projets : {e}")

def save_projects():
    """Sauvegarde les projets à la fermeture du logiciel"""
    try:
        with open(PROJECTS_XML_PATH, "w", encoding="utf-8") as f:
            f.write(project_manager.get_projects_xml())
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des projets : {e}")

# ---------------- Gestion de la présentation de l'édition ---------------- #

def load_presentation() -> Presentation:
    try:
        tree = ET.parse(PRESENTATION_XML_PATH)
        root = tree.getroot()
        return Presentation.from_xml_element(root)
    except FileNotFoundError:
        print("Présentation manquante. Création par défaut.")
        return create_default_presentation()
    except Exception as e:
        print(f"Erreur chargement présentation: {e}")
        return create_default_presentation()

def save_presentation(presentation: Presentation):
    try:
        content = '<?xml version="1.0" encoding="utf-8"?>\n' + presentation.to_xml_string()
        with open(PRESENTATION_XML_PATH, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Erreur sauvegarde présentation: {e}")

# ---------------- Gestion des mentions légales ---------------- #

def load_legal_mentions() -> LegalMentions:
    try:
        tree = ET.parse(LEGAL_MENTIONS_XML_PATH)
        root = tree.getroot()
        return LegalMentions.from_xml_element(root)
    except FileNotFoundError:
        print("Mentions légales manquantes. Création par défaut.")
        return create_default_legal_mentions()
    except Exception as e:
        print(f"Erreur chargement mentions légales: {e}")
        return create_default_legal_mentions()

def save_legal_mentions(legal_mentions: LegalMentions):
    try:
        content = '<?xml version="1.0" encoding="utf-8"?>\n' + legal_mentions.to_xml_string()
        with open(LEGAL_MENTIONS_XML_PATH, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Erreur sauvegarde mentions légales: {e}")

# ---------------- Gestion de la section à propos ---------------- #

def load_about() -> About:
    try:
        tree = ET.parse(ABOUT_XML_PATH)
        root = tree.getroot()
        return About.from_xml_element(root)
    except FileNotFoundError:
        print("A propos manquant. Création par défaut.")
        return create_default_about()
    except Exception as e:
        print(f"Erreur chargement à propos: {e}")
        return create_default_about()

def save_about(about: About):
    try:
        content = '<?xml version="1.0" encoding="utf-8"?>\n' + about.to_xml_string()
        with open(ABOUT_XML_PATH, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Erreur sauvegarde à propos: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    load_projects()
    presentation = load_presentation()
    legal_mentions = load_legal_mentions()
    about = load_about()

    widget = MainWindow(
        project_manager=project_manager,
        save_projects_callback=save_projects,
        presentation=presentation,
        save_presentation_callback=save_presentation,
        legal_mentions=legal_mentions,
        save_legal_mentions_callback=save_legal_mentions,
        about=about,
        save_about_callback=save_about
    )
    widget.resize(1000, 700)
    widget.show()

    exit_code = app.exec()

    save_projects()
    save_presentation(widget.presentation)
    save_legal_mentions(widget.legal_mentions)
    save_about(widget.about)
    sys.exit(exit_code)