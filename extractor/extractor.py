import re
import json
import ast

section_pattern = re.compile(r"SECTION:\s*(\w+)")
subsection_pattern = re.compile(r"/\*\*\s*(.+?)\s*\*\*\*/")
setting_pattern = re.compile(r'user_pref\("([^"]+)",\s*(.*?)\);')

sections = {}
current_section = None
current_subsection = None

def format_name(name):
    name = name.lower().replace(" ", "-").replace('/', 'with').replace('&', 'and').replace('+', 'plus')
    return re.sub(r'[^a-z0-9_-]', '', name)

def ensure_current_section():
    global current_section
    if current_section is None:
        start_new_section("default")

def ensure_subsection():
    global current_subsection
    if current_subsection is None:
        current_subsection = {"meta": {"title": "default", "description": "", "links": {}}, "settings": []}
        if current_section is not None:
            sections[current_section]["default"] = current_subsection

def start_new_section(name):
    global current_section, current_subsection
    current_section = format_name(name)
    sections[current_section] = {"meta": {}, "settings": []}
    current_subsection = None

def start_new_subsection(name):
    global current_subsection
    ensure_current_section()
    name = format_name(name)
    current_subsection = {"meta": {"title": name, "description": "", "links": {}}, "settings": []}
    sections[current_section][name] = current_subsection

def parse_setting_value(value):
    try:
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value

with open("temp_user.js", "r") as file:
    for line in file:
        line = line.strip()

        section_match = section_pattern.search(line)
        if section_match:
            start_new_section(section_match.group(1))
            continue

        subsection_match = subsection_pattern.match(line)
        if subsection_match:
            start_new_subsection(subsection_match.group(1))
            continue

        setting_match = setting_pattern.match(line)
        if setting_match:
            ensure_subsection()
            setting_name, setting_value_raw = setting_match.groups()
            setting_value = parse_setting_value(setting_value_raw)
            current_subsection["settings"].append({"name": setting_name, "enabled": True, "value": setting_value})

json_output = json.dumps(sections, indent=2)
print(json_output)
