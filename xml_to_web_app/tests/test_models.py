#!/usr/bin/env python3
"""
Script de test pour les modèles de données.
Vérifie le bon fonctionnement des classes Project et XMLData.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Ajout du chemin pour importer les modèles
sys.path.insert(0, str(Path(__file__).parent))

from models import Project, XMLData, ProjectValidationError, XMLDataError


def test_project_basic():
    """Test des fonctionnalités de base de la classe Project."""
    print("=== Test Project - Fonctionnalités de base ===")
    
    # Création d'un projet simple
    project = Project(name="Mon Premier Projet", description_html="<p>Description du projet</p>")
    
    print(f"Projet créé: {project}")
    print(f"Nom nettoyé: {project.name}")
    print(f"Aperçu: {project.get_preview_text()}")
    print(f"Est vide: {project.is_empty()}")
    
    # Test de mise à jour
    project.update_content("<h1>Nouveau contenu</h1><p>Avec plus de détails</p>")
    print(f"Après mise à jour: {project.get_preview_text()}")
    
    print("✓ Test de base réussi\n")


def test_project_xml_serialization():
    """Test de la sérialisation XML de Project."""
    print("=== Test Project - Sérialisation XML ===")
    
    # Création d'un projet avec du HTML
    original = Project(
        name="Projet Test XML",
        description_html="<h1>Titre</h1><p>Description avec <strong>HTML</strong></p>"
    )
    
    # Conversion en XML
    xml_string = original.to_xml_string()
    print("XML généré:")
    print(xml_string)
    
    # Reconstruction depuis XML
    reconstructed = Project.from_xml_string(xml_string)
    
    # Vérification
    assert original.name == reconstructed.name
    assert original.description_html == reconstructed.description_html
    
    print(f"Original: {original}")
    print(f"Reconstruit: {reconstructed}")
    print("✓ Sérialisation XML réussie\n")


def test_project_validation():
    """Test de la validation des projets."""
    print("=== Test Project - Validation ===")
    
    try:
        # Test nom vide
        Project(name="", description_html="contenu")
        assert False, "Devrait lever une exception pour nom vide"
    except ValueError:
        print("✓ Validation nom vide OK")
    
    try:
        # Test nom avec caractères spéciaux
        project = Project(name="Projet & Spécial!", description_html="contenu")
        print(f"✓ Nom nettoyé: '{project.name}'")
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
    
    print("✓ Tests de validation réussis\n")


def test_xml_data_from_string():
    """Test de XMLData avec une chaîne XML."""
    print("=== Test XMLData - Depuis chaîne ===")
    
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <data>
        <item project="projet_a">Données pour projet A</item>
        <item project="projet_b">Données pour projet B</item>
        <description>Référence à project_c dans le texte</description>
    </data>"""
    
    xml_data = XMLData.from_string(xml_content)
    
    print(f"XML Data: {xml_data}")
    print(f"Valide: {xml_data.is_valid}")
    print(f"Projets référencés: {xml_data.get_project_references()}")
    
    # Test des statistiques
    stats = xml_data.get_statistics()
    print(f"Statistiques: {stats}")
    
    print("✓ Test XMLData depuis chaîne réussi\n")


def test_xml_data_from_file():
    """Test de XMLData avec un fichier temporaire."""
    print("=== Test XMLData - Depuis fichier ===")
    
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <projects>
        <project id="web_app" status="active">
            <name>Application Web</name>
            <reference>Utilise project_framework</reference>
        </project>
        <project id="mobile_app" status="planning">
            <name>Application Mobile</name>
            <reference>Basé sur project_framework</reference>
        </project>
    </projects>"""
    
    # Crée un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
        f.write(xml_content)
        temp_file = f.name
    
    try:
        xml_data = XMLData.from_file(temp_file)
        
        print(f"Fichier: {xml_data.file_path}")
        print(f"Valide: {xml_data.is_valid}")
        print(f"Encodage: {xml_data.encoding}")
        print(f"Projets référencés: {xml_data.get_project_references()}")
        
        # Test du rapport de validation
        report = xml_data.get_validation_report()
        print("Rapport de validation:")
        print(report)
        
    finally:
        # Nettoyage du fichier temporaire
        Path(temp_file).unlink()
    
    print("✓ Test XMLData depuis fichier réussi\n")


def test_xml_data_project_analysis():
    """Test de l'analyse des projets dans XMLData."""
    print("=== Test XMLData - Analyse des projets ===")
    
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <data>
        <section project_ref="projet_a">Section A</section>
        <section project_ref="projet_b">Section B</section>
        <content>Mention de project_c dans le texte</content>
    </data>"""
    
    xml_data = XMLData.from_string(xml_content)
    
    # Liste des projets disponibles (simulée)
    available_projects = ["projet_a", "projet_d", "projet_e"]
    
    print(f"Projets référencés: {xml_data.get_project_references()}")
    print(f"Projets disponibles: {available_projects}")
    print(f"Projets manquants: {xml_data.get_missing_projects(available_projects)}")
    print(f"Projets non utilisés: {xml_data.get_unused_projects(available_projects)}")
    
    # Test de références spécifiques
    print(f"Projet 'projet_a' référencé: {xml_data.has_project_reference('projet_a')}")
    print(f"Projet 'projet_inexistant' référencé: {xml_data.has_project_reference('projet_inexistant')}")
    
    print("✓ Test analyse des projets réussi\n")


def test_xml_data_validation_errors():
    """Test de la gestion des erreurs de validation XMLData."""
    print("=== Test XMLData - Erreurs de validation ===")
    
    # Test XML malformé
    invalid_xml = "<data><item>Test non fermé"
    xml_data = XMLData.from_string(invalid_xml)
    
    print(f"XML invalide - Valide: {xml_data.is_valid}")
    print(f"Erreurs: {xml_data.validation_errors}")
    
    # Test XML vide
    empty_xml_data = XMLData.from_string("")
    print(f"XML vide - Valide: {empty_xml_data.is_valid}")
    print(f"Erreurs: {empty_xml_data.validation_errors}")
    
    # Test XML valide mais simple
    simple_xml = "<root><item>Simple</item></root>"
    simple_xml_data = XMLData.from_string(simple_xml)
    print(f"XML simple - Valide: {simple_xml_data.is_valid}")
    
    print("✓ Test erreurs de validation réussi\n")


def test_projects_collection():
    """Test de la gestion d'une collection de projets."""
    print("=== Test Collection de projets ===")
    
    # Création de plusieurs projets
    projects = [
        Project(name="Site Web", description_html="<h1>Site Web Corporate</h1><p>Description détaillée</p>"),
        Project(name="App Mobile", description_html="<h1>Application Mobile</h1><p>Pour iOS et Android</p>"),
        Project(name="API REST", description_html="<h1>API REST</h1><p>Backend pour les applications</p>")
    ]
    
    print("Projets créés:")
    for project in projects:
        print(f"  - {project.name}: {project.get_preview_text(50)}")
    
    # Simulation de sauvegarde XML collective
    import xml.etree.ElementTree as ET
    
    root = ET.Element("projects")
    for project in projects:
        root.append(project.to_xml_element())
    
    # Indentation pour lisibilité
    def indent_xml(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    indent_xml(root)
    
    xml_string = ET.tostring(root, encoding='unicode', method='xml')
    print("\nXML collection généré:")
    print(xml_string)
    
    # Test de reconstruction
    reconstructed_projects = []
    for project_elem in root.findall('project'):
        reconstructed_projects.append(Project.from_xml_element(project_elem))
    
    print(f"\nProjets reconstruits: {len(reconstructed_projects)}")
    for project in reconstructed_projects:
        print(f"  - {project.name}")
    
    print("✓ Test collection de projets réussi\n")


def run_all_tests():
    """Exécute tous les tests."""
    print("🧪 DÉBUT DES TESTS DES MODÈLES DE DONNÉES")
    print("=" * 50)
    
    try:
        test_project_basic()
        test_project_xml_serialization()
        test_project_validation()
        test_xml_data_from_string()
        test_xml_data_from_file()
        test_xml_data_project_analysis()
        test_xml_data_validation_errors()
        test_projects_collection()
        
        print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        
    except Exception as e:
        print(f"❌ ERREUR DANS LES TESTS: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def demo_usage():
    """Démonstration d'utilisation des modèles."""
    print("\n" + "=" * 50)
    print("📋 DÉMONSTRATION D'UTILISATION")
    print("=" * 50)
    
    # Création d'un projet
    print("1. Création d'un projet:")
    project = Project(
        name="Site E-commerce",
        description_html="""
        <h1>Site E-commerce</h1>
        <p>Développement d'une plateforme de vente en ligne moderne.</p>
        <h2>Fonctionnalités</h2>
        <ul>
            <li>Catalogue produits</li>
            <li>Panier d'achat</li>
            <li>Paiement sécurisé</li>
        </ul>
        """
    )
    print(f"  Projet: {project.name}")
    print(f"  Aperçu: {project.get_preview_text(80)}")
    
    # Simulation de données XML
    print("\n2. Chargement de données XML:")
    xml_sample = """<?xml version="1.0" encoding="utf-8"?>
    <database_export>
        <table name="projects">
            <row project_id="site_e_commerce">
                <column name="status">active</column>
                <column name="budget">50000</column>
            </row>
        </table>
        <references>
            <ref>Projet site_e_commerce nécessaire</ref>
        </references>
    </database_export>"""
    
    xml_data = XMLData.from_string(xml_sample)
    print(f"  Statut: {'✓ Valide' if xml_data.is_valid else '✗ Invalide'}")
    print(f"  Projets trouvés: {xml_data.get_project_references()}")
    
    # Analyse de cohérence
    print("\n3. Analyse de cohérence:")
    available_projects = [project.name]
    missing = xml_data.get_missing_projects(available_projects)
    unused = xml_data.get_unused_projects(available_projects)
    
    print(f"  Projets disponibles: {available_projects}")
    print(f"  Projets manquants: {missing}")
    print(f"  Projets non utilisés: {unused}")
    
    print("\n✨ Démonstration terminée!")


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        demo_usage()
    
    sys.exit(0 if success else 1)