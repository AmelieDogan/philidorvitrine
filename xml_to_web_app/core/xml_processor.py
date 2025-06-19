import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import QObject, Signal

from ..utils.xml_utils import (validate_xml_file, extract_xml_statistics, 
                       prettify_xml, clean_xml_content)


class XMLProcessor(QObject):
    """Worker thread pour traiter les fichiers XML sans bloquer l'interface"""
    
    progress_updated = Signal(int)
    stats_ready = Signal(dict)
    merge_completed = Signal(str, str)  # merged_file_path, stats_summary
    error_occurred = Signal(str)
    
    def __init__(self, xml_file_path, resources_dir):
        super().__init__()
        self.xml_file_path = xml_file_path
        self.resources_dir = Path(resources_dir)
        self.data_dir = self.resources_dir / "data"
        self.temp_dir = self.resources_dir / "temp"

    def process(self):
        """Traite le fichier XML et effectue la fusion"""
        try:
            self.progress_updated.emit(10)
            
            # 1. Préparation des répertoires (en premier pour éviter les erreurs)
            try:
                self.resources_dir.mkdir(parents=True, exist_ok=True)
                self.data_dir.mkdir(parents=True, exist_ok=True)
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.error_occurred.emit(f"Impossible de créer les répertoires: {str(e)}")
                return

            # 2. Validation du fichier uploadé
            is_valid, errors = validate_xml_file(self.xml_file_path)
            if not is_valid:
                self.error_occurred.emit(f"Fichier XML invalide: {', '.join(errors)}")
                return

            self.progress_updated.emit(20)

            # 3. Lecture et nettoyage du fichier XML
            with open(self.xml_file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Nettoyage du contenu XML
            cleaned_content = self._clean_xml_content(xml_content)
            self.progress_updated.emit(30)

            # 4. Extraction des statistiques (sur le contenu nettoyé)
            stats = extract_xml_statistics(cleaned_content)
            self.stats_ready.emit(stats)
            self.progress_updated.emit(50)

            # 5. Fusion avec les fichiers de données
            merged_content = self._merge_xml_files(cleaned_content)
            self.progress_updated.emit(80)

            # 6. Sauvegarde du fichier fusionné
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            merged_file_path = self.temp_dir / f"merged_data_{timestamp}.xml"
            with open(merged_file_path, 'w', encoding='utf-8') as f:
                f.write(merged_content)

            self.progress_updated.emit(100)

            # Résumé des statistiques
            stats_summary = self._create_stats_summary(stats)
            self.merge_completed.emit(str(merged_file_path), stats_summary)

        except Exception as e:
            self.error_occurred.emit(f"Erreur lors du traitement: {str(e)}")

    def _clean_xml_content(self, xml_content):
        """Nettoie le contenu XML en corrigeant et supprimant les balises défectueuses"""
        try:            
            # Correction des balises <Anonyme> et </Anonyme>
            xml_content = xml_content.replace('<Anonyme>', '<item key="Anonyme">')
            xml_content = xml_content.replace('</Anonyme>', '</item>')
            xml_content = xml_content.replace('<nomsFonctions><item key=""></item></nomsFonctions>', '')
            
            return xml_content
            
        except Exception as e:
            self.error_occurred.emit(f"Erreur lors du nettoyage XML: {str(e)}")
            return xml_content  # Retourne le contenu original en cas d'erreur
        
    def _merge_xml_files(self, main_xml_content):
        """Fusionne le fichier principal avec les fichiers de données"""
        
        # Parse le fichier principal
        main_root = ET.fromstring(clean_xml_content(main_xml_content))
        
        # Crée la structure fusionnée
        merged_root = ET.Element("merged_data")
        merged_root.set("generated", datetime.now().isoformat())
        merged_root.set("source_file", Path(self.xml_file_path).name)
        
        # Ajoute le contenu principal dans une section dédiée
        main_section = ET.SubElement(merged_root, "philidor4_data")
        main_section.append(main_root)
        
        # Fichiers de données à fusionner
        data_files = {
            "presentation_data": "presentation.xml",
            "projects_data": "projects.xml", 
            "legal_mentions_data": "legal_mentions.xml",
            "about_data": "about.xml"
        }
        
        # Ajoute chaque fichier de données
        for section_name, filename in data_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data_content = f.read()
                    
                    data_root = ET.fromstring(clean_xml_content(data_content))
                    
                    # Crée une section pour ce fichier
                    section = ET.SubElement(merged_root, section_name)
                    section.set("source_file", filename)
                    section.append(data_root)
                    
                except Exception as e:
                    # Ajoute une section vide avec l'erreur
                    section = ET.SubElement(merged_root, section_name)
                    section.set("error", str(e))
                    section.set("source_file", filename)
        
        # Formatage du XML final
        prettify_xml(merged_root)
        
        # Génération avec déclaration XML
        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml_content = ET.tostring(merged_root, encoding='unicode', method='xml')
        
        return xml_declaration + xml_content
    
    def _create_stats_summary(self, stats):
        """Crée un résumé textuel des statistiques"""
        if 'error' in stats:
            return f"Erreur d'analyse: {stats['error']}"
        
        summary = f"""=== STATISTIQUES DU FICHIER XML ===

Informations générales:
- Élément racine: {stats.get('root_tag', 'N/A')}
- Nombre total d'éléments: {stats.get('total_elements', 0)}
- Types d'éléments différents: {stats.get('element_types', 0)}
- Profondeur maximale: {stats.get('max_depth', 0)}
- Taille du fichier: {stats.get('xml_size_bytes', 0)} octets
- Longueur totale du texte: {stats.get('total_text_length', 0)} caractères

Répartition des éléments:"""
        
        element_counts = stats.get('element_counts', {})
        for tag, count in sorted(element_counts.items()):
            summary += f"\n- {tag}: {count} occurrence(s)"
        
        project_refs = stats.get('project_references', [])
        if project_refs:
            summary += f"\n\nRéférences de projets trouvées ({len(project_refs)}):"
            for ref in project_refs:
                summary += f"\n- {ref}"
        
        root_attrs = stats.get('root_attributes', {})
        if root_attrs:
            summary += f"\n\nAttributs de l'élément racine:"
            for attr, value in root_attrs.items():
                summary += f"\n- {attr}: {value}"
        
        return summary