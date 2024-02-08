import requests
import subprocess
import re
import os

def generate_version(default_file, version):
    print(f"Generating v{version}")

    url = f"https://raw.githubusercontent.com/yokoffing/Betterfox/{version}/user.js"
    response = requests.get(url)
    if response.status_code == 200:
        user_js_content = response.text

        # Writing the content to a temporary user.js file
        with open("temp_user.js", "w") as file:
            file.write(user_js_content)

        # Running the betterfox-extractor script on the user.js file
        extractor_command = f"betterfox-extractor temp_user.js > {version}.json"
        subprocess.run(extractor_command, shell=True)

        # Writing the Nix expression to the default file
        default_file.write(
            f'  "{version}" = builtins.readFile ./{version}.json;\n'
        )

        # Remove the temporary file
        os.remove("temp_user.js")
    else:
        print(f"Failed to download {url}")


def main():
    # Start writing to default.nix
    with open("default.nix", "w") as default_file:
        default_file.write("{\n")

        # Manually process the master version
        generate_version(default_file, "master")

        # Fetch tags from the Betterfox GitHub repository
        response = requests.get("https://api.github.com/repos/yokoffing/Betterfox/tags")
        tags = response.json()

        # Process each tag/version
        for tag in tags:
            version = tag["name"]
            # Check if the version matches the required format (e.g., "119.0", "118.0", etc.)
            if re.match(r"^\d+\.\d+$", version):
                generate_version(default_file, version)

        # End of the default.nix file
        default_file.write("}\n")

if __name__ == "__main__":
    main()
