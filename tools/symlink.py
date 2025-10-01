from pathlib import Path
import os

# Source directories in your local project
SOURCE = Path(__file__).resolve().parent.parent / "src"
FOLDERS = ["scripts", "submission", "plugins"]

# Target directory (Deadline Repository)
DEADLINE_REPO = Path(r"C:\DeadlineRepository10")

def link_new_files(src_dir: Path, dst_dir: Path):
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src_path in src_dir.rglob("*"):
        if src_path.is_file():
            rel_path = src_path.relative_to(src_dir)
            dst_path = dst_dir / rel_path
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            if not dst_path.exists():
                try:
                    os.symlink(src_path, dst_path)
                    print(f"✅ Symlinked: {dst_path} -> {src_path}")
                except OSError as e:
                    print(f"❌ Failed to create symlink: {dst_path} -> {src_path} | {e}")

def main():
    for folder_name in FOLDERS:
        src_folder = SOURCE / folder_name
        dst_folder = DEADLINE_REPO / folder_name

        if not src_folder.exists():
            print(f"❌ Source folder does not exist: {src_folder}")
            continue

        link_new_files(src_folder, dst_folder)

if __name__ == "__main__":
    main()