from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify, send_from_directory
import saxonche
import os
import tempfile
import shutil
import zipfile
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
    # Vérifier si les fichiers ont été soumis
    if 'xml_file' not in request.files or 'xslt_file' not in request.files:
        return redirect(request.url)
    
    xml_file = request.files['xml_file']
    xslt_file = request.files['xslt_file']
    
    # Vérifier si les fichiers sont vides
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
    
    # Fichier de sortie principal (même s'il ne sera pas utilisé)
    default_output = os.path.join(output_dir, "output.xml")
    
    try:
        # Initialiser Saxon
        processor = saxonche.PySaxonProcessor(license=False)
        xslt_processor = processor.new_xslt30_processor()
        
        # Définir les options de configuration
        # Spécifier explicitement où les fichiers xsl:result-document doivent être écrits
        xslt_processor.set_parameter("output-uri-resolver", 
                          processor.make_string_value(f"file://{transform_dir}/"))
        
        # Paramètre pour éviter les erreurs avec les chemins vides :
        xslt_processor.set_parameter("skip-empty-ids", processor.make_boolean_value(True))
        
        # Compiler et exécuter la transformation
        executable = xslt_processor.compile_stylesheet(stylesheet_file=xslt_path)
        
        # Pour XSLT 2.0 avec xsl:result-document, nous devons toujours fournir un fichier de sortie principal
        # même s'il n'est pas vraiment utilisé
        executable.transform_to_file(source_file=xml_path, output_file=default_output)
        
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

if __name__ == '__main__':
    # Créer les templates s'ils n'existent pas
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Template index.html
    template_path = os.path.join('templates', 'index.html')
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Transformateur XSLT 2.0 Multi-fichiers</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        label {
            font-weight: bold;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        .error {
            color: red;
            text-align: center;
            margin-bottom: 15px;
        }
        .info {
            background-color: #e0f7fa;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Transformateur XSLT 2.0 Multi-fichiers</h1>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <div class="info">
            <p>Cette application permet de transformer des fichiers XML avec des feuilles de style XSLT 2.0 qui produisent plusieurs fichiers de sortie.</p>
            <p>Après la transformation, vous pourrez télécharger un ZIP contenant tous les fichiers générés ou les visualiser individuellement.</p>
        </div>
        
        <form action="/transform" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="xml_file">Fichier XML :</label>
                <input type="file" id="xml_file" name="xml_file" accept=".xml" required>
            </div>
            
            <div class="form-group">
                <label for="xslt_file">Fichier XSLT :</label>
                <input type="file" id="xslt_file" name="xslt_file" accept=".xsl,.xslt" required>
            </div>
            
            <button type="submit">Transformer</button>
        </form>
    </div>
</body>
</html>
            ''')
    
    # Template results.html
    results_template_path = os.path.join('templates', 'results.html')
    if not os.path.exists(results_template_path):
        with open(results_template_path, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Résultats de la transformation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #333;
        }
        h1 {
            text-align: center;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            padding: 10px;
            margin: 5px 0;
            background-color: #fff;
            border-radius: 4px;
            border-left: 3px solid #4CAF50;
        }
        a {
            color: #2196F3;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .button {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #45a049;
        }
        .back-button {
            background-color: #607D8B;
        }
        .back-button:hover {
            background-color: #546E7A;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Transformation réussie !</h1>
        
        <h2>Fichiers générés :</h2>
        <ul>
            {% for file in files %}
            <li>
                <a href="{{ url_for('view_file', transform_id=transform_id, filename=file) }}" target="_blank">{{ file }}</a>
            </li>
            {% endfor %}
        </ul>
        
        <a href="{{ url_for('download_zip', transform_id=transform_id) }}" class="button">Télécharger tous les fichiers (ZIP)</a>
        <a href="{{ url_for('index') }}" class="button back-button">Retour à l'accueil</a>
    </div>
</body>
</html>
            ''')
    
    app.run(host='0.0.0.0', port=5000, debug=True)