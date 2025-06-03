from flask import Flask, render_template, request, send_file, redirect, send_from_directory
import saxonche
import os
import tempfile
import zipfile
import webbrowser
import threading
import time
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Limite à 100MB
app.config['TRANSFORMATIONS'] = {}  # Pour stocker les informations de transformation

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transform', methods=['POST'])
def transform():

    start_time = time.time()

    # Vérifier si les fichiers ont été soumis
    if 'xml_file' not in request.files or 'xslt_file' not in request.files:
        return redirect(request.url)
    
    xml_file = request.files['xml_file']
    xslt_file = request.files['xslt_file']
    
    # Vérifier si les noms de fichier sont vides
    if xml_file.filename == '' or xslt_file.filename == '':
        return render_template('index.html', error="Veuillez sélectionner les fichiers XML et XSLT")
    
    # Créer un identifiant unique pour cette transformation
    transform_id = str(uuid.uuid4())
    transform_dir = os.path.join(app.config['UPLOAD_FOLDER'], transform_id)
    os.makedirs(transform_dir, exist_ok=True)
    
    # Créer un sous-répertoire pour les fichiers de sortie
    output_dir = os.path.join(transform_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder les fichiers téléchargés
    xml_path = os.path.join(transform_dir, secure_filename(xml_file.filename))
    xslt_path = os.path.join(transform_dir, secure_filename(xslt_file.filename))
    
    xml_file.save(xml_path)
    xslt_file.save(xslt_path)
    
    # Fichier rapport principal
    report_output = os.path.join(output_dir, "report.xml")
    
    try:
        # Initialiser Saxon
        processor = saxonche.PySaxonProcessor(license=False)
        xslt_processor = processor.new_xslt30_processor()
        
        # Définir les options de configuration
        # Spécifier explicitement où les fichiers xsl:result-document doivent être écrits
        # En utilisant le répertoire output/ pour tous les fichiers générés
        output_dir_uri = f"file://{output_dir}/"
        xslt_processor.set_parameter("output-uri-resolver", processor.make_string_value(output_dir_uri))
        
        # Paramètre pour éviter les erreurs avec les chemins vides :
        xslt_processor.set_parameter("skip-empty-ids", processor.make_boolean_value(True))
        
        # Compiler et exécuter la transformation
        executable = xslt_processor.compile_stylesheet(stylesheet_file=xslt_path)
        
        # Exécuter la transformation avec un fichier de sortie principal explicite
        # C'est nécessaire pour que les xsl:result-document fonctionnent correctement
        executable.transform_to_file(source_file=xml_path, output_file=report_output)

        transform_timer = time.time() - start_time

        # Lister les fichiers générés dans le dossier output_dir
        generated_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                generated_files.append(os.path.join(root, file))

        output_files_count = len(generated_files)
        
        # Créer un rapport
        xml_filename = os.path.basename(xml_path)
        xslt_filename = os.path.basename(xslt_path)
        transform_time = time.strftime("%Y-%m-%d %H:%M:%S")
        transform_timer = str(round(transform_timer, 2)) + " secondes"
        
        # Générer un rapport XML avec des métadonnées sur la transformation
        report_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<transformation-report>
    <metadata>
        <source-file>{xml_filename}</source-file>
        <stylesheet-file>{xslt_filename}</stylesheet-file>
        <transform-date>{transform_time}</transform-date>
        <transform-time>{transform_timer}</transform-time>
        <transform-id>{transform_id}</transform-id>
    </metadata>
    <transformation-result>
        <status>success</status>
        <output-files-count>{output_files_count}</output-files-count>
    </transformation-result>
</transformation-report>"""
        
        # Écrire le rapport (remplace le fichier généré par transform_to_file)
        with open(report_output, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Créer un fichier zip avec tous les fichiers générés
        zip_filename = "transformation_results.zip"
        zip_path = os.path.join(transform_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        # Stocker les informations pour pouvoir accéder aux fichiers plus tard
        files = []
        for f in os.listdir(output_dir):
            if os.path.isfile(os.path.join(output_dir, f)):
                files.append(f)
        
        app.config['TRANSFORMATIONS'][transform_id] = {
            'output_dir': output_dir,
            'zip_path': zip_path,
            'files': files
        }
        
        return render_template('results.html', 
                             transform_id=transform_id, 
                             files=app.config['TRANSFORMATIONS'][transform_id]['files'])
    
    except Exception as e:
        error_message = str(e)
        return render_template('index.html', error=f"Erreur lors de la transformation : {error_message}")

@app.route('/download_zip/<transform_id>')
def download_zip(transform_id):
    if transform_id in app.config['TRANSFORMATIONS']:
        return send_file(
            app.config['TRANSFORMATIONS'][transform_id]['zip_path'],
            as_attachment=True,
            download_name="transformation_results.zip"
        )
    return "Transformation non trouvée", 404

@app.route('/view_file/<transform_id>/<path:filename>')
def view_file(transform_id, filename):
    if transform_id in app.config['TRANSFORMATIONS']:
        output_dir = app.config['TRANSFORMATIONS'][transform_id]['output_dir']
        return send_from_directory(output_dir, filename)
    return "Fichier non trouvé", 404

@app.route('/health')
def health():
    return "Application en cours d'exécution"

def open_browser():
    """Ouvre le navigateur après un court délai"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Créer les templates s'ils n'existent pas
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Template index.html
    template_path = os.path.join(templates_dir, 'index.html')
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>Transformateur XSLT 2.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --primary-color: #4361ee;
            --primary-hover: #3a56d4;
            --secondary-color: #3f37c9;
            --text-color: #333;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --border-radius: 10px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 30px;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        h1 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 30px;
            font-weight: 600;
        }
        
        .info-card {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 25px;
        }
        
        .error-card {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 25px;
        }
        
        form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        label {
            font-weight: 500;
            color: #555;
        }
        
        .file-input-container {
            position: relative;
            overflow: hidden;
            display: inline-block;
            cursor: pointer;
        }
        
        .file-input-label {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 15px;
            background-color: #e9ecef;
            border: 1px solid #ced4da;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .file-input-label:hover {
            background-color: #dee2e6;
        }
        
        .file-name {
            margin-top: 5px;
            font-size: 14px;
            color: #6c757d;
        }
        
        input[type="file"] {
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        
        button {
            background-color: var(--primary-color);
            color: white;
            padding: 12px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: background-color 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        button:hover {
            background-color: var(--primary-hover);
        }
        
        .button-icon {
            width: 20px;
            height: 20px;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            color: #6c757d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Transformateur XSLT 2.0 Multi-fichiers</h1>
            
            {% if error %}
            <div class="error-card">
                <p>{{ error }}</p>
            </div>
            {% endif %}
            
            <div class="info-card">
                <p>Cette application permet de transformer des fichiers XML avec des feuilles de style XSLT 2.0 qui produisent plusieurs fichiers de sortie.</p>
                <p>Après la transformation, vous pourrez télécharger un ZIP contenant tous les fichiers générés ou les visualiser individuellement.</p>
            </div>
            
            <form action="/transform" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="xml_file">Fichier XML :</label>
                    <div class="file-input-container">
                        <label class="file-input-label">
                            <svg class="button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="17 8 12 3 7 8"></polyline>
                                <line x1="12" y1="3" x2="12" y2="15"></line>
                            </svg>
                            Sélectionner un fichier XML
                            <input type="file" id="xml_file" name="xml_file" accept=".xml" required onchange="updateFileName(this, 'xml_file_name')">
                        </label>
                    </div>
                    <div id="xml_file_name" class="file-name">Aucun fichier sélectionné</div>
                </div>
                
                <div class="form-group">
                    <label for="xslt_file">Fichier XSLT :</label>
                    <div class="file-input-container">
                        <label class="file-input-label">
                            <svg class="button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="17 8 12 3 7 8"></polyline>
                                <line x1="12" y1="3" x2="12" y2="15"></line>
                            </svg>
                            Sélectionner un fichier XSLT
                            <input type="file" id="xslt_file" name="xslt_file" accept=".xsl,.xslt" required onchange="updateFileName(this, 'xslt_file_name')">
                        </label>
                    </div>
                    <div id="xslt_file_name" class="file-name">Aucun fichier sélectionné</div>
                </div>
                
                <button type="submit">
                    <svg class="button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="16 3 21 3 21 8"></polyline>
                        <line x1="4" y1="20" x2="21" y2="3"></line>
                        <path d="M21 13v8H3V5h8"></path>
                    </svg>
                    Transformer
                </button>
            </form>
        </div>
        
        <footer>
            <p>XSLT Transformer © 2025</p>
        </footer>
    </div>
    
    <script>
        function updateFileName(input, elementId) {
            const fileName = input.files[0] ? input.files[0].name : 'Aucun fichier sélectionné';
            document.getElementById(elementId).textContent = fileName;
        }
    </script>
</body>
</html>
            ''')
    
    # Template results.html
    results_template_path = os.path.join(templates_dir, 'results.html')
    if not os.path.exists(results_template_path):
        with open(results_template_path, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>Résultats de la transformation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --primary-color: #4361ee;
            --primary-hover: #3a56d4;
            --secondary-color: #3f37c9;
            --success-color: #38b000;
            --success-hover: #2b9348;
            --text-color: #333;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --border-radius: 10px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 30px;
            transition: transform 0.3s ease;
        }
        
        h1, h2 {
            color: var(--primary-color);
            margin-bottom: 20px;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-weight: 600;
        }
        
        .success-banner {
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .file-list {
            list-style-type: none;
            padding: 0;
            margin-bottom: 30px;
        }
        
        .file-item {
            padding: 15px;
            margin: 10px 0;
            background-color: #fff;
            border-radius: 5px;
            border-left: 3px solid var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .file-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .file-icon {
            color: var(--primary-color);
            width: 24px;
            height: 24px;
        }
        
        .file-link {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
            flex-grow: 1;
        }
        
        .file-link:hover {
            text-decoration: underline;
        }
        
        .button-container {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .button {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background-color: var(--primary-color);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            text-decoration: none;
            transition: background-color 0.3s ease;
        }
        
        .button:hover {
            background-color: var(--primary-hover);
        }
        
        .button-download {
            background-color: var(--success-color);
        }
        
        .button-download:hover {
            background-color: var(--success-hover);
        }
        
        .button-icon {
            width: 20px;
            height: 20px;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            color: #6c757d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Résultats de la transformation</h1>
            
            <div class="success-banner">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>Transformation complétée avec succès !</span>
            </div>
            
            <h2>Fichiers générés :</h2>
            <ul class="file-list">
                {% for file in files %}
                <li class="file-item">
                    <svg class="file-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        {% if file == 'report.xml' %}
                        <!-- Icône de rapport pour report.xml -->
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <path d="M16 13H8"></path>
                        <path d="M16 17H8"></path>
                        <path d="M10 9H8"></path>
                        {% else %}
                        <!-- Icône de fichier standard pour les autres fichiers -->
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                        {% endif %}
                    </svg>
                    <a href="{{ url_for('view_file', transform_id=transform_id, filename=file) }}" class="file-link" target="_blank">
                        {{ file }}
                        {% if file == 'report.xml' %}
                        <span style="font-size: 0.8em; color: #4361ee; margin-left: 5px;">(Rapport de transformation)</span>
                        {% endif %}
                    </a>
                </li>
                {% endfor %}
            </ul>
            
            <div class="button-container">
                <a href="{{ url_for('download_zip', transform_id=transform_id) }}" class="button button-download">
                    <svg class="button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Télécharger tous les fichiers (ZIP)
                </a>
                <a href="{{ url_for('index') }}" class="button">
                    <svg class="button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                        <polyline points="9 22 9 12 15 12 15 22"></polyline>
                    </svg>
                    Retour à l'accueil
                </a>
            </div>
        </div>
        
        <footer>
            <p>XSLT Transformer © 2025</p>
        </footer>
    </div>
</body>
</html>
            ''')
    
    # Démarrer le navigateur dans un thread séparé
    threading.Thread(target=open_browser).start()
    
    # Exécuter l'application uniquement sur localhost
    app.run(host='127.0.0.1', port=5000, debug=False)