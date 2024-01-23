import requests
import subprocess
import re

def generate_version(default_file, version):
    print(f"Generating v{version}")
    # Update the URL to point to the Betterfox repository
    script = f"curl -s https://raw.githubusercontent.com/yokoffing/Betterfox/{version}/user.js > {version}.js"
    subprocess.run(script, shell=True)
    # Add processing logic here if necessary
    default_file.write(
        f'  "{version}" = builtins.readFile ./{version}.js;\n'
    )

def main():
    # Fetch tags from the Betterfox GitHub repository
    response = requests.get("https://api.github.com/repos/yokoffing/Betterfox/tags")
    tags = response.json()

    with open("default.nix", "w") as default_file:
        default_file.write("{\n")

        # Process each tag
        for tag in tags:
            version = tag["name"]
            # Check if the version matches the required format (e.g., "119.0", "118.0", etc.)
            if re.match(r"^\d+\.\d+$", version):
                generate_version(default_file, version)

        default_file.write("}\n")
        print(f"Default file: {default_file}") 

if __name__ == "__main__":
    main()
