import os

def create_project_structure():
    # Define the base project structure
    structure = {
        "config": {
            "settings.py": ""  # Placeholder file for configuration
        },
        "src": {
            "main.py": "",  # Entry point for the application
            "oauth.py": "",  # OAuth 2.0 flow logic
            "api.py": "",  # Instagram Graph API interactions
            "automation.py": "",  # Reply automation logic
            "utils.py": ""  # Utility/helper functions
        },
        "templates": {
            "login.html": "",  # Login page for OAuth
            "error.html": ""  # Error page for failed logins
        },
        "static": {
            "css": {},  # Folder for CSS files
            "js": {}  # Folder for JavaScript files
        },
        "tests": {
            "test_api.py": "",  # Tests for Instagram API interactions
            "test_oauth.py": "",  # Tests for OAuth flow
            "test_automation.py": ""  # Tests for reply automation
        },
    }

    def create_dir(path, structure):
        for name, content in structure.items():
            full_path = os.path.join(path, name)
            if isinstance(content, dict):
                if os.path.exists(full_path):
                    os.rmdir(full_path)  # Remove the directory first if it exists
                os.makedirs(full_path, exist_ok=True)
                create_dir(full_path, content)
            else:
                if os.path.exists(full_path):
                    os.remove(full_path)  # Remove the file if it exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write(content)

    # Start creating directories from the current directory
    create_dir(".", structure)

if __name__ == "__main__":
    create_project_structure()
