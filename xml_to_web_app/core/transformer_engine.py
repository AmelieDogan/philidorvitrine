import os
import html
import tempfile
import zipfile
import time
import uuid
import saxonche
from typing import Optional, Dict, Any

from PySide6.QtCore import QThread, Signal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ← va à la racine du projet
STATICS_PATH = os.path.join(BASE_DIR, "resources", "statics")

class XSLTTransformationEngine:
    """Classe backend pour gérer les transformations XSLT avec Saxon"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.transformations: Dict[str, Dict[str, Any]] = {}

    def decode_html_entities(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Double décodage pour gérer les &amp;#xE9; → &#xE9; → é
        decoded = html.unescape(html.unescape(content))

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(decoded)
    
    def transform(self, xml_file_path: str, xslt_file_path: str) -> Dict[str, Any]:
        """
        Effectue une transformation XSLT
        
        Args:
            xml_file_path: Chemin vers le fichier XML source
            xslt_file_path: Chemin vers le fichier XSLT
            
        Returns:
            Dictionnaire contenant les résultats de la transformation
        """
        start_time = time.time()
        
        # Créer un identifiant unique pour cette transformation
        transform_id = str(uuid.uuid4())
        transform_dir = os.path.join(self.temp_dir, transform_id)
        os.makedirs(transform_dir, exist_ok=True)
        
        # Créer un sous-répertoire pour les fichiers de sortie
        output_dir = os.path.join(transform_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Fichier rapport principal
        report_output = os.path.join(output_dir, "report.xml")
        
        try:
            # Initialiser Saxon
            processor = saxonche.PySaxonProcessor(license=False)
            xslt_processor = processor.new_xslt30_processor()
            
            # Définir les options de configuration
            output_dir_uri = f"file://{output_dir}/"
            xslt_processor.set_parameter("output-uri-resolver", processor.make_string_value(output_dir_uri))
            xslt_processor.set_parameter("skip-empty-ids", processor.make_boolean_value(True))
            
            # Compiler et exécuter la transformation
            executable = xslt_processor.compile_stylesheet(stylesheet_file=xslt_file_path)
            executable.transform_to_file(source_file=xml_file_path, output_file=report_output)
            
            transform_timer = time.time() - start_time
            
            # Lister les fichiers générés
            generated_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    generated_files.append(os.path.join(root, file))
            
            output_files_count = len(generated_files)
            
            # Créer un rapport
            xml_filename = os.path.basename(xml_file_path)
            xslt_filename = os.path.basename(xslt_file_path)
            transform_time = time.strftime("%Y-%m-%d %H:%M:%S")
            transform_timer_str = str(round(transform_timer, 2)) + " secondes"
            
            # Générer un rapport XML
            report_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<transformation-report>
    <metadata>
        <source-file>{xml_filename}</source-file>
        <stylesheet-file>{xslt_filename}</stylesheet-file>
        <transform-date>{transform_time}</transform-date>
        <transform-time>{transform_timer_str}</transform-time>
        <transform-id>{transform_id}</transform-id>
    </metadata>
    <transformation-result>
        <status>success</status>
        <output-files-count>{output_files_count}</output-files-count>
    </transformation-result>
</transformation-report>"""
            
            # Écrire le rapport
            with open(report_output, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Créer un fichier zip avec tous les fichiers générés
            zip_filename = f"transformation_results_{transform_id[:8]}.zip"
            zip_path = os.path.join(transform_dir, zip_filename)

            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    self.decode_html_entities(os.path.join(root, file))

            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Ajouter tous les fichiers de output_dir
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)

                # Ajouter le dossier statics dans output/
                if os.path.exists(STATICS_PATH):
                    for root, dirs, files in os.walk(STATICS_PATH):
                        for file in files:
                            abs_path = os.path.join(root, file)
                            rel_path = os.path.relpath(abs_path, STATICS_PATH)
                            zipf.write(abs_path, arcname=os.path.join("output", "statics", rel_path))

            
            # Stocker les informations
            files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
            
            self.transformations[transform_id] = {
                'output_dir': output_dir,
                'zip_path': zip_path,
                'files': files,
                'xml_file': xml_filename,
                'xslt_file': xslt_filename,
                'transform_time': transform_time,
                'duration': transform_timer,
                'file_count': output_files_count
            }
            
            return {
                'success': True,
                'transform_id': transform_id,
                'zip_path': zip_path,
                'files': files,
                'duration': transform_timer,
                'file_count': output_files_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'transform_id': transform_id
            }
    
    def get_transformation_info(self, transform_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une transformation"""
        return self.transformations.get(transform_id)
    
    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass


class TransformationWorker(QThread):
    """Worker thread pour exécuter les transformations XSLT sans bloquer l'interface"""
    
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, engine: XSLTTransformationEngine, xml_path: str, xslt_path: str):
        super().__init__()
        self.engine = engine
        self.xml_path = xml_path
        self.xslt_path = xslt_path
    
    def run(self):
        try:
            self.progress.emit("Initialisation de la transformation...")
            result = self.engine.transform(self.xml_path, self.xslt_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))