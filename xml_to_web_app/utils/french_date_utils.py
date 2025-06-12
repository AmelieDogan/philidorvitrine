"""
Utilitaires pour le formatage des dates et heures à la française
"""

from datetime import datetime
from typing import Union, Optional
import locale

def format_french_datetime(
    dt: Union[datetime, str], 
    include_time: bool = True,
    include_seconds: bool = False,
    relative: bool = False
) -> str:
    """
    Formate une date/heure au format français.
    
    Args:
        dt: datetime object ou string ISO
        include_time: inclure l'heure (défaut: True)
        include_seconds: inclure les secondes (défaut: False)
        relative: afficher en format relatif si récent (défaut: False)
    
    Returns:
        str: Date formatée en français
        
    Examples:
        >>> format_french_datetime(datetime.now())
        "11 juin 2025 à 14:30"
        
        >>> format_french_datetime(datetime.now(), include_seconds=True)
        "11 juin 2025 à 14:30:45"
        
        >>> format_french_datetime(datetime.now(), include_time=False)
        "11 juin 2025"
    """
    
    # Conversion string vers datetime si nécessaire
    if isinstance(dt, str):
        try:
            # Essaie plusieurs formats courants
            formats = [
                "%Y-%m-%d %H:%M:%S.%f",  # Format avec microsecondes
                "%Y-%m-%d %H:%M:%S",     # Format standard
                "%Y-%m-%dT%H:%M:%S.%f",  # Format ISO avec microsecondes
                "%Y-%m-%dT%H:%M:%S",     # Format ISO
                "%Y-%m-%d",              # Date seule
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(dt, fmt)
                    break
                except ValueError:
                    continue
            else:
                # Si aucun format ne fonctionne, essaie le parsing automatique
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                
        except (ValueError, TypeError) as e:
            return f"Date invalide: {dt}"
    
    if not isinstance(dt, datetime):
        return "Format de date non supporté"
    
    # Noms des mois en français
    mois_francais = [
        "", "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]
    
    # Format de base : jour mois année
    jour = dt.day
    mois = mois_francais[dt.month]
    annee = dt.year
    
    date_str = f"{jour} {mois} {annee}"
    
    # Ajout de l'heure si demandé
    if include_time:
        if include_seconds:
            heure_str = dt.strftime("%H:%M:%S")
        else:
            heure_str = dt.strftime("%H:%M")
        date_str += f" à {heure_str}"
    
    # Format relatif si demandé et récent
    if relative:
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            # Aujourd'hui
            if include_time:
                if include_seconds:
                    return f"Aujourd'hui à {dt.strftime('%H:%M:%S')}"
                else:
                    return f"Aujourd'hui à {dt.strftime('%H:%M')}"
            else:
                return "Aujourd'hui"
        elif diff.days == 1:
            # Hier
            if include_time:
                if include_seconds:
                    return f"Hier à {dt.strftime('%H:%M:%S')}"
                else:
                    return f"Hier à {dt.strftime('%H:%M')}"
            else:
                return "Hier"
        elif diff.days < 7:
            # Cette semaine
            jours_francais = [
                "lundi", "mardi", "mercredi", "jeudi", 
                "vendredi", "samedi", "dimanche"
            ]
            jour_semaine = jours_francais[dt.weekday()]
            if include_time:
                if include_seconds:
                    return f"{jour_semaine.capitalize()} à {dt.strftime('%H:%M:%S')}"
                else:
                    return f"{jour_semaine.capitalize()} à {dt.strftime('%H:%M')}"
            else:
                return jour_semaine.capitalize()
    
    return date_str


def format_french_date_short(dt: Union[datetime, str]) -> str:
    """
    Formate une date au format court français (JJ/MM/AAAA).
    
    Args:
        dt: datetime object ou string ISO
        
    Returns:
        str: Date au format JJ/MM/AAAA
        
    Example:
        >>> format_french_date_short(datetime.now())
        "11/06/2025"
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return "Date invalide"
    
    if not isinstance(dt, datetime):
        return "Format non supporté"
    
    return dt.strftime("%d/%m/%Y")


def format_duration_french(seconds: Union[int, float]) -> str:
    """
    Formate une durée en secondes vers un format français lisible.
    
    Args:
        seconds: Durée en secondes
        
    Returns:
        str: Durée formatée en français
        
    Examples:
        >>> format_duration_french(3661)
        "1 heure et 1 minute"
        
        >>> format_duration_french(90)
        "1 minute et 30 secondes"
    """
    if seconds < 0:
        return "Durée négative"
    
    # Conversion en entier
    seconds = int(seconds)
    
    heures = seconds // 3600
    minutes = (seconds % 3600) // 60
    secondes = seconds % 60
    
    parts = []
    
    if heures > 0:
        if heures == 1:
            parts.append("1 heure")
        else:
            parts.append(f"{heures} heures")
    
    if minutes > 0:
        if minutes == 1:
            parts.append("1 minute")
        else:
            parts.append(f"{minutes} minutes")
    
    if secondes > 0 and heures == 0:  # Ne pas afficher les secondes si on a des heures
        if secondes == 1:
            parts.append("1 seconde")
        else:
            parts.append(f"{secondes} secondes")
    
    if not parts:
        return "0 seconde"
    
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} et {parts[1]}"
    else:
        return f"{', '.join(parts[:-1])} et {parts[-1]}"