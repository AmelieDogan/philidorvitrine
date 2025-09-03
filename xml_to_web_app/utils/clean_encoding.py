import html

# Lis ton fichier
with open("fichier.xml", "r", encoding="utf-8") as f:
    contenu = f.read()

# Décode les entités HTML/XML
contenu_decode = html.unescape(contenu)

# Sauvegarde dans un nouveau fichier (ou remplace l'ancien si tu préfères)
with open("fichier_decode.xml", "w", encoding="utf-8") as f:
    f.write(contenu_decode)