import os
import zipfile
from pathlib import Path
import shutil
from io import BytesIO

# ------------------------------
# Configurations
# ------------------------------
BASE_DIR = Path(__file__).parent.parent.resolve()
ZIP_ROOT = BASE_DIR / ".release"
FINAL_ZIP = ZIP_ROOT / "EasyStatesDeadlinePlugin.zip"

PLUGIN_SRC = BASE_DIR / "src/plugins/BlenderEasyStates"
SCRIPTS_SRC = BASE_DIR / "src/scripts/Submission"
SUBMISSION_CLIENT_SRC = BASE_DIR / r"src/submission/BlenderEasyStates/Client/EasyStatesDeadlineSubmitter"

INSTALLATION_FILE = BASE_DIR / "INSTALLATION.md"
README_FILE = BASE_DIR / "README.md"

# ------------------------------
# Utility Functions
# ------------------------------
def add_folder_to_zip(zipf: zipfile.ZipFile, folder: Path, arc_root: str = ""):
    """Adds all files from folder into the zip with optional archive root."""
    for root, _, files in os.walk(folder):
        for file in files:
            full_path = Path(root) / file
            relative_path = Path(arc_root) / full_path.relative_to(folder)
            zipf.write(full_path, relative_path)

def add_nested_zip(zipf: zipfile.ZipFile, folder: Path, zip_inside_path: str):
    """Creates a zip from a folder and adds it as a file inside another zip."""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as nested_zip:
        for root, _, files in os.walk(folder):
            for file in files:
                full_path = Path(root) / file
                relative_path = full_path.relative_to(folder)
                nested_zip.write(full_path, relative_path)
    zipf.writestr(zip_inside_path, buffer.getvalue())

def add_file_to_zip(zipf: zipfile.ZipFile, file_path: Path, arc_name: str = None):
    """Adds a single file to the zip, optionally with a specific archive name."""
    if file_path.exists():
        zipf.write(file_path, arc_name or file_path.name)

# ------------------------------
# Main
# ------------------------------
def main():
    # Clear previous dist folder
    if ZIP_ROOT.exists():
        shutil.rmtree(ZIP_ROOT)
    ZIP_ROOT.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(FINAL_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add plugins
        add_folder_to_zip(zipf, PLUGIN_SRC, arc_root="plugins/BlenderEasyStates")
        # Add scripts
        add_folder_to_zip(zipf, SCRIPTS_SRC, arc_root="scripts/Submission")
        # Add nested submission client zip
        add_nested_zip(
            zipf,
            SUBMISSION_CLIENT_SRC,
            "submission/BlenderEasyStates/Client/EasyStatesDeadlineSubmitter.zip"
        )
        # Add INSTALLATION.md and README.md to zip root
        add_file_to_zip(zipf, INSTALLATION_FILE)
        add_file_to_zip(zipf, README_FILE)

    print(f"Created final zip: {FINAL_ZIP}")

if __name__ == "__main__":
    main()
