import re
import json

# Définition des motifs regex pour les sections, sous-sections et paramètres
section_pattern = re.compile(r"SECTION:\s*(\w+)")
subsection_pattern = re.compile(r"/\*\*\s*(.+?)\s*\*\*\*/")
setting_pattern = re.compile(r'user_pref\("([^"]+)",\s*(.*?)\);')

# Initialisation des variables globales
sections = {}
current_section = None
current_subsection = None


# Fonction pour formater les noms
def format_name(name):
    # Convertit tous les caractères en minuscules et remplace les espaces par des tirets
    name = name.lower().replace(" ", "-")
    # Remplace d'autres caractères spécifiques par des chaînes plus parlantes
    name = name.replace("/", "with").replace("&", "and").replace("+", "plus")
    # Remplace les caractères restants non alphanumériques par des tirets
    name = re.sub(r"[^a-z0-9-]", "-", name)
    # Assurez-vous que le nom ne commence pas par un chiffre
    if name and name[0].isdigit():
        name = "_" + name
    return name


# Fonction pour nettoyer les chaînes pour Nix
def nix_sanitize(string):
    return string.strip().replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


# Fonction pour démarrer une nouvelle section
def start_new_section(name):
    global current_section, current_subsection
    current_section = format_name(name)
    current_subsection = None  # Réinitialisation de la sous-section
    sections[
        current_section
    ] = {}  # Initialiser avec un dictionnaire vide pour les sous-sections


# Fonction pour démarrer une nouvelle sous-section
def start_new_subsection(name):
    global current_subsection
    formatted_name = format_name(name)
    current_subsection = {
        "settings": []
    }  # Initialiser avec une liste vide pour les paramètres
    sections[current_section][formatted_name] = current_subsection


# Fonction pour fermer la section actuelle
def close_section():
    global current_section, sections
    if current_section and sections[current_section]:
        # Définir les métadonnées ici
        sections[current_section]["meta"] = {
            "title": current_section,  # Utiliser le nom de la section comme titre
            "description": "",
            "links": {},
            "parrots": [],
        }


# Fonction pour fermer la sous-section actuelle
def close_subsection():
    global current_subsection
    if current_subsection:
        # Définir les métadonnées ici
        current_subsection["meta"] = {
            "title": current_subsection.get("meta", {}).get("title", "default"),
            "description": "",
            "links": {},
        }


# Lecture du fichier user.js et traitement ligne par ligne
with open("temp_user.js", "r") as file:
    for line in file:
        line = line.strip()

        if section_match := section_pattern.search(line):
            close_subsection()  # Fermer la sous-section précédente
            close_section()  # Fermer la section précédente
            start_new_section(section_match.group(1).strip())
        elif subsection_match := subsection_pattern.match(line):
            close_subsection()  # Fermer la sous-section précédente
            start_new_subsection(subsection_match.group(1).strip())
        elif setting_match := setting_pattern.match(line):
            if current_subsection is None:
                start_new_subsection(
                    "default"
                )  # Créer une sous-section par défaut si nécessaire
            setting_name, setting_value = setting_match.groups()
            current_subsection["settings"].append(
                {
                    "name": setting_name,
                    "enabled": True,
                    "value": nix_sanitize(setting_value),
                }
            )

# Fermer la dernière sous-section et section avant de finir
close_subsection()
close_section()

# Convertir en JSON et imprimer
json_output = json.dumps(sections, indent=2)
print(json_output)
