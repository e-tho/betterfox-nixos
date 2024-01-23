import re
import json

def nix_sanitize(string):
    return string.strip().replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

section_pattern = re.compile(r'/\*\*\*\s*SECTION: (.+?)\s*\*\*\*/')
subsection_pattern = re.compile(r'/\*\*\s*(.+?)\s*\*\*\*/')
setting_pattern = re.compile(r'user_pref\("([^"]+)",\s*(.*?)\);')

sections = {}
current_section = None
current_subsection = None

def format_name(name):
    return name.lower().replace(' ', '-')

def start_new_subsection(name):
    global current_subsection
    formatted_name = format_name(name)
    current_subsection = {
        "meta": {"title": formatted_name, "description": "", "links": {}},
        "settings": []
    }
    if current_section not in sections:
        sections[current_section] = {}
    sections[current_section][formatted_name] = current_subsection

with open("/home/etho/Code/betterfox-nixos/extractor/user.js", "r") as file:
    for line in file:
        line = line.strip()

        # Check for a section header
        if section_match := section_pattern.match(line):
            current_section = format_name(section_match.group(1).strip())
            print(f"Starting new section: {current_section}")  # Debug print
            continue

        # Check for a subsection header
        if subsection_match := subsection_pattern.match(line):
            subsection_name = subsection_match.group(1).strip()
            start_new_subsection(subsection_name)
            print(f"Starting new subsection: {subsection_name}")  # Debug print
            continue

        # Check for a user preference setting
        if setting_match := setting_pattern.match(line):
            setting_name, setting_value = setting_match.groups()
            setting = {"name": setting_name, "enabled": True, "value": setting_value}
            current_subsection["settings"].append(setting)
            print(f"Adding setting: {setting_name}")  # Debug print
            continue

        # Other processing (e.g., metadata) can be added here

# Convert to JSON
json_output = json.dumps(sections, indent=2)
print(f"JSON Output: {json_output}") 

# Output to a file
with open("betterfox_sections.json", "w") as out_file:
    out_file.write(json_output)
