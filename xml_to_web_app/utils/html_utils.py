from bs4 import BeautifulSoup
import html

def truncate_html_safely(encoded_html: str, max_chars: int = 400) -> str:
    # Déséchapper le HTML encodé
    decoded_html = html.unescape(encoded_html)
    soup = BeautifulSoup(decoded_html, "html.parser")

    char_count = 0
    truncated = []
    last_text_node = None
    last_text_content = ""

    def recurse(node):
        nonlocal char_count, last_text_node, last_text_content
        if char_count >= max_chars:
            return None
        if node.name is None:
            text = node.string or ""
            allowed = max_chars - char_count
            cut = text[:allowed]
            char_count += len(cut)
            
            # Mémoriser le dernier nœud texte traité
            if cut:
                last_text_node = cut
                last_text_content = text
            
            return cut
        else:
            tag = soup.new_tag(node.name, **node.attrs)
            for child in node.contents:
                part = recurse(child)
                if part is None:
                    break
                tag.append(part)
            return tag

    for child in soup.body.contents if soup.body else soup.contents:
        part = recurse(child)
        if part:
            truncated.append(part)

    # Après traitement, si on a tronqué du texte, ajouter les points de suspension
    if char_count >= max_chars and last_text_node and len(last_text_content) > len(last_text_node):
        # Trouver le dernier nœud texte dans les éléments tronqués et y ajouter "..."
        result_html = ''.join(str(e) for e in truncated)
        
        # Si le dernier texte ajouté peut être rallongé de 3 caractères
        if len(last_text_node) >= 3:
            # Remplacer les 3 derniers caractères par "..."
            result_html = result_html.replace(last_text_node, last_text_node[:-3] + "...")
        else:
            # Simplement ajouter "..." à la fin
            result_html += "..."
        
        return result_html

    return ''.join(str(e) for e in truncated)