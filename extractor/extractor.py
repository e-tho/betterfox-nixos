import re
import json

section_pattern = re.compile(r"SECTION:\s*(\w+)")
subsection_pattern = re.compile(r"/\*\*\s*(.+?)\s*\*\*\*/")
setting_pattern = re.compile(r'user_pref\("([^"]+)",\s*(.*?)\);')

sections = {}
current_section = None
current_subsection = None


def format_name(name):
    return name.lower().replace(" ", "-")


def start_new_section(name):
    global current_section, current_subsection
    current_section = format_name(name)
    current_subsection = None  # Reset subsection when starting a new section


def start_new_subsection(name):
    global current_subsection
    if name is None:  # For default subsection
        name = "default"
    formatted_name = format_name(name)
    current_subsection = {
        "meta": {"title": formatted_name, "description": "", "links": {}},
        "settings": [],
    }
    if current_section not in sections:
        sections[current_section] = {}
    sections[current_section][formatted_name] = current_subsection


with open("temp_user.js", "r") as file:
    for line in file:
        line = line.strip()
        # print(f"COUCOU: {section_pattern.search(line)}")

        if section_match := section_pattern.search(line):
            start_new_section(section_match.group(1).strip())
            continue

        if subsection_match := subsection_pattern.match(line):
            start_new_subsection(subsection_match.group(1).strip())
            continue

        if setting_match := setting_pattern.match(line):
            if current_subsection is None:  # Initialize default subsection if necessary
                start_new_subsection(None)
            setting_name, setting_value = setting_match.groups()
            setting = {"name": setting_name, "enabled": True, "value": setting_value}
            current_subsection["settings"].append(setting)
            continue

json_output = json.dumps(sections, indent=2)
print(f"{json_output}")
