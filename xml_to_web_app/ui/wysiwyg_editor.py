"""
Composant d'édition HTML WYSIWYG pour l'application XML to Web.
Utilise QWebEngineView avec TinyMCE pour l'édition HTML.
"""

import os
import json
import logging
from typing import Callable, Optional, Any
from PySide6.QtCore import QUrl, QTimer, Signal
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget


class WysiwygEditor(QWebEngineView):
    """
    Composant d'édition HTML intégré utilisant TinyMCE.
    
    Fonctionnalités :
    - Utilise TinyMCE pour l'édition WYSIWYG
    - Communication bidirectionnelle avec Python
    - Sauvegarde automatique
    - Validation du contenu HTML
    
    Signals:
        content_changed: Émis quand le contenu change (str: nouveau_contenu)
        editor_ready: Émis quand l'éditeur est prêt
        save_requested: Émis quand l'utilisateur demande une sauvegarde
    """
    
    # Signaux Qt
    content_changed = Signal(str)
    editor_ready = Signal()
    save_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialise l'éditeur WYSIWYG.
        
        Args:
            parent: Widget parent
        """
        super().__init__(parent)
        
        self._logger = logging.getLogger(__name__)
        self._current_content = ""
        self._editor_ready = False
        self._auto_save_timer = QTimer()
        self._auto_save_enabled = True
        self._auto_save_interval = 5000  # 5 secondes
        self._content_change_callback: Optional[Callable[[str], None]] = None
        
        # Configuration de l'éditeur
        self._setup_webengine()
        self._setup_auto_save()
        self._load_editor_page()
        
        self._logger.info("WysiwygEditor initialisé")
    
    def _setup_webengine(self) -> None:
        """Configure les paramètres de QWebEngineView."""
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        # Connecte les signaux
        self.loadFinished.connect(self._on_page_loaded)
    
    def _setup_auto_save(self) -> None:
        """Configure la sauvegarde automatique."""
        self._auto_save_timer.timeout.connect(self._auto_save_content)
        self._auto_save_timer.setSingleShot(False)
    
    def _load_editor_page(self) -> None:
        """Charge la page HTML contenant l'éditeur TinyMCE."""
        # Construit le chemin vers le fichier HTML de l'éditeur
        current_dir = os.path.dirname(os.path.abspath(__file__))
        editor_path = os.path.join(current_dir, '..', 'resources', 'editor', 'editor.html')
        editor_path = os.path.abspath(editor_path)
        
        if os.path.exists(editor_path):
            editor_url = QUrl.fromLocalFile(editor_path)
            self.setUrl(editor_url)
            self._logger.info(f"Chargement de l'éditeur depuis: {editor_path}")
        else:
            self._logger.error(f"Fichier éditeur non trouvé: {editor_path}")
            self._load_fallback_editor()
    
    def _load_fallback_editor(self) -> None:
        """Charge un éditeur de base si le fichier principal n'est pas trouvé."""
        fallback_html = self._get_fallback_editor_html()
        self.setHtml(fallback_html)
        self._logger.warning("Utilisation de l'éditeur de base (fallback)")
    
    def _get_fallback_editor_html(self) -> str:
        """
        Retourne le HTML de base pour l'éditeur en cas de fallback.
        
        Returns:
            HTML contenant un éditeur TinyMCE minimal
        """
        return """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Éditeur WYSIWYG</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.8.2/tinymce.min.js"></script>
    <style>
        body { 
            margin: 0; 
            padding: 10px; 
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
        }
        #editor-container {
            background-color: white;
            border-radius: 4px;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div id="editor-container">
        <textarea id="wysiwyg-editor" style="width: 100%; height: 400px;">
            <p>Commencez à écrire votre contenu ici...</p>
        </textarea>
    </div>
    
    <script>
        tinymce.init({
            selector: '#wysiwyg-editor',
            height: 400,
            menubar: false,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'preview', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | ' +
                'bold italic forecolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | help',
            content_style: 'body { font-family: Arial, sans-serif; font-size: 14px }',
            setup: function (editor) {
                editor.on('init', function () {
                    console.log('TinyMCE initialisé');
                    window.editorReady = true;
                    if (window.pyqt_bridge) {
                        window.pyqt_bridge.editor_ready();
                    }
                });
                
                editor.on('change keyup setcontent', function () {
                    const content = editor.getContent();
                    if (window.pyqt_bridge) {
                        window.pyqt_bridge.content_changed(content);
                    }
                });
            }
        });
        
        // Interface JavaScript pour communication avec PyQt
        window.editorInterface = {
            setContent: function(html) {
                if (tinymce.activeEditor) {
                    tinymce.activeEditor.setContent(html);
                }
            },
            
            getContent: function() {
                if (tinymce.activeEditor) {
                    return tinymce.activeEditor.getContent();
                }
                return '';
            },
            
            insertContent: function(html) {
                if (tinymce.activeEditor) {
                    tinymce.activeEditor.insertContent(html);
                }
            },
            
            focus: function() {
                if (tinymce.activeEditor) {
                    tinymce.activeEditor.focus();
                }
            }
        };
    </script>
</body>
</html>
        """
    
    def _on_page_loaded(self, success: bool) -> None:
        """
        Callback appelé quand la page est chargée.
        
        Args:
            success: True si le chargement a réussi
        """
        if success:
            self._setup_editor_communication()
            self._logger.info("Page éditeur chargée avec succès")
        else:
            self._logger.error("Échec du chargement de la page éditeur")
    
    def setup_editor_communication(self) -> None:
        """Configure la communication entre Python et JavaScript."""
        # Cette méthode est appelée automatiquement après le chargement
        # mais peut être appelée manuellement si nécessaire
        self._setup_editor_communication()
    
    def _setup_editor_communication(self) -> None:
        """Configure la communication bidirectionnelle avec l'éditeur JavaScript."""
        # Injecte le bridge Python-JavaScript
        bridge_script = """
        window.pyqt_bridge = {
            content_changed: function(content) {
                // Cette fonction sera redéfinie par PyQt
                console.log('Content changed:', content.length, 'characters');
            },
            
            editor_ready: function() {
                // Cette fonction sera redéfinie par PyQt
                console.log('Editor ready');
            },
            
            save_requested: function() {
                // Cette fonction sera redéfinie par PyQt
                console.log('Save requested');
            }
        };
        """
        
        self.page().runJavaScript(bridge_script, self._on_bridge_setup)
    
    def _on_bridge_setup(self, result: Any) -> None:
        """Callback appelé après la configuration du bridge."""
        # Configure les callbacks Python
        self._setup_javascript_callbacks()
        
        # Attend que l'éditeur soit prêt
        self._wait_for_editor_ready()
    
    def _setup_javascript_callbacks(self) -> None:
        """Configure les callbacks JavaScript vers Python."""
        # Redéfinit les fonctions du bridge pour qu'elles appellent les méthodes Python
        callback_script = """
        window.pyqt_bridge.content_changed = function(content) {
            // Le contenu sera récupéré via get_content() pour éviter les problèmes d'encodage
            window.content_changed_flag = true;
        };
        
        window.pyqt_bridge.editor_ready = function() {
            window.editor_ready_flag = true;
        };
        
        window.pyqt_bridge.save_requested = function() {
            window.save_requested_flag = true;
        };
        """
        
        self.page().runJavaScript(callback_script)
        
        # Lance le timer de surveillance des changements
        self._start_change_monitoring()
    
    def _wait_for_editor_ready(self) -> None:
        """Attend que l'éditeur soit complètement initialisé."""
        check_script = "window.editorReady === true"
        
        def check_ready(ready: bool) -> None:
            if ready:
                self._editor_ready = True
                self.editor_ready.emit()
                self._logger.info("Éditeur WYSIWYG prêt")
                if self._auto_save_enabled:
                    self._auto_save_timer.start(self._auto_save_interval)
            else:
                # Réessaie dans 100ms
                QTimer.singleShot(100, lambda: self.page().runJavaScript(check_script, check_ready))
        
        self.page().runJavaScript(check_script, check_ready)
    
    def _start_change_monitoring(self) -> None:
        """Lance la surveillance des changements de contenu."""
        change_timer = QTimer(self)
        change_timer.timeout.connect(self._check_content_changes)
        change_timer.start(500)  # Vérifie toutes les 500ms
    
    def _check_content_changes(self) -> None:
        """Vérifie s'il y a eu des changements de contenu."""
        if not self._editor_ready:
            return
        
        # Vérifie les flags JavaScript
        self.page().runJavaScript(
            "window.content_changed_flag",
            self._handle_content_change_flag
        )
        
        self.page().runJavaScript(
            "window.save_requested_flag",
            self._handle_save_request_flag
        )
    
    def _handle_content_change_flag(self, flag: bool) -> None:
        """Gère le flag de changement de contenu."""
        if flag:
            # Remet le flag à False
            self.page().runJavaScript("window.content_changed_flag = false")
            # Récupère le nouveau contenu
            self.get_content(self._on_content_retrieved_for_change)
    
    def _handle_save_request_flag(self, flag: bool) -> None:
        """Gère le flag de demande de sauvegarde."""
        if flag:
            self.page().runJavaScript("window.save_requested_flag = false")
            self.save_requested.emit()
    
    def _on_content_retrieved_for_change(self, content: str) -> None:
        """Callback appelé quand le contenu est récupéré après un changement."""
        if content != self._current_content:
            self._current_content = content
            self.handle_content_changed(content)
    
    def load_content(self, html_content: str) -> None:
        """
        Charge du contenu HTML dans l'éditeur.
        
        Args:
            html_content: Contenu HTML à charger
        """
        if not self._editor_ready:
            # Attend que l'éditeur soit prêt
            QTimer.singleShot(100, lambda: self.load_content(html_content))
            return
        
        # Échape le contenu pour JavaScript
        escaped_content = json.dumps(html_content)
        script = f"window.editorInterface.setContent({escaped_content})"
        
        self.page().runJavaScript(script, self._on_content_loaded)
        self._current_content = html_content
        self._logger.debug(f"Contenu chargé: {len(html_content)} caractères")
    
    def _on_content_loaded(self, result: Any) -> None:
        """Callback appelé après le chargement du contenu."""
        pass
    
    def get_content(self, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Récupère le contenu HTML actuel de l'éditeur.
        
        Args:
            callback: Fonction appelée avec le contenu récupéré
        """
        if not self._editor_ready:
            if callback:
                callback("")
            return
        
        script = "window.editorInterface.getContent()"
        
        def handle_result(content: str) -> None:
            self._current_content = content or ""
            if callback:
                callback(self._current_content)
        
        self.page().runJavaScript(script, handle_result)
    
    def insert_content(self, html_content: str) -> None:
        """
        Insère du contenu HTML à la position du curseur.
        
        Args:
            html_content: Contenu HTML à insérer
        """
        if not self._editor_ready:
            return
        
        escaped_content = json.dumps(html_content)
        script = f"window.editorInterface.insertContent({escaped_content})"
        self.page().runJavaScript(script)
    
    def focus_editor(self) -> None:
        """Donne le focus à l'éditeur."""
        if self._editor_ready:
            self.page().runJavaScript("window.editorInterface.focus()")
    
    def handle_content_changed(self, new_content: str) -> None:
        """
        Gère les changements de contenu.
        
        Args:
            new_content: Nouveau contenu HTML
        """
        self.content_changed.emit(new_content)
        
        if self._content_change_callback:
            self._content_change_callback(new_content)
        
        self._logger.debug(f"Contenu modifié: {len(new_content)} caractères")
    
    def set_content_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Définit un callback pour les changements de contenu.
        
        Args:
            callback: Fonction appelée lors des changements
        """
        self._content_change_callback = callback
    
    def enable_auto_save(self, enabled: bool = True, interval: int = 5000) -> None:
        """
        Active ou désactive la sauvegarde automatique.
        
        Args:
            enabled: True pour activer la sauvegarde automatique
            interval: Intervalle en millisecondes entre les sauvegardes
        """
        self._auto_save_enabled = enabled
        self._auto_save_interval = interval
        
        if enabled and self._editor_ready:
            self._auto_save_timer.start(interval)
        else:
            self._auto_save_timer.stop()
        
        self._logger.info(f"Sauvegarde automatique {'activée' if enabled else 'désactivée'}")
    
    def _auto_save_content(self) -> None:
        """Effectue une sauvegarde automatique du contenu."""
        if self._editor_ready:
            self.get_content(self._on_auto_save_content)
    
    def _on_auto_save_content(self, content: str) -> None:
        """Callback pour la sauvegarde automatique."""
        if content != self._current_content:
            self._current_content = content
            # Émet le signal pour informer qu'une sauvegarde est nécessaire
            self.save_requested.emit()
    
    def is_editor_ready(self) -> bool:
        """
        Vérifie si l'éditeur est prêt.
        
        Returns:
            True si l'éditeur est prêt
        """
        return self._editor_ready
    
    def get_current_content_sync(self) -> str:
        """
        Retourne le contenu actuel en cache (synchrone).
        
        Returns:
            Contenu HTML actuel en cache
        """
        return self._current_content
    
    def clear_content(self) -> None:
        """Vide le contenu de l'éditeur."""
        self.load_content("")
    
    def set_readonly(self, readonly: bool = True) -> None:
        """
        Définit l'éditeur en lecture seule.
        
        Args:
            readonly: True pour activer le mode lecture seule
        """
        if self._editor_ready:
            script = f"tinymce.activeEditor.setMode('{'readonly' if readonly else 'design'}')"
            self.page().runJavaScript(script)