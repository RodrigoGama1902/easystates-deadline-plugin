from pathlib import Path
import shutil
import zipfile

# Paths
ROOT = Path(__file__).resolve().parent.parent

SRC_BLENDER_ADDON = ROOT / "src" / "blender-addon" / "easystates_deadline_plugin"
SRC_DEADLINE_PLUGIN = ROOT / "src" / "deadline-plugin" / "BlenderEasyStates"

RELEASE = ROOT / "release"
SUBMISSION = RELEASE / "submission" / "BlenderEasyStates"
PLUGINS = RELEASE / "plugins" / "BlenderEasyStates"

FINAL_DIST = RELEASE / "easystates_deadline_plugin.zip"
README = ROOT / "README.md"
INSTALLATION = ROOT / "INSTALLATION.md"


def ensure_clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def make_zip_from_folder(src_folder: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in src_folder.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(src_folder.parent)
                zf.write(file, rel_path)


def main():
    RELEASE.mkdir(exist_ok=True)

    # 1. Create submission subfolder and addon zip inside it
    ensure_clean_dir(SUBMISSION)
    addon_zip = SUBMISSION / "BlenderEasyStates.zip"
    make_zip_from_folder(SRC_BLENDER_ADDON, addon_zip)

    # 2. Copy Deadline plugin files
    ensure_clean_dir(PLUGINS)
    shutil.copytree(SRC_DEADLINE_PLUGIN, PLUGINS, dirs_exist_ok=True)

    # 3. Create final dist zip
    if FINAL_DIST.exists():
        FINAL_DIST.unlink()

    with zipfile.ZipFile(FINAL_DIST, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add submission folder contents
        for file in SUBMISSION.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(RELEASE)
                zf.write(file, rel_path)

        # Add plugins folder contents
        for file in (PLUGINS.parent).rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(RELEASE)
                zf.write(file, rel_path)

        # Add README.md at root
        zf.write(README, README.name)
        zf.write(INSTALLATION, INSTALLATION.name)

    print(f"✅ Final distribution created at: {FINAL_DIST}")


if __name__ == "__main__":
    main()
